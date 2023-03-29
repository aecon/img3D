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

Single file for whole data processing
```
./run_process_all.sh
```


