# Example: Mathematical Morphology

This folder contains examples with morphological operations supported by img3 on 3D images.


### Binarization
To run the binarization example:
```
python3 binarize.py
```
After running the example, two new files `binary.raw` and `binary.nrrd` should appear in this folder. Values 1 correspond to pixels in `../large_data.tif` that have value larger than the threshold 220. Likewise, values 0 correspond to pixels of `../large_data.tif` with values smaller than the threshold.


### Erosion
To run the example:
```
python3 erosion.py
```

