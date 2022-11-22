import pandas as pd
import matplotlib.pyplot as plt
import Subroutine as S
ExcelFileName  = "S_4x_All.xls"
ExcelSheelName = "Sheet1"
ExcelWaveLength = "wavelength"
ExcelReflectance = "10_8"

ExcelColumn    = [ExcelWaveLength, ExcelReflectance]

CCDPixel = 1024
Unit_nm = pow(10, -9)
Unit_um = pow(10, -6)
# Read File 
ExcelDataFrame = pd.read_excel( ExcelFileName              ,
                                sheet_name = ExcelSheelName,
                                usecols    = ExcelColumn    )
#======================================================================

# Change DataType "DataFrame" to "List"
ExcelDataList = ExcelDataFrame.values.tolist()
#======================================================================

# Put AllExcel List to WaveLength List, Reflectance List, WaveNumber List
# Wave Length: From small to large.
# Wave Number: From large to small.
InWLList = []
InRList  = []
InWNList = []
for Leng in range(len(ExcelDataList)):
    InWLList.append(ExcelDataList[Leng][0] * Unit_nm)
    InRList .append(ExcelDataList[Leng][1])
    InWNList.append(1 / InWLList[Leng])
#======================================================================
# Calculate DMax, DMin, Delta Wave Number
MinDepth = 1/(2*(max(InWNList)-min(InWNList)))
MaxDepth = CCDPixel/2 /(2*(max(InWNList)-min(InWNList)))
DeltaWN1  = (max(InWNList)-min(InWNList))/CCDPixel


# Calculate New Wave Number (Equal CCD Pixel)
NewWNList = S.GetNewWaveNumber2(CCDPixel, InWNList)

# Calculate New Reflectance(Interpolation)
NewRList = S.GetNewReflectance2(CCDPixel, InWNList, InRList)

# Calculate LowPass & HighPass Reflectance 
NewRListLowPass = S.Convolution(NewRList, 5, 20 , 1)
NewRListHighPass = S.HighPassFilter(NewRList, NewRListLowPass)
NewRListHPFFT = S.FFTABS(NewRListHighPass)
#======================================================================
print("Min Measureable: ", round(MinDepth/Unit_um,3), " um")
print("Max Measureable: ", round(MaxDepth/Unit_um,3), " um")
depth = S.TSVDepth(NewRListHPFFT, NewWNList)
print("Excel: " + ExcelFileName)
print("Column: " + ExcelReflectance)
print("TSV depth: " , round(depth/Unit_um,3), " um")

plt.subplot(221)
plt.title("Origin")
plt.plot(InWNList, InRList)

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