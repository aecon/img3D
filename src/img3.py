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



