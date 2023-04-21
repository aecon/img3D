# img3D

img3 is a python package, for image processing of large, 3D (volumetric) image data.

img3 is intended for
* storing NumPy arrays in raw file format
* storing and reading image metadata from corresponding nrrd files, used in bio-imaging
* perform copmutations on image data


## Code Structure

The img3D package is organized as follows:
* [src](src/)      : Source (C and Python) files.
* [examples](examples/) : Examples of simple use cases of the package.
* [pipelines](pipelines/) : Examples of complete pipelines for segmentation and object detection.



## Requirements

* C compiler
* numpy

## Optional requirements

* C compiler with OpenMP support
* ImageJ
* Python packages: tifffile, numba, scipy.signal

## Compilation

```
cd src
make install
```

To customize the python interpreter, C compiler, and the compilation
flags:

```
cd src
make install PY=python CC=clang CFLAGS_OPENMP= 'CFLAGS = -O2 -g'
```


## Authors

The package was developed in the labs of Prof. Petros Koumoutsakos (ETH Zurich) and Prof. Adriano Aguzzi (University of Zurich) by
* Sergey Litvinov (lisergey@ethz.ch)
* Athena Economides (athena.eco@gmail.com)

Data acquisition was performed by Francesca Catto.
