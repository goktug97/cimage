#!/usr/bin/env python3

import os
import sys
import ueberzug.lib.v0 as ueberzug
import array, fcntl, termios
import select
from image_size import get_image_size
import argparse
import types
from pathlib import Path
import atexit
import glob

parser = argparse.ArgumentParser(description='Python Command Line Image Viewer')
parser.add_argument('input', type=str, help='Input Images.', nargs='*')
parser.add_argument('--verbose', dest='verbose', action='store_true')
parser.add_argument('--no-config', dest='no_config',
                    action='store_true', help="don't load user configuration if set")
parser.set_defaults(verbose=False)
parser.set_defaults(no_config=False)
args = parser.parse_args()

config_path = os.path.join(str(Path.home()), '.config/cimage/config')
if not os.path.exists(config_path) or args.no_config:
    config_path = os.path.join(os.path.dirname(__file__), 'config.py')
config = types.ModuleType('config', 'Config')
with open(config_path) as f:
    code = compile(f.read(), "config", "exec")
    exec(code, config.__dict__)

if not len(args.input):
    parser.print_help(sys.stderr)
    sys.exit(1)

if args.verbose:
    print(f"Read config file: {config_path}")

def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

def clean():
    show_cursor()

atexit.register(clean)

def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    if args.verbose:
        debug_hook(exception_type, exception, traceback)
    else:
        print(f'{exception_type.__name__}: {exception}')

sys.excepthook = exception_handler

# https://stackoverflow.com/a/31736883
class KeyPoller():
    def __enter__(self):
        self.fd = sys.stdin.fileno()
        self.new_term = termios.tcgetattr(self.fd)
        self.old_term = termios.tcgetattr(self.fd)

        self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def poll(self):
        dr,dw,de = select.select([sys.stdin], [], [], 0.0)
        if not dr == []:
            return sys.stdin.read(1)
        return None

def terminal_size():
    rows, columns = map(int, os.popen('stty size', 'r').read().split())
    buf = array.array('H', [0, 0, 0, 0])
    fcntl.ioctl(1, termios.TIOCGWINSZ, buf)
    terminal_width, terminal_height = buf[2], buf[3]
    return rows, columns, terminal_width, terminal_height

def insensitive_glob(pattern):
    def either(c):
        return '[%s%s]' % (c.lower(), c.upper()) if c.isalpha() else c
    return glob.glob(''.join(map(either, pattern)))

class ImageViewer(object):
    def __init__(self):
        self.image_sizes = []
        self.images = []
        file_types = ['*.bmp', '*.gif', '*.ico', '*.jpeg', '*.png', '*.tiff']

        for input in args.input:
            if os.path.isdir(input):
                for file_type in file_types:
                    images = insensitive_glob(os.path.join(input, file_type))
                    [self.process_path(image) for image in images]
            else:
                self.process_path(input)

        if not len(self.images):
            raise ValueError('No images are found')

        self.current_idx = 0
        self.n_inputs = len(self.images)

    def process_path(self, path):
        try:
            image_width, image_height = get_image_size.get_image_size(path)
            self.images.append(path)
            self.image_sizes.append([image_width, image_height])
        except get_image_size.UnknownImageFormat:
            print(f'Unknown Image Format: {path}')

    def calculate_pos_and_size(self):
        rows, columns, terminal_width, terminal_height = terminal_size()

        image_width, image_height = self.image_sizes[self.current_idx]
        scale = min(terminal_width/image_width, terminal_height/image_height)
        image_width *= scale
        image_height *= scale

        vertical_pixel_ratio = rows/terminal_height
        horizontal_pixel_ratio = columns/terminal_width

        x = int((terminal_width - image_width)/2 * horizontal_pixel_ratio) - 1
        y = int((terminal_height - image_height)/2 * vertical_pixel_ratio) - 1

        return x, y, columns, rows-y

    @ueberzug.Canvas()
    def main(self, canvas):
        x, y, width, height = self.calculate_pos_and_size()

        image = canvas.create_placement('image', x=x, y=y,
                width=width,
                height=height,
                scaler=ueberzug.ScalerOption.FIT_CONTAIN.value)
        image.path = self.images[self.current_idx]
        image.visibility = ueberzug.Visibility.VISIBLE

        prev_width, prev_height, prev_idx = width, height, self.current_idx
        hide_cursor()

        with KeyPoller() as keyPoller:
            while True:
                key = keyPoller.poll()
                image.path = self.images[self.current_idx]
                print(f'[{self.current_idx+1}/{self.n_inputs}]', end='\r')

                x, y, width, height = self.calculate_pos_and_size()
                if (prev_width != width or
                    prev_height != height or
                    prev_idx != self.current_idx):
                    image.width = width
                    image.height = height
                    prev_width = width
                    prev_height = height
                    prev_idx = self.current_idx
                    image.x = x
                    image.y = y

                if key is not None:
                    if key == config.KeyBindings.move_image_down:
                        image.y += 1
                    elif key == config.KeyBindings.move_image_up:
                        image.y -= 1
                    elif key == config.KeyBindings.move_image_left:
                        image.x -= 1
                    elif key == config.KeyBindings.move_image_right:
                        image.x += 1
                    elif key == config.KeyBindings.next_image:
                        self.current_idx += 1
                        self.current_idx %= self.n_inputs
                    elif key == config.KeyBindings.previous_image:
                        self.current_idx -= 1
                        self.current_idx %= self.n_inputs
                    elif key == config.KeyBindings.zoom_in:
                        image.width += 1
                        image.height += 1
                    elif key == config.KeyBindings.zoom_out:
                        image.width = max(image.width-1, 1)
                        image.height = max(image.height-1, 1)
                    elif key == config.KeyBindings.reset:
                        image.width = width
                        image.height = height
                        image.x = x
                        image.y = y
                    elif key == config.KeyBindings.quit_program or ord(key) == 27:
                        break

def main():
    ImageViewer().main()


if __name__ == '__main__':
    main()

