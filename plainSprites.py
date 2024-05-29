from variables import IMAGES
from rects import rect


class plainSprite:
    def __init__(self, sprite, centerx, centery):
        """A plainSprite object is just something to draw."""
        self.sprite = sprite
        self.place = IMAGES[sprite].get_rect(center=(centerx, centery))
        self.hitbox = rect(self.place)
