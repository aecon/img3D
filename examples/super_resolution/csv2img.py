import os
import img3
import argparse
import numpy as np
import pandas as pd

me = "com2img.py"

parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, nargs='+', required=True, help="csv file")
args = parser.parse_args()


# Load CSV data
for cfile in args.i:
    odir = os.path.dirname(cfile)
    datafile = pd.read_csv(cfile)
    x = np.asarray(datafile['x [nm]'])
    y = np.asarray(datafile['y [nm]'])
    z = np.asarray(datafile['z [nm]']) + 1000. # make min(z)>0
    
    # choose a voxel size in um
    px = 0.0235
    py = 0.0235
    pz = 0.01
    
    # choose a 3D image shape
    shape = (2120, 3405, 200)
    limits = (shape[0]*px*1.e3, shape[1]*py*1.e3, shape[2]*pz*1.e3)
    
    # 3D histogram
    sample = (np.vstack([x,y,z])).T
    print(sample.shape)
    H, edges = np.histogramdd(sample, range=( (0,limits[0]), (0,limits[1]), (0,limits[2]) ), bins=shape )
    
    # Save to 3D image
    odir = "%s/../Analysis" % (os.path.dirname(cfile))
    if not os.path.exists(odir):
        os.makedirs(odir)

    fraw  = "%s/%s.raw"  % (odir, cfile)
    fnrrd = "%s/%s.nrrd" % (odir, cfile)
    particles = img3.mmap_create(fraw, np.dtype("uint16"), shape)
    img3.nrrd_write(fnrrd, fraw, particles.dtype, particles.shape, (px,py,pz))
    particles[:,:,:] = H[:,:,:]


