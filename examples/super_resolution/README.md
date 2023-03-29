# Super-Resolution Image Processing


## Data

CSV files are obtained from microscope
```
/home/shared/sa3400_3/Athena/Pierre_2023_03/404_pCaMKII_Bassoon/Data_Filtered/
```


## Image Processing

### Pre-processing
* Quntify percent of duplicate C2 marker entries based on a minimum separation distance between markers.  
```
python3.8 duplicates_C2.py -i <list of csv files (different Fields) from ONE group> -o <group name>
```


### Main processing pipeline

1. Map CSV data to 3D images
```
python3.8 csv2img.py -i <list of CSV files>
```

2. Identification of Cluster Overlays between C2-C1 and C2-C4
```
python3.8 cluster_overlay.py -m <C2 nrrd files> -c <C1/C4 nrrd files>
```

