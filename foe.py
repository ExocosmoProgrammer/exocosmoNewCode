import random

import pygame

from bullets import bullet
from definitions import getPath, sqrt, signOrRandom, getRadians, pointDistance, sign, lesser, greater, \
    getPartiallyRandomPath, skip, plusOrMinus, getDegrees
from variables import IMAGES, GAMESPEED, MOVESPEED, width, height, display, diagonal
from rects import rect
import math
watchdogLaserAnim = [f'watchdogLaser{i + 1}.png' for j in range(2) for i in range(4)]
watchdogFirePillarAnim = [f'firePillarFrame{i + 1}.png' for i in range(7) for h in range(36)]


class foe:
    def __init__(self, name, centerx, centery, room, dependentFoes=None, **extra):
        if dependentFoes is None:
            dependentFoes = []

        self.spawnsOnDefeat = None
        self.deathAnimation = None
        self.type = name
        self.rotated = False
        self.angle = 0
        self.x = centerx
        self.showsHp = 0
        self.hpBarTop = height / 10
        self.y = centery
        self.hr = 0
        self.vr = 0
        self.spawnDelay = 0
        self.yBoundary = 0
        self.delaySprite = 'moltenDelaySprite.png'
        self.newBullets = []
        self.newFoes = []
        self.cooldownPerRoomSwitch = 525
        self.hasFullHitbox = True
        self.fireCooldown = random.randint(100, 400)
        actions = {'brokenTurret': self.actAsBrokenTurret, 'flamingRobot': self.actAsFlamingRobot,
                   'robotBodyguard': self.actAsRobotBodyguard, 'shipMiniboss': self.actAsShipMiniboss,
                   'temporaryBrokenTurret': self.actAsTemporaryBrokenTurret,
                   'tougherShipMiniboss': self.actAsTougherWatchdog, 'hellhound': self.actAsHellhound,
                   'watchdogMeleeSummon': self.actAsWatchdogMeleeSummon,
                   'watchdogRangedSummon': self.actAsWatchdogRangedSummon, 'antlionLarva': self.actAsAntlionLarva,
                   'desertCaveExplosiveFoe': self.actAsDesertCaveExplosiveFoe,
                   'desertCaveSummoner': self.actAsDesertCaveSummoner,
                   'desertCaveSpittingGrub': self.actAsDesertCaveSpittingGrub,
                   'desertCaveJellyfish': self.actAsDesertCaveJellyfish,
                   'desertCaveSmallFly': self.actAsDesertCaveSmallFly,
                   'desertCaveLargeFly': self.actAsDesertCaveLargeFly, 'desertCaveSpider': self.actAsDesertCaveSpider,
                   }
        wanderingMethods = {'brokenTurret': skip, 'flamingRobot': skip, 'robotBodyguard': skip,
                            'tougherShipMiniboss': skip, 'hellhound': skip, 'desertCaveLargeFly': skip,
                            'desertCaveSmallFly': skip}

        try:
            self.wanderingMethod = wanderingMethods[name]

        except KeyError:
            self.wanderingMethod = self.actAsGenericWanderingFoe

        self.action = actions[self.type]
        self.room = list(room)
        self.shieldedBy = None
        self.animationFrame = 0
        self.dependentFoes = dependentFoes
        self.aggressionRadius = 225
        self.turnCooldownWhileWandering = 0
        self.maximumDistanceFromHomeWhileWandering = 1
        self.initialRoom = list(self.room).copy()

        if name == 'brokenTurret':
            self.hp = 10
            self.sprite = 'brokenTurret.png'
            self.damage = 26
            self.rotated = True
            self.fireCooldown = 0
            self.aggressionRadius = float('inf')

        elif name == 'flamingRobot':
            self.hp = 5
            self.sprite = 'flamingRobotTemporarySprite.png'
            self.damage = 26
            self.accelerationCooldown = 0
            self.fireCooldown = 0
            self.aggressionRadius = float('inf')

        elif name == 'robotBodyguard':
            self.hp = 15
            self.sprite = 'temporaryRobotBodyguard.png'
            self.damage = 26
            self.modeDuration = random.randint(100, 1400)
            self.mode = 'chasing'
            self.aggressionRadius = float('inf')

        elif name == 'antlionLarva':
            self.hp = 3
            self.sprite = 'desertCaveAntlionLarvaFrame1.png'
            self.animation = [f'desertCaveAntlionLarvaFrame{i}.png' for i in [1, 2] for j in range(20)]
            self.rotated = True
            self.damage = 45
            self.spawnDelay = 100
            self.cooldownPerRoomSwitch = 125

        elif name == 'desertCaveExplosiveFoe':
            self.hp = 3
            self.sprite = 'meleeBlob.png'
            self.damage = 30
            self.duration = 1000

        elif name == 'desertCaveSummoner':
            self.hp = 23
            self.sprite = 'desertCaveSummonerFrame2.png'
            self.animation = [f'desertCaveSummoner2Frame{i}.png' for i in range(1, 4) for j in range(30)]
            self.damage = 0
            self.fireCooldown = 500
            self.altFireCooldown = 1000
            self.thirdFireCooldown = 1500
            self.spawnDelay = random.randint(50, 500)
            self.cooldownPerRoomSwitch = 0

        elif name == 'desertCaveSpittingGrub':
            self.hp = 2
            self.damage = 20
            self.spawnDelay = random.randint(10, 100)
            self.sprite = 'blobSummon.png'

        elif name == 'desertCaveJellyfish':
            self.hp = 5
            self.rotated = True
            self.angle = 0
            self.damage = 35
            self.sprite = 'desertCaveJellyfishFrame1.png'
            self.momentum = 1
            self.fireCooldown = 0
            self.animation = [f'desertCaveJellyfishFrame{i}.png' for i in range(1, 5) for j in range(50)]
            self.deathAnimation = [f'desertCaveJellyfishDeathFrame{i}.png' for i in [1, 2] for j in range(60)]

        elif name == 'desertCaveLargeFly':
            self.hp = 15
            self.damage = 20
            self.sprite = 'largeFlyFrame1.png'
            self.summons = {'left': None, 'top': None, 'right': None}
            self.cooldownPerRoomSwitch = float('inf')
            self.animation = [f'largeFlyFrame{i}.png' for i in [1, 2] for j in range(45)]
            self.deathAnimation = [f'desertCaveLargeFlyDeathFrame{i}.png' for i in [1, 2] for j in range(150)]

        elif name == 'desertCaveSmallFly':
            self.hp = 1
            self.damage = 20
            self.sprite = 'desertCaveSmallFlyFrame1.png'
            self.animation = [f'desertCaveSmallFlyFrame{i}.png' for i in [1, 2] for j in range(15)]
            self.currentDuration = 0
            self.cooldownPerRoomSwitch = float('inf')
            self.aggressionRadius = float('inf')
            self.deathAnimation = [f'desertCaveSmallFlyDeathFrame{i}.png' for i in [1, 2] for j in range(100)]

        elif name == 'desertCaveSpider':
            self.hp = 30
            self.damage = 50
            self.sprite = 'desertCaveSpider.png'
            self.altFireCooldown = float('inf')
            self.cooldownPerRoomSwitch = 50
            self.aggressionRadius = float('inf')

        elif name == 'tougherShipMiniboss':
            self.hp = 500
            self.sprite = 'watchdog2.png'
            self.damage = 26
            self.modeDuration = 2200
            self.standardModeDuration = 2200
            self.altFireCooldown = 0
            self.mode = 'standard'
            self.standardMode = 'randomMovement'
            self.accelerationCooldown = 0
            self.summonCooldown = 18000
            self.dashing = 0
            self.showsHp = 1
            self.altFireCooldown = 0
            self.laserAngle = 0
            self.pause = 0
            self.laser2Angle = 0
            self.enraged = 0
            self.thirdFireCooldown = 0
            self.randomLaser1Angle = 0
            self.randomLaser2Angle = 0

        elif name == 'shipMiniboss':
            self.hp = 500
            self.sprite = 'watchdog2.png'
            self.damage = 26
            self.modeDuration = 1000
            self.mode = 'chasing'
            self.summonCooldown = 18000
            self.dashing = 0
            self.showsHp = 1

        elif name == 'temporaryBrokenTurret':
            self.hp = float('inf')
            self.duration = 2000
            self.sprite = 'brokenTurret.png'
            self.damage = 26
            self.rotated = True

        elif name == 'hellhound':
            self.hp = 1250
            self.sprite = 'watchdog.png'
            self.mode = 'standard'
            self.modeDuration = 1900
            self.damage = 26
            self.altFireCooldown = 100
            self.dashing = 0
            self.hpBarTop = height / 20
            self.showsHp = 1
            self.enraged = 0

        elif name == 'watchdogMeleeSummon':
            self.sprite = 'flamingRobotTemporarySprite.png'
            self.hp = 2
            self.damage = 26

        elif name == 'watchdogRangedSummon':
            self.sprite = 'temporaryRobotBodyguard.png'
            self.hp = 2
            self.damage = 26

        self.roomSwitchCooldown = self.cooldownPerRoomSwitch
        self.place = IMAGES[self.sprite].get_rect(center=(centerx, centery))
        self.hitbox = rect(self.place)
        self.initialHp = self.hp

        for enemy in self.dependentFoes:
            enemy.dependentFoes.append(self)
            self.newFoes.append(enemy)

        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')

            if self.type == 'desertCaveSmallFly':
                print(stat, extra[stat], eval(f'self.{stat}'), 'greatInfo')

    def progressAnimation(self):
        self.animationFrame += GAMESPEED

        try:
            self.sprite = self.animation[int(self.animationFrame)]

        except IndexError:
            self.animationFrame = 0
            self.sprite = self.animation[0]

        self.place = IMAGES[self.sprite].get_rect(center=(self.x, self.y))

    def actAsBrokenTurret(self, target):
        self.angle += 0.015 * GAMESPEED
        self.place = IMAGES[self.sprite].get_rect(center=(self.x, self.y))
        self.fireCooldown -= GAMESPEED

        if self.fireCooldown <= 0:
            self.newBullets.append(bullet(math.cos(self.angle) * 2, math.sin(self.angle) * 2, 26,
                                   'brokenTurretFireball.png', self.x, self.y, rotation=-self.angle * 180 / math.pi))
            self.fireCooldown = random.randint(27, 50)

    def actAsTemporaryBrokenTurret(self, target):
        self.actAsBrokenTurret(target)
        self.duration -= GAMESPEED

        if self.duration <= 0:
            self.hp = 0

    def estimatePredictivePath(self, target, speed):
        delay = pointDistance((self.x, self.y), (target.x, target.y)) / speed
        newTargetX = lesser(greater(target.x + target.hr * delay, 0), width)
        newTargetY = lesser(greater(target.y + target.vr * delay, 0), width)
        return getPath(speed, (self.x, self.y), (newTargetX, newTargetY))

    def moveWithoutWallCollision(self):
        self.x += self.hr * GAMESPEED * MOVESPEED
        self.y += self.vr * GAMESPEED * MOVESPEED
        self.hitbox.move(self.hr * GAMESPEED * MOVESPEED, self.vr * GAMESPEED * MOVESPEED)
        self.place.centerx = self.x
        self.place.centery = self.y
        self.hitbox.getEnds()

    def moveWithPotentialToSwitchRooms(self, rooms):
        self.moveWithoutWallCollision()
        roomSwitchDirections = []

        if self.hitbox.left < 0:
            self.place.right = width
            self.hitbox.move(width - self.hitbox.right, 0)
            self.room[0] -= 1
            roomSwitchDirections += ['left']
            self.spawnDelay = 250

        elif self.hitbox.right > width:
            self.place.left = 0
            self.hitbox.move(-self.hitbox.left, 0)
            self.room[0] += 1
            roomSwitchDirections += ['right']
            self.spawnDelay = 250

        if self.hitbox.top < self.yBoundary:
            self.place.bottom = height
            self.hitbox.move(0, height - self.hitbox.bottom)
            self.room[1] += 1
            roomSwitchDirections += ['top']
            self.spawnDelay = 250

        elif self.hitbox.bottom > height:
            self.place.top = 0
            self.hitbox.move(0, -self.hitbox.top)
            self.room[1] -= 1
            roomSwitchDirections += ['bottom']
            self.spawnDelay = 250

        self.x = self.place.centerx
        self.y = self.place.centery
        self.hitbox.updatePoints()

        if tuple(self.room) not in list(rooms.rooms.keys()):
            if 'left' in roomSwitchDirections:
                self.place.left = 0
                self.hitbox.move(-self.hitbox.left, 0)
                self.room[0] += 1

            if 'right' in roomSwitchDirections:
                self.place.right = width
                self.hitbox.move(width - self.hitbox.right, 0)
                self.room[0] -= 1

            if 'top' in roomSwitchDirections:
                self.place.top = 0
                self.hitbox.move(0, -self.hitbox.top)
                self.room[1] -= 1

            if 'bottom' in roomSwitchDirections:
                self.place.bottom = height
                self.hitbox.move(0, height - self.hitbox.bottom)
                self.room[1] += 1

            self.hitbox.getEnds()
            self.x = self.place.centerx
            self.y = self.place.centery
            return 1

    def moveNormally(self):
        self.moveWithoutWallCollision()
        wallCollision = 0

        if self.hitbox.left < 0:
            self.hitbox.move(-self.hitbox.left, 0)
            self.place.left = 0
            self.x = self.place.centerx
            wallCollision = 1

        elif self.hitbox.right > width:
            self.hitbox.move(width - self.hitbox.right, 0)
            self.place.right = width
            self.x = self.place.centerx
            wallCollision = 1

        if self.hitbox.top < self.yBoundary:
            self.hitbox.move(0, self.yBoundary - self.hitbox.top)
            self.place.top = self.yBoundary
            self.y = self.place.centery
            wallCollision = 1

        elif self.hitbox.bottom > height:
            self.hitbox.move(0, height - self.hitbox.bottom)
            self.place.bottom = height
            self.y = self.place.centery
            wallCollision = 1

        return wallCollision

    def actAsFlamingRobot(self, target):
        if self.accelerationCooldown <= 0:
            self.setMovementNearTarget(target, 1.2, 30)
            self.accelerationCooldown = 300

        if self.fireCooldown <= 0:
            self.newBullets.append(bullet(0, 0, 26, 'flamingRobotFireTrail.png', self.x, self.y))
            self.fireCooldown = 100

        self.accelerationCooldown -= GAMESPEED
        self.fireCooldown -= GAMESPEED

        if self.moveNormally():
            self.setMovementNearTarget(target, 1.2, 30)
            self.accelerationCooldown = 300

    def actAsRobotBodyguard(self, target):
        if self.mode == 'chasing':
            self.setMovementToTarget(target, 0.9)
            self.moveNormally()

        else:
            self.fireCooldown -= GAMESPEED

            if self.fireCooldown <= 0:
                self.basicStraightShot(2.1, 'brokenTurretFireball.png', 26, target)
                self.fireCooldown = 90

        self.modeDuration -= GAMESPEED

        if self.modeDuration <= 0:
            if self.mode == 'chasing':
                self.mode = 'firing'
                self.modeDuration = 1000

            else:
                self.mode = 'chasing'
                self.modeDuration = random.randint(2000, 4000)

    def actAsAntlionLarva(self, target):
        self.angle = getRadians(target.x - self.x, self.y - target.y)
        self.setMovementToTarget(target, 0.6)
        self.progressAnimation()
        self.moveNormally()

    def actAsDesertCaveExplosiveFoe(self, target):
        self.duration -= GAMESPEED
        angleIncNeeded = 2 * math.pi - (self.angle - getRadians(target.x - self.x, self.y - target.y)) % (2 * math.pi)
        angleDecNeeded = (self.angle - getRadians(target.x - self.x, self.y - target.y)) % (2 * math.pi)

        if angleIncNeeded > angleDecNeeded:
            self.angle -= 1 / 20

        else:
            self.angle += 1 / 20

        self.hr = math.cos(self.angle) * 2
        self.vr = math.sin(self.angle) * 2

        if self.duration <= 400:
            self.hr += random.randint(-1, 1)
            self.vr += random.randint(-1, 1)

        if self.moveNormally():
            self.angle = getRadians(target.x - self.x, self.y - target.y)

        if self.duration <= 0:
            self.newBullets.append(bullet(0, 0, 65, 'aLargerFire.png', self.x, self.y, dissappearsAtEdges=0,
                                          piercing=float('inf')))
            self.hp = 0

    def actAsDesertCaveSpittingGrub(self, target):
        self.fireCooldown -= GAMESPEED

        if self.fireCooldown <= 0:
            self.basicStraightShot(1.5, 'brokenTurretFireball.png', 15, target)
            self.fireCooldown = 500

    def actAsDesertCaveJellyfish(self, target):
        self.fireCooldown -= GAMESPEED
        self.momentum -= 0.005 * GAMESPEED
        self.progressAnimation()

        self.hr = math.cos(self.angle) * self.momentum * 2
        self.vr = math.sin(self.angle) * self.momentum * 2

        if self.moveNormally():
            self.fireCooldown = 0

        if self.fireCooldown <= 0:
            self.angle = getRadians(target.x - self.x, self.y - target.y)
            self.momentum = 1
            self.fireCooldown = 200

    def actAsDesertCaveLargeFly(self, target):
        self.fireCooldown -= GAMESPEED
        self.progressAnimation()

        if self.fireCooldown <= 0:
            self.fireCooldown = 800

            if self.summons['top'] is None or self.summons['top'].hp <= 0:
                self.newFoes.append(foe('desertCaveSmallFly', self.x, self.y, self.room, dependentFoes=[self],
                                        vr=-0.3))
                self.summons['top'] = self.newFoes[-1]

            elif self.summons['left'] is None or self.summons['left'].hp <= 0:
                self.newFoes.append(foe('desertCaveSmallFly', self.x, self.y, self.room, dependentFoes=[self],
                                        hr=-0.3))
                self.summons['left'] = self.newFoes[-1]

            elif self.summons['right'] is None or self.summons['right'].hp <= 0:
                self.newFoes.append(foe('desertCaveSmallFly', self.x, self.y, self.room, dependentFoes=[self],
                                        hr=0.3))
                self.summons['right'] = self.newFoes[-1]

    def actAsDesertCaveSmallFly(self, target):
        self.fireCooldown -= GAMESPEED
        self.currentDuration += GAMESPEED
        self.progressAnimation()
        print(self.hr, self.vr, self.currentDuration, 'important')

        if self.currentDuration < 200:
            self.moveWithoutWallCollision()

        if self.fireCooldown <= 0:
            self.basicStraightShot(2, 'brokenTurretFireball.png', 35, target)
            self.fireCooldown = 600

    def actAsDesertCaveSummoner(self, target):
        self.fireCooldown -= GAMESPEED
        self.altFireCooldown -= GAMESPEED
        self.thirdFireCooldown -= GAMESPEED
        self.progressAnimation()

        if self.fireCooldown <= 0:
            self.newFoes.append(foe('desertCaveExplosiveFoe',
                                    self.x + random.randint(-int(width / 10), int(width / 10)),
                                    self.y + random.randint(-int(height / 10), int(height / 10)), self.room,
                                    angle=getRadians(target.x - self.x, self.y - target.y), spawnDelay=250))

            self.fireCooldown = 1500

        elif self.altFireCooldown <= 0:
            self.basicSpreadShot(7, math.pi * 2 / 3, target, 1.2, 'bouncySplittingProjectileFromWatchdog.png', 45)
            self.altFireCooldown = 1500

        elif self.thirdFireCooldown <= 0:
            self.teleportRandomly(250)
            self.thirdFireCooldown = 1500

    def actAsDesertCaveSpider(self, target):
        self.fireCooldown -= GAMESPEED
        self.altFireCooldown -= GAMESPEED

        if self.moveNormally():
            self.altFireCooldown = 0

        if self.fireCooldown <= 0:
            self.setMovementNearTarget(target, 2.5, 30)
            self.fireCooldown = float('inf')
            self.altFireCooldown = random.randint(25, 175)

        elif self.altFireCooldown <= 0:
            self.hr = 0
            self.vr = 0
            self.basicSpreadShot(3, math.pi / 6, target, 3, 'brokenTurretFireball.png', 60)
            self.altFireCooldown = float('inf')
            self.fireCooldown = random.randint(15, 150)

    def basicSpreadShot(self, qty, totalAngle, target, speed, sprite, damage):
        indivisualAngle = totalAngle / (qty - 1)
        radians = getRadians(target.x - self.x, self.y - target.y)

        for i in range(qty):
            angle = radians - totalAngle / 2 + indivisualAngle * i
            self.newBullets.append(bullet(math.cos(angle) * speed, math.sin(angle) * speed,
                                          damage, sprite, self.x, self.y))

    def basicStraightShot(self, speed, sprite, damage, target, linger=1600):
        path = getPath(speed, (self.x, self.y), (target.x, target.y))
        self.newBullets.append(bullet(path[0], path[1], damage, sprite, self.x, self.y, linger=linger))

    def fireBouncySplittingProjectile(self, target, speed, damage, sprite, splitBulletsQty):
        path = getPath(speed, (self.x, self.y), (target.x, target.y))
        endEffect = f'for i in range({splitBulletsQty}): ' \
                    f'enemyBullets.append(bullet(math.cos(i * 2 * math.pi / {splitBulletsQty}), ' \
                    f'math.sin(i * 2 * math.pi / {splitBulletsQty}),' \
                    f' 26, "brokenTurretFireball.png", projectile.x, projectile.y, dissappearsAtEdges=0))'
        self.newBullets.append(bullet(path[0], path[1], damage, sprite, self.x, self.y, endEffect=endEffect, bounces=1,
                                      dissappearsAtEdges=0, linger=1200))

    def setMovementToTarget(self, target, speed):
        path = getPath(speed, (self.x, self.y), (target.x, target.y))
        self.hr = path[0]
        self.vr = path[1]

    def setMovementNearTarget(self, target, speed, variation):
        path = getPartiallyRandomPath(speed, (self.x, self.y), (target.x, target.y), variation)
        self.hr = path[0]
        self.vr = path[1]

    def setMovementPredictively(self, target, speed):
        path = self.estimatePredictivePath(target, speed)
        self.hr = path[0]
        self.vr = path[1]

    def fireBasicSemirandomLaserProjectile(self, target, angleVariation, sprite, damage, checksCollisionWhen='True',
                                           animation=None, linger=10):
        radians = getRadians(target.x - self.x, target.y - self.y) + random.randint(-10, 10) * angleVariation / 20
        offset = [math.cos(radians) * diagonal / 2, -math.sin(radians) * diagonal / 2]
        self.newBullets.append(bullet(0, 0, damage, sprite, self.x + offset[0], self.y + offset[1],
                                      linger=linger, animation=animation, checksCollisionWhen=checksCollisionWhen,
                                      rotation=radians * 180 / math.pi, piercing=float('inf')))

        return radians

    def fireLaserToAngle(self, angle, sprite, damage, animation=None, linger=10, checksCollisionWhen='True', delay=0,
                         delaysprite='moltenDelaySprite.png'):
        offset = [math.cos(angle) * diagonal / 2, -math.sin(angle) * diagonal / 2]
        self.newBullets += [bullet(0, 0, damage, sprite, self.x + offset[0], self.y + offset[1],
                                   linger=linger, animation=animation, rotation=angle * 180 / math.pi,
                                   piercing=float('inf'), checksCollisionWhen=checksCollisionWhen, delay=delay,
                                   delayedSprite=delaysprite)]

    def fireLaserWithWarning(self, angle, sprite, damage, warningLinger, laserLinger, laserDelay, animation=None):
        self.fireLaserToAngle(angle, sprite, 0, animation=animation, linger=warningLinger,
                              checksCollisionWhen='False')
        self.fireLaserToAngle(angle, sprite, damage, animation=animation, linger=laserLinger, delay=laserDelay,
                              delaysprite='invisiblePixels.png')

    def actAsTougherWatchdogNotEnraged(self, target):
        self.modeDuration -= GAMESPEED
        self.fireCooldown -= GAMESPEED
        self.altFireCooldown -= GAMESPEED
        self.pause -= GAMESPEED

        if self.pause <= 0:
            if self.mode == 'standard':
                self.standardModeDuration -= GAMESPEED

                if self.pause <= 0:
                    if self.standardMode == 'randomMovement':
                        self.accelerationCooldown -= GAMESPEED

                        if self.moveNormally():
                            self.accelerationCooldown = 0

                        if self.accelerationCooldown <= 0:
                            self.setMovementNearTarget(target, 0.6, 57)
                            self.accelerationCooldown = 100

                        if self.fireCooldown <= 0:
                            self.basicStraightShot(2.5, 'brokenTurretFireball.png', 26, target)
                            self.fireCooldown = 150

                    elif self.standardMode == 'spreadShotWithMovement':
                        self.setMovementToTarget(target, 0.4)
                        self.moveNormally()

                        if self.fireCooldown <= 0:
                            self.basicSpreadShot(5, math.pi / 3, target, 1.4, 'brokenTurretFireball.png', 26)
                            self.fireCooldown = 350

                    elif self.standardMode == 'spreadShotWithTeleportation':
                        if self.fireCooldown <= 0 and self.modeDuration >= 100:
                            self.basicSpreadShot(5, math.pi / 3, target, 1.2, 'brokenTurretFireball.png', 26)
                            self.fireCooldown = 145
                            self.altFireCooldown = 100

                        elif self.altFireCooldown <= 0:
                            self.teleportRandomly()
                            self.altFireCooldown = 145

                    if self.standardModeDuration <= 0:
                        self.standardModeDuration = 2200
                        self.pause = 200

                        if self.standardMode == 'randomMovement':
                            self.standardMode = 'spreadShotWithMovement'

                        elif self.standardMode == 'spreadShotWithMovement':
                            self.standardMode = 'spreadShotWithTeleportation'
                            self.fireCooldown = 145
                            self.altFireCooldown = 195

                        elif self.standardMode == 'spreadShotWithTeleportation':
                            self.basicSpreadShot(5, math.pi / 3, target, 1.2, 'brokenTurretFireball.png', 26)
                            self.standardMode = 'randomMovement'

            elif self.mode == 'randomLasers':
                if self.fireCooldown <= 0 and self.modeDuration >= 50:
                    self.laserAngle = self.fireBasicSemirandomLaserProjectile(target, 0.4, 'watchdogLaser1.png', 0,
                                                                              animation=watchdogLaserAnim,
                                                                              checksCollisionWhen='False', linger=100)
                    self.laser2Angle = self.fireBasicSemirandomLaserProjectile(target, 0.4, 'watchdogLaser1.png', 0,
                                                                               animation=watchdogLaserAnim,
                                                                               checksCollisionWhen='False', linger=100)
                    self.altFireCooldown = 124
                    self.fireCooldown = 149

                elif self.altFireCooldown <= 0:
                    self.fireLaserToAngle(self.laserAngle, 'watchdogLaser1.png', 26,  animation=watchdogLaserAnim,
                                          linger=40)
                    self.fireLaserToAngle(self.laser2Angle, 'watchdogLaser1.png', 26,  animation=watchdogLaserAnim,
                                          linger=40)
                    self.altFireCooldown = 276

            elif self.mode == 'bouncySplittingProjectiles':
                if self.fireCooldown <= 0:
                    self.fireBouncySplittingProjectile(target, 1, 26, 'bouncySplittingProjectileFromWatchdog.png', 15)
                    self.fireCooldown = 241
                    self.altFireCooldown = 50

                elif self.altFireCooldown <= 0:
                    self.teleportRandomly()
                    self.altFireCooldown = 241

            elif self.mode == 'ringsOfProjectiles':
                if self.fireCooldown <= 0:
                    self.basicSpreadShot(21, 2 * math.pi, target, 1.5, 'brokenTurretFireball.png', 26)
                    self.fireCooldown = 250

            elif self.mode == 'closingLasers':
                if self.altFireCooldown <= 0:
                    self.laserAngle = getRadians(target.x - self.x, target.y - self.y) - math.pi / 4
                    self.laser2Angle = getRadians(target.x - self.x, target.y - self.y) + math.pi / 4
                    self.fireLaserToAngle(self.laserAngle, 'watchdogLaser1.png', 26, animation=watchdogLaserAnim,
                                          checksCollisionWhen='False', linger=12)
                    self.fireLaserToAngle(self.laser2Angle, 'watchdogLaser1.png', 26, animation=watchdogLaserAnim,
                                          checksCollisionWhen='False', linger=12)
                    self.fireCooldown = 75
                    self.altFireCooldown = 2200

                if self.fireCooldown <= 0:
                    self.laserAngle += math.pi / 120
                    self.laser2Angle -= math.pi / 120
                    self.fireLaserToAngle(self.laserAngle, 'watchdogLaser1.png', 26, animation=watchdogLaserAnim,
                                          linger=16)
                    self.fireLaserToAngle(self.laser2Angle, 'watchdogLaser1.png', 26, animation=watchdogLaserAnim,
                                          linger=16)
                    self.fireCooldown = 10

            elif self.mode == 'pillarsOfFire':
                if self.fireCooldown <= 0:
                    xInterval = int(width / 7)
                    yInterval = int((height - self.yBoundary) / 7)
                    minX = int(width / 7)
                    minY = int(height / 7)

                    for i in range(5):
                        for j in range(5):
                            self.createStillBulletRandomlyInSpace(i * xInterval + minX, (i + i) * xInterval + minX,
                                                                  j * yInterval + self.yBoundary + minY,
                                                                  (j + 1) * yInterval + self.yBoundary + minY,
                                                                  'firePillarFrame8.png', 26, 417,
                                                                  delayAnim=watchdogFirePillarAnim)

                    self.fireCooldown = 667

            elif self.mode == 'pulledFires':
                if self.fireCooldown <= 0:
                    xInterval = int(width / 7)
                    yInterval = int((height - self.yBoundary) / 7)
                    minX = int(width / 7)
                    minY = int(height / 7)

                    for i in range(5):
                        for j in range(5):
                            self.fireAndPullProjectileInSpace(i * xInterval + minX, (i + i) * xInterval + minX,
                                                              j * yInterval + self.yBoundary + minY,
                                                              (j + 1) * yInterval + self.yBoundary + minY,
                                                              'flamingRobotFireTrail.png', 26, 2)

                    self.fireCooldown = float('inf')

        if self.modeDuration <= 0:
            self.fireCooldown = 0
            self.modeDuration = 2200

            if self.mode == 'standard':
                newModeNumber = random.randint(0, 6)

                if newModeNumber == 0:
                    self.mode = 'turretSummoning'
                    self.pause = 2000
                    self.newFoes += [foe('temporaryBrokenTurret', width * 3 / 4, height / 4, self.room,
                                         spawnDelay=250),
                                     foe('temporaryBrokenTurret', width * 3 / 4, height * 3 / 4,
                                         self.room, spawnDelay=250),
                                     foe('temporaryBrokenTurret', width / 4, height * 3 / 4, self.room,
                                         spawnDelay=250),
                                     foe('temporaryBrokenTurret', width / 4, height / 4, self.room, spawnDelay=250)]
                    self.teleportToPoint(width / 2, height / 2)

                elif newModeNumber == 1:
                    self.mode = 'bouncySplittingProjectiles'
                    self.fireCooldown = 251
                    self.altFireCooldown = 301
                    self.pause = 200

                elif newModeNumber == 2:
                    self.mode = 'randomLasers'
                    self.fireCooldown = 200
                    self.altFireCooldown = 326
                    self.teleportToPoint(width / 2, height / 2)

                elif newModeNumber == 3:
                    self.mode = 'ringsOfProjectiles'
                    self.pause = 200

                elif newModeNumber == 4:
                    self.mode = 'closingLasers'
                    self.teleportToPoint(width / 2, height / 2)
                    self.fireCooldown = 200
                    self.altFireCooldown = 200
                    self.modeDuration = 700

                elif newModeNumber == 5:
                    self.mode = 'pillarsOfFire'

                elif newModeNumber == 6:
                    self.mode = 'pulledFires'
                    self.modeDuration = 1400

            else:
                self.mode = 'standard'
                self.pause = 200

        self.dependentFoes[0].hp = -1

        if self.dependentFoes[0].hp <= 0:
            self.enraged = 1
            self.fireCooldown = 0
            self.altFireCooldown = 0
            self.modeDuration = 0

    def actAsTougherWatchdogEnraged(self, target):
        self.modeDuration -= GAMESPEED
        self.fireCooldown -= GAMESPEED
        self.altFireCooldown -= GAMESPEED

        if self.mode == 'lasers':
            self.thirdFireCooldown -= GAMESPEED

            if self.altFireCooldown <= 0:
                self.altFireCooldown = float('inf')
                self.laserAngle = getRadians((target.x - self.x), (target.y - self.y)) - math.pi / 4
                self.laser2Angle = getRadians((target.x - self.x), (target.y - self.y)) + math.pi / 4
                self.fireLaserToAngle(self.laserAngle, 'watchdogLaser1.png', 0,
                                      watchdogLaserAnim, checksCollisionWhen='False', linger=100)
                self.fireLaserToAngle(self.laser2Angle, 'watchdogLaser1.png', 0,
                                      watchdogLaserAnim, checksCollisionWhen='False', linger=100)
            else:
                if self.fireCooldown <= 0:
                    self.laserAngle += math.pi / 70
                    self.laser2Angle -= math.pi / 70
                    self.fireLaserToAngle(self.laserAngle, 'watchdogLaser1.png', 26,
                                          watchdogLaserAnim)
                    self.fireLaserToAngle(self.laser2Angle, 'watchdogLaser1.png', 26,
                                          watchdogLaserAnim)
                    self.fireCooldown = 10

                if self.thirdFireCooldown <= 0:
                    self.randomLaser1Angle = getRadians(target.x - self.x, target.y - self.y) + \
                                             random.randint(-100, 100) / 300
                    self.randomLaser2Angle = getRadians(target.x - self.x, target.y - self.y) + \
                                             random.randint(-100, 100) / 300
                    self.fireLaserWithWarning(self.randomLaser1Angle, 'watchdogLaser1.png', 26, 60, 30, 80,
                                              animation=watchdogLaserAnim)
                    self.fireLaserWithWarning(self.randomLaser2Angle, 'watchdogLaser1.png', 26, 60, 30, 80,
                                              animation=watchdogLaserAnim)
                    self.thirdFireCooldown = 120

        elif self.mode == 'flamingPillars':
            if self.fireCooldown <= 0:
                for i in range(5):
                    for j in range(4):
                        xmin = int(width * i / 5)
                        xmax = xmin + random.randint(0, int(width / 5))
                        ymin = int((height - self.yBoundary) * j / 4 + self.yBoundary)
                        ymax = ymin + random.randint(0, int((height - self.yBoundary) / 4))
                        coords = self.createStillBulletRandomlyInSpace(xmin, xmax, ymin, ymax, 'firePillarFrame8.png',
                                                              26, 750, delayAnim=watchdogFirePillarAnim)
                        self.createRingOfSpiralingBullets(8, 40, 3, 26, 'flamingRobotFireTrail.png', x=coords[0],
                                                          y=coords[1], delay=250, delaySprite='invisiblePixels.png',
                                                          linger=750)
                self.fireCooldown = 1000

        if self.modeDuration <= 0:
            newMode = random.randint(0, 1)
            self.altFireCooldown = 0
            self.fireCooldown = 0

            if newMode == 0:
                self.thirdFireCooldown = 0
                self.mode = 'lasers'
                self.modeDuration = 3500
                self.altFireCooldown = 50
                self.fireCooldown = 150
                self.teleportToPoint(width / 2, height / 2)

    def actAsTougherWatchdog(self, target):
        if not self.enraged:
            self.actAsTougherWatchdogNotEnraged(target)

        else:
            self.actAsTougherWatchdogEnraged(target)

    def teleportToTarget(self, target):
        self.x, self.y = target.x, target.y
        self.spawnDelay = 250
        self.place.centerx, self.place.centery = self.x, self.y
        self.hitbox = rect(self.place)

    def createRingOfSpiralingBullets(self, speed, radiusToTheta, qty, damage, sprite, x=None,
                                     y=None, linger=1600, delay=0, delaySprite='moltenDelaySprite.png'):
        if x is None:
            x = self.x

        if y is None:
            y = self.y

        thetaIncreaseRate = f'{speed} / sqrt(self.radius ** 2 + {radiusToTheta ** 2})'
        radiusIncreaseRate = f'{speed * radiusToTheta} / sqrt(self.radius ** 2 + {radiusToTheta ** 2})'

        for i in range(qty):
            self.newBullets.append(bullet(0, 0, damage, sprite, x, y,
                                          polarMovement=f'({radiusIncreaseRate}, {thetaIncreaseRate})',
                                          dissappearsAtEdges=0, theta=2 * i * math.pi / qty, delay=delay,
                                          delayedSprite=delaySprite, linger=linger))

    def createStillBulletRandomlyInSpace(self, xMin, xMax, yMin, yMax, sprite, damage, linger, rotation=0,
                                         delayAnim=None):
        centerx = random.randint(xMin, xMax)
        centery = random.randint(yMin, yMax)
        self.newBullets.append(bullet(0, 0, damage, sprite, centerx, centery, linger=linger, delay=250,
                                      rotation=rotation, delayedAnimation=delayAnim, consistentPoint='midbottom',
                                      dissappearsAtEdges=0))
        return centerx, centery

    def fireAndPullProjectileInSpace(self, xMin, xMax, yMin, yMax, sprite, damage, speed):
        centerx = random.randint(xMin, xMax)
        centery = random.randint(yMin, yMax)
        path = getPath(speed * pointDistance((self.x, self.y), (centerx, centery)) / 1850,
                       (centerx, centery), (self.x, self.y))
        movement = f'([0, 0] if self.currentDuration <= 150 else [{path[0]}, {path[1]}])'
        self.newBullets.append(bullet(0, 0, damage, sprite, centerx, centery, delay=250, rotation=0,
                                      linger=1850 / speed + 150, durationBasedMovement=movement))

    def teleportRandomly(self, spawnDelay=250):
        self.x = random.randint(math.floor(self.place.width / 2), math.floor(width - self.place.height / 2))
        self.y = random.randint(math.floor(self.yBoundary + self.place.height / 2),
                                math.floor(height - self.place.height / 2))
        self.spawnDelay = spawnDelay
        self.place.centerx, self.place.centery = self.x, self.y
        self.hitbox = rect(self.place)

    def teleportToPoint(self, x, y):
        self.x, self.y = x, y
        self.spawnDelay = 250
        self.place.centerx, self.place.centery = self.x, self.y
        self.hitbox = rect(self.place)

    def actAsHellhound(self, target):
        self.modeDuration -= GAMESPEED
        self.fireCooldown -= GAMESPEED
        self.altFireCooldown -= GAMESPEED
        self.delaySprite = 'moltenDelaySprite.png'

        if self.mode == 'standard':
            if pointDistance((self.x, self.y), (target.x, target.y)) > diagonal / 10:
                self.setMovementToTarget(target, 1.8)

            else:
                self.setMovementToTarget(target, 0.6)

                if self.fireCooldown <= 0:
                    path = getPath(1.6, (self.x, self.y), (target.x, target.y))
                    self.newBullets.append(bullet(path[0], path[1], 26, 'wraithSwing.png', self.x, self.y, linger=200))
                    self.fireCooldown = 250

            self.moveNormally()

            if self.altFireCooldown <= 0:
                self.teleportRandomly()
                self.altFireCooldown = 1000

        elif self.mode == 'flamingRobot':
            if self.moveNormally():
                self.dashing = 0

                if self.modeDuration > 0:
                    self.setMovementToTarget(target, 3)
                    self.dashing = 1
                    self.moveNormally()

            self.fireCooldown -= GAMESPEED

            if self.fireCooldown <= 0:
                self.newBullets.append(bullet(0, 0, 26, 'flamingRobotFireTrail.png', self.x, self.y))

                self.fireCooldown = 50

        elif self.mode == 'dashingAndFiring':
            if self.fireCooldown <= 0:
                self.newBullets.append(bullet(0, 0, 26, 'flamingRobotFireTrail.png', self.x, self.y))
                self.fireCooldown = 40

            if self.altFireCooldown <= 0:
                self.newBullets.append(bullet(-self.vr / 2, self.hr / 2, 26,
                                              'brokenTurretFireball.png', self.x, self.y))
                self.newBullets.append(bullet(self.vr / 2, -self.hr / 2, 26,
                                              'brokenTurretFireball.png', self.x, self.y))
                self.altFireCooldown = 40

            if self.moveNormally():
                self.basicSpreadShot(45, 2 * math.pi, target, 1, 'brokenTurretFireball.png', 26)
                self.modeDuration = 0
                self.fireCooldown = 100
                self.altFireCooldown = 100

        elif self.mode == 'dashingAndSwiping':
            if self.moveNormally():
                self.dashing = 0

                if self.modeDuration > 0:
                    self.dashing = 1
                    self.setMovementToTarget(target, 3)

            if pointDistance((self.x, self.y), (target.x, target.y)) < diagonal / 5 and self.fireCooldown <= 0:
                self.basicStraightShot(2.5, 'largerWraithSwing.png', 26, target, linger=200)
                self.fireCooldown = 250

        elif self.mode == 'hidingInFire':
            if self.moveNormally():
                self.fireCooldown = lesser(15, self.fireCooldown)

            if self.fireCooldown <= 0:
                xInterval = int(width / 7)
                yInterval = int((height - self.yBoundary) / 7)
                minX = int(width / 7)
                minY = int(height / 7)

                for i in range(5):
                    for j in range(5):
                        self.createStillBulletRandomlyInSpace(i * xInterval + minX, (i + i) * xInterval + minX,
                                                              j * yInterval + self.yBoundary + minY,
                                                              (j + 1) * yInterval + self.yBoundary + minY,
                                                              'flamingRobotFireTrail.png', 26, 417)

                self.fireCooldown = 1333
                self.delaySprite = 'invisiblePixels.png'
                self.teleportRandomly(spawnDelay=417)
                self.newBullets.append(bullet(0, 0, 26, 'flamingRobotFireTrail.png', self.x, self.y,
                                              delay=250, linger=167,
                                              durationBasedPlace=f'({self.x} + math.cos(self.currentDuration / 5) * 5,'
                                              f'{self.y} + math.sin(self.currentDuration / 5) * 5)'))
                self.altFireCooldown = 0

            elif self.altFireCooldown <= 0:
                self.fireCooldown = 500
                self.altFireCooldown = 501
                self.setMovementPredictively(target, 6)

        elif self.mode == 'dashingFromWalls':
            if self.moveNormally():
                self.dashing = 0

                if self.modeDuration > 0:
                    self.dashing = 1
                    self.delaySprite = self.sprite
                    self.spawnDelay = 75
                    self.setMovementPredictively(target, 15)
                    self.fireLaserToAngle(getRadians(self.hr, self.vr), 'watchdogLaser1.png', 0,
                                          animation=watchdogLaserAnim, linger=75, checksCollisionWhen='False')

        if self.modeDuration <= 0 and not self.dashing:
            self.fireCooldown = 0
            self.altFireCooldown = 0
            self.teleportRandomly()

            if self.mode == 'standard':
                newMode = random.randint(0, 4)

                if newMode == 0:
                    self.mode = 'flamingRobot'
                    self.modeDuration = 2900
                    self.dashing = 1
                    self.setMovementToTarget(target, 2)

                elif newMode == 1:
                    self.mode = 'dashingAndFiring'
                    self.modeDuration = float('inf')
                    self.setMovementToTarget(target, 2.5)

                elif newMode == 2:
                    self.mode = 'dashingAndSwiping'
                    self.setMovementToTarget(target, 2.3)
                    self.modeDuration = 2900
                    self.dashing = 1

                elif newMode == 3:
                    self.mode = 'hidingInFire'
                    self.modeDuration = 599

                else:
                    self.mode = 'dashingFromWalls'
                    self.dashing = 1
                    self.modeDuration = 2900
                    self.setMovementToTarget(target, 3)

            else:
                self.mode = 'standard'
                self.modeDuration = 2900

    def actAsWatchdogMeleeSummon(self, target):
        self.setMovementToTarget(target, 0.3)
        self.moveNormally()

    def actAsWatchdogRangedSummon(self, target):
        self.fireCooldown -= GAMESPEED

        if self.fireCooldown <= 0:
            path = getPath(0.5, (self.x, self.y), (target.x, target.y))
            self.newBullets.append(bullet(path[0], path[1], 26, 'brokenTurretFireball.png', self.x, self.y,
                                          linger=1800))
            self.fireCooldown = 1000

    def actAsShipMiniboss(self, target):
        self.modeDuration -= GAMESPEED
        self.summonCooldown -= GAMESPEED

        if self.mode == 'chasing':
            self.setMovementToTarget(target, 0.65)
            self.moveNormally()

        elif self.mode == 'firingInSpread':
            self.fireCooldown -= GAMESPEED

            if self.fireCooldown <= 0:
                radians = getRadians(target.x - self.x, self.y - target.y)

                if self.hp > 250:
                    for i in range(5):
                        angle = radians - 0.6 + 0.3 * i
                        self.newBullets.append(bullet(1.65 * math.cos(angle),
                                                      1.65 * math.sin(angle),
                                                      26, 'brokenTurretFireball.png', self.x, self.y))

                    self.fireCooldown = 270

                else:
                    for i in range(32):
                        angle = radians + i * math.pi / 16
                        self.newBullets.append(bullet(1.5 * math.cos(angle),
                                                      1.5 * math.sin(angle),
                                                      26, 'brokenTurretFireball.png', self.x, self.y))

                    self.fireCooldown = 300

        elif self.mode == 'firing':
            self.fireCooldown -= GAMESPEED

            if self.fireCooldown <= 0:
                path = getPath(3, (self.x, self.y), (target.x, target.y))
                self.newBullets.append(bullet(path[0], path[1], 26, 'brokenTurretFireball.png', self.x, self.y,
                                              linger=400))
                self.fireCooldown = 50

        elif self.mode == 'hasSummons':
            if pointDistance((self.x, self.y), (width / 2, height / 2)) > height / 300:
                self.setMovementToTarget(target, 1)
                self.moveNormally()

            else:
                self.fireCooldown -= GAMESPEED

                if self.fireCooldown <= 0:
                    path = getPath(2, (self.x, self.y), (target.x, target.y))
                    self.newBullets.append(bullet(path[0], path[1], 26, 'brokenTurretFireball.png', self.x, self.y))
                    self.fireCooldown = 600

        elif self.mode == 'flamingRobot':
            if self.moveNormally():
                self.dashing = 0

                if self.modeDuration > 0:
                    self.setMovementToTarget(target, 2)
                    self.dashing = 1
                    self.moveNormally()

            self.fireCooldown -= GAMESPEED

            if self.fireCooldown <= 0:
                self.newBullets.append(bullet(0, 0, 26, 'flamingRobotFireTrail.png', self.x, self.y))
                self.fireCooldown = 50

        if self.modeDuration <= 0 and not self.dashing:
            if self.summonCooldown <= 0:
                self.mode = 'hasSummons'
                self.modeDuration = 3000
                self.summonCooldown = 18000
                self.newFoes = [foe('temporaryBrokenTurret', width / 20, height / 20, self.room, spawnDelay=500),
                                foe('temporaryBrokenTurret', width * 19 / 20, height / 20, self.room,
                                    spawnDelay=500),
                                foe('temporaryBrokenTurret', width * 19 / 20, height * 19 / 20,
                                    self.room, spawnDelay=500),
                                foe('temporaryBrokenTurret', width / 20, height * 19 / 20, self.room,
                                    spawnDelay=500)]

            elif self.mode == 'chasing':
                self.mode = random.choice(['firing', 'firingInSpread'])
                self.modeDuration = random.randint(2000, 4000)
                self.fireCooldown = 500

            elif self.mode == 'firing' or self.mode == 'firingInSpread':
                if random.randint(0, 1):
                    self.mode = 'chasing'
                    self.modeDuration = random.randint(2000, 4000)

                else:
                    self.mode = 'flamingRobot'
                    self.setMovementToTarget(target, 2)
                    self.dashing = 1
                    self.moveNormally()
                    self.modeDuration = random.randint(4000, 6000)

            elif self.mode == 'hasSummons':
                self.mode = 'chasing'
                self.modeDuration = random.randint(2000, 4000)

            elif self.mode == 'flamingRobot':
                self.mode = 'chasing'
                self.modeDuration = random.randint(2000, 4000)

    def actAsGenericWanderingFoe(self, rooms):
        self.turnCooldownWhileWandering -= GAMESPEED

        try:
            self.progressAnimation()

        except AttributeError:
            pass

        if self.turnCooldownWhileWandering <= 0:
            self.hr = random.randint(-100, 100) / 400
            self.vr = plusOrMinus(sqrt(1 / 16 - self.hr ** 2))
            self.turnCooldownWhileWandering = 350

        if self.moveWithPotentialToSwitchRooms(rooms):
            self.hr = -self.hr
            self.vr = -self.vr

        if self.room[0] - self.initialRoom[0] > self.maximumDistanceFromHomeWhileWandering:
            self.hr = -1

        elif self.room[0] - self.initialRoom[0] < -self.maximumDistanceFromHomeWhileWandering:
            self.hr = 1

        if self.room[1] - self.initialRoom[1] > self.maximumDistanceFromHomeWhileWandering:
            self.vr = 1

        elif self.room[1] - self.initialRoom[1] < -self.maximumDistanceFromHomeWhileWandering:
            self.vr = -1

        if self.rotated:
            self.angle = getRadians(self.hr, -self.vr)

        if self.hasFullHitbox and False:
            self.place.centerx = self.x
            self.place.centery = self.y

            if self.rotated:
                self.hitbox = rect(self.place, -self.angle)

            else:
                self.hitbox = rect(self.place)

    def showHp(self):
        hpGoneRect = pygame.Rect(width * 4 / 5, self.hpBarTop, width * 1 / 6, height / 70)
        hpRect = pygame.Rect(width * 4 / 5, self.hpBarTop, width * 1 / 6 * self.hp / self.initialHp, height / 70)
        display.fill('#1abdbd', hpGoneRect)
        display.fill('#cd300e', hpRect)

    def actAsFoe(self, target):
        if self.spawnDelay <= 0:
            self.action(target)

            if self.hasFullHitbox:
                self.hitbox.updatePoints()

                if self.rotated:
                    self.hitbox = rect(IMAGES[self.sprite].get_rect(center=(self.x, self.y)), -self.angle)

                else:
                    self.hitbox = rect(IMAGES[self.sprite].get_rect(center=(self.x, self.y)))

        else:
            self.spawnDelay -= GAMESPEED

    def chaseThroughRooms(self, target, axis):
        self.roomSwitchCooldown -= GAMESPEED
        self.room = list(self.room)
        initialX = self.x
        initialY = self.y

        if self.roomSwitchCooldown <= 0:
            self.roomSwitchCooldown = 525
            self.spawnDelay = 50
            xDis = target.room[0] - self.room[0]
            yDis = target.room[1] - self.room[1]

            if axis == 'x':
                if target.room[0] > self.room[0]:
                    self.x = width / 20
                    self.room[0] += 1

                else:
                    self.x = 19 * width / 20
                    self.room[0] -= 1

            else:
                if target.room[1] > self.room[1]:
                    self.y = 14 * height / 15
                    self.room[1] += 1

                else:
                    self.y = height / 15
                    self.room[1] -= 1

            self.place.centerx = self.x
            self.place.centery = self.y
            self.hitbox.move(self.x - initialX, self.y - initialY)

