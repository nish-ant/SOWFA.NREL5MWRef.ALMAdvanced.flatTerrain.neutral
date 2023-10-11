#!/gpfs/softs/contrib/apps/python/2.7.6/bin/python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Adria B-N
# Created Date: 21/12/2021
# ---------------------------------------------------------------------------
""" 
Script to preProcess
"""

import numpy as np
import os
from scipy import interpolate
# import matplotlib.pyplot as plt

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
inflow    = -3    #- in D
dwake     = 0.25  #- Space between each wake probeLine
wakeStart = 0.25  #- in D
wakeEnd   = 20    #- in D, for the last turbine only
startTime = 20100
endTime   = 20400
timeStep  = 1

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

# ---------------------------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------------------------

def interpRotSpeedAndPitch(turbineProperties,SOWFAwind_speed):
    #- NREL5MW law control from Marie FarmShadow
    if turbineProperties == "NREL5MWRef":
        wind_speed = [3.0, 4.0  , 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0]
        rot_speed = [06.972, 7.183, 7.506, 7.942, 8.469, 9.156, 10.296, 11.431, 11.890, 12.100, 12.100, 12.100, 12.100, 12.100, 12.100, 12.100, 12.100, 12.100, 12.100, 12.100, 12.100, 12.100, 12.100]
        pitch= [0, 0, 0, 0, 0, 0, 0, 0, 0, 3.823, 6.602, 8.668, 10.450, 12.055, 13.536, 14.920, 16.226, 17.473, 18.699, 19.941, 21.177, 22.347, 23.469]
        if SOWFAwind_speed < wind_speed[9]:
            pitch_i = 0
        else:
            pitch_i = interpolate.splrep(wind_speed[9:], pitch[9:],k=3)        
    #- DTU10MW law control from Marie ?
    elif turbineProperties == "DTU10MW":
        wind_speed = [4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0]
        rot_speed = [6.0, 6.0, 6.0, 6.0, 6.0, 6.424595, 7.226943, 8.031387, 8.840100, 9.6, 9.6, 9.6, 9.6, 9.6, 9.6, 9.6, 9.6,  9.6, 9.6, 9.6, 9.6, 9.6]
        pitch = [2.893113, 2.122761, 1.086778, 0.000078, 0.000018, 0.000078, 0.000018, 0.000048, 4.784481, 7.373210, 9.283288, 10.893463, 12.338398, 13.675584, 14.931824, 16.127375, 17.272142, 18.376651, 19.449540, 20.487920, 21.499238, 22.486403]
        if SOWFAwind_speed < wind_speed[4]:
            f_pitch = interpolate.splrep(wind_speed[0:4], pitch[0:4],k=3)
            pitch_i = interpolate.splev(SOWFAwind_speed,f_pitch)
        elif SOWFAwind_speed >=7 and wind_speed <= 11:
            pitch_i = 0
        else:
            f_pitch = interpolate.splrep(wind_speed[7:], pitch[7:],k=3)
            pitch_i = interpolate.splev(SOWFAwind_speed,f_pitch)
            
    f_rotSpeed = interpolate.splrep(wind_speed,rot_speed,k=3) #- Construction of the spline of order 3
    rotSpeed_i = interpolate.splev(SOWFAwind_speed,f_rotSpeed)

    return(rotSpeed_i,pitch_i)
           
# ---------------------------------------------------------------------------
# READ DATA CASE
# ---------------------------------------------------------------------------

#- Path to write in the SOWFA case 
casePath = "./"

file_path_turbineProperties=casePath+"constant/turbineProperties/"+turbineProperties
file_path_setUp = casePath+"setUp"

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

hubHeight = int(towerHt + twr2Shft)+1 #- 90m in the example
print("      Hub height in the turbineProperties file is "+str(hubHeight)+" m")
print("      Shaft tilt in the turbineProperties file is "+str(shftTilt)+" deg")

for line in open(file_path_setUp):
   if line.startswith("windDir") == True:
      wind_direction = float(line.rstrip().split(';')[0].split(" ")[-1])
      print("      Wind direction in the setUp file is "+str(wind_direction)+" deg")
   #- Extract wind Speed
for line in open(file_path_setUp):
    if line.startswith("windSpeed") == True:
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
      print("      Set the NacYaw in the turbineArrayProperties file to "+str(wind_direction)+'\n')

wind_direction_conventionWest = 270 - wind_direction

# ---------------------------------------------------------------------------
# READ DATA CASE
# ---------------------------------------------------------------------------
#- RotSpeed & Pitch calculation

