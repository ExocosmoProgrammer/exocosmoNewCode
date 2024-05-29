import pygame

from variables import IMAGES, display, width, height
from rects import rect
from textBox import textBox


class item:
    def __init__(self, name, sprite, description=None, qty=1, stackSize = 99, **extra):
        self.sprite = sprite
        self.name = name
        self.place = IMAGES[self.sprite].get_rect(center=(-width, -height))
        self.hitbox = rect(pygame.Rect( -width, -height, width / 15, height * 3 / 80))
        self.dragged = 0
        self.qty = qty
        self.stackSize = stackSize

        if description is None:
            self.description = f'{name.title()} is a material.'

        else:
            self.description = description

        self.textBox = textBox(self.description, 'newLetter', 'textBox.png', self.hitbox.centerx,
                               self.hitbox.centery, width / 4)

        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')

    def updateHitbox(self):
        self.hitbox = rect(pygame.Rect(self.place.centerx - width / 30, self.place.centery - height * 3 / 160,
                                       width / 15, height * 3 / 80))
        self.hitbox.updatePoints()
        self.textBox = textBox(self.description, 'newLetter', 'textBox.png', self.hitbox.centerx,
                               self.hitbox.centery, width / 4)
