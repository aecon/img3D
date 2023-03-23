#!/bin/bash
set -eu

C=4
M=2
GROUP=Ctl

BASEDIR="/home/aecono/DATA/${GROUP}"
OUTPDIR="/home/aecono/work/"

# Get number of fields (F?)
DATA_M="${BASEDIR}/*_C${M}_*.csv"
NDATA=`ls -ltr $DATA_M | wc -l`


for i in `seq 1 ${NDATA}`; do
    echo "Processing Field: $i"

    # Convert to image
    DATA_M=`ls ${BASEDIR}/*_C${M}_*_F${i}_*.csv`
    DATA_C=`ls ${BASEDIR}/*_C${C}_*_F${i}_*.csv`
    ls $DATA_M
    ls $DATA_C
    python3 csv2img.py -i "${DATA_M}" "${DATA_C}" -o "${OUTPDIR}"

    # Cluster overlay from images
    DATA_M=`ls ${OUTPDIR}/*_C${M}_*_F${i}_*.nrrd`
    DATA_C=`ls ${OUTPDIR}/*_C${C}_*_F${i}_*.nrrd`
    ls $DATA_M
    ls $DATA_C
    python3 cluster_overlay.py -m "${DATA_M}" -c "${DATA_C}" -o "${OUTPDIR}"

    # Remove intermediate files
    rm -rf ${OUTPDIR}/*raw
    rm -rf ${OUTPDIR}/*nrrd

done

