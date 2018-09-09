# DialogueState
# Logical and graphical state of the dialogue screen.
# By snarlinger (@gmail.com)
# Released under an MIT license

import pygame
import pygame.freetype
from os import path
import xml.etree.ElementTree as et
import logging as log
import sys

import src.gui.Characters as Characters
from src.StringManip import text_wrap

pygame.init()


class DialogueState:
    # font constants
    FONT_SIZE = 14
    FONT = pygame.freetype.SysFont(None, FONT_SIZE)
    FONT.pad = True
    # TODO - can probably make the below more efficient by using one of the other functions (size()?)
    LINE_HEIGHT = FONT.get_sized_ascender(FONT_SIZE) + abs(FONT.get_sized_descender(FONT_SIZE))
    DEFAULT_CHAR_COL = (0, 255, 0)

    def __init__(self, save: dict, x1: float, x2: float, y1: float, display: pygame.Surface):
        """
        Initialises the DialogueState.
        :param save: Dictionary of save file attributes.
        :param x1: First x-point of the dialogue window
        :param x2: Second x-point of the dialogue window.
        :param y1: First y-point of the dialogue window.
        """
        self.root = None
        self.screens = []  # all 'screen' ET.Elements in the current tree
        self.para_groups = []  # CharacterGroups
        self.save = save  # state of play variables
        self.display = display
        self.millis_since = 0  # milliseconds since the last character blit
        # display
        self.bg_colour = (255, 255, 255)  # the current background colour
        # character positioning
        self.LEFT_OFFSET = x1 + 5
        self.TOP_OFFSET = y1 + 5  # FIXME - this is probably too much
        self.MAX_WIDTH = x2 - self.LEFT_OFFSET  # FIXME - why left_offset? why not x2 - 5?
        # indices
        self.p = 0  # paragraph
        self.s = 0  # screen
        # logging
        log.basicConfig(stream=sys.stderr, level=log.DEBUG)

        self.load(save)
        self.new_xml('test2')
        return

    def load(self, save: dict):
        """ Sets variables based on the given save dictionary. """
        pass

    def new_xml(self, name: str) -> bool:
        """
        Tries to find and store the xml file with the requested name.
        Then, gets the screens and initial paragraphs from this xml.
        """
        try:
            tree = et.parse(path.join('dialogue', '{0}.xml'.format(name)))
            self.root = tree.getroot()
            self.screens = self.root.find('screens').findall('screen')
            self.create_para_groups()
            return True
        except FileNotFoundError:
            raise FileNotFoundError("Invalid xml file name specified.", name)
            # return False TODO

    def eval_tag(self, paragraph: et.Element) -> ([Characters.Phrase], str):
        """ Calls a slave possibly-recursive function to evaluate tags of a paragraph element. """
        def recurse(phrases, i, text, phrase_start, elements) -> ([Characters.Phrase], int, str, int):
            """
            Evaluates the tags of a paragraph element.
            Recurses on if-statements if the required conditional is met.
            :param phrases: A list of Phrases.
            :param i: The current index in the paragraph.
            :param text: The current text in the paragraph.
            :param phrase_start: The index that the current phrase starts at.
            :param elements: Elements to iterator over.
            :type elements: iter
            :return: The parameters as altered by the tags iterated in eval_tag's paragraph.
            """
            for el in elements:
                tag = el.tag
                log.debug("Tag: {}".format(tag))
                # tag cases
                if tag == 'phrasestart':
                    phrase_start = i
                elif tag == 'phraseend':
                    assert phrase_start is not None
                    phrases.append(Characters.Phrase(phrase_start, i - 1))
                    phrase_start = None
                elif tag == 'content':
                    i += len(el.text)
                    text += el.text
                elif tag == 'if':
                    phrases, i, text, phrase_start = recurse(phrases, i, text, phrase_start, el.findall('*'))
                else:
                    raise ValueError('Unsupported tag', tag, el)
            return phrases, i, text, phrase_start

        return recurse([], 0, '', None, paragraph)[0::2]  # first and third arguments

    def create_para_groups(self):
        """ Replaces self.para_groups with groups based on the current self.screen value. """
        paragraphs = self.screens[self.s].findall('para')
        para_offset = 0
        new_paragraph_groups = []
        for paragraph in paragraphs:
            # Creating paragraph of Characters
            phrases, text = self.eval_tag(paragraph.findall('*'))
            wrap = text_wrap(self.FONT, text, self.MAX_WIDTH)
            text_height = self.FONT.get_rect(text).height
            para_group = Characters.GroupCharacters(phrases, 30)
            char_i = 0
            top = 0
            for line, string in enumerate(wrap):
                count_width = 0
                top = line * self.LINE_HEIGHT + self.TOP_OFFSET + para_offset
                # Creating Character
                for ch in string:
                    left = count_width + self.LEFT_OFFSET
                    # character indexed in phrase?
                    for phrase in phrases:
                        if phrase.start <= char_i <= phrase.end:
                            phrase_group = phrase
                            break  # no overlapping phrases
                    else:
                        phrase_group = None
                    # animating spaces doesn't feel right, so we don't
                    should_anim = ch == ' '
                    char = Characters.Character(self.DEFAULT_CHAR_COL, ch, self.FONT, (top, left), char_i, line,
                                                phrase_group, should_anim, self.display)
                    count_width += char.rect.width
                    para_group.add(char)
                    char_i += 1
                char_i += 1  # TODO - why this one?
            new_paragraph_groups.append(para_group)
            para_offset = top + text_height

        self.para_groups = new_paragraph_groups
        self.p = 0

    def next_screen(self):
        """ Finds the next screen and updates the state. """
        self.s += 1
        if self.s >= len(self.screens):
            raise IndexError('Screen index out of range. There should have been an event to change the xml file by '
                             'now.', 'screen', 'screens')
        else:
            log.debug("NEXT SCREEN")
            self.p = 0
            self.create_para_groups()

    def next_paragraph(self):
        """
        Handles the logic for when a new paragraph is requested.
        If there is no next paragraph, next_screen() is called.
        """
        self.p += 1
        if self.p >= len(self.para_groups):
            self.next_screen()

    def update(self):
        """ Go through each CharacterGroup in para_groups and call their update functions. """

        return
