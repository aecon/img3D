import os
import numba
import argparse
import numpy as np
import pandas as pd
import img3


parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, nargs='+', required=True, help="csv file")
parser.add_argument('-o', type=str, required=True, help="group")
args = parser.parse_args()


# Load CSV data
allremoved = []
ZRES_ = [0.1, 0.5, 1, 2, 10, 20, 100, 200] # minimum resolution in nm
for cfile in args.i:

    print("Processing file:", cfile)

    # read data from CSV file
    datafile = pd.read_csv(cfile)
    x = np.asarray(datafile['x [nm]'])
    y = np.asarray(datafile['y [nm]'])
    z = np.asarray(datafile['z [nm]'])

    zmin = abs(np.min(z))
    z += zmin
    zmax = np.max(z)

    # truncated data
    nremoved = []
    for zres in ZRES_:
        xt = np.floor(x/zres)
        yt = np.floor(y/zres)
        zt = np.floor(z/zres)

        # keep only unique particle rows
        C2 = (np.vstack([xt,yt,zt])).T
        unique_C2 = np.unique(C2, axis=0)

        nremoved.append( (len(C2)-len(unique_C2)) / len(C2) * 100. )

    print(nremoved)
    allremoved.append(nremoved)


import matplotlib.pyplot as plt
fig = plt.figure(figsize=(12,8))
for p in allremoved:
    plt.plot(ZRES_,p, '-o')

plt.xlabel("threshold [nm]")
plt.ylabel("percentage of C2 points removed")
plt.savefig("percentage_removed_%s.png" % args.o)
plt.close()



