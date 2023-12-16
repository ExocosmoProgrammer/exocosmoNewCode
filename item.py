import pygame

from variables import IMAGES, display, width, height
from rects import rect
from textBox import textBox


class item:
    def __init__(self, name, sprite, description='This is a material.', qty=1, **extra):
        self.sprite = sprite
        self.name = name
        self.place = IMAGES[self.sprite].get_rect(center=(0, 0))
        self.hitbox = rect(pygame.Rect(self.place.centerx - width / 30,
                                       self.place.centery - height * 3 / 160,
                                       width * 3 / 80, height / 15))

        self.dragged = 0
        self.qty = qty
        self.description = description
        self.textBox = textBox(description, 'newLetter', 'textBox.png', self.hitbox.centerx, self.hitbox.centery,
                               width / 4)

        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')

    def updateHitbox(self):
        self.hitbox = rect(pygame.Rect(self.place.centerx - display.get_width() * 3 / 160,
                                       self.place.centery - display.get_height() * 3 / 160,
                                       display.get_width() * 3 / 80, display.get_height() * 3 / 80))
        self.hitbox.updatePoints()
        self.textBox = textBox(self.description, 'newLetter', 'textBox.png', self.hitbox.centerx, self.hitbox.centery,
                               width / 4)
