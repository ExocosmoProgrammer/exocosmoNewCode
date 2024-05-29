import pygame
from variables import IMAGES, GAMESPEED


class temporaryAnimation:
    def __init__(self, animation, x, y):
        self.animation = animation
        self.frame = 0
        self.sprite = animation[0]
        self.x = x
        self.y = y
        self.place = IMAGES[self.sprite].get_rect(center=(x, y))

    def progressAnimation(self):
        self.frame += GAMESPEED

        try:
            self.sprite = self.animation[int(self.frame)]
            self.place = IMAGES[self.sprite].get_rect(center=(self.x, self.y))

        except IndexError:
            return 1
