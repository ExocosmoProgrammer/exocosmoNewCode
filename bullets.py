import time

from variables import IMAGES, GAMESPEED, MOVESPEED, width, height, display
from rects import rect
from definitions import getDegrees, sqrt, getRadians, pointDistance
from debuff import debuff

import math
import pygame


class bullet:
    def __init__(self, hr, vr, damage, sprite, x, y, animation=None,
                 linger=1600, piercing=0, rotation=None, dissappearsAtEdges=1, checksCollisionWhen='True',
                 endEffect='pass', causeAndEffect={}, bounces=0, delay=0, delayedSprite='hellhoundFootstep.png',
                 durationBasedPlace=None, durationBasedMovement=None, delayedAnimation=None,
                 polarDurationBasedPlace=None, polarMovement=None, radius=0, theta=0, impactAnimation=None,
                 timeBeforeStop=1600, playerContactEffect = 'pass', alwaysChecksCollisionWithPro=False,
                 hitboxOnProjectile=None, debuffInflictions=[], firer=None, source=None, foeContactEffect='pass',
                 hitboxForFragmentsAsSplittingProjectile=None, additionalMethods={}, unusualTargets=[], **extra):
        self.hr = hr
        self.vr = vr
        self.damage = damage
        self.timeBeforeStop = timeBeforeStop
        self.sprite = sprite
        self.dissappearsAtEdges = dissappearsAtEdges

        # self.additionalMethods should be a dict where each key n will be called with arguments
        # *self.additionalMethods[n]
        self.additionalMethods = additionalMethods.copy()

        # If self will split into more projectiles, hitboxForFragmentsAsSplittingProjectile may be used to track what
        # the hitboxes should be for the fragments.
        self.hitboxForFragmentsAsSplittingProjectile = hitboxForFragmentsAsSplittingProjectile

        # When self hits a target, a copy of self.debuffInfliction will be added to the target's debuffs.
        self.debuffInflictions = debuffInflictions.copy()

        # If self.alwaysChecksCollisionWithPro, self checks collision with pro even when pro.invincibility > 0.
        self.alwaysChecksCollisionWithPro = alwaysChecksCollisionWithPro

        # self can only detect collision when the eval of self.checksCollisionWhen is True.
        self.checksCollisionWhen = checksCollisionWhen
        self.impactAnimation = impactAnimation

        # exec is called with argument self.endEffect when self must be gotten rid of.
        # exec is called with argument of self.playerContactEffect when self collides with the player.
        # self.conditionalEffects should be a dictionary. For each key, i, of its keys, if the eval of i is true,
        # the corresponding value self.conditionalEffects for the key i is executed.
        # exec is called with argument self.foeContactEffect when self hits a foe.
        # To understand how to use self.playerContactEffect and self,foeContactEffect, read the code around
        # where they are executed.
        self.endEffect = endEffect
        self.playerContactEffect = playerContactEffect
        self.foeContactEffect = foeContactEffect
        self.conditionalEffects = causeAndEffect.copy()
        self.bounces = bounces
        self.delay = delay
        self.currentDuration = 0
        self.placeByDuration = durationBasedPlace
        self.movementByDuration = durationBasedMovement
        self.initialDelay = self.delay
        self.polarDurationBasedPlace = polarDurationBasedPlace
        self.polarMovement = polarMovement
        self.y = y
        self.x = x

        # self will check collision with everything in self.unusualTargets.
        self.unusualTargets = unusualTargets.copy()

        # self.firer can be used to track who fired self, and self.source can be used to track which item was used to
        # fire self.
        self.firer = firer
        self.source = source

        if not (self.polarDurationBasedPlace is self.polarMovement is None):
            # If self uses polar coordinates, the pole for self's polar coordinate plane is at
            # (self.initialX, self.initialY) in the x y coordinate plane.
            self.initialY = y
            self.initialX = x

        self.radius = radius
        self.theta = theta

        # If self has a delay before using its move method and checking collision, self will use self.delayedAnimation
        # as an animation while waiting to use the move method and check collision.
        if delayedAnimation is not None:
            self.delayedAnimation = delayedAnimation

        else:
            self.delayedAnimation = [delayedSprite]

        if rotation is not None:
            self.rotation = rotation

        else:
            try:
                self.rotation = getDegrees(self.hr, self.vr)

            except ZeroDivisionError:
                self.rotation = 0


        place = IMAGES[self.sprite].get_rect(center=[x, y])
        self.place = pygame.transform.rotate(IMAGES[sprite], self.rotation).get_rect(center=[x, y])

        # Self can be given a hitbox that does not perfectly fit self.
        if hitboxOnProjectile is None:
            self.hitbox = rect(place, self.rotation * math.pi / 180)

        else:
            self.hitbox = hitboxOnProjectile

            # TODO Make this block account for if rotation is not None.
            self.hitbox.rotate(getRadians(self.hr, self.vr))
            self.hitbox.move(self.x, self.y)

        # self.linger represents how long the bullet will exist for.
        self.linger = linger
        self.piercing = piercing
        self.animationFrame = 0

        # If I specify an animation for a bullet, the bullet will cycle through the animation, else the
        # bullet will have a constant sprite.

        if animation == None:
            self.animated = 0

        else:
            self.animated = 1
            self.animation = animation

        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')

    def move(self):
        # Update some attributes as needed.
        oldX = self.x
        oldY = self.y
        self.currentDuration += GAMESPEED
        self.timeBeforeStop -= GAMESPEED
        self.linger -= GAMESPEED

        # Stop self's movement if needed.
        if self.timeBeforeStop <= 0:
            self.hr = self.vr = 0

        # if needed, adjust self's movement based on self.movementByDuration.
        if self.movementByDuration is not None:
            self.hr = eval(self.movementByDuration)[0]
            self.vr = eval(self.movementByDuration)[1]

        # Move self as needed.
        self.x += self.hr * GAMESPEED * MOVESPEED
        self.y += self.vr * GAMESPEED * MOVESPEED

        # Progress self's animation if needed.
        if self.animated:
            self.animationFrame += GAMESPEED

            # Go back to the start of self's animation if needed.
            if self.animationFrame > len(self.animation) - 1:
                self.animationFrame = 0

            # Update self.sprite and self.place. Stay centered at (self.x, self.y)
            self.sprite = self.animation[int(self.animationFrame)]
            self.place = pygame.transform.rotate(IMAGES[self.sprite], self.rotation).get_rect(center=[self.x, self.y])

        # if needed, adjust self's position based on self.placeByDuration.
        if self.placeByDuration is not None:
            self.x = eval(self.placeByDuration)[0]
            self.y = eval(self.placeByDuration)[1]
            self.hitbox = rect(self.place, self.rotation * math.pi / 180)

        # if needed, adjust self's position based on self.polarDurationBasedPlace.
        elif self.polarDurationBasedPlace is not None:
            self.x = self.initialX + eval(self.polarDurationBasedPlace[0]) * \
                     math.cos(eval(self.polarDurationBasedPlace[1]))
            self.y = self.initialY + eval(self.polarDurationBasedPlace[0]) * \
                     math.sin(eval(self.polarDurationBasedPlace[1]))
            self.hitbox = rect(self.place, self.rotation * math.pi / 180)

        # if needed, add to self's radius and theta based on self.polarMovement. Then, place self appropriately using
        # polar coordinates.
        elif self.polarMovement is not None:
            # Adjust self.radius and self.theta.
            self.radius += eval(self.polarMovement)[0]
            self.theta += eval(self.polarMovement)[1]

            # Move self to the correct position using polar coordinates.
            self.x = self.initialX + self.radius * math.cos(self.theta)
            self.y = self.initialY + self.radius * math.sin(self.theta)
            self.hitbox = rect(self.place, self.rotation * math.pi / 180)

        # Update self.place
        self.place.centerx = self.x
        self.place.centery = self.y

        # set self.linger to 0 if needed self is out of the screen and should disappear when self is out of the screen.
        if self.dissappearsAtEdges  and \
                (self.place.bottom < 0 or self.place.right < 0 or self.place.left > width or self.place.top > height):
            self.linger = 0

        # Make self bounce off of a wall if necessary.
        elif self.bounces:
            if self.place.top < 0:
                self.place.top = 0
                self.vr *= -1
                self.rotation = getDegrees(self.hr, self.vr)

            elif self.place.bottom > height:
                self.place.bottom = height
                self.vr *= -1
                self.rotation = getDegrees(self.hr, self.vr)

            if self.place.right > width:
                self.place.right = width
                self.hr *= -1
                self.rotation = getDegrees(self.hr, self.vr)

            elif self.place.left < 0:
                self.place.left = 0
                self.hr *= -1
                self.rotation = getDegrees(self.hr, self.vr)

            # Update self.x and self.y.
            self.x, self.y = self.place.centerx, self.place.centery

        # Call each of self's additional methods.
        for method in self.additionalMethods.keys():
            method(*self.additionalMethods[method])

        # Move self.hitbox.
        self.hitbox.move(self.x - oldX, self.y - oldY)

    def visuallyConnectToFirer(self, sprite):
        """Draws sprite to connect self to self.firer. May only be used if self.firer is specified instead of
        defaulting to 1."""

        # Scale sprite to the right size.
        distanceToFirer = pointDistance((self.x, self.y), (self.firer.x, self.firer.y))
        scaledSprite = pygame.transform.scale(IMAGES[sprite], (distanceToFirer, IMAGES[sprite].get_height()))

        # Rotate the sprite.
        angleToFirer = getDegrees(self.firer.x - self.x, self.firer.y - self.y)
        finalSprite = pygame.transform.rotate(scaledSprite, angleToFirer)

        # Get a pygame.Rect object at which to draw the scaled sprite.
        place = finalSprite.get_rect(center=((self.x + self.firer.x) / 2, (self.y + self.firer.y) / 2))

        # Draw the scaled sprite.
        display.blit(finalSprite, place)

    def getSpriteWhenDelayed(self):
        """self.getSpriteWhenDelayed() returns the sprite that should be drawn to represent self when self.delay > 0."""
        return self.delayedAnimation[int((self.initialDelay - self.delay) % len(self.delayedAnimation))]