# rotSpeed_i,pitch_i = interpRotSpeedAndPitch(turbineProperties,SOWFAwind_speed)
rotSpeed,pitch = interpRotSpeedAndPitch(turbineProperties,uinf)

print("   interpolation splev, deg3",np.round(pitch,3),"deg")
print("   interpolation splev, deg3",np.round((pitch)*np.pi/180.,3),"rad")
print("---------------------")
print("   interpolation splev, deg3",np.round(rotSpeed,3),"rpm")
print("   interpolation splev, deg3",np.round((rotSpeed)*(2.*np.pi)/60.,3),"rad/s") 

# ---------------------------------------------------------------------------
# CREATE OUTPUT
# ---------------------------------------------------------------------------
#- turbineArrayProperties creation for 1 or several turbines

file_path_turbineArrayProperties=open(casePath+"constant/turbineArrayProperties",'w')
file_path_turbineArrayProperties.write("/*--------------------------------*- C++ -*----------------------------------*\ \n")
file_path_turbineArrayProperties.write("| =========                 |                                                 | \n")
file_path_turbineArrayProperties.write("| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           | \n")
file_path_turbineArrayProperties.write("|  \\    /   O peration     | Version:  2.0                                   | \n")
file_path_turbineArrayProperties.write("|   \\  /    A nd           | Web:      http://www.OpenFOAM.org               | \n")
file_path_turbineArrayProperties.write("|    \\/     M anipulation  |                                                 | \n")
file_path_turbineArrayProperties.write("\*---------------------------------------------------------------------------*/ \n")
file_path_turbineArrayProperties.write("FoamFile \n")
file_path_turbineArrayProperties.write("{ \n")
file_path_turbineArrayProperties.write("    version     2.0; \n")
file_path_turbineArrayProperties.write("    format      ascii; \n")
file_path_turbineArrayProperties.write("    class       dictionary; \n")
file_path_turbineArrayProperties.write('    location    "system"; \n')
file_path_turbineArrayProperties.write("    object      turbineArrayProperties; \n")
file_path_turbineArrayProperties.write("} \n")
file_path_turbineArrayProperties.write("// ************************************************************************* // \n")
file_path_turbineArrayProperties.write("\n")
file_path_turbineArrayProperties.write("globalProperties\n")
file_path_turbineArrayProperties.write("{\n")
file_path_turbineArrayProperties.write("    outputControl       \"timeStep\";\n")
file_path_turbineArrayProperties.write("    outputInterval       1;\n")
file_path_turbineArrayProperties.write("}\n")

#- Turbine Spacing

upstream_distance = diameter*upstream_distance_diam
yposition = (yMax-yMin)/2

