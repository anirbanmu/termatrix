#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import time, random, locale, pygame
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
        return Point(self.rendered_text.get_width(), self.rendered_text.get_height())

class MatrixRain(object):
    def __init__(self, dimensions, font_widths, font_rain, font_text):
        self.max_dims = Point(max([v.x for v in font_widths.values()]), max([v.y for v in font_widths.values()]))
        self.font_rain = font_rain
        self.dimensions = Point(int(dimensions.x / self.max_dims.x), int(dimensions.y / self.max_dims.y))
        self.pixel_dimensions = dimensions
        self.surface = pygame.Surface(dimensions, pygame.HWSURFACE)
        self.next_row = []
        for i in range(0, self.dimensions.x):
            x_position = self.max_dims.x * i + (self.max_dims.x - font_widths[font_rain].x) / 2
            self.next_row.append(DisplayCharacter(Point(x_position, 0), chr(random.randrange(0x3041, 0x3085, 0x1)), Color(0, random.randrange(0, 255, 1), 0), Color(0, 0, 0), font_rain))

        #self.render_chars(0)
        self.row_portion = 0
        self.row_height = self.get_row_height()

    def get_row_height(self):
        return max([c.size().y for c in self.next_row])

    def render_chars(self, y_offset):
        for i,c in enumerate(self.next_row):
            row_height_compensation = (self.row_height - c.size().y) / 2
            c.render(self.surface, y_offset + row_height_compensation)

    # Scroll the whole surface by one row, fill top row with black, render each character & blit them to the top row
    def advance(self):
        advance_size = max(1, int(self.row_height / 5))
        self.surface.scroll(0, advance_size)

        self.row_portion += advance_size
        if (self.row_portion > self.row_height):
            self.render_chars(self.row_portion - self.row_height)
            self.row_portion = abs(self.row_height - self.row_portion)

            for i,c in enumerate(self.next_row):
                # Figure out what to draw next time we're called.
                fg_color = Color(c.fg_color.r, c.fg_color.g - 1 if c.fg_color.g > 10 else 250, c.fg_color.b)
                self.next_row[i] = DisplayCharacter(Point(*c.pos), chr(random.randrange(0x3041, 0x3085, 0x1)), fg_color, c.bg_color, self.font_rain)
            self.row_height = self.get_row_height()

        self.render_chars(self.row_portion - self.row_height)

def find_dimensions(fonts):
    return {f: Point(*f.size(ch)) for f,ch in fonts}

def main_pygame():
    pygame.init()

    display_dim = Point(1280, 720)
    pygame.display.set_caption('termatrix')
    print(pygame.display.get_driver())
    print(pygame.display.Info())
    screen = pygame.display.set_mode(display_dim, pygame.DOUBLEBUF)
    clock = pygame.time.Clock()

    font_japanese = pygame.font.SysFont('mikachan', 10)
    font_english = pygame.font.SysFont('inconsolata', 10)
    font_dims = find_dimensions([(font_japanese, chr(0x3041)), (font_english, 'D')])
    print(font_dims[font_japanese])
    matrix_rain = MatrixRain(display_dim, font_dims, font_japanese, font_english)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return
        matrix_rain.advance()
        screen.blit(matrix_rain.surface, (0, 0))
        pygame.display.flip()
        clock.tick(120)

if __name__ == '__main__':
    main_pygame()