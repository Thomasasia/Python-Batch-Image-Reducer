import argparse
import glob
from alive_progress import alive_bar
import os

# Setting up arguments
parser = argparse.ArgumentParser(
                    prog='Batch Image Reducer',
                    description='This program reduces a batch of images by decreasing the resolution, either to meet a max file size or to fit the images within a certain kB budget.',
                    epilog="Because png compression generally gets less efficient with smaller images, the final batch size may be greater than the budget. It should not be more than a 20% difference unless you're making really tiny images.")
parser.add_argument('input', help='input folder')
parser.add_argument('output', help='output folder')
parser.add_argument('-b', '--budget', type=float, default = 50000, help='The max size of the output in kilobytes. Default is 50000 (50 MB)')
parser.add_argument('-f', '--filesize', type=float, default=0, help='The max size of a single file in kilobytes. Setting this ignores the budget.')
parser.add_argument('-r', '--recursive', action='store_true', help='recursively gets all images in subdirectories')

args = vars(parser.parse_args())



# format directories, to enforce unix style
def format_directory_path(path):
    lpath = list(path)
    for i in range(len(lpath)):
        if lpath[i] == '\\':
            lpath[i] = '/'
    if lpath[-1] != '/':
        lpath.append('/')
    path = ''.join(lpath)
    return path

input_path = format_directory_path(args['input'])
output_path = format_directory_path(args['output'])

# extensions are a regex for the supported file types. more can be added.
extensions = ['*.[jJ][pP][gG]', '*.[jJ][pP][eE][gG]', '*.[pP][nN][gG]', '*.[gG][iI][fF]']

# Search for images in the directory
files = []
with alive_bar(len(extensions), title='Discovering Images', length=10, bar='filling', unknown='waves2', spinner_length = 20, stats=False) as bar:
    for e in extensions:
        if args['recursive']:
            # if it's recursive, the regex needs to be slightly different.
            e = '**/' + e
        files += glob.glob(input_path + e, recursive = args['recursive'])
        bar()

# create output path, and a directory to store converted images into.
if not os.path.exists(output_path):
    os.makedirs(output_path)
workingdir = output_path + '/workingdir/'
if not os.path.exists(workingdir):
    os.makedirs(workingdir)
else:
    #raise Exception(workingdir + " exists, please rename this directory to avoid loss of data")
    pass

from PIL import Image
import PIL

# convert image to PNG. It takes longer to do this before resizing, but it will make the resizing more accurate.
# This could be skipped if the compression rate could be calculated or estimated differently.
newpaths=[]
image_names = []
itr = 0
with alive_bar(len(files), title='Converting images', length=40, bar='bubbles', spinner='waves2', spinner_length = 15, stats=True) as bar:
    for path in files:
        try:
            im = Image.open(r''+path)
            nsplit = os.path.basename(path).split('.')
            nsplit.pop()
            name = ''.join(nsplit)
            image_names.append(name)
            newpath = workingdir + name + '.png'
            im.save(r''+newpath)
            im.close()
            newpaths.append(newpath)
            bar()
            itr += 1
        except PIL.UnidentifiedImageError:
            files.remove(path)
            bar()

# Calculate the pixel compression. That is, how many bytes per pixel are used in the image.
# this is different for each image, because pngs can compress more efficiently under certain circumstances.
pixel_sizes = []
with alive_bar(len(files), title='Calculating Pixel Compression', length=40, bar='checks', spinner='stars', spinner_length = 6, stats=True) as bar:
    for path in newpaths:
        file_size = os.path.getsize(path)
        pixels = 0
        with Image.open(path) as im:
            pixels = im.size[0] * im.size[1]
        pixel_sizes.append(file_size / pixels)
        bar()

budget = args['budget']
max_filesize = args['filesize'] * 1000
if max_filesize == 0:
    max_filesize = budget / len(files) * 1000

global total_reduction
total_reduction= 0
global total_old
total_old = 0
global total_new
total_new = 0

# this function is for calculating the statistics for display after the program runs.
def calculate_reduction(path1, path2):
    size1 = os.path.getsize(path1)
    size2 = os.path.getsize(path2)
    sizediff = size1 - size2
    global total_old
    global total_new
    total_old += size1
    total_new += size2
    global total_reduction
    total_reduction += sizediff

# The images are resized to meet the required byte size, while maintaining the aspect ratio.
# images are deleted from the working directory (not the input) after they are resized, so that the whole batch isnt stored three times.
with alive_bar(len(files), title='Resizing Images', length=40, bar='filling', spinner='radioactive', spinner_length = 11, stats=True) as bar:
    for i in range(len(newpaths)):
        path = newpaths[i]
        pixel_size = pixel_sizes[i]
        newpath = output_path + image_names[i] + '.png'
        try:
            im = Image.open(path)
        except FileNotFoundError:
            im.close()
            bar()
            continue
        # skip if the image is already small enough to be acceptable
        if os.path.getsize(path) <= max_filesize:
            im.save(newpath)
            im.close()
            calculate_reduction(files[i], newpath)
            os.remove(newpaths[i])
            bar()
            continue

        # get the ideal number of pixels:
        ideal_pixelcount = max_filesize / pixel_size

        # skip if the image is already at an optimal size
        if im.size[0] * im.size[1] <= int(ideal_pixelcount):
            im.save(newpath)
            im.close()
            calculate_reduction(files[i], newpath)
            os.remove(newpaths[i])
            bar()
            continue

        aspect_ratio = im.size[0] / im.size[1]

        # calculate the new x & y, thanks to algebra
        y = (ideal_pixelcount / aspect_ratio) ** 0.5
        x = aspect_ratio * y

        newsize = (int(x),int(y))
        im = im.resize(newsize)
        im.save(newpath)
        im.close()
        calculate_reduction(files[i], newpath)
        os.remove(newpaths[i])
        bar()


# clean up working directory
os.rmdir(workingdir)

print("Image reduction successful!")
print("Fun stats:")
print("\tMB Budget:" + str(round((max_filesize /1000000) * len(files),3)))
print("\tOld batch size: " + str(round(total_old / 1000000,2)) + "MB")
print("\tNew batch size: " + str(round(total_new / 1000000,2)) + "MB")
print("\tAverage old file size: " + str(round(total_old / len(files) / 1000,2)) + "kB")
print("\tAverage new file size: " + str(round(total_new / len(files) / 1000,2)) + "kB")
print("\tTotal space saved: " + str(round(total_reduction / 1000000,2)) + "MB")
print("\tAverage image reduction: " + str(round(total_reduction / len(files) / 1000,2)) + "kB")
