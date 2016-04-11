if [ $# -eq 3 ]; then


BASE_PATH=/gpfs/projects/bsc19/COMPSs_APPS/pyProCT/Data/exe
DATA_PATH=$3

mkdir -p $BASE_PATH/results_$1.$2
rm -rf $BASE_PATH/results_$1.$2/*
#BSUB -M 16000
#BSUB -x


echo "#!/bin/bash
#BSUB -J p_$1.$2
#BSUB -W 07:00
#BSUB -cwd $BASE_PATH 
#BSUB -eo $BASE_PATH/results_$1.$2/err
#BSUB -oo $BASE_PATH/results_$1.$2/out
#BSUB -n $1


python hdd_main.py $BASE_PATH/results_$1.$2 $DATA_PATH $1

" > $BASE_PATH/results_$1.$2/job

bsub < $BASE_PATH/results_$1.$2/job

else 
    echo "No arguments provided [threads name data_path]"
    exit 1
fi
