# Thermal impedance measurement

Newest version:
ET4510-LCR-PID_v4 (Dec 11th, 2025)
- b0s are to check the system with known capacitors and resistors.
- b1-3 are for actual experiments; they have different inputs and outputs depending your experimental plan/design.
- c0s are for plotting from old files and for temp control only.
- For details, check the readme file in the folder

<div align="center">
  <img width="1000" src="https://github.com/JasonL1422/Images/blob/main/thermal%20impedance.png" />
  <img width="600" src="https://github.com/JasonL1422/Images/blob/main/lcr%2Bpid2.png" />
</div>


--------------------------------------



Scripts to control both LCR meter and Temperature controller. The LCR part was revised from @ https://github.com/TheDuckenEngineer

- 'ET4510-LCR_o1': for LCR meter control only. Some plotting scripts and others has been added.
- 'ET4510-LCR_PID': includes scripts to control the PID temp controller. Up and running as of Oct 13th, 2025
- 'ET4510-LCR_PID_v3': three different Jupyter notebook files to run three diff experiments. Details are in the README file. [Oct 16th, 2025]

[Note]:
- The arguments in DeviceConnect() is for Mac.
- Make sure that the Omega CN740 settings match the DeviceConnect_cn740() arguments - baud rate, parity, etc.
- Be sure to use the correct cable compatible with the script and Mac. 
- Check out the README files in each folder.
