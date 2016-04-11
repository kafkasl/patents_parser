#!/bin/bash  -e
if [ $# -eq 1 ]; then


./launch.sh $1 2012_1_N /gpfs/projects/bsc19/COMPSs_APPS/pyProCT/Data/files/2012_1
./launch.sh $1 2012_2_N /gpfs/projects/bsc19/COMPSs_APPS/pyProCT/Data/files/2012_2
./launch.sh $1 2013_1_N /gpfs/projects/bsc19/COMPSs_APPS/pyProCT/Data/files/2013_1
./launch.sh $1 2013_2_N /gpfs/projects/bsc19/COMPSs_APPS/pyProCT/Data/files/2013_2
./launch.sh $1 2013_3_N /gpfs/projects/bsc19/COMPSs_APPS/pyProCT/Data/files/2013_3
./launch.sh $1 2014_1_N /gpfs/projects/bsc19/COMPSs_APPS/pyProCT/Data/files/2014_1
./launch.sh $1 2014_2_N /gpfs/projects/bsc19/COMPSs_APPS/pyProCT/Data/files/2014_2
./launch.sh $1 2014_3_N /gpfs/projects/bsc19/COMPSs_APPS/pyProCT/Data/files/2014_3
./launch.sh $1 2015_N /gpfs/projects/bsc19/COMPSs_APPS/pyProCT/Data/files/2015

else
   echo "Invalid number of args [nthreads]"
fi
