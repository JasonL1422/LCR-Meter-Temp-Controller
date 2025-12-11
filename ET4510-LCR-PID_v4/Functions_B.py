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
def DataExport(params, Data, info,timestamp):
    fileName = f'{timestamp}_{params[0]}_{params[1][0]}_{params[2][0]}'
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

def DataExport2(params, DataFrame, info, timestamp):
    material = params[0]
    mainParam = "_".join(params[1])
    minorParam = "_".join(params[2])
    fileName = f"{timestamp}_{material}_{mainParam}_{minorParam}"

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

def DataExport3(params, Data, info, timestamp):
    fileName = f'{timestamp}_{params[0]}_{params[1][0]}_{params[2][0]}'
    if os.path.isfile(fileName) == 0:
        np.savetxt(f"Data/{fileName}.csv", Data, header = f'Freqency (Hz), {params[1][0]}, std, {params[2][0]}, std', delimiter = ",",
                   fmt = "%e", comments = f'{info}\n\n')
        
    elif os.path.isfile(fileName) == 1:
        os.remove(fileName)
        np.savetxt(f"Data/{fileName}.csv", Data, header = f'Freqency (Hz), {params[1][0]}, std, {params[2][0]}, std', delimiter = ",",
                   fmt = "%e", comments = f'{info}\n\n')


"""Experiment_eff"""
def Experiment_eff(ser, freqencies, voltage, biasVoltage, numMeasurements):
    df = pd.DataFrame(freqencies, columns = ['Frequency'])

    LCRCommander(ser, f'VOLT {voltage*1e3}')
    if biasVoltage is not None:
        LCRCommander(ser, f'BIAS:VOLT {int(biasVoltage*1e3)}') # mV in SCPI

    LCRCommander(ser, f'FUNC:IMP:A Z') # Major parameter to be measured
    LCRCommander(ser, f'FUNC:IMP:B THR') # Minor parameter to be measured

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
    df[f'Z Avg.'] = majorParamAvg
    df[f'Z Std.'] = majorParamStd
    df[f'THR Avg.'] = minorParamAvg
    df[f'THR Std.'] = minorParamStd

    df.reset_index(drop = True, inplace = True) # remove the index column
    print(df)
    print('Test completed\n\n')
    return df

"""Experiment_b1"""
def Experiment_b1(ser, freqencies, voltage, biasVoltage, numMeasurements, ser2, set_temp):
    df = pd.DataFrame(freqencies, columns = ['Frequency'])

    # Set PID SV and RUN
    PIDcommander(ser2, 0x4701, set_temp*10)
    PIDcommander(ser2, 0x4719, 1)  # RUN

    LCRCommander(ser, f'VOLT {voltage*1e3}')
    if biasVoltage is not None:
        LCRCommander(ser, f'BIAS:VOLT {int(biasVoltage*1e3)}') # mV in SCPI

    LCRCommander(ser, f'FUNC:IMP:A Z') # Major parameter to be measured
    LCRCommander(ser, f'FUNC:IMP:B THR') # Minor parameter to be measured

    # preallocate data lists to populate per frequency
    majorParamAvg = []
    majorParamStd = []
    minorParamAvg = []
    minorParamStd = []
    pv_list, sv_list = [], []

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
        pv_list.append(pv)
        sv_list.append(sv)
    

    # store the data in the dataframe
    df[f'PV'] = pv_list
    df[f'SV'] = sv_list
    df[f'Z Avg.'] = majorParamAvg
    df[f'Z Std.'] = majorParamStd
    df[f'THR Avg.'] = minorParamAvg
    df[f'THR Std.'] = minorParamStd

    df.reset_index(drop = True, inplace = True) # remove the index column
    print(df)
    print('Test completed\n\n')
    return df

