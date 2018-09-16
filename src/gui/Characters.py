# Characters
#
# By snarlinger (@gmail.com)
# Released under an MIT license

import pygame
import pygame.mixer
import pygame.freetype as freetype
from os import path
import sys
import logging as log

import src.StringManip

pygame.init()
# mixer initialisation
pygame.mixer.pre_init(16000, -16, 2, 1024)
pygame.mixer.quit()
pygame.mixer.init(16000, -16, 2, 512)


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

    def blit(self):
        """ Blits the Character to the display with any effects. """
        self.display.blit(self.image, self.rect)
        # add effects here #


class GroupCharacters(pygame.sprite.Group):
    """ Group of Characters """
    PUNCTUATION = [',', '.', ':', ';', '?', '!']

    def __init__(self, display: pygame.Surface, phrases: list, base_speed: int):
        super().__init__()
        self.base_speed = base_speed
        self.speed = base_speed
        self.display = display
        # highlighting
        self.phrases = phrases
        self.highlights = []
        # animating
        self.i = -1
        self.pause_punctuation = True  # whether we should pause if this is punctuation
        # states
        self.animating = True
        self.hovered_phrase = None
        self.selected_phrase = None
        # sound
        self.sound = pygame.mixer.Sound(path.join('assets', 'sound', 'sfx', 'cowbell-short.ogg'))
        self.sound.set_volume(0.1)
        self.skip = False
        # logging
        log.basicConfig(stream=sys.stderr, level=log.DEBUG)

    def play_sound(self):
        self.sound.play()

    def update(self, millis_since):
        """
        Animates each Character in this Group. Calls to phrase_selection() if there's nothing to animate.
        :param millis_since: milliseconds since the last Character was animated.
        :return: the current milliseconds if it has been long enough since the last animation (self.speed), the old
                 milliseconds if it hasn't
        """
        chars = self.sprites()
        millis = millis_since
        current_millis = pygame.time.get_ticks()
        # more characters to animate?
        if self.i + 1 < len(self):
            diff = current_millis - millis_since
            # enough time passed to animate?
            if diff >= self.speed:
                self.i += 1
                if not chars[self.i].should_anim:
                    pass#self.skip = False  # if we're about to animate the start of a word, we want it to sound TODO - do we want this or not?
                overlap = int(diff / self.speed)  # how many characters we need to animate
                try:
                    for x in range(overlap):
                        while not chars[self.i].should_anim:
                            self.i += 1
                        self.speed = self.base_speed
                        # punctuation pause
                        if self.pause_punctuation and chars[self.i].char in self.PUNCTUATION:
                            self.speed += 150  # TODO - should be different depending on punctuation mark
                            break  # so we pause w/o animating any more characters
                except IndexError:
                    pass
                # sound
                if not self.skip:
                    self.sound.play()
                self.skip = not self.skip

                millis = current_millis
        # no more animation - now phrase selection
        else:
            self.animating = False
            millis = current_millis

        return millis

    def mouse_events(self, coord, mousestate) -> bool:
        # phrases
        for ch in self:
            if ch.phrase is not None and ch.rect.collidepoint(coord):
                self.phrase_interaction(mousestate, ch)
                return True
        return False

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

    def phrase_hovering(self, ch):
        """ Renders the highlights for the phrase associated with a Character. """
        phrase = ch.phrase
        if self.hovered_phrase != phrase:
            self.hovered_phrase = phrase
            if self.hovered_phrase.known:
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

    def phrase_selection(self, mousedown, ch):
        if mousedown:
            # colour
            if self.selected_phrase is not None:
                self.selected_phrase.colour = self.selected_phrase.base_colour
            self.selected_phrase = ch.phrase
            self.selected_phrase.colour = (0, 255, 0)
        else:
            pass

    def phrase_interaction(self, mousedown, ch):
        self.phrase_hovering(ch)
        self.phrase_selection(mousedown, ch)

    def blit(self):
        # characters
        for ch in self.sprites()[:self.i + 1]:
            ch.blit()


class Phrase(pygame.sprite.Group):
    def __init__(self, start, end):
        super().__init__()
        # bounds
        self.start = start
        self.end = end
        # states
        self.known = True
        # colour
        self.base_colour = (0, 0, 255)
        self.colour = self.base_colour
