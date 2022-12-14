import scipy
import sys


def ReadCommand(Command):
    # Find file mode
    ModeIndex = Command.index("-m")
    Mode = Command[ModeIndex + 1]
    #Excel Command dict
    ExcelCommand = {
        "-m": "Mode",
        "-f": "ExcelFileName",
        "-s": "ExcelFileSheet",
        "-l": "ExcelWaveLength",
        "-r": "Reflectance"
    }

    #spt Command dict
    SptCommand = {
        "-m": "Mode",
        "-f": "SptFileName"
    }

    #Read Command and return
    match Mode:
        case "excel":
            for cnt in range(len(Command)):
                if Command[cnt] in ExcelCommand:
                    ExcelCommand[Command[cnt]] = Command[cnt+1]
            return ExcelCommand
                    

        case "spt":
            for cnt in range(len(Command)):
                if Command[cnt] in SptCommand:
                    SptCommand[Command[cnt]] = Command[cnt+1]
            return SptCommand
    
        

def Convolution(lis,num,times,mode):
    l = lis.copy()
    NewL = []
    if num % 2 == 0: # Convolution kernal need odd number
        print("Please enter a odd number")
        return -1

    for t in range(times):

        if t != 0:
            l = NewL.copy()

        NewL = []

        for n in range(int(num/2)): # zero padding
            if mode == 1:
                l.insert(0, l[0])
                l.append(l[len(l) - 1])
            elif mode == 0:
                l.insert(0, 0)
                l.append(0)
            else:
                print("Invaild mode (0: zero padding, 1: pass value)")
                return -1

        for c in range(0, len(l) - num +1): # Do convolution From list[0] to list[len-num]. (Because zero padding)
           
            S = 0
            for n in range(num):
                S += l[c+n]
            NewL.append(S/num)
        
    return NewL


def GetNewWaveNumber1(CCDPixel, InWNList):
    # Calculate New Wave: delta t = (tmax-tmin)/Pixel
    DeltaWN1  = (max(InWNList)-min(InWNList))/CCDPixel

    # Calculate New Wave Number (Equal CCD Pixel)
    # New Wave Number: From Large to small
    NewWNList = []
    for Leng in range(CCDPixel):
        NewWNList.append(max(InWNList) - DeltaWN1 * Leng)

    return NewWNList


def GetNewReflectance1(CCDPixel, InWNList, InRList):

    # Calculate New Reflectance(Interpolation)
    NewWNList = GetNewWaveNumber1(CCDPixel, InWNList)
    NewRList = []
    for Leng in range(CCDPixel):
        Closest = min(InWNList, key=lambda x: abs(x-NewWNList[Leng]))
        Closest_Location = InWNList.index(Closest)
        # Fine NewWaveNumber in InputWaveNumber
        if (NewWNList[Leng] == InWNList[Closest_Location]): 
            Location = InWNList.index(NewWNList[Leng])
            Value = InRList[Location]
        
        # Find the closest value to "NewWaveNumber" in InputWaveNumber list
        # The closest value > NewWaveNumber
        elif (InWNList[Closest_Location] > NewWNList[Leng]): 
            if Closest_Location == len(InWNList): # InputWaveNumber[len] > NewWaveNumber (NewWaveNumber out of InputWaveNumber list)
                Value = -1
            else:
                LowerLocation = Closest_Location + 1
                Lower = InWNList[LowerLocation]
                LowerGap = NewWNList[Leng] - Lower

                UpperLocation = Closest_Location
                Upper = InWNList[UpperLocation]
                UpperGap = Upper - NewWNList[Leng]
                Value = (InRList[UpperLocation] * LowerGap + InRList[LowerLocation] * UpperGap) / (LowerGap + UpperGap) #(Interpolation)
                
        # Find the closest value to "NewWaveNumber" in InputWaveNumber list
        # NewWaveNumber > The closest value 
        elif (InWNList[Closest_Location] < NewWNList[Leng]): 
            if Closest_Location == 0: # NewWaveNumber > InputWaveNumber[0] (NewWaveNumber out of InputWaveNumber list)
                Value = -1
            else:
                LowerLocation = Closest_Location
                Lower = InWNList[LowerLocation]
                LowerGap = NewWNList[Leng] - Lower
                UpperLocation = Closest_Location - 1
                Upper = InWNList[UpperLocation]
                UpperGap = Upper - NewWNList[Leng]
                Value = (InRList[UpperLocation] * LowerGap + InRList[LowerLocation] * UpperGap) / (LowerGap + UpperGap) #(Interpolation)

        NewRList.append(Value)
    return NewRList


