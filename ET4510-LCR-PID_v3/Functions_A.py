import os
import pandas as pd
import numpy as np
import time
import serial

"""Device communication functions."""
def DeviceConnect(COMPort): # for ET4510 LCR meter
    ser = serial.Serial(COMPort, 9600, timeout = 1) 
    return ser 

def DeviceConnect_CN740(COMPort): # for CN740
    ser = serial.Serial(COMPort, 9600, 
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_EVEN, 
        stopbits=serial.STOPBITS_ONE,
        timeout = 1) 
    return ser 

def DeviceDisconnect(ser):
    return ser.close()

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

"""PID communication functions."""
def calc_lrc(hexstr):
    total = 0
    for i in range(0, len(hexstr), 2):
        total += int(hexstr[i:i+2], 16)
    return f"{(-total) & 0xFF:02X}"
    # sth & 0xFF (0b11111111) --> masking trick to get last 8 bits of sth
    # & is bitwise AND operator
    # :02X converts to 2-digit uppercase hex

def PIDDataReadout(ser):
    # Send command to read 2 words (0002): 4700H (PV) and 4701H (SV)
    ser.write(':010347000002B3\r\n'.encode())
    raw = ser.readline().decode().strip() # strip() removes \r\n
    if not raw.startswith(':'):
        return None 
    
    body = raw[1:]  # Strip ':' and \r\n
    # addr = body[0:2]
    # func_code = body[2:4]
    # byte_cnt  = int(body[4:6], 16)
    data1 = body[6:10]  # PV
    data2 = body[10:14] # SV
    lrc_recv = body[14:16]

    lrc_calc = calc_lrc(body[:-2])

    if lrc_calc != lrc_recv:
        print(f"LRC mismatch")
        return f'raw={raw}, body={body}, lrc_calc={lrc_calc}, lrc_recv={lrc_recv}'
    
    pv = int(data1, 16) / 10
    sv = int(data2, 16) / 10
    temp = [pv, sv]

    return temp

def PIDcommander(ser, register_hex, value_int):
    # examples: 
    # PIDcommander(ser_cn740,0x4701,400) to set SV to 40.0C
    # PIDcommander(ser_cn740,0x4719, 0) --> STOP
    # PIDcommander(ser_cn740,0x4719, 1) --> RUN
    dev_addr = '01' # Device address
    func = '06' # Function code to write = 06H
    reg = f"{int(register_hex):04X}" #
    val = f"{value_int:04X}"              # Convert int to 4-digit hex

    msg_body = dev_addr + func + reg + val
    lrc = calc_lrc(msg_body)              
    full_command = f":{msg_body}{lrc}\r\n"  # Full ASCII message
    
    ser.write(full_command.encode())
    response = ser.readline().decode()

    if full_command != response:
        return f"Error: Response mismatch: sent={full_command} and received={response}"
        
    return f'{response} was sent. confirmed.'