hubLocation = []
baseLocation = []
print("        ________________             _______ ")
print("        |               |            |      |")
print("        |               |            |      |")
print("ypos => |       X       |   or       |  X   |")
print("        |               |            | /    |")
print("        |               |       ypos |/     |")
print("        |_______|_______|            |__|___|")
print("                xpos                    xpos ")
for iTurb in range(nb_turbines):
    if iTurb == 0:
        hubLocation_tmp = [upstream_distance*np.cos(wind_direction_conventionWest*np.pi/180.),yposition+upstream_distance*np.sin(wind_direction_conventionWest*np.pi/180.),hubHeight]
        hubLocation.append(hubLocation_tmp)
        baseLocation_tmp = [hubLocation[iTurb][0]-overhang*np.cos(shftTilt*np.pi/180.)*np.cos(wind_direction_conventionWest*np.pi/180.),hubLocation[iTurb][1]-overhang*np.cos(shftTilt*np.pi/180.)*np.sin(wind_direction_conventionWest*np.pi/180.),0.]
        baseLocation.append(baseLocation_tmp)
    else:
        hubLocation_tmp = [hubLocation[iTurb-1][0] + between*diameter*np.cos(wind_direction_conventionWest*np.pi/180.),hubLocation[iTurb-1][1] +between*diameter*np.sin(wind_direction_conventionWest*np.pi/180.),hubHeight]
        hubLocation.append(hubLocation_tmp)
        baseLocation_tmp = [hubLocation[iTurb][0]-overhang*np.cos(shftTilt*np.pi/180.)*np.cos(wind_direction_conventionWest*np.pi/180.),hubLocation[iTurb][1]-overhang*np.cos(shftTilt*np.pi/180.)*np.sin(wind_direction_conventionWest*np.pi/180.),0.]
        baseLocation.append(baseLocation_tmp)
    print("      Hub location of turbine "+str(iTurb+1)+" is "+str(np.round(hubLocation[iTurb],2))+" m")
    print("      Base location of turbine "+str(iTurb+1)+" is "+str(np.round(baseLocation[-1],2))+" m")
    file_path_turbineArrayProperties.write("turbine"+str(iTurb)+"\n")
    file_path_turbineArrayProperties.write("{\n")
    file_path_turbineArrayProperties.write("       turbineType        "+turbineProperties+";\n")
    file_path_turbineArrayProperties.write("       baseLocation       ("+str(round(baseLocation[iTurb][0],1))+" "+str(round(baseLocation[iTurb][1],1))+" "+str(round(baseLocation[iTurb][2],1))+");\n")
    if "ADM" == libType:
        file_path_turbineArrayProperties.write("       nRadial              64;\n")
        file_path_turbineArrayProperties.write("       azimuthMaxDis        2.0;\n")
        file_path_turbineArrayProperties.write("       nAvgSector           1;\n")                                       
        file_path_turbineArrayProperties.write("       pointDistType       \"uniform\";\n")
        file_path_turbineArrayProperties.write("       pointInterpType     \"linear\";\n")
        file_path_turbineArrayProperties.write("       bladeUpdateType     \"oldPosition\";\n")
        file_path_turbineArrayProperties.write("       epsilon              20.0;\n")
        file_path_turbineArrayProperties.write("       forceScalar          1.0;\n")
        file_path_turbineArrayProperties.write("       inflowVelocityScalar 0.94;\n")
    elif "ALM" == libType:
        file_path_turbineArrayProperties.write("       numBladePoints       40;\n")    
        file_path_turbineArrayProperties.write("       pointDistType       \"uniform\";\n")
        file_path_turbineArrayProperties.write("       pointInterpType     \"linear\";\n")
        file_path_turbineArrayProperties.write("       bladeUpdateType     \"oldPosition\";\n")
        file_path_turbineArrayProperties.write("       epsilon              5.0; // PAY ATTENTION TO REFINEMENT NEAR BLADES\n")
    elif "ALMAdvanced" == libType:
        file_path_turbineArrayProperties.write("    includeNacelle                    true;\n")
        file_path_turbineArrayProperties.write("    includeTower                      true;\n")
        file_path_turbineArrayProperties.write("    numNacellePoints                  10;\n")
        file_path_turbineArrayProperties.write("    numTowerPoints                    40;\n")
        file_path_turbineArrayProperties.write("    numBladePoints                    40;\n")
        file_path_turbineArrayProperties.write("    pointDistType                   \"uniform\";\n")
        file_path_turbineArrayProperties.write("    pointInterpType                 \"linear\";\n")
        file_path_turbineArrayProperties.write("    bladeUpdateType                 \"oldPosition\";\n")
        file_path_turbineArrayProperties.write("    bladePointDistType               \"uniform\";\n")
        file_path_turbineArrayProperties.write("    nacellePointDistType             \"uniform\";\n")
        file_path_turbineArrayProperties.write("    towerPointDistType               \"uniform\";\n")
        file_path_turbineArrayProperties.write("    bladeSearchCellMethod            \"disk\";\n")
        file_path_turbineArrayProperties.write("    bladeActuatorPointInterpType     \"integral\";\n")
        file_path_turbineArrayProperties.write("    nacelleActuatorPointInterpType   \"linear\";\n")
        file_path_turbineArrayProperties.write("    towerActuatorPointInterpType     \"linear\";\n")
        file_path_turbineArrayProperties.write("    actuatorUpdateType               \"oldPosition\";\n")
        file_path_turbineArrayProperties.write("    velocityDragCorrType             \"none\";\n")
        file_path_turbineArrayProperties.write("    bladeForceProjectionType         \"uniformGaussian\";\n")
        file_path_turbineArrayProperties.write("    nacelleForceProjectionType       \"diskGaussian\";\n")
        file_path_turbineArrayProperties.write("    towerForceProjectionType         \"advanced\";\n")
        file_path_turbineArrayProperties.write("    bladeForceProjectionDirection    \"localVelocityAligned\";\n")
        file_path_turbineArrayProperties.write("    bladeEpsilon                     (5.0 0.0 0.0);\n")
        file_path_turbineArrayProperties.write("    nacelleEpsilon                   (4.0 4.0 0.0);\n")
        file_path_turbineArrayProperties.write("    towerEpsilon                     (4.0 4.0 0.0);\n")
        file_path_turbineArrayProperties.write("    nacelleSampleDistance             1.0;\n")
        file_path_turbineArrayProperties.write("    towerSampleDistance               3.5;\n")
    #- Common data    
    file_path_turbineArrayProperties.write("        tipRootLossCorrType              \"Glauert\";\n")
    file_path_turbineArrayProperties.write("        dynamicStallModel                \"none\";\n")
    file_path_turbineArrayProperties.write("        rotationDir                      \"cw\";\n")
    file_path_turbineArrayProperties.write("        Azimuth              0.0;\n")
    file_path_turbineArrayProperties.write("        RotSpeed             "+str(rotSpeed)+";  //rpm  // wind "+str(uinf)+"m/s  \n")
    file_path_turbineArrayProperties.write("        Pitch                "+str(pitch)+"; //deg \n")
    file_path_turbineArrayProperties.write("        TorqueGen            0.0;\n")
    file_path_turbineArrayProperties.write("        NacYaw               "+str(wind_direction)+";  //yaw 0deg\n")
    file_path_turbineArrayProperties.write("        fluidDensity         1.225;\n")
    file_path_turbineArrayProperties.write("}\n")
    

