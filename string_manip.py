# String Manipulation
# Basic string manipulation functions necessary for displaying text.
# By snarlinger (@gmail.com)
# Released under an MIT license

import pygame, pygame.freetype

pygame.init()

def concatenate(lst, sep=' '):
    """Joins all strings in a given list into a string of separated words."""
    str = ''
    lst_length = len(lst) - 1
    for i, x in enumerate(lst):
        str += x
        if i < lst_length: str += sep
    return str

def text_wrap(font, text, max_width):
    """Returns the text that can fit in a given width and the text that can't."""
    size = font.size
    space_width = font.get_rect(' ').width
    lines = []
    words = text.split()
    while True:
        current_width = 0
        concat = ''
        for i, word in enumerate(words):
            word_width = font.get_rect(word).width
            if word_width >= max_width:
                raise ValueError("Word too large",words,word)
            if i > 0:
                current_width += space_width
                concat += ' '
            current_width += word_width
            if current_width > max_width:
                # Wrap
                lines.append(concat[:-1])
                words = words[i:]
                break
            concat += word
        else:
            lines.append(concat)
            return lines

def index_string(string):
    """Given a string, print an indexed representation of each character"""
    indexes = ''
    chs = ''
    for i, ch in enumerate(string):
        # New line after each 10 characters
        if i % 10 == 0:
            print(indexes)
            print(chs)
            indexes = ''
            chs = ''
        if i >= 100:
            indexes += str(i)
        elif i >= 10:
            indexes += str(i) + ' '
        else:
            indexes += str(i) + '  '
        chs += ch + '  '
    print(indexes)
    print(chs)