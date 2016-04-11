#if [ $# -eq 1 ]; then

DATA_PATH=/gpfs/projects/bsc19/COMPSs_APPS/pyProCT/Data/files
BASE_PATH=/gpfs/projects/bsc19/COMPSs_APPS/pyProCT/Data
     runcompss \
     --lang=python \
     --classpath=/gpfs/projects/bsc19/COMPSs_APPS/pyProCT/Data/exe \
     /gpfs/projects/bsc19/COMPSs_APPS/pyProCT/Data/exe/compss_main.py $BASE_PATH/results_compss $DATA_PATH 1

#     --tracing=true \

#--resources=${base_app_dir}/resources_tracing.xml \


#else
#    echo "No arguments provided"
#    exit 1
#fi
