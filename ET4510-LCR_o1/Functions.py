import os
import pandas as pd
import numpy as np
import time
import serial

"""Device communication functions."""
def DeviceConnect(COMPort): 
    ser = serial.Serial(COMPort, 9600, timeout = 1) 
    return ser 

def DeviceDisconnect(ser):
    return ser.close()

"""Omega CN740 communication functions."""


"""LCR meter communication."""
def LCRDataReadout(ser):
    ser.write('FETCH?\n'.encode()) 
    readout = []
    while True:
        readout.append(ser.readline().decode().strip())
        if len(readout) == 2:
            break
    return readout[1]

def LCRCommander(ser, command):
    ser.write(f'{command} \n'.encode())

    while True:
        if ser.readline().decode().strip() == 'exec success':
            break

def Frequencies(minFreq, maxFreq, numberOfpoints):
    frequencies = np.logspace(np.log10(minFreq), np.log10(maxFreq), num = numberOfpoints)
    return np.round(frequencies).astype(int)

def DataAveraging(ser,numMeasurements):
    data = np.array([0,2]) #preallocate array
    for i in range(0,numMeasurements): # number of measurements to average
        data = np.vstack([data, np.float64(LCRDataReadout(ser).split(','))])
    data = np.delete(data, 0, axis = 0) # remove the preallocated row
    data = np.array([np.mean(data[::,0]), np.std(data[::,0]), np.mean(data[::,1]), np.std(data[::,1])])
    return data

# create a stablity timer based on frequency
def TimeAdjustments(freq):
    if freq < 100:
        time.sleep(10)
    elif freq <= 1000:
        time.sleep(2)

def Experiment(ser, freqencies, mainMeasurement, minorMeasurement, voltage, biasVoltage, numMeasurements):
    df = pd.DataFrame(freqencies, columns = ['Frequency'])
    
    LCRCommander(ser, f'VOLT {voltage*1e3}')
    if biasVoltage is not None:
        LCRCommander(ser, f'BIAS:VOLT {int(biasVoltage*1e3)}') # mV in SCPI

    for k in mainMeasurement:
        LCRCommander(ser, f'FUNC:IMP:A {k}') # Major parameter to be measured

        for i in minorMeasurement:
            LCRCommander(ser, f'FUNC:IMP:B {i}') # Minor parameter to be measured
            
            # create a name for the column
            minorParmName = "-".join([k,i])

            # preallocate data lists to populate per frequency
            majorParamAvg = []
            majorParamStd = []
            minorParamAvg = []
            minorParamStd = []

            for j in freqencies:
                LCRCommander(ser, f'FREQ {j}')
                TimeAdjustments(j) # for system stabilization

                measurements = DataAveraging(ser,numMeasurements) # [Maj Avg, Maj Std, Min Avg, Min Std]
                majorParamAvg.append(measurements[0])
                majorParamStd.append(measurements[1])
                minorParamAvg.append(measurements[2])
                minorParamStd.append(measurements[3])

            # store the data in the dataframe
            df[f'{k} Avg.'] = majorParamAvg
            df[f'{k} Std.'] = majorParamStd
            df[f'{minorParmName} Avg.'] = minorParamAvg
            df[f'{minorParmName} Std.'] = minorParamStd

    df.reset_index(drop = True, inplace = True) # remove the index column
    print(df)
    print('Test completed\n\n')
    return df

# data export
def DataExport(params, Data, info):
    fileName = f'{params[0]}_{params[1][0]}_{params[2][0]}_{time.strftime("%H%M%S")}'
    if os.path.isfile(fileName) == 0:
        np.savetxt(f"Data/{fileName}.csv", Data, header = f'Freqency (Hz), {params[1][0]}, std, {params[2][0]}, std', delimiter = ",",
                   fmt = "%e", comments = f'{info}\n\n')
        
    elif os.path.isfile(fileName) == 1:
        os.remove(fileName)
        np.savetxt(f"Data/{fileName}.csv", Data, header = f'Freqency (Hz), {params[1][0]}, std, {params[2][0]}, std', delimiter = ",",
                   fmt = "%e", comments = f'{info}\n\n')
