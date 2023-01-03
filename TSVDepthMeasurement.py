import pandas as pd
import matplotlib.pyplot as plt
import Subroutine as S
import sys
import re
Command = sys.argv
Command = S.ReadCommand(Command)


#The CCD Pixel Value 
CCDPixel = 1024

#MinFFTBoundary is The peak value corresponds to the value of the x-axis
#If the x-axis value is less than this value
MinFFTBoundary = 10

# MinFFTValue is the FFT minimum peak-to-average ratio
# If FFT Peak x-aris less than this value
# The Depth is "unknown"
MinFFTRatio = 13

# define unit
Unit_nm = pow(10, -9)
Unit_um = pow(10, -6)

#Read Excel
if Command["-m"] == "excel":
    #Read Excel Data
    ReadExcelFileName  = Command["-f"]
    ReadExcelSheelName = Command["-s"]
    ReadExcelWaveLength = Command["-l"]
    ReadExcelReflectance = Command["-r"]
    ReadExcelColumn    = [ReadExcelWaveLength, ReadExcelReflectance]

    # Read File 
    ExcelDataFrame = pd.read_excel( ReadExcelFileName              ,
                                    sheet_name = ReadExcelSheelName,
                                    usecols    = ReadExcelColumn )
    #======================================================================
    # Change DataType "DataFrame" to "List"
    InputDataList = ExcelDataFrame.values.tolist()
    # Put All List to WaveLength List, Reflectance List, WaveNumber List
    # Wave Length: From small to large.
    # Wave Number: From large to small.
    ReadWLList = []
    ReadRList  = []
    ReadWNList = []
    for Leng in range(len(InputDataList)):
        ReadWLList.append(InputDataList[Leng][0] * Unit_nm)
        ReadRList .append(InputDataList[Leng][1])
        ReadWNList.append(1 / ReadWLList[Leng])
    #======================================================================

#Read Spt
elif Command["-m"] == "spt":
    ReadSptFileName = Command["-f"]
    ReadWLList = []
    ReadRList  = []
    ReadWNList = []
    f = open(ReadSptFileName, "r")
    text = f.readlines() 
    for cnt in range(len(text)):
        if text[cnt].find(":") == -1:
            SplitSign = re.compile('\s+') 
            textTemp = SplitSign.split(text[cnt])
            ReadWLList.append(float(textTemp[0])* Unit_nm)
            ReadRList.append(float(textTemp[1]))
            ReadWNList.append(1 / (float(textTemp[0])* Unit_nm))
    f.close()





# Calculate DMax, DMin, Delta Wave Number
MinDepth = 1/(2*(max(ReadWNList)-min(ReadWNList)))
MaxDepth = CCDPixel/2 /(2*(max(ReadWNList)-min(ReadWNList)))
DeltaWN1  = (max(ReadWNList)-min(ReadWNList))/CCDPixel


# Calculate New Wave Number (Equal CCD Pixel)
NewWNList = S.GetNewWaveNumber2(CCDPixel, ReadWNList)

# Calculate New Reflectance(Interpolation)
NewRList = S.GetNewReflectance2(CCDPixel, ReadWNList, ReadRList)

# Calculate LowPass & HighPass Reflectance 
NewRListLowPass = S.Convolution(NewRList, 5, 20 , 1)
NewRListHighPass = S.HighPassFilter(NewRList, NewRListLowPass)
NewRListHPFFT = S.FFTABS(NewRListHighPass)
FFTABSListCopy = NewRListHPFFT.copy()
depth = S.TSVDepth(NewRListHPFFT, NewWNList, MinFFTBoundary, MinFFTRatio)
depth_axis = [(i/(2*(NewWNList[0]-NewWNList[-1]))/Unit_um) for i in range(1024)]
#======================================================================

#plt.subplot(121)
#plt.title("FFT")
#plt.plot(NewWNList, FFTABSListCopy)
#
#plt.subplot(122)
#plt.title("FFT")
#plt.plot(depth_axis, NewRListHPFFT)
#plt.tight_layout()
#plt.show()
if Command["-m"] == "excel":
    print("Excel: " + ReadExcelFileName)
    print("Column: " + ReadExcelReflectance)
    print("Min Measureable: ", round(MinDepth/Unit_um,3), " um")
    print("Max Measureable: ", round(MaxDepth/Unit_um,3), " um")
    print("TSV depth: " , depth)

elif Command["-m"] == "spt":
    print("Spt: " + ReadSptFileName)
    print("Min Measureable: ", round(MinDepth/Unit_um,3), " um")
    print("Max Measureable: ", round(MaxDepth/Unit_um,3), " um")
    print("TSV depth: " , depth)
#
plt.subplot(221)
plt.title("Origin")
plt.plot(ReadWNList, ReadRList)

plt.subplot(222)
plt.title("New")
plt.plot(NewWNList, NewRList)

plt.subplot(223)
plt.title("HighPass")
plt.plot(NewWNList, NewRListHighPass)

plt.subplot(224)
plt.title("HighPassFFT")
plt.plot(NewWNList, NewRListHPFFT)

plt.tight_layout()
plt.show()




#OutputExcelName = "3_1 Result"
#
#
#OriDataFrame = pd.DataFrame({   "Original Wave Number"       : InWNList ,
#                                "Original Reflectance"       : InRList  ,
#                            })
#
#NewDataFrame = pd.DataFrame({   "New Wave Number"            : NewWNList,
#                                "New Reflectance"            : NewRList ,
#                                "Low Pass (Smooth 20 times)" : LowPass  ,
#                                "High Pass (Division)"       : HighPass
#                            })
#writer = pd.ExcelWriter(OutputExcelName + ".xlsx", engine='xlsxwriter')
#
#OriDataFrame.to_excel(writer, sheet_name="Origin")
#NewDataFrame.to_excel(writer, sheet_name="New")
#writer.save()