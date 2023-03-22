#include <inttypes.h>
#include <math.h>
#ifdef _OPENMP
#include <omp.h>
#endif
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>



void convolve(uint64_t nx, uint64_t ny, uint64_t nz, const float *input,
              const uint8_t *mask, float *output) {
  int Verbose;
  Verbose = (getenv("ADV_VERBOSE") != NULL);
  if (Verbose)
    fprintf(stderr,
            "adv.convolve: nx, ny, nz: %" PRIu64 ", %" PRIu64 ", %" PRIu64 "\n",
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


