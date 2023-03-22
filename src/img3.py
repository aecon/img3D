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


def nrrd_read(path):
    me = "adv.py"
    D = {"byte skip": 0, "endian": "little"}
    try:
        with open(path, "r") as file:
            line = file.readline()
            if line == "":
                sys.stderr.write("%s: fail to read '%s'\n" % (me, path))
                sys.exit(2)
            if line != "NRRD0001\n":
                sys.stderr.write("%s: not a nrrd file '%s'\n" % (me, path))
                sys.exit(2)
            nline = 1
            while True:
                line = file.readline()
                nline += 1
                if line == "":
                    break
                line = line.rstrip("\n")
                line0 = line.split(":")
                if len(line0) != 2:
                    sys.stderr.write("%s:%d: unexpected line '%s'\n" %
                                     (path, nline, line))
                    sys.exit(2)
                key = line0[0].strip()
                value = line0[1].strip()
                if key == "type":
                    try:
                        D[key] = {
                            "float": numpy.dtype("float32"),
                            "double": numpy.dtype("float64"),
                            "uchar": numpy.dtype("uint8"),
                            "ushort": numpy.dtype("uint16"),
                            "uint32": numpy.dtype("uint32"),
                            "uint64": numpy.dtype("uint64"),
                            "int": numpy.dtype("int64"),
                        }[value]
                    except KeyError:
                        sys.stderr.write("%s:%d: unknown type '%s'\n" %
                                         (path, nline, value))
                        sys.exit(2)
                elif key == "dimension":
                    try:
                        D[key] = int(value)
                    except ValueError:
                        sys.stderr.write("%s:%d: wrong value '%s'\n" %
                                         (path, nline, value))
                        sys.exit(2)
                elif key == "sizes":
                    D[key] = tuple(map(int, value.split()))
                elif key == "encoding":
                    if value != "raw":
                        sys.stderr.write("%s:%d: wrong encoding '%s'\n" %
                                         (path, nline, value))
                        sys.exit(2)
                elif key == "endian":
                    D[key] = value
                elif key == "data file":
                    D[key] = value
                elif key == "byte skip":
                    D[key] = int(value)
                elif key == "spacings":
                    D[key] = tuple(map(float, value.split()))
                else:
                    sys.stderr.write("%s:%d: unknown key '%s'\n" %
                                     (path, nline, key))
                    sys.exit(2)
            if not "spacings" in D:
                D["spacings"] = (1, ) * D["dimension"]
            D["path"] = os.path.join(os.path.dirname(path), D["data file"])
    except UnicodeDecodeError:
        sys.stderr.write("%s: not an nrrd file '%s'\n" % (me, path))
        sys.exit(2)
    except FileNotFoundError:
        sys.stderr.write("%s: not a file '%s'\n" % (me, path))
        sys.exit(2)
    except PermissionError:
        sys.stderr.write("%s: fail to read '%s'\n" % (me, path))
        sys.exit(2)
    return D


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

def memset(input, value):
    path = os.path.dirname(os.path.realpath(__file__))
    lib = numpy.ctypeslib.load_library('img3.so', path)
    fun = lib.memset0
    fun.restype = None
    fun.argtypes = [
        numpy.ctypeslib.ndpointer(flags='aligned, f_contiguous, writeable'),
        ctypes.c_int,
        ctypes.c_ulong,
    ]
    fun(input, value, input.nbytes)


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


def labels(input, output, work):
    assert input.ndim == 3
    assert input.shape == output.shape
    assert input.shape == work.shape
    path = os.path.dirname(os.path.realpath(__file__))
    lib = numpy.ctypeslib.load_library('img3.so', path)
    fun = lib.labels
    fun.restype = ctypes.c_ulong
    fun.argtypes = [
        ctypes.c_ulong,
        ctypes.c_ulong,
        ctypes.c_ulong,
        numpy.ctypeslib.ndpointer(numpy.dtype("uint8"),
                                  flags='aligned, f_contiguous, writeable'),
        numpy.ctypeslib.ndpointer(numpy.dtype("int64"),
                                  flags='aligned, f_contiguous, writeable'),
        numpy.ctypeslib.ndpointer(numpy.dtype("int64"),
                                  flags='aligned, f_contiguous, writeable'),
    ]
    return fun(*input.shape, input, output, work)


def remove_small_objects(input, min_size, work):
    assert input.size == work.size
    path = os.path.dirname(os.path.realpath(__file__))
    lib = numpy.ctypeslib.load_library('adv0.so', path)
    fun = lib.remove_small_objects
    fun.restype = ctypes.c_ulong
    fun.argtypes = [
        ctypes.c_ulong,
        numpy.ctypeslib.ndpointer(numpy.dtype("int64"),
                                  flags='aligned, f_contiguous, writeable'),
        ctypes.c_ulong,
        numpy.ctypeslib.ndpointer(numpy.dtype("int64"),
                                  flags='aligned, f_contiguous, writeable'),
    ]
    return fun(input.size, input, min_size, work)


def objects(label, nobj):
    assert label.ndim == 3
    assert nobj >= 0
    dtype = numpy.uint64
    npixel = numpy.count_nonzero(label)
    start = numpy.empty(nobj + 1, dtype=dtype)
    work = numpy.empty(npixel, dtype=dtype)
    path = os.path.dirname(os.path.realpath(__file__))
    lib = numpy.ctypeslib.load_library('adv0.so', path)
    fun = lib.objects
    fun.restype = None
    fun.argtypes = [
        ctypes.c_ulong,
        numpy.ctypeslib.ndpointer(numpy.int64,
                                  flags='aligned, f_contiguous, writeable'),
        ctypes.c_ulong,
        numpy.ctypeslib.ndpointer(dtype,
                                  flags='aligned, f_contiguous, writeable'),
        numpy.ctypeslib.ndpointer(dtype,
                                  flags='aligned, f_contiguous, writeable'),
    ]

    fun(label.size, label, nobj, start, work)
    idx = numpy.empty((npixel, 3), dtype=dtype)
    idx[:, 0], idx[:, 1], idx[:, 2] = numpy.unravel_index(work, label.shape, order='F')
    lst = [idx[a:b] for a, b in zip(start[:nobj], start[1:nobj + 1])]
    return lst



