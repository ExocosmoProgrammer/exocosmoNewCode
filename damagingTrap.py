from variables import IMAGES, GAMESPEED
from rects import rect
from definitions import draw


class damagingTrap:
    def __init__(self, sprite, damage, centerx, centery, animation=None):
        self.sprite = sprite
        self.damage = damage
        self.place = IMAGES[self.sprite].get_rect(center=(centerx, centery))
        self.hitbox = rect(self.place)
        # self.drawingMethod will be called to draw self and to update self's sprite if self is animated.

        if animation is None:
            self.drawingMethod = self.draw

        else:
            self.drawingMethod = self.drawAsAnimatedDamagingTrap
            self.animation = animation
            self.animationFrame = 0

    def progressAnimation(self):
        """Update self's sprite."""

        # Update self's frame.
        self.animationFrame = int(self.animationFrame + GAMESPEED)

        # If self's frame is past the end of self's animation, take self's frame back to 0.
        if self.animationFrame > len(self.animation) - 1:
            self.animationFrame = 0

        # Update self.sprite.
        self.sprite = self.animation[self.animationFrame]

    def draw(self, offset=(0, 0)):
        """Draw self."""
        draw(self, offset=offset)

    def drawAsAnimatedDamagingTrap(self, offset=(0, 0)):
        """Update self's sprite and draw self."""
        self.progressAnimation()
        self.draw(offset=offset)