def GetNewWaveNumber2(CCDPixel, InWNList):
    # Calculate New Wave: delta t = (tmax-tmin)/(Pixel-1)
    DeltaWN1  = (max(InWNList)-min(InWNList))/(CCDPixel-1)

    # Calculate New Wave Number (Equal CCD Pixel)
    # New Wave Number: From Large to small
    NewWNList = []
    for Leng in range(CCDPixel):
        NewWNList.append(max(InWNList) - DeltaWN1 * Leng)

    return NewWNList


def GetNewReflectance2(CCDPixel, InWNList, InRList):

    # Calculate New Reflectance(Interpolation)
    NewWNList = GetNewWaveNumber2(CCDPixel, InWNList)
    NewRList = []
    for Leng in range(CCDPixel):
        Closest = min(InWNList, key=lambda x: abs(x-NewWNList[Leng]))
        Closest_Location = InWNList.index(Closest)
        # Fine NewWaveNumber in InputWaveNumber
        if (NewWNList[Leng] == InWNList[Closest_Location]): 
            Location = InWNList.index(NewWNList[Leng])
            Value = InRList[Location]
        
        # Find the closest value to "NewWaveNumber" in InputWaveNumber list
        # The closest value > NewWaveNumber
        elif (InWNList[Closest_Location] > NewWNList[Leng]): 
            if Closest_Location == len(InWNList): # InputWaveNumber[len] > NewWaveNumber (NewWaveNumber out of InputWaveNumber list)
                Value = -1
            else:
                LowerLocation = Closest_Location + 1
                Lower = InWNList[LowerLocation]
                LowerGap = NewWNList[Leng] - Lower

                UpperLocation = Closest_Location
                Upper = InWNList[UpperLocation]
                UpperGap = Upper - NewWNList[Leng]
                Value = (InRList[UpperLocation] * LowerGap + InRList[LowerLocation] * UpperGap) / (LowerGap + UpperGap) #(Interpolation)
                
        # Find the closest value to "NewWaveNumber" in InputWaveNumber list
        # NewWaveNumber > The closest value 
        elif (InWNList[Closest_Location] < NewWNList[Leng]): 
            if Closest_Location == 0: # NewWaveNumber > InputWaveNumber[0] (NewWaveNumber out of InputWaveNumber list)
                Value = -1
            else:
                LowerLocation = Closest_Location
                Lower = InWNList[LowerLocation]
                LowerGap = NewWNList[Leng] - Lower
                UpperLocation = Closest_Location - 1
                Upper = InWNList[UpperLocation]
                UpperGap = Upper - NewWNList[Leng]
                Value = (InRList[UpperLocation] * LowerGap + InRList[LowerLocation] * UpperGap) / (LowerGap + UpperGap) #(Interpolation)

        NewRList.append(Value)
    return NewRList


def HighPassFilter(NewRList, LowPass):
    HighPass = []
    for l in range(len(NewRList)):
        HighPass.append(NewRList[l]/LowPass[l])
    return HighPass


def FFTABS(List):
    Array = scipy.fftpack.fft(List)
    ABSArray = abs(Array)

    ABSList  = ABSArray.tolist()
    return ABSList


def TSVDepth(FFTHPList, NewWNList, MinBoundary, MinRatio):
    #InputList = FFTHPList.copy()
    InputList = FFTHPList
    InputList[0] = 0
    for leng in range(len(InputList)):
        if leng >= len(NewWNList)/2:
            InputList[leng] = 0
    location = 0
    
    while(location < MinBoundary):
        InputList[location] = 0
        location = InputList.index(max(InputList))
    Average = round(sum(InputList)/len(InputList),3)
    Peak = round(InputList[location],3)
    if Peak/Average < MinRatio:
        Depth = "Unknown"
    else:
        Depth = location/(2*(NewWNList[0]-NewWNList[-1]))
        Unit_um = pow(10, -6)
        Depth = round(Depth/Unit_um,3)
        Depth = str(Depth) + " um"
    return Depth

