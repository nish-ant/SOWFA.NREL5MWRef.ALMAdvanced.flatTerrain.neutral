#!/bin/bash
#
#SBATCH --job-name=<rN>.0.ABL
#SBATCH --output=log.0.solve
#
#SBATCH --nodes=7
#SBATCH --ntasks-per-node=32
#SBATCH --time=3-12:00:00
#SBATCH --ear=off
#SBATCH --mem=90G

echo "#############################"
echo "User:" $USER
echo "Submit time:" $(squeue -u $USER -o '%30j %20V' | \
    grep -e $SLURM_JOB_NAME | awk '{print $2}')
echo "Launch time:" `date +"%Y-%m-%dT%T"`
echo "Host:" `hostname`
echo "Directory:" `pwd`
echo "SLURM_JOBID:" $SLURM_JOBID
echo "SLURM_JOB_NAME:" $SLURM_JOB_NAME
echo "SLURM_SUBMIT_DIR:" $SLURM_SUBMIT_DIR
echo "SLURM_JOB_NODELIST:" $SLURM_JOB_NODELIST
echo "#############################"

# Ensure only owner can read the output
umask 0077

export SLURM_COMP_VERBOSE=3
export SLURM_LOADER_VERBOSE=3

# ******************************* USER INPUT ******************************* #
startTime=0                     # Start time (DO NOT change for restarted runs)
writeIntervalBeforeBdData=5000  # Averages computation starts with "BdData" times
endTimeBeforeBdData=20000
startTimeBdData=$endTimeBeforeBdData
writeIntervalBdData=1500
endTimeBdData=21000
solver=superDeliciousVanilla
initializer=setFieldsABL
runNumber=0
cores=216 # $SLURM_NTASKS
# ************************************************************************** #

unset LD_LIBRARY_PATH

#- Source the bash profile and then call the appropriate OpenFOAM version function
echo "Sourcing the bash profile, loading modules, and setting the OpenFOAM environment variables..."
source /home/nishant/.bash_profile
module purge
module load gcc/7.3.0
#
source /home/nishant/tools/spack/share/spack/setup-env.sh
spack env activate preciceFoam 
#
export SOWFA_DIR=$WM_PROJECT_USER_DIR/SOWFA6
export SOWFA_APPBIN=$SOWFA_DIR/platforms/$WM_OPTIONS/bin
export SOWFA_LIBBIN=$SOWFA_DIR/platforms/$WM_OPTIONS/lib
export LD_LIBRARY_PATH=$SOWFA_LIBBIN:$LD_LIBRARY_PATH
export PATH=$SOWFA_APPBIN:$PATH

#- Copy appropriate controlDict
cp system/controlDict.$runNumber system/controlDict

echo "Starting OpenFOAM job at: " $(date)
echo "using " $cores " cores"
start=`date +%s.%N`

#- Find latestTime
if [ ! -d "processor0" ]; then
    latestTime=$startTime
else
    latestTime=$(foamListTimes -processor -latestTime -withZero -noFunctionObjects | tail -1)
fi

#- Run the flow field initializer
if [ $initializer = setFieldsABL ];  then
   mpirun -n $cores --bind-to core $initializer -parallel > log.$runNumber.$initializer 2>&1
fi

#- Split run to get to developed-flow stage
if [ $latestTime -lt $endTimeBeforeBdData ]; then
    foamDictionary -entry "temporalAverages.enabled" -set "false" system/sampling/temporalAverages
    foamDictionary -entry "boundaryData.enabled" -set "false" system/sampling/boundaryData
    foamDictionary -entry "startTime" -set $latestTime -disableFunctionEntries system/controlDict
    foamDictionary -entry "endTime" -set $endTimeBeforeBdData -disableFunctionEntries system/controlDict
    foamDictionary -entry "writeInterval" -set $writeIntervalBeforeBdData -disableFunctionEntries system/controlDict
    mpirun -n $cores --bind-to core $solver -parallel > log.$runNumber.$solver.startAt$latestTime 2>&1
fi

#- Make the precursor data ready for future mapping 
if [ -d processor0/$startTimeBdData ] && [ ! -f log.$runNumber.reconstructPar ]; then
    foamDictionary -entry "writeFormat" -set ascii -disableFunctionEntries system/controlDict
    reconstructPar -time $startTimeBdData -fields '(U T k p_rgh kappat nut qwall Rwall)'> log.reconstructPar.$runNumber 2>&1
    #- NOTE: The value of z0 gets recomposed as 0, sometimes with '-nan` values. 
    #-       This is a known bug. Workaround below:
    z0=$(foamDictionary -entry "z0" -value setUp)
    sed -i 's/-nan/0/g' $startTimeBdData/Rwall
    foamDictionary -entry "boundaryField.lower.z0" -set $z0 $startTimeBdData/Rwall
    foamDictionary -entry "writeFormat" -set binary -disableFunctionEntries system/controlDict
else
    touch "WARNING_caseNotReconstructed"
    echo "Case not reconstructed and first time of boundaryData not fixed. Check if endTime dir exists."
fi

#- Split run to save boundaryData and averages
continueTime=$(( $latestTime > $endTimeBeforeBdData ? $latestTime : $startTimeBdData ))
foamDictionary -entry "temporalAverages.timeStart" -set $startTimeBdData system/sampling/temporalAverages
foamDictionary -entry "temporalAverages.enabled"   -set "true" system/sampling/temporalAverages
foamDictionary -entry "boundaryData.enabled"       -set "true" system/sampling/boundaryData
foamDictionary -entry "startTime" -set $continueTime -disableFunctionEntries system/controlDict
foamDictionary -entry "endTime" -set $endTimeBdData -disableFunctionEntries system/controlDict
foamDictionary -entry "writeInterval" -set $writeIntervalBdData -disableFunctionEntries system/controlDict
mpirun -n $cores --bind-to core $solver -parallel > log.$runNumber.$solver.saveBdData.startAt$continueTime 2>&1

#- Adjust the initial time of boundaryData if it hasn't been adjusted yet
if [ ! -d postProcessing/boundaryData/north/$startTimeBdData ]; then
    for dir in north south east west; do
        ln -sf $(ls -v postProcessing/boundaryData/$dir | head -1) postProcessing/boundaryData/$dir/$startTimeBdData
    done
fi

end=`date +%s.%N`
td=$( echo "$end - $start" | bc -l )
echo "Time elapsed:" $( date -d "@$td" -u "+$((${td%.*}/86400))-%H:%M:%S" )

# mv log.solve.${SLURM_JOBID} log.solve.startAt$continueTime

# ------------------------------------------------------------------------EOF