from word import word
from definitions import draw
from variables import IMAGES, height, width
import pygame


class textBox:
    def __init__(self, text, font, boxSprite, left, top, maximumWidth):
        """textBox(text, font, boxSprite, left, top, maximumWidth).draw() draws a text box with sprite boxSprite,
        leftmost point at left, topmost point at top, and width maximumWidth and that contains text text in
        font font."""
        self.sprite = boxSprite
        self.words = []
        text = text.upper()
        wordsLeft = text.split()
        currentRight = left + maximumWidth * 2 / 33
        currentY = height / 60 + top

        while wordsLeft:
            nextWord = word(currentRight, currentY, wordsLeft[0], font)
            currentRight += nextWord.width + width / 160
            # If the next word can be fit into the text box without the text going down a line, fit the next word into
            # the text's current line. Otherwise, go down a line, go back to the left, and add the next word.

            if currentRight < maximumWidth * 32 / 33 + left:
                self.words.append(nextWord)
                wordsLeft.pop(0)

            else:
                currentRight = left + maximumWidth * 2 / 33
                currentY += height / 45

        self.height = currentY + height / 21 - top
        self.width = maximumWidth
        self.place = pygame.Rect(left, top, maximumWidth, self.height)

    def draw(self):
        draw(self, scaling=(self.width, self.height))

        for i in self.words:
            i.draw()
