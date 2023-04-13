import argparse
import glob
from alive_progress import alive_bar
import os
#options:
#input folder
#output folder
# max file size (ignores batch size)
# max batch size (default 50mb)
# 16 bit color
parser = argparse.ArgumentParser(
                    prog='Batch Image Reducer',
                    description='This program reduces a batch of images by decreasing the resolution, either to meet a max file size or to fit the images within a certain kB budget.')
parser.add_argument('input', help='input folder')
parser.add_argument('output', help='output folder')
parser.add_argument('-b', '--budget', type=int, default = 50000, help='The max size of the output in kilobytes. Default is 50000 (50 MB)')
parser.add_argument('-f', '--filesize', type=int, default=0, help='The max size of a single file in kilobytes. Setting this ignores the budget.')
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

extensions = ['*.[jJ][pP][gG]', '*.[jJ][pP][eE][gG]', '*.[pP][nN][gG]']
files = []
with alive_bar(len(extensions), title='Discovering Images', length=10, bar='filling', unknown='waves2', spinner_length = 20, stats=False) as bar:
    for e in extensions:
        if args['recursive']:
            e = '**/' + e
        files += glob.glob(input_path + e, recursive = args['recursive'])
        bar()

if not os.path.exists(output_path):
    os.makedirs(output_path)
workingdir = output_path + '/workingdir/'
if not os.path.exists(workingdir):
    os.makedirs(workingdir)
else:
    #raise Exception(workingdir + " exists, please rename this directory to avoid loss of data")
    pass

from PIL import Image

newpaths=[]
image_names = []
with alive_bar(len(files), title='Converting images', length=40, bar='filling', spinner='waves2', spinner_length = 7, stats=True) as bar:
    for path in files:
        im = Image.open(r''+path)
        name = os.path.basename(path).split('.')[0]
        image_names.append(name)
        newpath = workingdir + name + '.png'
        im.save(r''+newpath)
        im.close()
        newpaths.append(newpath)
        bar()

pixel_sizes = []
with alive_bar(len(files), title='Calculating Pixel Compression', length=40, bar='filling', spinner='waves2', spinner_length = 7, stats=True) as bar:
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

def calculate_reduction(path1, path2):
    sizediff = os.path.getsize(path1) - os.path.getsize(path2)
    global total_reduction
    total_reduction += sizediff

with alive_bar(len(files), title='Resizing Images', length=40, bar='filling', spinner='waves2', spinner_length = 7, stats=True) as bar:
    for i in range(len(newpaths)):
        path = newpaths[i]
        pixel_size = pixel_sizes[i]
        newpath = output_path + image_names[i] + '.png'
        im = Image.open(path)
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

        # calculate the new X & Y, thanks to algebra
        y = (ideal_pixelcount / aspect_ratio) ** 0.5
        x = aspect_ratio * y
        newsize = (int(x),int(y))
        im = im.resize(newsize)
        im.save(newpath)
        im.close()
        calculate_reduction(files[i], newpath)
        os.remove(newpaths[i])
        bar()


os.rmdir(workingdir)

print("Image reduction successful!")
print("Total space saved: " + str(round(total_reduction / 1000000,2)) + "MB")
print("Average image reduction: " + str(round(total_reduction / len(files) / 1000,2)) + "kB")
