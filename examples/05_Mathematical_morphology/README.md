# Example: Mathematical Morphology

This folder contains examples with morphological operations supported by img3 on 3D images.


### Binarization
To run the binarization example:
```
python3 binarize.py
```
After running the example, two new files `binary.raw` and `binary.nrrd` should appear in this folder. Values 1 correspond to pixels in `../data/example.raw` that have value larger than the threshold 220. Likewise, values 0 correspond to pixels of `../data/example.raw` with values smaller than the threshold.


### Erosion
To run the example:
```
python3 erosion.py
```

After running the example, two new files `output.raw` and `output.nrrd` should appear in this folder.
All pixels of `output.raw` should have a value 10.

