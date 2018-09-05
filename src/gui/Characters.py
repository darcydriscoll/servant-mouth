# Characters
#
# By snarlinger (@gmail.com)
# Released under an MIT license

import pygame
import pygame.freetype as freetype

pygame.init()


class Character(pygame.sprite.Sprite):
    """ Single character """

    def __init__(self, colour, char: str, font: freetype.Font, topleft: (int, int), i: int, line: int, phrase,
                 should_anim: bool, visible: bool = True):
        """
        Initialisation method for Character.
        :param colour: The colour of the Character.
        :type colour: RGB
        :param char: The str representation of the Character.
        :param font: The font to be used in the creation of the Character.
        :param topleft: The topleft position of the Character.
        :param i: The index of the Character in its paragraph.
        :param line: The line of the Character in its paragraph.
        :param phrase: The Phrase this Character is in. 'None' if n/a.
        :type phrase: Phrase
        :param should_anim: Whether the DialogueState should wait a period after blitting this Character.
        :param visible: Whether the Character is visible at a given time or not.
        """


class GroupCharacters(pygame.sprite.Group):
    """ Group of Characters """

    def __init__(self, phrases: list, base_speed: int):
        pass


class Phrase:
    def __init__(self, start, end):
        pass
