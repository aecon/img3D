#include <inttypes.h>
#include <math.h>
#ifdef _OPENMP
#include <omp.h>
#endif
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void objects(uint64_t npixel, const int64_t *c, uint64_t nobj, uint64_t *start,
             uint64_t *idx) {
  uint64_t *cum;
  uint64_t *count;
  uint64_t s;
  uint64_t i;
  int Verbose;

  if (npixel < 0) {
    fprintf(stderr, "%s:%d: npixel < 0\n", __FILE__, __LINE__);
    exit(2);
  }

  if (nobj < 0) {
    fprintf(stderr, "%s:%d: nobj < 0\n", __FILE__, __LINE__);
    exit(2);
  }

  Verbose = (getenv("ADV_VERBOSE") != NULL);
  if (Verbose)
    fprintf(stderr, "adv.objects: npixel, nobj: %" PRIu64 ", %" PRIu64 "\n",
            npixel, nobj);

  if ((cum = malloc((nobj + 1) * sizeof *cum)) == NULL) {
    fprintf(stderr, "%s:%d: malloc failed\n", __FILE__, __LINE__);
    exit(2);
  }
  if ((count = calloc(nobj, sizeof *count)) == NULL) {
    fprintf(stderr, "%s:%d: malloc failed\n", __FILE__, __LINE__);
    exit(2);
  }

#pragma omp parallel for
  for (i = 0; i < npixel; i++)
    if (c[i] != 0)
#pragma omp atomic
      count[c[i] - 1]++;

  if (Verbose)
    for (i = 0; i < nobj; i++)
      fprintf(stderr, "adv.objects: count[%ld] = %ld\n", i, count[i]);

  start[0] = cum[0] = s = 0;
  for (i = 0; i < nobj; i++) {
    s += count[i];
    start[i + 1] = cum[i + 1] = s;
  }

#pragma omp parallel for
  for (i = 0; i < npixel; i++) {
    uint64_t v;
    uint64_t j;
    if ((v = c[i]) != 0) {
#pragma omp atomic capture
      j = cum[v - 1]++;
      idx[j] = i;
    }
  }
  free(count);
  free(cum);
}



void convolve(uint64_t nx, uint64_t ny, uint64_t nz, const float *input,
              const uint8_t *mask, float *output) {
  int Verbose;
  Verbose = (getenv("IMG3_VERBOSE") != NULL);
  if (Verbose)
    fprintf(stderr,
            "img3.convolve: nx, ny, nz: %" PRIu64 ", %" PRIu64 ", %" PRIu64 "\n",
            nx, ny, nz);
  const double s[3][3][3] = {
      {
          {0., 0., 0.},
          {0., -1., 0.},
          {0., 0., 0.},
      },
      {
          {0., -1., 0.},
          {-1., 6., -1.},
          {0., -1., 0.},
      },
      {
          {0., 0., 0.},
          {0., -1., 0.},
          {0., 0., 0.},
      },
  };

#pragma omp parallel for
  for (int64_t k = 0; k < nz; k++) {
    for (int64_t j = 0; j < ny; j++)
      for (int64_t i = 0; i < nx; i++) {
        int64_t u, v, w;
        int64_t x, y, z;
        double sum;
        sum = 0;
        for (w = -1; w < 2; w++)
          for (v = -1; v < 2; v++)
            for (u = -1; u < 2; u++) {
              x = i + u;
              y = j + v;
              z = k + w;
              if (s[u + 1][v + 1][w + 1] != 0)
                if (x >= 0 && x < nx && y >= 0 && y < ny && z >= 0 && z < nz &&
                    mask[z * nx * ny + y * nx + x] != 0)
                  sum +=
                      input[z * nx * ny + y * nx + x] * s[u + 1][v + 1][w + 1];
                else {
                  sum = 0;
                  goto end;
                }
            }
      end:
        output[k * nx * ny + j * nx + i] = sum;
      }
  }
}


void memset0(void *input, int c, uint64_t n) {
  int Verbose;
  Verbose = (getenv("IMG3_VERBOSE") != NULL);
  if (Verbose)
    fprintf(stderr, "img3.fill: c, n: %d %" PRIu64 "\n", c, n);
  memset(input, c, n);
}



static uint64_t find(int64_t *root, int64_t v) {
  if (v == root[v])
    return v;
  return root[v] = find(root, root[v]);
}

static void union0(int64_t *root, int64_t a, int64_t b) {
  a = find(root, a);
  b = find(root, b);
  if (a != b)
    root[b] = a;
}

uint64_t labels(uint64_t nx, uint64_t ny, uint64_t nz, const uint8_t *input,
                int64_t *output, int64_t *work) {
  int Verbose;
  uint64_t n;
  int64_t cnt;
  const int64_t delta[][3] = {
      {0, 0, 1},
      {0, 1, 0},
      {1, 0, 0},
  };

  Verbose = (getenv("IMG3_VERBOSE") != NULL);
  if (Verbose)
    fprintf(stderr,
            "img3.labels: nx, ny, nz: %" PRIu64 ", %" PRIu64 ", %" PRIu64 "\n",
            nx, ny, nz);

  n = nx * ny * nz;
  for (uint64_t i = 0; i < n; i++)
    output[i] = i;

  for (int64_t k = 0; k < nz; k++) {
    if (Verbose)
      fprintf(stderr, "img3.labels: %" PRIi64 " / %" PRIi64 "\n", k + 1, nz);
    for (int64_t j = 0; j < ny; j++)
      for (int64_t i = 0; i < nx; i++) {
        int64_t o, a, b;
        int64_t x, y, z;
        a = k * nx * ny + j * nx + i;
        if (input[a] != 0)
          for (o = 0; o < sizeof delta / sizeof *delta; o++) {
            x = i + delta[o][0];
            y = j + delta[o][1];
            z = k + delta[o][2];
            if (x < nx && y < ny && z < nz) {
              b = z * nx * ny + y * nx + x;
              if (input[b] != 0)
                union0(output, a, b);
            }
          }
      }
  }

  memset(work, 0, n * sizeof *work);
  cnt = 0;
  for (uint64_t i = 0; i < n; i++)
    if (input[i] != 0) {
      uint64_t j;
      j = find(output, i);
      if (work[j] == 0)
        work[j] = ++cnt;
    }

  for (uint64_t i = 0; i < n; i++)
    output[i] = input[i] != 0 ? work[output[i]] : 0;

  return cnt;
}

uint64_t remove_small_objects(uint64_t n, int64_t *input, uint64_t min_size,
                              int64_t *work) {
  int Verbose;
  uint64_t i;
  uint64_t cnt;
  Verbose = (getenv("ADV_VERBOSE") != NULL);
  if (Verbose)
    fprintf(stderr,
            "adv.remove_small_objects: n, min_size: %" PRIu64 " %" PRIu64 "\n",
            n, min_size);

  memset(work, 0, n * sizeof *work);

#pragma omp parallel for
  for (i = 0; i < n; i++)
    if (input[i] > 0)
#pragma omp atomic
      work[input[i]]++;

  cnt = 0;
#pragma omp parallel for
  for (i = 1; i < n; i++) {
    uint64_t j;
    if (work[i] >= min_size) {
#pragma omp atomic capture
      j = ++cnt;
      work[i] = j;
    } else
      work[i] = 0;
  }

#pragma omp parallel for
  for (i = 0; i < n; i++)
    input[i] = work[input[i]];

  return cnt;
}


