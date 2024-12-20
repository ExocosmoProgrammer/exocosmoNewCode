from variables import IMAGES
from rects import rect
from definitions import draw, checkMouseCollision


class button:
    def __init__(self, sprite, x, y, spriteWhenTouchingMouse=None):
        # self.spriteWhenTouching mouse should default to being self.sprite.
        # self should use a method to draw based on if self has a different sprite when touching the mouse.

        if spriteWhenTouchingMouse is not None:
            self.spriteWhenTouchingMouse = spriteWhenTouchingMouse
            self.drawingMethod = self.drawAsButtonWithSpriteWhenTouchingMouse
            self.normalSprite = sprite

        else:
            self.drawingMethod = self.draw

        # Define the other attributes.
        self.sprite = sprite
        self.place = IMAGES[sprite].get_rect(center=(x, y))
        self.hitbox = rect(self.place)

    def drawAsButtonWithSpriteWhenTouchingMouse(self):
        """Adjust self's sprite based on whether self is touching the mouse and draw self."""

        # Adjust self.sprite based on if the mouse is touching self. Then draw self.
        self.sprite = self.spriteWhenTouchingMouse if checkMouseCollision(self.hitbox) else self.normalSprite
        draw(self)

    def draw(self):
        """Draw self."""
        draw(self)
