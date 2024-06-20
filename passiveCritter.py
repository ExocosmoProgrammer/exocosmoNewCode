from variables import MOVESPEED, IMAGES, GAMESPEED, width, height
from rects import rect
from definitions import getDirection, lesser, greater, getYBoundary, sign, sqrt

import random
import pygame


class passiveCritter:
    def __init__(self, name, x, y, room):
        self.type = name
        self.direction = 'w'
        self.hr = 0
        self.vr = 0
        self.cooldown = 0
        self.x = x
        self.y = y
        self.room = room
        self.action = self.actNormally
        self.methodToGetHitbox = self.updateHitboxNormally

        match name:
            case 'desertCaveSlug':
                self.sprite = 'desertCaveSlugD1.png'
                self.animation = [f'desertCaveSlugD{i}.png' for i in [1, 2] for j in range(30)]
                self.animationsPerDirection = {}
                self.speed = 0.1
                self.timeBetweenAcceleration = 1000
                self.methodToGetHitbox = self.updateHitboxAsDesertCaveSlug

                for i in ['W', 'A', 'S', 'D']:
                    self.animationsPerDirection[i] = [f'desertCaveSlug{i}{j}.png' for j in [1, 2] for h in range(30)]

            case 'desertCaveButterfly':
                self.sprite = 'desertCaveForestButterfly1.png'
                self.animation = [f'desertCaveForestButterfly{i}.png' for i in [1, 2] for j in range(30)]
                self.speed = 0.3
                self.timeBetweenAcceleration = 500

            case 'desertCaveAmphipod':
                self.sprite = 'desertCaveAmphipod1.png'
                self.animation = [f'desertCaveAmphipod{i}.png' for i in [1, 2] for j in range(30)]
                self.speed = 0.4
                self.timeBetweenAcceleration = 500
                self.altCooldown = 500
                self.speedMultiplier = 1
                self.action = self.actAsDesertCaveAmphipod

            case 'desertCaveCritterWithThreeLegs':
                self.sprite = 'desertCaveCritterWithThreeLegs1.png'
                self.animation = [f'desertCaveCritterWithThreeLegs{i}.png' for i in range(1, 6) for j in range(30)]
                self.speed = 0.4
                self.timeBetweenAcceleration = 500
                self.action = self.actNormally

        if not hasattr(self, 'animationsPerDirection') and hasattr(self, 'animation'):
            self.animationsPerDirection = {}

            for i in ['W', 'A', 'S', 'D']:
                self.animationsPerDirection[i] = self.animation.copy()

        self.animation = self.animationsPerDirection['W'].copy()
        self.animationFrame = 0
        self.sprite = self.animation[0]
        self.place = IMAGES[self.sprite].get_rect(center=(x, y))
        self.hitbox = rect(self.place)
        self.yBoundaries = getYBoundary(self, self.room.yBoundaries)
        self.getOutOfObjects()

    def updateHitboxNormally(self):
        self.hitbox = rect(self.place)

    def updateHitboxAsDesertCaveSlug(self):
        match self.direction:
            case 'a':
                self.hitbox = rect(pygame.Rect(self.place.left, self.place.top, width * 19 / 800, self.place.height))

            case 'w':
                self.hitbox = rect(pygame.Rect(self.place.left, self.place.top, self.place.width, height * 11 / 300))

            case 's':
                self.hitbox = rect(pygame.Rect(self.place.left, self.place.bottom - height * 11 / 300, self.place.width,
                                               height * 11 / 300))
            case _:
                self.hitbox = rect(pygame.Rect(self.place.right - width * 19 / 800, self.place.top, width * 19 / 800,
                                               self.place.height))

    def changeDirection(self):
        self.cooldown = self.timeBetweenAcceleration

        direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.hr = direction[0]
        self.vr = direction[1]
        self.direction = getDirection(self.hr, self.vr)
        self.faceProperly()

    def faceProperly(self):
        self.direction = getDirection(self.hr, self.vr)
        self.animation = self.animationsPerDirection[self.direction.upper()].copy()

    def progressAnimation(self):
        self.animationFrame += GAMESPEED
        sprite = self.sprite
        place = self.place.__copy__()

        try:
            self.sprite = self.animation[int(self.animationFrame)]

        except IndexError:
            self.animationFrame = 0
            self.sprite = self.animation[0]

        self.place = IMAGES[self.sprite].get_rect(center=(self.x, self.y))

        if self.sprite != sprite:
            match self.direction:
                case 'a':
                    self.place.left = place.left

                case 'd':
                    self.place.right = place.right

                case 'w':
                    self.place.top = place.top

                case _:
                    self.place.bottom = place.bottom

            deltaX = self.place.centerx - place.centerx
            deltaY = self.place.centery - place.centery
            self.x += deltaX
            self.y += deltaY
            self.updateHitboxAndPlaceNormally()
            collision = False

            if self.room.leftXBoundary <= self.hitbox.left and self.hitbox.right <= self.room.rightXBoundary and \
                    self.hitbox.top >= self.yBoundaries and self.hitbox.bottom <= self.room.bottomYBoundary:
                for i in self.room.environmentObjects:
                    if i.hitbox.checkCollision(self.hitbox):
                        collision = True

            else:
                collision = True

            if collision:
                self.x += sign(self.hr) * (self.place.width - place.width)
                self.y += sign(self.vr) * (self.place.height - place.height)
                self.updateHitboxAndPlaceNormally()

    def getOutOfObjects(self):
        unavailableRegions = [[i.hitbox.left, i.hitbox.right] for i in self.room.environmentObjects if \
                              i.hitbox.top < self.hitbox.bottom and i.hitbox.bottom > self.hitbox.top]

        if unavailableRegions:
            stop = 0

            while not stop:
                stop = 1
                simplerRegions = unavailableRegions.copy()

                for i in range(len(unavailableRegions) - 1):
                    for j in unavailableRegions[i + 1:]:
                        if unavailableRegions[i][0] <= j[1] and unavailableRegions[i][1] > j[0]:
                            stop = 0
                            simplerRegions.pop(i)
                            simplerRegions.remove(j)
                            simplerRegions.append([lesser(unavailableRegions[i][0], j[0]),
                                                   greater(unavailableRegions[i][1], j[1])])

                unavailableRegions = simplerRegions.copy()
                unavailableRegions.sort()

            availableRegions = [[self.hitbox.width / 2 + 1, unavailableRegions[0][0]],
                                [unavailableRegions[-1][1], width - (1 + self.hitbox.width / 2)]]

            for i in range(len(unavailableRegions) - 1):
                availableRegions.append([unavailableRegions[i][1], unavailableRegions[i + 1][0]])

            for i in availableRegions:
                if i[1] - i[0] > self.hitbox.width:
                    self.x = (i[1] + i[0]) / 2
                    self.place.centerx = self.x
                    self.hitbox = rect(self.place)

    def stayInBounds(self):
        leftBounds = False
        hitObject = False

        for i in self.room.environmentObjects:
            if i.hitbox.checkCollision(self.hitbox):
                hitObject = True
                objectHit = i

        if self.hitbox.right > width:
            self.hr = -1
            self.faceProperly()
            self.x -= self.hitbox.right - width
            leftBounds = True
            self.updateHitboxAndPlaceNormally()

        elif self.hitbox.left < 0:
            self.hr = 1
            self.faceProperly()
            self.x -= self.hitbox.left
            leftBounds = True
            self.updateHitboxAndPlaceNormally()

        if self.hitbox.bottom > self.room.bottomYBoundary:
            self.vr = -1
            self.faceProperly()
            self.y -= self.hitbox.bottom - self.room.bottomYBoundary
            leftBounds = True
            self.updateHitboxAndPlaceNormally()

        elif self.hitbox.top < self.yBoundaries:
            self.vr = 1
            self.faceProperly()
            self.y -= self.hitbox.top - self.yBoundaries
            leftBounds = True
            self.updateHitboxAndPlaceNormally()

        if hitObject:
            self.updateHitboxAndPlaceNormally()

            if ((self.hitbox.bottom > objectHit.hitbox.bottom) and ((self.hitbox.top > self.hitbox.top))) or \
                    ((self.hitbox.bottom <= objectHit.hitbox.bottom) and ((self.hitbox.top <= self.hitbox.top))):
                if self.hitbox.centerx > objectHit.hitbox.centerx:
                    self.hr = 1
                    self.x -= self.hitbox.left - objectHit.hitbox.right - 1

                else:
                    self.hr = -1
                    self.x -= self.hitbox.right - objectHit.hitbox.right + 1

            elif ((self.hitbox.right > objectHit.hitbox.right) and ((self.hitbox.left > self.hitbox.left))) or \
                    ((self.hitbox.right <= objectHit.hitbox.right) and ((self.hitbox.left <= self.hitbox.left))):
                if self.hitbox.centery > objectHit.hitbox.centery:
                    self.vr = 1
                    self.y -= self.hitbox.top - objectHit.hitbox.bottom + 1

                else:
                    self.vr = -1
                    self.y -= self.hitbox.bottom - objectHit.hitbox.top - 1

            else:
                if self.hitbox.centery > objectHit.hitbox.centery:
                    self.vr = sqrt(2) / 2
                    self.y -= self.hitbox.top - objectHit.hitbox.bottom + 1

                else:
                    self.vr = -sqrt(2) / 2
                    self.y -= self.hitbox.bottom - objectHit.hitbox.top - 1

                if self.hitbox.centerx > objectHit.hitbox.centerx:
                    self.hr = sqrt(2) / 2
                    self.x -= self.hitbox.left - objectHit.hitbox.right - 1

                else:
                    self.hr = -sqrt(2) / 2
                    self.x -= self.hitbox.right - objectHit.hitbox.right + 1

            self.updateHitboxAndPlaceNormally()

        if hitObject or leftBounds:
            self.faceProperly()

            try:
                tryAgain = True

                while tryAgain:
                    tryAgain = False
                    self.x += self.hr
                    self.y += self.vr
                    self.faceProperly()
                    self.updateHitboxAndPlaceNormally()

                    if 0 <= self.hitbox.left and self.hitbox.right <= width and self.hitbox.top >= self.yBoundaries \
                            and self.hitbox.bottom <= self.room.bottomYBoundary:
                        for i in self.room.environmentObjects:
                            if i.hitbox.checkCollision(self.hitbox):
                                tryAgain = True

                    else:
                        tryAgain = True

            except RecursionError:
                if hitObject:
                    self.getOutOfObjects()

                if leftBounds:
                    self.x = greater(lesser(self.x, width - self.hitbox.width / 2), self.hitbox.width / 2)
                    self.y = greater(lesser(self.y, height - self.hitbox.height / 2), self.hitbox.height / 2)

                self.updateHitboxAndPlaceNormally()

    def updateHitboxAndPlaceNormally(self):
        self.place.centerx = self.x
        self.place.centery = self.y
        self.methodToGetHitbox()

    def actNormally(self):
        self.x += self.hr * GAMESPEED * MOVESPEED * self.speed
        self.y += self.vr * GAMESPEED * MOVESPEED * self.speed
        self.cooldown -= GAMESPEED
        self.progressAnimation()
        self.stayInBounds()

        if self.cooldown <= 0:
            self.changeDirection()

        self.updateHitboxAndPlaceNormally()

    def actAsDesertCaveAmphipod(self):
        self.actNormally()
        self.altCooldown -= GAMESPEED
        self.speed -= 0.0008 * GAMESPEED

        if self.altCooldown <= 0:
            self.speed = 0.4
            self.altCooldown = 500
