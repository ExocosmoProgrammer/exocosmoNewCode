from variables import IMAGES
from rects import rect


class damagingTrap:
    def __init__(self, sprite, damage, centerx, centery):
        self.sprite = sprite
        self.damage = damage
        self.place = IMAGES[self.sprite].get_rect(center=(centerx, centery))
        self.hitbox = rect(self.place)