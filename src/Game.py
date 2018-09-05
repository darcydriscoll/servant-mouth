# Game
# Main game class - everything is centralised here.
# By snarlinger (@gmail.com)
# Released under an MIT license

import pygame
import pygame.freetype
from src.DialogueState import *

pygame.init()


class Game:
    """ Main game class. """
    FPS = 60
    WH = (640, 480)
    BG_COLOUR = (128, 128, 128)
    # key constants
    KEY_ENTER = 13
    KEY_SPACE = -1

    def __init__(self):
        """ Initialises everything for the first time. """
        self.state = DialogueState
        # display
        self.display = pygame.display.set_mode(self.WH)
        self.clock = pygame.time.Clock()

    def load(self):
        pass

    def main(self):
        """ Initiates the main game loop. """
        self.event_handling()
        self.update()
        self.blit()
        # enforce FPS and flip display
        self.clock.tick()
        self.display.flip()

    def event_handling(self):
        """
        Main event handling function.
        Handles top-level events and calls to other event functions.
        """

    def update(self):
        """ Updates the states of everything. """
        # background
        # everything else
        self.state.update()

    def blit(self):
        """ Blits everything to the display. """


if __name__ == "__main__":
    game = Game()
    game.main()
