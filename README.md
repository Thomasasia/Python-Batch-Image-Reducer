# Python-Batch-Image-Reducer

This program reduces a batch of images by decreasing the resolution, either to meet a max file size or to fit the images within a certain kB budget.
It does this by resizing the images, prioritizing accuracy over space and speed.

positional arguments:
  input                 input folder
  output                output folder

optional arguments:
  -h, --help            show this help message and exit
  -b BUDGET, --budget BUDGET
                        The max size of the output in kilobytes. Default is 50000 (50 MB)
  -f FILESIZE, --filesize FILESIZE
                        The max size of a single file in kilobytes. Setting this ignores the budget.
  -r, --recursive       recursively gets all images in subdirectories
