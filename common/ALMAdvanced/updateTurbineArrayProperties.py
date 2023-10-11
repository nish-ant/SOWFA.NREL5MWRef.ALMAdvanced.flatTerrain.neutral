#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Adria Borras-Nadal
# Adapted by  : Nishant Kumar
# Created Date: 21/12/2021
# ---------------------------------------------------------------------------
""" 
Script to manually introduce turbineArrayProperties required for calculation restart
"""

import numpy as np
import os
import re

# ---------------------------------------------------------------------------
# INPUT
# ---------------------------------------------------------------------------

#- 1. TURBINE CHOICE
#- NOTE: Two turbines available: NREL5MWRef or DTU10MW
turbineProperties = 'NREL5MWRef'

#- 2. AERO FORCES CALCULATION METHOD
#- NOTE: Changes the constant/turbineArrayProperties 
#-       3 choices: ADM, ALM or ALMAdvanced 
#-       ALMAdvanced also activates nacelle/tower models and projected forces
#-       CAUTION: BLADES DEFINITION DIFFERENT from ALM !!!
libType = 'ALMAdvanced' # ADM or ALM

#- 3. TURBINE(S) SPACING
#- NOTE: Edits also the constant/turbineArrayProperties spacing each turbine
nb_turbines             = 1     #- Minimum 1 expected
upstream_distance_diam  = 10    #- in D, x-position of turbine1 in the domain
between                 = 5     #- in D, y-position of turbine1 in the domain

#- 4. REFINEMENT AROUND THE TURBINE 
#- NOTE: Refinement to go from 10m default mesh size to 2.5m cells 
#-       ~25 cells/blade targeted 
#-       nb_refineMesh forced to 2 (not scripted yet)
nb_refineMesh   = 2
#- NOTE: Equivalent diameters to extend the refinemnent zone  
xD_refine_up    = 4  #- in -D
xD_refine_down  = 16 #- in D
yD_refine       = 6  #- in D
zD_refine       = 2  #- in D
D_BetweenLevels = 2  #- in D, transition between the nb_refineMesh levels

#- 5. POSTPROCESSING WAKE LINE PROBES
#- NOTE: probeLines to catch the wake profiles
#-       Writes a dedicated file already included in controlDict.1
inflow    = -3   #- in D
dwake     = 0.25 #- Space between each wake probeLine
wakeStart = 0.25 #- in D
wakeEnd   = 20   #- in D, for the last turbine only

# ---------------------------------------------------------------------------

#- Print the input parameters
print("*** Informations about turbine properties")
print("Turb  type        = "+turbineProperties)
print("Actuator Model    = "+libType)
print("Nb of turbines    = "+str(nb_turbines))
print("Upstream distance = "+str(upstream_distance_diam)+"D")
if nb_turbines > 1:
	print("Dist between turb = "+str(between)+"D")
print("Refinement numbers = "+str(nb_refineMesh))

cwd = os.getcwd()
print("Current working directory: {0}".format(cwd))

# ---------------------------------------------------------------------------
# READ DATA CASE
# ---------------------------------------------------------------------------

#- Path to write in the SOWFA case 
casePath = "./"

file_path_turbineProperties=casePath+"constant/turbineProperties/"+turbineProperties
file_path_setUp = casePath+"../ABL/setUp"
file_path_turbineArrayProperties=casePath+"constant/turbineArrayProperties"
file_path_turbineOutput=casePath+"postProcessing/turbineOutput"

print("*** Informations about turbine properties")
for line in open(file_path_turbineProperties):
   if line.startswith("TipRad") == True: 
      diameter = 2*float(line.rstrip().split(';')[0].split(" ")[-1]) 
      print("      Turbine diameter in the turbineProperties file is "+str(diameter)+"  m")
   elif line.startswith("TowerHt") == True:
      towerHt = float(line.rstrip().split(';')[0].split(" ")[-1])
   elif line.startswith("Twr2Shft") == True:
      twr2Shft = float(line.rstrip().split(';')[0].split(" ")[-1])
   elif line.startswith("ShftTilt") == True:
      shftTilt = float(line.rstrip().split(';')[0].split(" ")[-1])
   elif line.startswith("OverHang") == True:
      overhang = float(line.rstrip().split(';')[0].split(" ")[-1])

