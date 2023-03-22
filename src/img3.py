import ctypes
import functools
import mmap
import numpy
import operator
import os
import re
import scipy.signal
import site
import sys



#~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Input / Output
#~~~~~~~~~~~~~~~~~~~~~~~~~~~


def mmap_create(path, dtype, shape, order='F'):
    with open(path, "wb+") as file:
        size = functools.reduce(operator.mul, shape, 1) * dtype.itemsize
        file.seek(size - 1, 0)
        file.write(b'\0')
        file.seek(0, 0)
        buffer = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_WRITE)
    return numpy.ndarray(shape, dtype, buffer, order=order)



def nrrd_write(path, raw_path, dtype, shape, space, byte_skip=0):
    dim = len(shape)
    order = "big" if dtype.byteorder == ">" else "little"
    try:
        type = {
            2: "uchar",
            3: "int16",
            4: "ushort",
            6: "uint32",
            7: "int",
            8: "uint64",
            11: "float",
            12: "double",
        }[dtype.num]
    except KeyError:
        raise Exception("unsuported type '%s'" % str(dtype))
    with open(path, "w") as file:
        if dim == 3:
            file.write("""\
NRRD0001
type: %s
dimension: 3
sizes: %d %d %d
spacings: %.16e %.16e %.16e
encoding: raw
endian: %s
data file: %s
byte skip: %d
""" % (type, *shape, *space, order, os.path.basename(raw_path), byte_skip))
        else:
            file.write("""\
NRRD0001
type: %s
dimension: 2
sizes: %d %d
spacings: %.16e %.16e
encoding: raw
endian: %s
data file: %s
byte skip: %d
""" % (type, *shape, *space, order, os.path.basename(raw_path), byte_skip))



def tif2raw(input_path, output_raw, output_nrrd):
    """
    input_path: path to tif file, eg: /path/to/data.tif
    output_raw: path to raw file, eg: /path/to/data.raw
    """
    print("...converting tif to raw!")
    input = tifffile.TiffFile(input_path)
    dtype = input.pages[0].dtype
    nz = len(input.pages)
    ny, nx = input.pages[0].shape
    shape = nx, ny, nz
    sys.stderr.write("%s %s\n" % (shape, dtype))
    output = io.mmap_create(output_raw, dtype, shape)
    for k, page in enumerate(input.pages):
        sys.stderr.write("%d/%d\n" % (k + 1, nz))
        a = page.asarray().T
        np.copyto(output[:, :, k], a, 'no')
    io.nrrd_write(output_nrrd, output_raw, dtype, shape, (1, 1, 1))




#~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Processing
#~~~~~~~~~~~~~~~~~~~~~~~~~~~

def convolve(input, mask, output):
    assert input.ndim == 3
    assert mask.ndim == 3
    assert output.ndim == 3
    assert input.shape == mask.shape
    assert input.shape == output.shape
    path = os.path.dirname(os.path.realpath(__file__))
    lib = numpy.ctypeslib.load_library('img3.so', path)
    fun = lib.convolve
    fun.restype = None
    fun.argtypes = [
        ctypes.c_ulong,
        ctypes.c_ulong,
        ctypes.c_ulong,
        numpy.ctypeslib.ndpointer(numpy.dtype("float32"),
                                  flags='aligned, f_contiguous, writeable'),
        numpy.ctypeslib.ndpointer(numpy.dtype("uint8"),
                                  flags='aligned, f_contiguous, writeable'),
        numpy.ctypeslib.ndpointer(numpy.dtype("float32"),
                                  flags='aligned, f_contiguous, writeable'),
    ]
    fun(*input.shape, input, mask, output)



