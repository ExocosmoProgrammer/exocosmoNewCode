from variables import IMAGES
from rects import rect


class teleporter:
    def __init__(self, x, y, sprite, destination, destinationXandY=None, hitbox=None):
        self.sprite = sprite
        self.place = IMAGES[self.sprite].get_rect()
        self.place.centerx = x
        self.place.centery = y
        self.hitbox = rect(self.place)
        self.destination = destination

        if hitbox is not None:
            self.hitbox = hitbox

        if destinationXandY is None:
            self.destinationX = x
            self.destinationY = y

        else:
            self.destinationX = destinationXandY[0]
            self.destinationY = destinationXandY[1]
