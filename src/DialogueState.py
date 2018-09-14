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

from src.Mouse import MouseState
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
    DEFAULT_CHAR_COL = (255, 255, 255)

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
        self.millis_since = None # milliseconds since the last character blit
        # display and animation
        self.speed = 30
        self.show_debug = False
        self.animating = True
        # phrases
        self.highlights = []
        self.hovered_phrase = None
        self.selected_phrase = None
        # character positioning
        self.PAD = 10
        self.LEFT_OFFSET = x1 + self.PAD
        self.TOP_OFFSET = y1 + self.PAD
        self.MAX_WIDTH = x2 - x1 - (self.PAD * 2)
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

    def update_millis_since(self):
        self.millis_since = pygame.time.get_ticks()

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
            para_group = Characters.GroupCharacters(self.display, phrases, self.speed)
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
                    should_anim = ch != ' '
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
        self.update_millis_since()

    def blit_highlights(self):
        """ Blits each highlight in highlights. """
        for h in self.highlights:
            self.display.blit(h[0], h[1])

    def draw_highlight(self, top_left, bottom_right, colour):
        """ Returns the surface and rectangle for a given highlight. """
        x = bottom_right[0] - top_left[0]
        y = bottom_right[1] - top_left[1]
        surf = pygame.Surface((x, y))
        surf.fill(colour)
        return surf, surf.get_rect(topleft=top_left)

    def create_highlights(self, phrase):
        """ Given a phrase, create highlights for the phrase. """
        self.highlights = []
        sprites = phrase.sprites()
        top_left = sprites[0].rect.topleft
        bottom_right = sprites[0].rect.bottomright
        line = sprites[0].line
        for s in sprites[1:]:
            if s.line > line:
                # append highlight
                highlight = self.draw_highlight(top_left, bottom_right, phrase.colour)
                self.highlights.append(highlight)
                # resetting/updating vars
                line = s.line
                top_left = s.rect.topleft
            bottom_right = s.rect.bottomright
        # append final highlight
        highlight = self.draw_highlight(top_left, bottom_right, phrase.colour)
        self.highlights.append(highlight)

    def phrase_hovering(self, phrase):
        """ Controls phrase hovering actions. """
        if self.hovered_phrase != phrase:
            self.hovered_phrase = phrase
            if self.hovered_phrase.known:
                self.create_highlights(phrase)

    def reset_phrase(self):
        self.selected_phrase.reset_colour()
        self.selected_phrase = None

    def phrase_selection(self, phrase, mousestate: MouseState):
        """ Handles phrase selection. """
        if mousestate == MouseState.DOWN:
            phrase.colour = (255, 0, 0)
            # creating highlights if the phrase is known
            self.hovered_phrase = None
            self.phrase_hovering(phrase)
            self.selected_phrase = phrase
        elif mousestate == MouseState.UP:
            if self.selected_phrase == phrase:
                phrase.known = True
                self.hovered_phrase = None
                pass  # TODO - phrase selected
                # resetting colour
                # self.reset_phrase()
            else:
                # phrase selection failed - resetting
                self.reset_phrase()

    def phrase_interaction(self, coord, mousestate: MouseState):
        """
        Goes through each paragraph and runs phrase functions on the first character at the given coordinate.
        If no such character is found, resets hovering and selection variables.
        """
        for para in self.para_groups[:self.p + 1]:
            for ch in para:
                phrase = ch.phrase
                if ch.phrase is not None and ch.rect.collidepoint(coord):
                    self.phrase_selection(phrase, mousestate)
                    self.phrase_hovering(phrase)
                    return
            else:
                # removing highlights
                self.hovered_phrase = None
                self.highlights = []
                # if the mouse has been released, we don't have a selected phrase anymore
                if mousestate == MouseState.UP:
                    if self.selected_phrase is not None:
                        self.reset_phrase()

    def mouse_events(self, coord, mousestate: MouseState):
        """ Handles mouse events for the dialogue state. """
        if not self.animating:
            self.phrase_interaction(coord, mousestate)

    def debug_blits(self):
        if self.show_debug:
            pygame.draw.line(self.display, (255, 0, 0), (self.LEFT_OFFSET, 300), (self.LEFT_OFFSET + self.MAX_WIDTH, 300), 1)

    def update(self):
        """ Update all currently on-screen paragraphs. """
        for para in self.para_groups[:self.p + 1]:
            self.millis_since = para.update(self.millis_since)
        self.animating = self.para_groups[self.p].animating

    def blit(self):
        """ Blit all currently on-screen paragraphs and their characters. """
        # phrase highlights
        self.blit_highlights()
        # characters
        for para in self.para_groups[:self.p + 1]:
            for ch in para.sprites()[:para.i + 1]:
                ch.blit()
        # debug
        self.debug_blits()
        # TODO - phrases
