import random

import pygame

from bullets import bullet
from definitions import getPath, sqrt, signOrRandom, getRadians, pointDistance, sign, lesser, greater
from variables import IMAGES, GAMESPEED, MOVESPEED, width, height, display, diagonal
from rects import rect
import math
watchdogLaserAnim = [f'watchdogLaser{i + 1}.png' for j in range(2) for i in range(4)]
watchdogFirePillarAnim = [f'firePillarFrame{i + 1}.png' for i in range(7) for h in range(36)]


class foe:
    def __init__(self, name, centerx, centery, room, **extra):
        self.spawnsOnDefeat = None
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
        self.fireCooldown = 0
        actions = {'brokenTurret': self.actAsBrokenTurret, 'flamingRobot': self.actAsFlamingRobot,
                   'robotBodyguard': self.actAsRobotBodyguard, 'shipMiniboss': self.actAsShipMiniboss,
                   'temporaryBrokenTurret': self.actAsTemporaryBrokenTurret,
                   'tougherShipMiniboss': self.actAsTougherShipMiniboss, 'hellhound': self.actAsHellhound,
                   'watchdogMeleeSummon': self.actAsWatchdogMeleeSummon,
                   'watchdogRangedSummon': self.actAsWatchdogRangedSummon}
        self.action = actions[self.type]
        self.room = room
        self.shieldedBy = None
        self.animationFrame = 0

        if name == 'brokenTurret':
            self.hp = 20
            self.sprite = 'brokenTurret.png'
            self.damage = 26
            self.rotated = True

        elif name == 'flamingRobot':
            self.hp = 10
            self.sprite = 'flamingRobotTemporarySprite.png'
            self.damage = 26
            self.accelerationCooldown = 0

        elif name == 'robotBodyguard':
            self.hp = 30
            self.sprite = 'temporaryRobotBodyguard.png'
            self.damage = 26
            self.modeDuration = random.randint(100, 2000)
            self.mode = 'chasing'

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

        elif name == 'watchdogMeleeSummon':
            self.sprite = 'flamingRobotTemporarySprite.png'
            self.hp = 2
            self.damage = 26

        elif name == 'watchdogRangedSummon':
            self.sprite = 'temporaryRobotBodyguard.png'
            self.hp = 2
            self.damage = 26

        self.place = IMAGES[self.sprite].get_rect(center=(centerx, centery))
        self.hitbox = rect(self.place)
        self.initialHp = self.hp

        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')

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

    def moveNormally(self):
        self.x += self.hr * GAMESPEED * MOVESPEED
        self.y += self.vr * GAMESPEED * MOVESPEED
        self.hitbox.move(self.hr * GAMESPEED * MOVESPEED, self.vr * GAMESPEED * MOVESPEED)
        self.place.centerx = self.x
        self.place.centery = self.y
        wallCollision = 0
        self.hitbox.getEnds()

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
            self.setMovementNearTarget(target, 1.2, math.pi / 6)
            self.accelerationCooldown = 300

        if self.fireCooldown <= 0:
            self.newBullets.append(bullet(0, 0, 26, 'flamingRobotFireTrail.png', self.x, self.y))
            self.fireCooldown = 100

        self.accelerationCooldown -= GAMESPEED
        self.fireCooldown -= GAMESPEED

        if self.moveNormally():
            self.setMovementNearTarget(target, 0.5, math.pi / 6)
            self.accelerationCooldown = 300

    def actAsRobotBodyguard(self, target):
        if self.mode == 'chasing':
            self.setMovementToTarget(target, 0.7)
            self.moveNormally()

        else:
            self.fireCooldown -= GAMESPEED

            if self.fireCooldown <= 0:
                self.basicStraightShot(1.7, 'brokenTurretFireball.png', 26, target)
                self.fireCooldown = 125

        self.modeDuration -= GAMESPEED

        if self.modeDuration <= 0:
            if self.mode == 'chasing':
                self.mode = 'firing'
                self.modeDuration = 1000

            else:
                self.mode = 'chasing'
                self.modeDuration = random.randint(2000, 4000)

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
        angle = getRadians(target.x - self.x, target.y - self.y) + random.randint(-100, 100) * variation / 200
        self.hr = math.cos(angle) * speed
        self.vr = -math.sin(angle) * speed

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

    def fireLaserToAngle(self, angle, sprite, damage, animation=None, linger=10, checksCollisionWhen='True'):
        offset = [math.cos(angle) * diagonal / 2, -math.sin(angle) * diagonal / 2]
        self.newBullets += [bullet(0, 0, damage, sprite, self.x + offset[0], self.y + offset[1],
                                   linger=linger, animation=animation, rotation=angle * 180 / math.pi,
                                   piercing=float('inf'), checksCollisionWhen=checksCollisionWhen)]

    def actAsTougherShipMiniboss(self, target):
        self.modeDuration -= GAMESPEED
        self.fireCooldown -= GAMESPEED
        self.altFireCooldown -= GAMESPEED
        self.pause -= GAMESPEED

        if self.pause <= 0:
            if self.mode == 'standard':
                self.pause -= GAMESPEED
                self.standardModeDuration -= GAMESPEED

                if self.pause <= 0:
                    if self.standardMode == 'randomMovement':
                        self.accelerationCooldown -= GAMESPEED

                        if self.moveNormally():
                            self.accelerationCooldown = 0

                        if self.accelerationCooldown <= 0:
                            self.setMovementNearTarget(target, 0.6, 1)
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
                    self.newFoes += [foe('temporaryBrokenTurret', width * 19 / 20, height / 7, self.room,
                                         spawnDelay=250),
                                     foe('temporaryBrokenTurret', width * 19 / 20, height * 19 / 20,
                                         self.room, spawnDelay=250),
                                     foe('temporaryBrokenTurret', width / 20, height * 19 / 20, self.room,
                                         spawnDelay=250),
                                     foe('temporaryBrokenTurret', width / 20, height / 7, self.room, spawnDelay=250)]
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

    def teleportToTarget(self, target):
        self.x, self.y = target.x, target.y
        self.spawnDelay = 250
        self.place.centerx, self.place.centery = self.x, self.y
        self.hitbox = rect(self.place)

    def createStillBulletRandomlyInSpace(self, xMin, xMax, yMin, yMax, sprite, damage, linger, rotation=0,
                                         delayAnim=None):
        centerx = random.randint(xMin, xMax)
        centery = random.randint(yMin, yMax)
        self.newBullets.append(bullet(0, 0, damage, sprite, centerx, centery, linger=linger, delay=250,
                                      rotation=rotation, delayedAnimation=delayAnim, consistentPoint='midbottom'))

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

            if self.mode == 'standard':
                newMode = random.randint(4, 4)

                if newMode == 0:
                    self.mode = 'flamingRobot'
                    self.modeDuration = 2900
                    self.dashing = 1
                    self.setMovementToTarget(target, 2)

                elif newMode == 1:
                    self.mode = 'dashingAndFiring'
                    self.modeDuration = float('inf')
                    self.teleportRandomly()
                    self.setMovementToTarget(target, 2.5)

                elif newMode == 2:
                    self.mode = 'dashingAndSwiping'
                    self.teleportRandomly()
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

    def showHp(self):
        hpGoneRect = pygame.Rect(width * 4 / 5, self.hpBarTop, width * 1 / 6, height / 70)
        hpRect = pygame.Rect(width * 4 / 5, self.hpBarTop, width * 1 / 6 * self.hp / self.initialHp, height / 70)
        display.fill('#1abdbd', hpGoneRect)
        display.fill('#cd300e', hpRect)

    def actAsFoe(self, target):
        if self.spawnDelay <= 0:
            self.action(target)

        else:
            self.spawnDelay -= GAMESPEED
