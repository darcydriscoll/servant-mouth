# Characters
#
# By snarlinger (@gmail.com)
# Released under an MIT license

import pygame
import pygame.freetype as freetype

pygame.init()


class Character(pygame.sprite.Sprite):
    """ Single character """

    def __init__(self, colour, char, font, topleft, i, line, phrase, should_anim, display, visible=True):
        """
        Initialisation method for Character.
        :param colour: The colour of the Character.
        :type colour: RGB
        :param char: The str representation of the Character.
        :type char: str
        :param font: The font to be used in the creation of the Character.
        :type font: freetype.Font
        :param topleft: The topleft position of the Character.
        :type topleft: (int, int)
        :param i: The index of the Character in its paragraph.
        :type i: int
        :param line: The line of the Character in its paragraph.
        :type line: int
        :param phrase: The Phrase this Character is in. 'None' if n/a.
        :type phrase: Phrase
        :param should_anim: Whether the DialogueState should wait a period after blitting this Character.
        :type should_anim: bool
        :type display: pygame.Surface
        :param visible: Whether the Character is visible at a given time or not.
        :type visible: bool
        """
        super().__init__()
        self.colour = colour
        self.char = char
        self.font = font
        self.topleft = topleft
        self.i = i
        self.line = line
        self.phrase = phrase
        self.should_anim = should_anim
        self.display = display
        self.visible = visible
        # add character to phrase, if phrase exists
        try:
            self.phrase.add(self)
        except AttributeError:
            pass  # Character has no Phrase - it's ok
        # render
        self.image = None
        self.rect = None
        self.render()

    def render(self):
        """ Renders the surface and rectangle of the character. """
        # create render
        rend = self.font.render(self.char, self.colour)
        rend[1].top = self.topleft[0]
        rend[1].left = self.topleft[1]
        # save
        self.image = rend[0].convert_alpha()  # TODO - potentially very inefficient - change to convert w/ specified background?
        self.rect = rend[1]

    def update(self):
        """ Blits the Character to the display with any effects. """
        self.display.blit(self.image, self.rect)
        # add effects here #


class GroupCharacters(pygame.sprite.Group):
    """ Group of Characters """

    def __init__(self, phrases: list, base_speed: int):
        super().__init__()
        self.phrases = phrases
        self.base_speed = base_speed
        pass


class Phrase(pygame.sprite.Group):
    def __init__(self, start, end):
        super().__init__()
        self.start = start
        self.end = end
        pass
