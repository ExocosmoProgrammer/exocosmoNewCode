import pygame

from variables import IMAGES, display
from rects import rect


class item:
    def __init__(self, name, sprite, **extra):
        self.sprite = sprite
        self.name = name
        self.place = IMAGES[self.sprite].get_rect(center=(0, 0))
        self.hitbox = rect(pygame.Rect(self.place.centerx - display.get_width() / 30,
                                       self.place.centery - display.get_height() * 3 / 160,
                                       display.get_width() * 3 / 80, display.get_height() / 15))

        self.dragged = 0
        self.qty = 1

        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')

    def updateHitbox(self):
        self.hitbox = rect(pygame.Rect(self.place.centerx - display.get_width() / 30,
                                       self.place.centery - display.get_height() * 3 / 160,
                                       display.get_width() * 3 / 80, display.get_height() / 15))