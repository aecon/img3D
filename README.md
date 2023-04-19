# img3D
Image Processing package for large, 3D (volumetric) image data


## Code Structure

The img3D package is organized as follows:
* [src][src/]      : Contains source (C and Python) files.
* [examples][examples/] : Contains examples use cases of the package.



## Requirements

* C compiler
* numpy

## Optional requirements

* C compiler with OpenMP support
* ImageJ
* Python packages: tifffile, numba, scipy.signal, matplotlib

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
