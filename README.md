Cimage: Command Line Image Viewer
===================================

![Example Screenshot](https://github.com/goktug97/cimage/blob/master/example.png)

### Dependencies
- [ueberzug](https://github.com/seebye/ueberzug)

### Installation

``` bash
git clone --recursive https://github.com/goktug97/cimage
cd cimage
python3 setup.py install --user
```

### Usage
```
usage: cimage [-h] [--verbose] [input [input ...]]

Python Command Line Image Viewer

positional arguments:
  input       Input Images.

optional arguments:
  -h, --help  show this help message and exit
  --verbose
```

### Default Keybindings
| Action  | Keybinding  |
|:-:|:-:|
| move-up  | <kbd>k</kbd> |
| move-down  | <kbd>j</kbd> |
| move-left  | <kbd>h</kbd> |
| move-right  | <kbd>l</kbd> |
| next-image  | <kbd>n</kbd> |
| previous-image  | <kbd>j</kbd> |
| zoom-in  | <kbd>K</kbd> |
| zoom-out  | <kbd>J</kbd> |
| reset  | <kbd>r</kbd> |
| quit-program  | <kbd>q</kbd> |

- You can change keybindings using a config file.
Put your configs in `~/.config/cimage/config`.


### BUGS and LIMITATIONS
- Doesn't work in tmux, getting terminal size fails (works fine in gnu-screen)
- Doesn't work with SSH
- Doesn't work in eshell, emacs ansi-term
- Ueberzug works with Image Path so can't really do any image processing without 
creating temporary image file in the system, check [this issue](https://github.com/seebye/ueberzug/issues/19#issuecomment-517761124).

