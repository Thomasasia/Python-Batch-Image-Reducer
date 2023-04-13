import argparse
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

args = parser.parse_args()
print(args)