hubHeight = int(towerHt + twr2Shft)+1 #- 90 m in the example
print("      Hub height in the turbineProperties file is "+str(hubHeight)+" m")
print("      Shaft tilt in the turbineProperties file is "+str(shftTilt)+" deg")

for line in open(file_path_setUp):
   if line.startswith("windDir") == True:
      wind_direction = float(line.rstrip().split(';')[0].split(" ")[-1])
      print("      Wind direction in the setUp file is "+str(wind_direction)+" deg")
#- Extract wind speed
for line in open(file_path_setUp):
    if line.startswith("U0Mag") == True:
      uinf = float(line.rstrip().split(';')[0].split(" ")[-1])
      print("      Incoming wind speed at the hub is "+str(uinf)+" m/s")  
for line in open(file_path_setUp):
   if line.startswith("xMax") == True:
      xMax = float(line.rstrip().split(';')[0].split(" ")[-1])
      print("      xMax in the setUp file is "+str(xMax)+" m")
for line in open(file_path_setUp):      
   if line.startswith("yMin") == True:
      yMin = float(line.rstrip().split(';')[0].split(" ")[-1])
      print("      yMin in the setUp file is "+str(yMin)+" m")            
for line in open(file_path_setUp):      
   if line.startswith("yMax") == True:
      yMax = float(line.rstrip().split(';')[0].split(" ")[-1])
      print("      yMax in the setUp file is "+str(yMax)+" m")                  
   
      # str_NacYaw = "    NacYaw                            "+str(wind_direction)+";"
      # os.system('sed -i \'s/    NacYaw                            toBeModified;/'+str_NacYaw+'/\' '+file_path_turbineArrayProperties)
      print("      Set the NacYaw in the turbineArrayProperties file to "+str(wind_direction))

wind_direction_conventionWest = 270 - wind_direction

# ---------------------------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------------------------

def find_strings(file):
    with open(file) as temp_f:
        datafile = temp_f.readlines()
    for line in datafile:
        if 'Azimuth' in line:
#            return line #- The string is found
            azimuth = line
        if 'RotSpeed'in line:
            rotSpeed = line
        if 'Pitch'in line:
            pitch = line            
        if 'TorqueGen'in line:
            torqueGen = line            
    return(azimuth,rotSpeed,pitch,torqueGen)

def find_timeDataTurbineOutPut(file,lastTime,nb_turbines):
    for iTurb in range(nb_turbines):
        for iFile in range(len(file)):
            if int(file[iFile,0]) == iTurb and file[iFile,1] == float(lastTime):
                lastVal = file[iFile,3]
    return(lastVal)

def replaceAzimuth(file,val,last,time):
    #- Open file
    with open(file, 'r') as f:
        #- Read file
        file_source = f.read()
        replace_string = file_source.replace(val,"        Azimuth              "+str(last)+";//value at "+time+" s \n")
    with open(file, 'w') as f:
        #- Save output
        f.write(replace_string)
    return(file)
    
def replaceRotSpeed(file,val,last,time):
    #- Open file
    with open(file, 'r') as f:
        #- Read file
        file_source = f.read()
        replace_string = file_source.replace(val,"        RotSpeed              "+str(last)+";//value at "+time+" s \n")
    with open(file, 'w') as f:
        #- Save output
        f.write(replace_string)
    return(file)    

def replacePitch(file,val,last,time):
    #- Open file
    with open(file, 'r') as f:
        #- Read file
        file_source = f.read()
        replace_string = file_source.replace(val,"        Pitch                "+str(last)+";//value at "+time+" s \n")            
    with open(file, 'w') as f:
        #- Save output
        f.write(replace_string)
    return(file)    
    
