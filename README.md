## Thinsight
Thinsight is a software tool meant for thin section analysis.
Currently its only focus is on segmentation. It has been tested on Windows 10 and 11, but not on any unix systems.

## Running the application
To run the application, run `main.py` in the `src` folder using Python.

### Required packages
- PyQt5
- Scikit-image
- numpy
- matplotlib

### Known issues
- Histogram does not work the first time after performing global segmentation.
- Selecting regions through the viewport only works on a certain screen sizes.
- Zoom functionality is not fully correct.
