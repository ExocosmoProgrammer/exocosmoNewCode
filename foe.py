import random

from bullets import bullet
from definitions import getPath, sqrt, signOrRandom
from variables import IMAGES, GAMESPEED, MOVESPEED, display
from rects import rect
import math


class foe:
    def __init__(self, name, centerx, centery, room, delayed=0, **extra):
        self.type = name
        self.rotated = False
        self.angle = 0
        self.bullets = []
        self.x = centerx
        self.y = centery
        self.hr = 0
        self.vr = 0
        self.spawnDelay = 0
        self.newBullets = []
        self.fireCooldown = 0
        actions = {'brokenTurret': self.actAsBrokenTurret, 'flamingRobot': self.actAsFlamingRobot,
                   'robotBodyguard': self.actAsRobotBodyguard}
        self.action = actions[self.type]
        self.room = room

        if name == 'brokenTurret':
            self.hp = 20
            self.sprite = 'brokenTurret.png'
            self.damage = 26
            self.rotated = True

        elif name == 'flamingRobot':
            self.hp = 20
            self.sprite = 'flamingRobotTemporarySprite.png'
            self.damage = 26
            self.accelerationCooldown = 0

        elif name == 'robotBodyguard':
            self.hp = 50
            self.sprite = 'temporaryRobotBodyguard.png'
            self.damage = 26
            self.modeDuration = random.randint(100, 2000)
            self.mode = 'chasing'

        self.place = IMAGES[self.sprite].get_rect(center=(centerx, centery))
        self.hitbox = rect(self.place)

        if delayed:
            self.spawnDelay = 1000

        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')

    def actAsBrokenTurret(self, target):
        self.angle += 0.02 * GAMESPEED
        self.place = IMAGES[self.sprite].get_rect(center=(self.x, self.y))
        self.fireCooldown -= GAMESPEED

        if self.fireCooldown <= 0:
            self.newBullets.append(bullet(math.cos(self.angle) * 2, math.sin(self.angle) * 2, 26,
                                   'brokenTurretFireball.png', self.x, self.y, rotation=-self.angle * 180 / math.pi))
            self.fireCooldown = random.randint(5, 50)

    def accelerateAsFlamingRobot(self, target):
        self.hr = getPath(0.075, (self.x, self.y), (target.x, target.y))[0]
        self.vr = getPath(0.075, (self.x, self.y), (target.x, target.y))[1]
        hrAddition = random.randint(0, 10)
        vrAddition = sqrt(100 - hrAddition ** 2)
        self.hr += hrAddition / 12 * signOrRandom(self.hr)
        self.vr += vrAddition / 12 * signOrRandom(self.vr)
        self.accelerationCooldown = random.randint(100, 700)

    def moveNormally(self):
        self.x += self.hr * GAMESPEED * MOVESPEED
        self.y += self.vr * GAMESPEED * MOVESPEED
        self.hitbox.move(self.hr * GAMESPEED * MOVESPEED, self.vr * GAMESPEED * MOVESPEED)
        self.place.centerx = self.x
        self.place.centery = self.y

        if self.place.left < 0:
            self.hitbox.move(-self.place.left, 0)
            self.place.left = 0
            self.x = self.place.centerx
            return 'wall'

        elif self.place.right > display.get_width():
            self.hitbox.move(display.get_width() - self.place.right, 0)
            self.place.right = display.get_width()
            self.x = self.place.centerx
            return 'wall'

        elif self.place.top < 0:
            self.hitbox.move(0, -self.place.top)
            self.place.top = 0
            self.y = self.place.centery
            return 'wall'

        elif self.place.bottom > display.get_height():
            self.hitbox.move(0, display.get_height() - self.place.bottom)
            self.place.bottom = display.get_height()
            self.y = self.place.centery
            return 'wall'

    def actAsFlamingRobot(self, target):
        if self.accelerationCooldown <= 0:
            self.accelerateAsFlamingRobot(target)

        if self.fireCooldown <= 0:
            self.newBullets.append(bullet(0, 0, 26, 'flamingRobotFireTrail.png', self.x, self.y))
            self.fireCooldown = 200

        self.accelerationCooldown -= GAMESPEED
        self.fireCooldown -= GAMESPEED

        if self.moveNormally() == 'wall':
            self.accelerateAsFlamingRobot(target)

    def actAsRobotBodyguard(self, target):
        if self.mode == 'chasing':
            self.hr = getPath(0.5, (self.x, self.y), (target.x, target.y))[0]
            self.vr = getPath(0.5, (self.x, self.y), (target.x, target.y))[1]
            self.moveNormally()

        else:
            self.fireCooldown -= GAMESPEED

            if self.fireCooldown <= 0:
                self.newBullets.append(bullet(getPath(1.4, (self.x, self.y), (target.x, target.y))[0],
                                              getPath(1.4, (self.x, self.y), (target.x, target.y))[1], 26,
                                              'brokenTurretFireball.png', self.x, self.y))

                self.fireCooldown = 125

        self.modeDuration -= GAMESPEED

        if self.modeDuration <= 0:
            if self.mode == 'chasing':
                self.mode = 'firing'
                self.modeDuration = 1000

            else:
                self.mode = 'chasing'
                self.modeDuration = random.randint(2000, 4000)

    def actAsFoe(self, target):
        if self.spawnDelay <= 0:
            self.action(target)

        else:
            self.spawnDelay -= GAMESPEED