file_path_turbineArrayProperties.close

#- Refinement

origin  = [] 
iVector = []
jVector = []
kVector = []

#- Table has to be generated in accordance with nb_refineMesh input parameter... TO CORRECT !!
xremesh_up   = [xD_refine_up,  xD_refine_up+D_BetweenLevels]   #- in -D
xremesh_down = [xD_refine_down,xD_refine_down+D_BetweenLevels] #- in D, important to obtain almost 15D with good resolution
yremesh      = [yD_refine,     yD_refine+D_BetweenLevels] #- in D
zremesh      = [zD_refine,     zD_refine+D_BetweenLevels] #- in D

for i in range(nb_refineMesh+1):
    if i < nb_refineMesh:
        print("*****")
    origin.append([hubLocation[0][0]+yremesh[i-1]/2*diameter*np.sin(wind_direction_conventionWest*np.pi/180.)-xremesh_up[i-1]*diameter*np.cos(wind_direction_conventionWest*np.pi/180.),hubLocation[0][1]-yremesh[i-1]/2*diameter*np.cos(wind_direction_conventionWest*np.pi/180.)-xremesh_up[i-1]*diameter*np.sin(wind_direction_conventionWest*np.pi/180.),0.])
    iVector.append([(xremesh_up[i-1]+xremesh_down[i-1])*diameter*np.cos(wind_direction_conventionWest*np.pi/180.),(xremesh_up[i-1]+xremesh_down[i-1])*diameter*np.sin(wind_direction_conventionWest*np.pi/180.),0.])
    jVector.append([-yremesh[i-1]*diameter*np.sin(wind_direction_conventionWest*np.pi/180.),yremesh[i-1]*diameter*np.cos(wind_direction_conventionWest*np.pi/180.),0.])
    kVector.append([0.,0.,zremesh[i-1]*diameter])
    file_topoSetDict = open(casePath+"system/topoSetDict.local."+str(i+1),'w')
    file_topoSetDict.write("/*--------------------------------*- C++ -*----------------------------------*\ \n")
    file_topoSetDict.write("| =========                 |                                                 | \n")
    file_topoSetDict.write("| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           | \n")
    file_topoSetDict.write("|  \\    /   O peration     | Version:  2.0                                   | \n")
    file_topoSetDict.write("|   \\  /    A nd           | Web:      http://www.OpenFOAM.org               | \n")
    file_topoSetDict.write("|    \\/     M anipulation  |                                                 | \n")
    file_topoSetDict.write("\*---------------------------------------------------------------------------*/ \n")
    file_topoSetDict.write("FoamFile \n")
    file_topoSetDict.write("{ \n")
    file_topoSetDict.write("    version     2.0; \n")
    file_topoSetDict.write("    format      ascii; \n")
    file_topoSetDict.write("    class       dictionary; \n")
    file_topoSetDict.write('    location    "system"; \n')
    file_topoSetDict.write("    object      topoSetDict.local."+str(i+1)+"; \n")
    file_topoSetDict.write("} \n")
    file_topoSetDict.write("// ************************************************************************* // \n")
    file_topoSetDict.write("actions \n")
    file_topoSetDict.write("( \n")
    file_topoSetDict.write("    { \n")
    file_topoSetDict.write("        name         local; \n")
    file_topoSetDict.write("        type         cellSet; \n")
    file_topoSetDict.write("        action       new; \n")
    file_topoSetDict.write("        source       rotatedBoxToCell; \n")
    file_topoSetDict.write("        sourceInfo \n")
    file_topoSetDict.write("        { \n")
    file_topoSetDict.write("            origin ("+'{:7.1f}'.format(origin[i][0])+" "+'{:7.1f}'.format(origin[i][1])+" "+'{:7.1f}'.format(origin[i][2])+"); \n")
    file_topoSetDict.write("            i      ("+'{:7.1f}'.format(iVector[i][0])+" "+'{:7.1f}'.format(iVector[i][1])+" "+'{:7.1f}'.format(iVector[i][2])+"); \n")
    file_topoSetDict.write("            j      ("+'{:7.1f}'.format(jVector[i][0])+" "+'{:7.1f}'.format(jVector[i][1])+" "+'{:7.1f}'.format(jVector[i][2])+"); \n")
    file_topoSetDict.write("            k      ("+'{:7.1f}'.format(kVector[i][0])+" "+'{:7.1f}'.format(kVector[i][1])+" "+'{:7.1f}'.format(kVector[i][2])+"); \n")
    file_topoSetDict.write("        } \n")
    file_topoSetDict.write("    } \n")
    file_topoSetDict.write("); \n")
    file_topoSetDict.write(" \n")
    file_topoSetDict.write("// ************************************************************************* // \n")
    file_topoSetDict.close
