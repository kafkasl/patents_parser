if [ $# -eq 1 ]; then


BASE_PATH=/gpfs/projects/bsc19/COMPSs_APPS/pyProCT/Data/exe


echo "#!/bin/bash
#BSUB -J p_zip
#BSUB -W 02:00
#BSUB -cwd $BASE_PATH 
#BSUB -eo $BASE_PATH/zip_err
#BSUB -oo $BASE_PATH/zip_out
#BSUB -n 4

zip patents_reassignments.zip $1/*

" > $BASE_PATH/zip_job

bsub < $BASE_PATH/zip_job

else 
    echo "No arguments provided [path]"
    exit 1
fi
