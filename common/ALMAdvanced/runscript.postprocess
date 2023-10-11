#!/bin/bash
#
#SBATCH --job-name=<rN>.post.ALA
#SBATCH --output=log.postprocess
#
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --time=2-00:00:00
#SBATCH --ear=off
#SBATCH --mem=90G

echo "#############################"
echo "User:" $USER
echo "Submit time:" $(squeue -u $USER -o '%30j %20V' | grep -e $SLURM_JOB_NAME | awk '{print $2}')
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
OpenFOAMversion=OpenFOAM-6      # OpenFOAM/SOWFA version
parallel=1                      # Boolean for whether or not the preprocessing is parallel.
# ************************************************************************** #

unset LD_LIBRARY_PATH

#- Source the bash profile and then call the appropriate OpenFOAM version function
echo "Sourcing the bash profile, loading modules, and setting the OpenFOAM environment variables..."
source /home/nishant/.bash_profile
module purge
module load gcc/7.3.0
#
module load Openblas/0.3.6
module load hdf5/1.10.5/openmpi_4.0.2/gcc_7.3.0
#
source /home/nishant/tools/spack/share/spack/setup-env.sh
spack env activate preciceFoam 
#
source /home/nishant/tools/spack/opt/spack/linux-centos7-skylake_avx512/gcc-7.3.0/openfoam-org-6-oaf4546m4iah7mjkzwhel24fsocepagj/etc/bashrc
#
export OPENFAST_DIR=/home/$USER/tools/OpenFAST/install
export HDF5_DIR=/softs/contrib/apps/hdf5/1.10.5
export BLASLIB="/softs/contrib/apps/Openblas/0.3.6/lib -lopenblas"
#
export SOWFA_DIR=$WM_PROJECT_USER_DIR/SOWFA6
export SOWFA_APPBIN=$SOWFA_DIR/platforms/$WM_OPTIONS/bin
export SOWFA_LIBBIN=$SOWFA_DIR/platforms/$WM_OPTIONS/lib
export LD_LIBRARY_PATH=$SOWFA_LIBBIN:$OPENFAST_DIR/lib:$BLASLIB:$LD_LIBRARY_PATH
export PATH=$SOWFA_APPBIN:$OPENFAST_DIR/bin:$PATH
#
# conda activate sowfa
pythonPATH=/home/nishant/tools/spack/var/spack/environments/preciceFoam/.spack-env/view/bin/python

echo "Starting OpenFOAM job at: " $(date)
echo "using" $cores "core(s)"
start=`date +%s.%N`

if [ $parallel -eq 1 ]; then
   ./parReconstructPar -n 32 > log.parReconstructPar 2>&1
else
   reconstructPar -latestTime > log.reconstructPar 2>&1
fi
foamToVTK -noZero > log.foamToVTK 2>&1

end=`date +%s.%N`
td=$( echo "$end - $start" | bc -l )
echo "Time elapsed:" $( date -d "@$td" -u "+$((${td%.*}/86400))-%H:%M:%S" )

# ------------------------------------------------------------------------EOF