os.remove(file_topoSetDict.name) #- To remove the refineMesh +1 (unused)

#- Plot
# plt.figure(1)
# c = ['b','r']
# for iTurb in range(nb_turbines):
#     plt.scatter(hubLocation[iTurb][0],hubLocation[iTurb][1],marker='o',label='Turbine '+str(iTurb+1))
# for i in range(nb_refineMesh):
#     plt.plot([origin[i][0]+iVector[i][0],origin[i][0],origin[i][0]+jVector[i][0],origin[i][0]+iVector[i][0]+jVector[i][0],origin[i][0]+iVector[i][0]],[origin[i][1]+iVector[i][1],origin[i][1],origin[i][1]+jVector[i][1],origin[i][1]+iVector[i][1]+jVector[i][1],origin[i][1]+iVector[i][1]],'--',color = c[i],label="Refinement "+str(i+1))
   
#- Associated probeLines creation
D = diameter    
wakeEndLastTurb = wakeEnd #- in D, for the last turbine only
xD = list(np.arange(wakeStart,wakeEnd+dwake,dwake)) #- every dwake m
xDLastTurb = list(np.arange(wakeStart,wakeEndLastTurb+dwake,dwake)) #- for last Turbine we look at 10D
posx = hubLocation[0][0]
ymin = -3*D
ymax = +3*D
# outputInterval = 50 #- outputInterval*dt = Frequncy of acquisition is 0.9s
num = int((ymax-ymin)/1)
# y = np.linspace(ymin,ymax,num)
y = list(np.arange(ymin,ymax,1)) # every 0.25 m
z = hubLocation[0][2]

file = open(casePath+'/system/sampling/probes_xD.0','w')
for iTurb in range(nb_turbines):
    for i in range(len(xD)):
        file.write('turb'+str(iTurb+1)+'_x_'+str(xDLastTurb[i])+'D\n')
        file.write('{ \n')
        file.write('   type probes;\n')
        file.write('   functionObjectLibs ("libsampling.so");\n')
        file.write('   name turb'+str(iTurb+1)+'_x_'+str(xDLastTurb[i])+'D;\n')
        file.write('   interpolationScheme cellPoint;\n')
        # file.write('   outputControl timeStep;\n')
        # file.write('   outputInterval'+str(outputInterval)+';\n')    
        file.write('   outputControl adjustableTime;\n')
        file.write('   writeInterval '+str(timeStep)+';\n') #- Acquisition at 1Hz
        file.write('   timeStart '+str(startTime)+';\n') #- Start recording
        file.write('   timeEnd '+str(endTime)+';\n') #- End recording
        file.write('   fields (U UAvg uRMS nuSGS k kSGS kResolved uuPrime2 Uprime nuSGSmean kSGSmean Smean Rmean);\n')
        file.write('   probeLocations\n')
        file.write('   (\n')
        for ii in range(len(y)):
            file.write('        ('+str(int(hubLocation[iTurb][0] + xD[i]*D))+' '+str(int(hubLocation[iTurb][1]+y[ii]))+' '+str(z)+')\n')
        file.write('   );\n')
        file.write('}\n')

        #- Plot
        # plt.figure(1)
        # plt.plot(hubLocation[iTurb][0] + xD[i]*D,hubLocation[iTurb][1] + y[ii],'.',color = 'C'+str(iTurb),markersize=0.05)            
