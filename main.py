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
                    description='This program reduces a batch of images by decreasing the resolution, either to meet a max file size or to bit the images within a certain kB budget.')
parser.add_argument('input', help='input folder')
parser.add_argument('output', help='output folder')
parser.add_argument('-b', '--budget', type=int, default = 50000, help='The max size of the output in kilobytes. Default is 50000 (50 MB)')
parser.add_argument('-f', '--filesize', type=int, default=0, help='The max size of a single file in kilobytes. Setting this ignores the budget.')
parser.add_argument('-cb', '--colorbits', choices = [24,32], type=int, default=32, help='The number of bits to store color with. Default is 32')
parser.add_argument('-r', '--recursive', action='store_true', help='recursively gets all images in subdirectories')

args = vars(parser.parse_args())

print(args)
# format directories, to enforce unix style
def format_directory_path(path):
    for i in range(len(path)):
        if path[i] == '\\':
            path[i] = '/'
    if path[-1] != '/':
        path += '/'
    return path

input_path = format_directory_path(args['input'])
output_path = format_directory_path(args['input'])

extensions = ['*.[jJ][pP][gG]', '*.[jJ][pP][eE][gG]', '*.[pP][nN][gG]']
files = []
for e in extensions:
    if args['recursive']:
        e = '**/' + e
    files += glob.glob(input_path + e, recursive = args['recursive'])

if not os.path.exists(output_path):
    os.makedirs(output_path)
workingdir = output_path + '/workingdir/')
if not os.path.exists(workingdir):
    os.makedirs(workingdir)
else:
    raise Exception(workingdir + " exists, please rename this directory to avoid loss of data")

from PIL import Image

for path in files:
    im = Image.open(r''+path)
    p = os.path.splitext(path)[0]
    p = format_directory_path(p)
    im.save(r''+p+'.png')
