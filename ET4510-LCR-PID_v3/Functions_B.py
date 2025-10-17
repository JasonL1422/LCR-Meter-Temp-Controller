import os
import pandas as pd
import numpy as np
import time
from Functions_A import *

"""Experiment1 for a1_..."""
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
    fileName = f'a1_{params[0]}_{params[1][0]}_{params[2][0]}_{time.strftime("%H%M_%S")}'
    if os.path.isfile(fileName) == 0:
        np.savetxt(f"Data/{fileName}.csv", Data, header = f'Freqency (Hz), {params[1][0]}, std, {params[2][0]}, std', delimiter = ",",
                   fmt = "%e", comments = f'{info}\n\n')
        
    elif os.path.isfile(fileName) == 1:
        os.remove(fileName)
        np.savetxt(f"Data/{fileName}.csv", Data, header = f'Freqency (Hz), {params[1][0]}, std, {params[2][0]}, std', delimiter = ",",
                   fmt = "%e", comments = f'{info}\n\n')

"""Experiment2 for a2_..."""
def Experiment2(ser, freq_fixed, mainMeasurement, minorMeasurement,
                voltage, biasVoltage, numMeasurements, ser2, set_temp, exptime):

    # Set PID SV and RUN
    PIDcommander(ser2, 0x4701, set_temp*10)
    PIDcommander(ser2, 0x4719, 1)  # RUN

    # Set LCR meter parameters
    LCRCommander(ser, f'FREQ {freq_fixed}')
    LCRCommander(ser, f'VOLT {int(voltage * 1e3)}')
    if biasVoltage is not None:
        LCRCommander(ser, f'BIAS:VOLT {int(biasVoltage * 1e3)}')

    # Prepare result storage
    result_rows = []

    t_start = time.time()

    while True:
        t_now = time.time() - t_start
        if t_now > exptime:
            break
        
        for k in mainMeasurement:
            LCRCommander(ser, f'FUNC:IMP:A {k}')
            for i in minorMeasurement:
                LCRCommander(ser, f'FUNC:IMP:B {i}')
                minorParmName = f"{k}-{i}"

                # Read temperature
                temp = PIDDataReadout(ser2)
                if temp is None:
                    pv, sv = None, None
                else:
                    pv, sv = temp[0], temp[1]

                measurements = DataAveraging(ser, numMeasurements)

            row = {
                "Time (s)": round(t_now, 1),
                "PV (degC)": pv,
                "SV (degC)": sv,
                f"{k} Avg.": measurements[0],
                f"{k} Std.": measurements[1],
                f"{minorParmName} Avg.": measurements[2],
                f"{minorParmName} Std.": measurements[3]
            }

        result_rows.append(row)

    # Stop PID
    PIDcommander(ser2, 0x4701, 180)  # SV = 18.0°C
    PIDcommander(ser2, 0x4719, 0)    # STOP

    # Create DataFrame
    df = pd.DataFrame(result_rows)
    df.reset_index(drop=True, inplace=True)
    print(df)
    print('Test completed\n\n')
    return df

def DataExport2(params, DataFrame, info):
    material = params[0]
    mainParam = "_".join(params[1])
    minorParam = "_".join(params[2])
    timestamp = time.strftime("%H%M_%S")
    fileName = f"a2_{material}_{mainParam}_{minorParam}_{timestamp}"

    os.makedirs("Data", exist_ok=True)

    with open(f"Data/{fileName}.csv", 'w', encoding='utf-8') as f:
        f.write(f"Material: {material}\n")
        f.write(f"Main Parameters: {params[1]}\n")
        f.write(f"Minor Parameters: {params[2]}\n")
        f.write(f"Info: {info}\n\n")
        DataFrame.to_csv(f, index=False)

    print(f"Data saved to Data/{fileName}.csv")


"""Experiment3 for a3_..."""
def Experiment3(ser, freqencies, mainMeasurement, minorMeasurement, voltage, biasVoltage, numMeasurements, ser2):
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

                # Read temperature
                temp = PIDDataReadout(ser2)
                if temp is None:
                    pv, sv = None, None
                else:
                    pv, sv = temp[0], temp[1]

                measurements = DataAveraging(ser,numMeasurements) # [Maj Avg, Maj Std, Min Avg, Min Std]
                majorParamAvg.append(measurements[0])
                majorParamStd.append(measurements[1])
                minorParamAvg.append(measurements[2])
                minorParamStd.append(measurements[3])

            # store the data in the dataframe
            df[f'PV'] = pv
            df[f'SV'] = sv
            df[f'{k} Avg.'] = majorParamAvg
            df[f'{k} Std.'] = majorParamStd
            df[f'{minorParmName} Avg.'] = minorParamAvg
            df[f'{minorParmName} Std.'] = minorParamStd

    # Stop PID
    PIDcommander(ser2, 0x4701, 180)  # SV = 18.0°C
    PIDcommander(ser2, 0x4719, 0)    # STOP

    df.reset_index(drop = True, inplace = True) # remove the index column
    print(df)
    print('Test completed\n\n')
    return df

def DataExport3(params, Data, info):
    fileName = f'a3_{params[0]}_{params[1][0]}_{params[2][0]}_{time.strftime("%H%M_%S")}'
    if os.path.isfile(fileName) == 0:
        np.savetxt(f"Data/{fileName}.csv", Data, header = f'Freqency (Hz), {params[1][0]}, std, {params[2][0]}, std', delimiter = ",",
                   fmt = "%e", comments = f'{info}\n\n')
        
    elif os.path.isfile(fileName) == 1:
        os.remove(fileName)
        np.savetxt(f"Data/{fileName}.csv", Data, header = f'Freqency (Hz), {params[1][0]}, std, {params[2][0]}, std', delimiter = ",",
                   fmt = "%e", comments = f'{info}\n\n')

