from variables import IMAGES, GAMESPEED
from rects import rect


class damagingTrap:
    def __init__(self, sprite, damage, centerx, centery, animation=None):
        self.sprite = sprite
        self.damage = damage
        self.place = IMAGES[self.sprite].get_rect(center=(centerx, centery))
        self.hitbox = rect(self.place)
        self.animation = animation if animation is not None else [sprite]
        self.animationFrame = 0

    def progressAnimation(self):
        self.animationFrame = int(self.animationFrame + GAMESPEED)

        if self.animationFrame > len(self.animation) - 1:
            self.animationFrame = 0

        self.sprite = self.animation[self.animationFrame]
