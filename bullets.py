from variables import IMAGES, GAMESPEED, MOVESPEED, width, height
from rects import rect
import pygame
from definitions import getDegrees, sqrt
import math


class bullet:
    def __init__(self, hr, vr, damage, sprite, x, y, animation=None,
                 linger=1600, piercing=0, rotation=None, hasRotatedHitbox=1, hasShrunkHitbox = 0,
                 pointOfRotation=None, dissappearsAtEdges=1, checksCollisionWhen = 'True', endEffect='pass',
                 causeAndEffect={}, bounces=0, delay=0, delayedSprite='moltenDelaySprite.png', durationBasedPlace=None,
                 durationBasedMovement=None, delayedAnimation=None, consistentPoint='center', updatesPlace=False,
                 polarDurationBasedPlace=None, polarMovement=None, radius=0, theta=0, **extra):
        # hr and vr represent horizontal movement per frame and vertical movement per frame.
        self.hr = hr
        self.vr = vr
        self.damage = damage
        self.sprite = sprite
        self.dissappearsAtEdges = dissappearsAtEdges
        self.checksCollisionWhen = checksCollisionWhen
        self.endEffect = endEffect
        self.conditionalEffects = causeAndEffect
        self.bounces = bounces
        self.delay = delay
        self.delayedSprite = delayedSprite
        self.currentDuration = 0
        self.placeByDuration = durationBasedPlace
        self.movementByDuration = durationBasedMovement
        self.initialDelay = self.delay
        self.consistentPoint = consistentPoint
        self.polarDurationBasedPlace = polarDurationBasedPlace
        self.polarMovement = polarMovement
        self.radius = radius
        self.theta = theta

        if delayedAnimation is not None:
            self.delayedAnimation = delayedAnimation

        else:
            self.delayedAnimation = [self.delayedSprite]

        if rotation is not None:
            self.rotation = rotation

        else:
            try:
                self.rotation = getDegrees(self.hr, self.vr)

            except ZeroDivisionError:
                self.rotation = 0

        self.y = self.initialY = y
        self.x = self.initialX = x
        self.place = pygame.transform.rotate(IMAGES[sprite], self.rotation).get_rect(center=[x, y])
        place = IMAGES[self.sprite].get_rect(center=[x, y])
        self.hitbox = rect(place, self.rotation * math.pi / 180)
        self.updatesPlace = updatesPlace
        # self.linger represents how long the bullet will exist for.
        self.linger = linger
        self.piercing = piercing
        self.animationFrame = 0
        # If i specify an animation for a bullet, the bullet will cycle through the animation, else the bullet will have a constant sprite.

        if animation == None:
            self.animated = 0

        else:
            self.animated = 1
            self.animation = animation

        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')

    def move(self):
        self.currentDuration += GAMESPEED

        if self.movementByDuration is not None:
            self.hr = eval(self.movementByDuration)[0]
            self.vr = eval(self.movementByDuration)[1]

        self.x += self.hr * GAMESPEED * MOVESPEED
        self.y += self.vr * GAMESPEED * MOVESPEED
        self.hitbox.move(self.hr * GAMESPEED * MOVESPEED, self.vr * GAMESPEED * MOVESPEED)
        self.linger -= GAMESPEED

        if self.animated:
            self.animationFrame += GAMESPEED

            if self.animationFrame > len(self.animation) - 1:
                self.animationFrame = 0

            self.sprite = self.animation[int(self.animationFrame)]

        if self.placeByDuration is not None:
            self.x = eval(self.placeByDuration)[0]
            self.y = eval(self.placeByDuration)[1]
            self.hitbox = rect(self.place, self.rotation * math.pi / 180)

        elif self.polarDurationBasedPlace is not None:
            self.x = self.initialX + eval(self.polarDurationBasedPlace[0]) * \
                     math.cos(eval(self.polarDurationBasedPlace[1]))
            self.y = self.initialY + eval(self.polarDurationBasedPlace[0]) * \
                     math.sin(eval(self.polarDurationBasedPlace[1]))
            self.hitbox = rect(self.place, self.rotation * math.pi / 180)

        elif self.polarMovement is not None:
            self.radius += eval(self.polarMovement)[0]
            self.theta += eval(self.polarMovement)[1]
            self.x = self.initialX + self.radius * math.cos(self.theta)
            self.y = self.initialY + self.radius * math.sin(self.theta)
            self.hitbox = rect(self.place, self.rotation * math.pi / 180)

        self.place.centerx = self.x
        self.place.centery = self.y

        if self.dissappearsAtEdges:
            if self.place.bottom < 0 or self.place.right < 0 or self.place.left > width or self.place.top > height:
                self.linger = 0

        elif self.bounces:
            if self.place.top < 0 or self.place.bottom > height:
                self.place.y -= self.vr
                self.vr *= -1
                self.rotation = getDegrees(self.hr, self.vr)

            if self.place.right > width or self.place.left < 0:
                self.place.x -= self.hr
                self.hr *= -1
                self.rotation = getDegrees(self.hr, self.vr)

            self.x, self.y = self.place.centerx, self.place.centery

    def getSpriteWhenDelayed(self):
        self.delayedSprite = self.delayedAnimation[int((self.initialDelay - self.delay) % len(self.delayedAnimation))]
        return self.delayedAnimation[int((self.initialDelay - self.delay) % len(self.delayedAnimation))]
