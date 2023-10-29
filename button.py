from variables import IMAGES
from rects import rect


class button:
    def __init__(self, sprite, x, y):
        self.sprite = sprite
        self.place = IMAGES[self.sprite].get_rect(center=(x, y))
        self.hitbox = rect(self.place)
