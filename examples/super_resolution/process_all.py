###################################################
# File Name     : process_all.py
# Creation Date : 29-03-2023
# Last Modified : Wed 29 Mar 2023 12:21:59 PM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################


import os
import numba
import argparse
import numpy as np
import pandas as pd
import img3


WORK = "/home/aecono/work"

parser = argparse.ArgumentParser()
parser.add_argument('-m', type=str, nargs='+', required=True, help="MARKER (C2) csv file")
parser.add_argument('-c', type=str, nargs='+', required=True, help="LOCATION (C1/4) csv file")
parser.add_argument('-g', type=str, required=True, help="group (condition)")
parser.add_argument('-o', type=str, required=True, help="output directory")
args = parser.parse_args()


# Loop over csv file pairs
for fm,fc in zip(args.m, args.c):

    print("Processing files:")
    print("  %s" % fc)
    print("  %s" % fm)


    #----------------------------------
    # Exclude duplicate C2 entries
    #----------------------------------
    datafile = pd.read_csv(fm)
    x = np.asarray(datafile['x [nm]'])
    y = np.asarray(datafile['y [nm]'])
    z = np.asarray(datafile['z [nm]'])

    zmin = abs(np.min(z))
    z += zmin
    zmax = np.max(z)

    # truncated data
    zres = 15 # minimum resolution (accuracy) in nm
    xt = np.floor(x/zres)
    yt = np.floor(y/zres)
    zt = np.floor(z/zres)

    # keep only unique particle rows
    C2 = (np.vstack([xt,yt,zt])).T
    unique_C2 = np.unique(C2, axis=0)

    percentage_removed = (len(C2)-len(unique_C2)) / len(C2) * 100.



import matplotlib.pyplot as plt
fig = plt.figure(figsize=(12,8))
for p in allremoved:
    plt.plot(ZRES_,p, '-o')

plt.xlabel("threshold [nm]")
plt.ylabel("percentage of C2 points removed")
plt.xscale('log')
plt.grid()
plt.savefig("percentage_removed_%s.png" % args.o)
plt.close()


