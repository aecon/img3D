import os
import sys
import numba
import argparse
import numpy as np
import pandas as pd
import img3


#@numba.njit(parallel=True)
#def distance(x, y, z, distances2):
#    n = len(x)
#    for j in numba.prange(n):
#        for i in numba.prange(n):
#            x_ = x[i]-x[j]
#            x2 = x_*x_
#            y_ = y[i]-y[j]
#            y2 = y_*y_
#            z_ = z[i]-z[j]
#            z2 = z_*z_
#            d2 = x2+y2+z2
#            if d2<1.0:
#
#i/j/k
#loop over H[:,:,:]:
#


parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, nargs='+', required=True, help="csv file")
parser.add_argument('-o', type=str, required=True, help="output directory")
args = parser.parse_args()


# Load CSV data
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


    sys.exit()



    # truncated data
    threshold = 1  # nm
    xt = np.floor(x/threshold)
    yt = np.floor(y/threshold)
    zt = np.floor(z/threshold)

    


    # choose a voxel size in um
    px = 0.001
    py = 0.001

    # choose a 3D image shape
    shape = (2120, 3405)
    limits = (shape[0]*px*1.e3, shape[1]*py*1.e3)

    # 3D histogram
    sample = (np.vstack([x,y])).T
    print(sample.shape)
    H, edges = np.histogramdd(sample, range=( (0,limits[0]), (0,limits[1]) ), bins=shape )

    # check distances for C2
    N = len(x)
    Npairs = int(0.5*(N*(N-1)) + N)
    distances2 = np.zeros(Npairs)
    distance(x, y, z, distances2)

    # write to file



