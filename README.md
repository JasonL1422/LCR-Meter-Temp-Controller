# LCR-Meter-Temp-Controller
Scripts to control both LCR meter and Temperature controller. The LCR part was revised from @ https://github.com/TheDuckenEngineer

- 'ET4510-LCR_o1': for LCR meter control only. Some plotting scripts and others has been added.
- 'ET4510-LCR_PID': includes scripts to control the PID temp controller. Up and running as of Oct 13th, 2025
- 'ET4510-LCR_PID_v3': three different Jupyter notebook files to run three diff experiments. Details are in the README file. [Oct 16th, 2025]

[Note]:
- The arguments in DeviceConnect() is for Mac.
- Make sure that the Omega CN740 settings match the DeviceConnect_cn740() arguments - baud rate, parity, etc.
- Be sure to use the correct cable compatible with the script and Mac. 
- Check out the README files in each folder.
