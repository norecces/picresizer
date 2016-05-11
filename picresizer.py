# -*- coding: utf-8 -*-

import argparse
import os
import imghdr
from PIL import Image
import math


class WritableDirectory(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not os.path.isdir(values):
            raise argparse.ArgumentTypeError('%s is not a valid folder path' % (values, ))
        if not os.access(values, os.W_OK):
            raise argparse.ArgumentError('%s is not writable' % (values, ))
        else:
            setattr(namespace, self.dest, values)


class SizeSetter(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if len(values.split('x')) != 2:
            raise argparse.ArgumentTypeError('size should be in format 150x200, got %s' % (values, ))
        try:
            map(int, values.split('x'))
        except ValueError:
            raise argparse.ArgumentTypeError('width and height should be integers')

        setattr(namespace, self.dest, tuple(map(int, values.split('x'))))



def process_pic(pic_path, out_folder, namespace):
    size = namespace.size
    pic_type = namespace.type
    bg_color = namespace.color
    try:
        im = Image.open(pic_path)
        # resize to minimal size to fit image to background, width and height are locked
        im.thumbnail((min(size), min(size)), Image.ANTIALIAS)
        # create background
        bg = Image.new('RGBA', size, bg_color)
        # paste image to center
        bg.paste(im, tuple(map(lambda px: math.ceil(px/2.0) - math.ceil(min(size)/2.0), size)))
        if not pic_type:
            bg.save(os.path.join(out_folder, os.path.basename(pic_path)))
        else:
            bg.save(
                os.path.join(out_folder, os.path.basename(os.path.splitext(pic_path)[0]) + '.' + pic_type),
                format=pic_type
            )
        im.close()
        bg.close()
    except IOError:
        print('cannot create %s' % (os.path.basename(pic_path)))


def is_pic(file_path):
    try:
        file_type = imghdr.what(file_path)
    except (OSError, FileNotFoundError, Exception):
        return False
    else:
        return bool(file_type)


def main():
    input_directory = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description='Resize pics to specified size')
    parser.add_argument('-f', '--folder', action=WritableDirectory, default=input_directory)
    parser.add_argument('-s', '--size', action=SizeSetter, default=(150, 150))
    parser.add_argument('-t', '--type', choices=('jpg', 'png'))
    parser.add_argument('-c', '--color', default=None)
    args = parser.parse_args()

    output_directory = os.path.join(args.folder, 'resized')
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    files_in_dir = filter(os.path.isfile, [os.path.join(args.folder, f) for f in os.listdir(args.folder)])
    pics_in_dir = filter(is_pic, files_in_dir)
    for pic in pics_in_dir:
        process_pic(pic_path=pic, out_folder=output_directory, namespace=args)


if __name__ == '__main__':
    main()