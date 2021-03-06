#!/usr/bin/env python3

from dataclasses import dataclass

@dataclass
class KeyBindings:
    move_image_left: str = 'h'
    move_image_right: str = 'l'
    move_image_up: str = 'k'
    move_image_down: str = 'j'
    next_image: str = 'n'
    previous_image: str = 'p'
    quit_program: str = 'q'
    zoom_in: str = 'K'
    zoom_out: str = 'J'
    reset: str = 'r'
