from variables import IMAGES
from rects import rect
from definitions import draw, checkMouseCollision


class button:
    def __init__(self, sprite, x, y, spriteWhenTouchingMouse=None):
        self.spriteWhenTouchingMouse = spriteWhenTouchingMouse

        if spriteWhenTouchingMouse is None:
            self.spriteWhenTouchingMouse = sprite

        self.sprite = sprite
        self.normalSprite = sprite
        self.place = IMAGES[sprite].get_rect(center=(x, y))
        self.hitbox = rect(self.place)

    def draw(self):
        self.sprite = self.spriteWhenTouchingMouse if checkMouseCollision(self.hitbox) else self.normalSprite
        draw(self)