def replaceTorqueGen(file,val,last,time):
    #- Open file
    with open(file, 'r') as f:
        #- Read file
        file_source = f.read()
        replace_string = file_source.replace(val,"        TorqueGen            "+str(last)+";//value at "+time+" s \n")                        
    with open(file, 'w') as f:
        #- Save output
        f.write(replace_string)
    return(file)        
    
def natsort(list_):
    #- Decorate
    tmp = [ (int(re.search('\d+', i).group(0)), i) for i in list_ ]
    tmp.sort()
    #- Undecorate
    return [ i[1] for i in tmp ]

# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------
#- Time folder to catch last turbine values 
#- MOTE: Done only once with azimuth and processor0

#- 1. lastTime before stopping the simulation
lastTime = os.listdir(casePath+'processor0') 
lastTime.remove('constant')
lastTime = sorted(lastTime)
#- Print the input parameters
print("*** Informations about restart time")
for iTimes in range(len(lastTime)):
    print(lastTime[iTimes]+' s')
lastTime = lastTime[-1] #- Last time folder kept 
print('Selected time is -> '+ lastTime+' s')

#- 2. timePost to catch all the Turbine parameters 
timePost = sorted(os.listdir(file_path_turbineOutput), key=float)
timePost = timePost[-1]
# if len(timePost) > 1:
#     timePost = timePost[-2] #- Use lastTime-1 
# else:
#     name_fileAz = file_path_turbineOutput+'/'+str(timePost[-1])+"/azimuth" #- Use lastTime if only one
#     timePost = timePost[-1] #- Use lastTime 

# ---------------------------------------------------------------------------
# REPLACE
# ---------------------------------------------------------------------------
#- Automatic values replacement

#- 1. We search just once the Turbine values (az,rotSpeed,...)    
azimuth,rotSpeed,pitch,torqueGen = find_strings(file_path_turbineArrayProperties)

#- 2. We catch last timestep Turbine values (az,rotSpeed,...)
# azimuth,rotSpeed,pitch,torqueGen = find_strings(file_path_turbineArrayProperties)

#- AZIMUTH
name_fileAz = file_path_turbineOutput+'/'+str(timePost)+"/rotorAzimuth"
azimuthFile = np.loadtxt(name_fileAz,skiprows=1)
lastAz = find_timeDataTurbineOutPut(azimuthFile,lastTime,nb_turbines)
replaceAzimuth(file_path_turbineArrayProperties,azimuth,lastAz,lastTime)

#- ROTSPEED
name_fileR = file_path_turbineOutput+'/'+str(timePost)+"/rotorSpeed"
rotSpeedFile = np.loadtxt(name_fileR,skiprows=1)
lastRot = find_timeDataTurbineOutPut(rotSpeedFile,lastTime,nb_turbines)
replaceRotSpeed(file_path_turbineArrayProperties,rotSpeed,lastRot,lastTime)

#- PITCH
#- NOTE: No pitch in ADM
name_fileP = file_path_turbineOutput+'/'+str(timePost)+"/bladePitch"
rotSpeedFile = np.loadtxt(name_fileR,skiprows=1)
lastRot = find_timeDataTurbineOutPut(rotSpeedFile,lastTime,nb_turbines)
replaceRotSpeed(file_path_turbineArrayProperties,rotSpeed,lastRot,lastTime)

#- TORQUE
name_fileT = file_path_turbineOutput+'/'+str(timePost)+"/generatorTorque"
torqueGenFile = np.loadtxt(name_fileT,skiprows=1)
lastTorque = find_timeDataTurbineOutPut(torqueGenFile,lastTime,nb_turbines)
replaceTorqueGen(file_path_turbineArrayProperties,torqueGen,lastTorque,lastTime)    

#- Print conclusion
print("*** Informations about turbine parameters update")
for iTurb in range(nb_turbines):
    print("turbine"+str(iTurb)+" parameters updated at "+lastTime+" s")
