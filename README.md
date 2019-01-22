# batch-imageprocessing
Script for batch processing Micasense rededge sensor images to reflectance, based on the Micasense image processing repository (https://github.com/micasense/imageprocessing).


This repository includes scripts in the python programming language that can be used to batch process imagery from the Micasense Rededge sensor. This repository is largely based on [scripts](https://github.com/micasense/imageprocessing) and [tutorials](https://www.micasense.com) provided by Micasense.


## Getting Started

To run this model, you will need [Python 3.6](https://www.anaconda.com/download/) and [Exiftool](https://www.sno.phy.queensu.ca/~phil/exiftool/). To run this model with the test data, download this repository to a local directory or `git clone` this repository using [git](https://git-scm.com/downloads).

Once the repository is downloaded or cloned, you are ready to run the model in R. Check out “Running the model” below to get started. 

## Files included in this repository
* **batch-imageprocessing.py** - python script for batch processing raw images to reflectance.
* **Micasense/imageprocessing** – folder containing the cloned repository from Micasense with functions for processing images to reflectance
* **test_images** – folder containing a set of test imagery for batch processing.

## Running the model
With the repository data saved to your local working directory, open the python script **batch-imageprocessing.py**. With the script open in an IDE, like [Spyder](https://www.spyder-ide.org/), change the working directory `chdir()` to the same local working directory where you saved the repository. Here, you can also define the file paths where you want the processed images to be saved. 

The script consists of two parts. In part 1, we read in the calibration photos taken before and after each flight. Preflight and post-flight calibration photo sets contain 5 images corresponding to each band of the Micasense sensor (B, G, R, Rededge, and Near-infrared). For each photo, the area of the calibration panel must be masked out manually. Part 1 produces average radiance-to-reflectance conversions factors for each band. 

Part 2 consists of a loop that reads through the raw images directory and applies the correct radiance-to-reflectance conversion factor based on the band contained in the image metadata. The output of part two are images that have been converted to reflectance. 

Part 3 transfers metadata from the raw images to the converted images. Reflectance images will not contain the original metadata, so the Exiftool command should be run in the python command prompt to transfer the original metadata to the converted images. 


## Suggested Citation
Doughty, C.L., Batch processing Micasense images to reflectance (batch-imageprocessing), (2019), GitHub repository, https://github.com/cldoughty/batch-imageprocessing

## License
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
