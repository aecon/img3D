.POSIX:
.SUFFIXES:
PY = python3
CC = c99
CFLAGS = -O3
CFLAGS_OPENMP = -fopenmp
CFLAGS_SHARED = -shared -fPIC

all: install
M = \
img3.py\
img30.so\

install: $M
	@p=`"$(PY)" -m site --user-site` || exit 2 && \
	mkdir -p "$$p" && \
	for i in $M; do cp -- "$$i" "$$p/$$f" || exit 2; done && \
	printf '%s\n' "$$p"

img30.so: img3.c
	$(CC) $(CFLAGS) $(CFLAGS_OPENMP) $(CFLAGS_SHARED) -o $@ $< $(LDFLAGS)
clean:; rm -f img30.so