file.close()

#-
xD = list(np.arange(inflow,1,dwake))

file = open(casePath+'/system/sampling/probes_inflow_xD.0','w')
for i in range(len(xD)):
    file.write('inflow_x_'+str(abs(xD[i]))+'D\n')
    file.write('{ \n')
    file.write('   type probes;\n')
    file.write('   functionObjectLibs ("libsampling.so");\n')   
    file.write('   name inflow_x_'+str(abs(xD[i]))+'D;\n')
    file.write('   interpolationScheme cellPoint;\n')
    file.write('   outputControl adjustableTime;\n')
    file.write('   writeInterval '+str(timeStep)+';\n') #- Acquisition at 1Hz
    # file.write('   outputControl timeStep;\n')
    # file.write('   outputInterval'+str(outputInterval)+';\n')
    file.write('   timeStart '+str(startTime)+';\n') #- Start recording
    file.write('   timeEnd '+str(endTime)+';\n') #- End recording
    file.write('   fields (U UAvg uRMS nuSGS k kSGS kResolved uuPrime2 Uprime nuSGSmean kSGSmean Smean Rmean);\n')
    file.write('   probeLocations\n')
    file.write('   (\n')
    for ii in range(len(y)):
        file.write('        ('+str(int(hubLocation[0][0] + xD[i]*D))+' '+str(int(hubLocation[0][1]+y[ii]))+' '+str(z)+')\n')
    #- Plot
    # plt.figure(1)
    # plt.plot(hubLocation[0][0] + xD[i]*D,hubLocation[0][1] + y[ii],'k.')#,markersize=0.05)
    file.write('   );\n')
    file.write('}\n')
file.close()

#- 
file_planes=open(casePath+"system/sampling/cuttingPlanes.0",'w')

file_planes.write("cuttingPlanes   // You can change the name \n")
file_planes.write("     { \n")
file_planes.write("         type surfaces; \n")
file_planes.write("         functionObjectLibs (\"libsampling.so\"); \n")
file_planes.write("         enabled true; \n")
file_planes.write("         verbose true; \n")
file_planes.write("         interpolationScheme cellPoint; \n")
file_planes.write("         //outputControl timeStep; \n")
file_planes.write("         //outputInterval 50; \n")
file_planes.write("         outputControl adjustableTime; \n")
file_planes.write("         writeInterval "+str(timeStep)+";  // to modify  \n")
file_planes.write("         surfaceFormat raw;  //vtk; \n")
file_planes.write("         timeStart "+str(startTime)+"; \n")
file_planes.write("         timeEnd "+str(endTime)+"; \n")
file_planes.write("         fields (U UAvg uRMS uuPrime2 Uprime nuSGSmean kSGSmean kResolved Smean); \n")
file_planes.write("         surfaces \n")
file_planes.write("         ( \n")
file_planes.write("            hubHeight // You can change the name \n")
file_planes.write("            { \n")
file_planes.write("               type cuttingPlane; \n")
file_planes.write("               planeType  pointAndNormal; \n")
file_planes.write("               pointAndNormalDict \n")
file_planes.write("               { \n")
file_planes.write("               basePoint (0. 0. "+str(hubHeight)+");  // to modify \n")
file_planes.write("               normalVector (0. 0. 1.); // to modify \n")
file_planes.write("               } \n")
file_planes.write("               interpolate true; \n")
file_planes.write("            } \n")
file_planes.write(" \n")
file_planes.write(" \n")
file_planes.write("            turbineWidth // You can change the name \n")
file_planes.write("            { \n")
file_planes.write("               type cuttingPlane; \n")
file_planes.write("               planeType  pointAndNormal; \n")
file_planes.write("               pointAndNormalDict \n")
file_planes.write("               { \n")
file_planes.write("               basePoint (0. 1500. 0);  // to modify \n")
file_planes.write("               normalVector (0. 1. 0.); // to modify \n")
file_planes.write("               } \n")
file_planes.write("               interpolate true; \n")
file_planes.write("            } \n")
file_planes.write("         ); \n")
file_planes.write("      } \n")
    
file_planes.close