def DataExport_b(material, DataFrame, info, timestamp):
    fileName = f"{timestamp}_{material}_Z_THR"

    os.makedirs("Data", exist_ok=True)

    with open(f"Data/{fileName}.csv", 'w', encoding='utf-8') as f:
        f.write(f"Material: {material}\n")
        f.write(f"Main Parameters: Z\n")
        f.write(f"Minor Parameters: THR\n")
        f.write(f"Info: {info}\n\n")
        DataFrame.to_csv(f, index=False)

    print(f"Data saved to Data/{fileName}.csv")

"""Experiment_b2 for b2_..."""
def Experiment_b2(ser, freq_fixed, voltage, biasVoltage, numMeasurements, ser2, set_temp, exptime):

    # Set PID SV and RUN
    PIDcommander(ser2, 0x4701, set_temp*10)
    PIDcommander(ser2, 0x4719, 1)  # RUN

    # Set LCR meter parameters
    LCRCommander(ser, f'FREQ {freq_fixed}')
    LCRCommander(ser, f'VOLT {int(voltage * 1e3)}')
    if biasVoltage is not None:
        LCRCommander(ser, f'BIAS:VOLT {int(biasVoltage * 1e3)}')

    LCRCommander(ser, f'FUNC:IMP:A Z') # Major parameter to be measured
    LCRCommander(ser, f'FUNC:IMP:B THR') # Minor parameter to be measured
    
    # Prepare result storage
    result_rows = []

    t_start = time.time()
    while True:
        t_now = time.time() - t_start
        if t_now > exptime:
            break

        temp = PIDDataReadout(ser2)
        pv, sv = (temp[0], temp[1]) if temp is not None else (np.nan, np.nan)

        measurements = DataAveraging(ser, numMeasurements)

        row = {
            "Time (s)": round(t_now, 1),
            "PV": pv,
            "SV": sv,
            f"Z Avg.": measurements[0],
            f"Z Std.": measurements[1],
            f"THR Avg.": measurements[2],
            f"THR Std.": measurements[3]
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

"""Experiment_b3 for b3_..."""
def Experiment_b3(ser, freq_fixed, voltage, biasVoltage, numMeasurements, ser2, set_temp, until_temp):

    # Set PID SV and RUN
    PIDcommander(ser2, 0x4701, set_temp*10)
    PIDcommander(ser2, 0x4719, 1)  # RUN

    # Set LCR meter parameters
    LCRCommander(ser, f'FREQ {freq_fixed}')
    LCRCommander(ser, f'VOLT {int(voltage * 1e3)}')
    if biasVoltage is not None:
        LCRCommander(ser, f'BIAS:VOLT {int(biasVoltage * 1e3)}')

    LCRCommander(ser, f'FUNC:IMP:A Z') # Major parameter to be measured
    LCRCommander(ser, f'FUNC:IMP:B THR') # Minor parameter to be measured
    
    # Prepare result storage
    result_rows = []

    t_start = time.time()

    initial_temp = PIDDataReadout(ser2)[0]
    is_heating = until_temp > initial_temp

    while True:

        temp = PIDDataReadout(ser2)
        pv, sv = (temp[0], temp[1]) if temp is not None else (np.nan, np.nan)

        t_now = time.time() - t_start

        # Stop condition adapted for both heating and cooling
        if (is_heating and pv >= until_temp) or (not is_heating and pv <= until_temp):
            break

        measurements = DataAveraging(ser, numMeasurements)

        row = {
            "Time (s)": round(t_now, 1),
            "PV": pv,
            "SV": sv,
            f"Z Avg.": measurements[0],
            f"Z Std.": measurements[1],
            f"THR Avg.": measurements[2],
            f"THR Std.": measurements[3]
        }

        result_rows.append(row)
        pd.DataFrame(result_rows).to_csv("temp_output_b3.csv", index=False)    # Temporary save

    # Stop PID
    PIDcommander(ser2, 0x4701, 180)  # SV = 18.0°C
    PIDcommander(ser2, 0x4719, 0)    # STOP

    # Create DataFrame
    df = pd.DataFrame(result_rows)
    df.reset_index(drop=True, inplace=True)
    print(df)
    print('Test completed\n\n')
    return df