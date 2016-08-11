#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys, random, os, pygame
import numpy as np
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
Color = namedtuple('Color', ['r', 'g', 'b'])

class DisplayCharacter(object):
    def __init__(self, pos, char, fg_color, bg_color, font):
        self.pos = pos
        self.char = char
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.font = font
        self.rendered_text = self.font.render(self.char, True, self.fg_color, self.bg_color)

    def render(self, surface, y_offset):
        surface.blit(self.rendered_text, (self.pos.x, self.pos.y + y_offset))

    def size(self):
        assert(self.rendered_text.get_height() == self.font.get_height())
        return Point(self.rendered_text.get_width(), self.rendered_text.get_height())

class MatrixRain(object):
    def __init__(self, dimensions, font_widths, font_rain, font_text, text_embeds):
        self.max_dims = Point(max([v.x for v in font_widths.values()]), max([f.get_height() for f in [font_rain, font_text]]))
        self.font_rain = font_rain
        self.font_text = font_text
        self.text_embeds = text_embeds
        self.font_widths = font_widths
        self.pixel_dimensions = dimensions
        self.surface = pygame.Surface(dimensions, pygame.HWSURFACE)

        self.row_colors, self.row_render = self.generate_row(font_rain, self.max_dims.x, self.max_dims.y, self.pixel_dimensions.x, (0, 0, 0))

        # row_portion keeps track of how much of the current row is exposed
        self.row_portion = 0
        self.row_height = font_rain.get_height()

    # if previous is an array, it will be reused!
    def generate_row(self, font, char_width, char_height, row_width, bg_color, previous = None):
        char_cell_height = char_height
        char_count = int(row_width / char_width)
        char_cell_width = row_width / char_count # leave as float till later

        assert(not isinstance(previous, np.ndarray) or len(previous) == char_count)

        row_surface = pygame.Surface((row_width, char_cell_height), pygame.HWSURFACE)

        row_color = previous if isinstance(previous, np.ndarray) else np.zeros(char_count, dtype=[('r', 'i4'), ('g', 'i4'), ('b', 'i4')])
        for i in range(0, char_count):
            char = chr(random.randrange(0x3041, 0x308F, 0x1)) # Pick a random Hiragana character (U+3040 - U+309F)
            row_color[i] = Color(previous[i]['r'], previous[i]['g'] - 1 if previous[i]['g'] > 10 else 190, previous[i]['b']) if isinstance(previous, np.ndarray) else Color(0, random.randrange(10, 190, 1), 0)
            char_render = font.render(char, True, row_color[i], bg_color)
            row_surface.blit(char_render, (int(char_cell_width * i + (char_cell_width - char_render.get_width()) / 2), int((char_cell_height - char_render.get_height()) / 2)))

        return (row_color, row_surface)

    # Scroll the whole surface by one row, render current row at it's new location. Generate the next row if needed.
    def advance(self):
        advance_size = max(1, int(self.row_height / 5))
        self.surface.scroll(0, advance_size)

        self.row_portion += advance_size
        if (self.row_portion > self.row_height):
            self.surface.blit(self.row_render, (0, self.row_portion - self.row_height))
            self.row_portion = abs(self.row_height - self.row_portion)
            self.row_colors, self.row_render = self.generate_row(self.font_rain, self.max_dims.x, self.max_dims.y, self.pixel_dimensions.x, (0, 0, 0), self.row_colors)

        self.surface.blit(self.row_render, (0, self.row_portion - self.row_height))

def find_dimensions(fonts):
    return {f: Point(*f.size(ch)) for f,ch in fonts}

def main_pygame():
    os.environ['SDL_VIDEODRIVER'] = 'directx'

    pygame.init()

    display_dim = Point(1920, 1080)
    pygame.display.set_caption('termatrix')
    print(pygame.display.get_driver())
    print(pygame.display.Info())
    screen = pygame.display.set_mode(display_dim, pygame.DOUBLEBUF)
    clock = pygame.time.Clock()

    fonts = pygame.font.get_fonts()

    font_japanese = pygame.font.SysFont([f for f in fonts if 'mikachan' in f][0], 10)
    font_english = pygame.font.SysFont([f for f in fonts if 'inconsolata' in f][0], 10)
    font_dims = find_dimensions([(font_japanese, chr(0x3041)), (font_english, 'D')])
    matrix_rain = MatrixRain(display_dim, font_dims, font_japanese, font_english, sys.argv[1:])

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return
        matrix_rain.advance()
        screen.blit(matrix_rain.surface, (0, 0))
        pygame.display.flip()
        print(clock.get_fps())
        clock.tick(60)

if __name__ == '__main__':
    main_pygame()