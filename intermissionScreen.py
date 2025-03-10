from textBox import textBox
from variables import width, fullscreenRect, height
from definitions import lesser, drawToFullScreen, getEvents, temporarilyPlay

import pygame
import datetime

class intermissionScreen:
    def __init__(self, text, sprite, music, font='newLetter', top=height / 5):
        """Creates an intermissionScreen object."""

        self.length = len(text)
        self.text = text + "Press 'y' to continue."
        self.font = font

        # self.sprite should be the name of an image in the backgrounds folder.
        self.sprite = sprite
        self.place = fullscreenRect
        self.music = music
        self.exitInfoBox = textBox("Press the y key to exit this intermission screen.", font,
                                   'invisiblePixels.png', 0, height * 8 / 9, width,
                                   lineSpacing=height / 20)
        self.top = top

    def play(self, initialMusic=None):
        """Shows self and plays music."""

        # Play music.
        pygame.mixer.music.load(f'music/{self.music}')
        pygame.mixer.music.play(loops=-1)

        # Store when self started being shown.
        startTime = datetime.datetime.now()

        # Repeatedly draw self. The following loop will end when a return statement is executed.
        while True:
            # Determine how many characters to draw based on self's duration.
            timePassedTimedelta = datetime.datetime.now() - startTime
            timePassedInSeconds = timePassedTimedelta.total_seconds()
            charactersShownQTY = int(lesser(timePassedInSeconds * 18, self.length))
            print(charactersShownQTY)

            # Store a text box to draw.
            textBoxShown = textBox(self.text[:charactersShownQTY], self.font, 'invisiblePixels.png', 0,
                                   self.top, width)
            print(len(textBoxShown.words))

            # Draw the screen.
            drawToFullScreen(self.sprite)
            textBoxShown.draw()

            if charactersShownQTY == self.length:
                self.exitInfoBox.draw()

            pygame.display.flip()

            # Exit if the intermission screen is finished and the player pressed the y key.
            if getEvents({pygame.KEYDOWN: [pygame.K_y]}) and charactersShownQTY == self.length:
                if initialMusic is not None:
                    temporarilyPlay(initialMusic)

                return
