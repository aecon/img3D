#!/bin/bash
set -eu

Dataset="PSD-Syn-TDP"
Number=404

CONDITIONS=("Ctl" "Gly" "PB" "TTX")
CHANNELS=("1" "4")



# Loop over Conditions
for Condition in ${CONDITIONS[@]}; do
# Loop over Channels
for Channel in ${CHANNELS[@]}; do

    echo "CONDITION:" $Condition
    echo "CHANNEL:" $Channel

    # Location of data
    # e.g. /mnt/vol500/DATA/PSD-Syn-TDP/404/Gly
    DATADIR="/mnt/vol500/DATA/${Dataset}/${Number}/${Condition}"
    
    # Generation of image and data files
    WORKDIR="/mnt/vol500/WORK/${Dataset}/${Number}/${Condition}"
    
    # Get number of fields (F?)
    Nfields=`find ${DATADIR} -name "*_C2_*.csv" | wc -l`
    echo "Found $Nfields Fields in ${DATADIR}"
    
    # Loop over Fields in DATADIR
    for i in `seq 1 ${Nfields}`; do
        echo ">> Processing Field: $i"
    
        DATA_M=`find ${DATADIR} -name "*_C2_*_Field${i}_*.csv"`
        DATA_C=`find ${DATADIR} -name "*_C${Channel}_*_Field${i}_*.csv"`
        ls $DATA_M
        ls $DATA_C
    
        python3 process_all.py -m "${DATA_M}" -c "${DATA_C}" -g "${Dataset}/${Number}/${Condition}"
    
        # Remove intermediate files
        echo "Removing temporary work files ..."
        rm -rf ${WORKDIR}/work.raw
        rm -rf ${WORKDIR}/tmp8.raw
        rm -rf ${WORKDIR}/labels.raw
    
    done
done  # channels loop
done  # conditions loop


