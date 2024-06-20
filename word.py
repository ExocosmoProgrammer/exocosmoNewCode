from variables import IMAGES, width, height
from definitions import draw
from plainSprites import plainSprite


class word:
    def __init__(self, left, y, text, font):
        """wordObject(left, y, text, font).draw() will draw the requested text to the display with the requested
        leftmost point and with a vertical center at y."""
        # self.currentRight will always determine the leftmost point of the next letter to be added to self.
        self.currentRight = left
        self.characters = [font + i for i in text]
        self.drawnLetters = []

        for i in self.characters:
            self.currentRight += width / 320

            if i[-1] != ' ':
                characterWidth = IMAGES[f'{i}.png'].get_width()
                centerx = self.currentRight + characterWidth / 2
                self.currentRight += characterWidth

                if i[-1] == ',' or i[-1] == '.':
                    # Commas and periods will have lower centers than other characters.
                    centery = y + 11 * height / 1800

                else:
                    centery = y

                self.drawnLetters.append(plainSprite(f'{i}.png', centerx, centery))

            else:
                self.currentRight += width / 320

        self.width = self.currentRight - left

    def draw(self):
        for i in self.drawnLetters:
            draw(i)
