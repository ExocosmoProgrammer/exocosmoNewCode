from variables import IMAGES, diagonal, GAMESPEED
from rects import rect
from definitions import pointDistance, skip


class teleporter:
    def __init__(self, x, y, sprite, destination, destinationXandY=None, hitbox=None, animationWhenApproached=None,
                 distanceToPlayAnimation=diagonal / 5, animation=None):
        self.sprite = sprite
        self.place = IMAGES[self.sprite].get_rect()
        self.place.centerx = x
        self.place.centery = y
        self.hitbox = rect(self.place)
        self.destination = destination

        if animationWhenApproached is None:
            if animation is None:
                self.functionToGetSprite = skip

            else:
                self.functionToGetSprite = self.progressAnimation
                self.animationFrame = 0
                self.animation = self.standardAnimation.copy()

        else:
            self.standardAnimation = [self.sprite] if animation is None else animation
            self.animation = self.standardAnimation.copy()
            self.animationFrame = 0
            self.functionToGetSprite = self.getSpriteAsTeleporterWithAnimationWhenApproached
            self.animationWhenApproached = animationWhenApproached
            self.distanceToPlayAnimation = distanceToPlayAnimation


        if hitbox is not None:
            self.hitbox = hitbox

        if destinationXandY is None:
            self.destinationX = x
            self.destinationY = y

        else:
            self.destinationX = destinationXandY[0]
            self.destinationY = destinationXandY[1]

    def progressAnimation(self, player, locked):
        self.animationFrame += GAMESPEED

        if self.animationFrame >= len(self.animation):
            self.animationFrame = 0

        self.sprite = self.animation[self.animationFrame]

    def getSpriteAsTeleporterWithAnimationWhenApproached(self, player, locked):
        self.animationFrame += GAMESPEED

        if pointDistance(self.hitbox.center, player.hitbox.center) <= self.distanceToPlayAnimation and not locked:
            if self.animation != self.animationWhenApproached:
                self.animationFrame = 0
                self.animation = self.animationWhenApproached.copy()

            if self.animationFrame >= len(self.animation):
                self.animationFrame = len(self.animation) - 1

        elif self.animation == self.animationWhenApproached:
            self.animation = self.standardAnimation.copy()
            self.animationFrame = 0

        elif self.animationFrame >= len(self.animation):
            self.animationFrame = 0

        self.sprite = self.animation[self.animationFrame]
