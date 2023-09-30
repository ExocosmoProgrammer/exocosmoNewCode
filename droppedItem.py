from item import item
from variables import IMAGES
from rects import rect


class droppedItem:
    def __init__(self, centerx, centery, sprite, whatYouGetForPickingUpTheItem: item):
        self.sprite = sprite
        self.place = IMAGES[self.sprite].get_rect(center=(centerx, centery))
        self.hitbox = rect(self.place)
        self.item = whatYouGetForPickingUpTheItem