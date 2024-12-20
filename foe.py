import copy
import random
import time
import pygame
import math

from bullets import bullet
from definitions import getPath, sqrt, getRadians, pointDistance, lesser, greater, \
    getPartiallyRandomPath, skip, plusOrMinus, fillWithOffset
from temporaryAnimation import temporaryAnimation
from variables import IMAGES, GAMESPEED, MOVESPEED, width, height, display, diagonal
from rects import rect
from droppedItem import droppedItem
from item import item
from debuff import debuff

watchdogLaserAnim = [f'watchdogLaser{i + 1}.png' for j in range(2) for i in range(4)]
watchdogFirePillarAnim = [f'watchdogFirePillar{i + 1}.png' for i in range(7) for h in range(36)]
hellhoundTeleportAnimation = ['hellhoundTeleport1.png'] * 8 + \
                             [f'hellhoundTeleport{i}.png' for i in range(1, 12) for j in range(22)]
watchdogTeleportAnimation = [f'watchdogTeleport{i}.png' for i in range(1, 13) for j in range(21)]


class foe:
    def __init__(self, name, centerx, centery, room, dependentFoes=None, unusualTarget=None, **extra):
        if dependentFoes is None:
            dependentFoes = []

        # Initialize attributes.
        self.spawnsOnDefeat = None
        self.deathAnimation = None
        self.type = name
        self.rotated = False
        self.angle = 0
        self.x = centerx
        self.showsHp = False
        self.shieldedBy = None
        self.hpBarTop = height / 10
        self.y = centery
        self.hr = 0
        self.vr = 0
        self.spawnDelay = 0
        self.yBoundary = 0
        self.bottomYBoundary = height
        self.leftXBoundary = 0
        self.rightXBoundary = width
        self.delaySprite = 'hellhoundFootstep.png'
        self.delayFrame = 0
        self.newBullets = []
        self.newFoes = []
        self.cooldownPerRoomSwitch = 525
        self.hasFullHitbox = True
        self.fireCooldown = random.randint(100, 400)
        self.locksRoomOnAggression = False
        self.goesThroughObjects = False
        self.speed = 1
        self.debuffs = []
        
        # A foe that is attacking self may also hurt enemies in self.summons.
        self.summons = []

        # Self will call the function that will be determined by actions[self.type] as a general action.
        actions = {'brokenTurret': self.actAsBrokenTurret, 'flamingRobot': self.actAsFlamingRobot,
                   'robotBodyguard': self.actAsRobotBodyguard, 'shipMiniboss': self.actAsShipMiniboss,
                   'temporaryBrokenTurret': self.actAsTemporaryBrokenTurret,
                   'tougherShipMiniboss': self.actAsTougherWatchdog, 'hellhound': self.actAsHellhound,
                   'antlionLarva': self.actAsAntlionLarva,
                   'desertCaveExplosiveFoe': self.actAsDesertCaveExplosiveFoe,
                   'desertCaveSummoner': self.actAsDesertCaveSummoner,
                   'desertCaveSpittingGrub': self.actAsDesertCaveSpittingGrub,
                   'desertCaveJellyfish': self.actAsDesertCaveJellyfish,
                   'desertCaveSmallFly': self.actAsDesertCaveSmallFly,
                   'desertCaveLargeFly': self.actAsDesertCaveLargeFly, 'desertCaveSpider': self.actAsDesertCaveSpider,
                   'desertCaveMoth': self.actAsDesertCaveMoth, 'desertCaveFlyMiniboss': self.actAsDesertCaveFlyMiniboss,
                   'scary': self.actAsScary}

        # Self will call the function that will be determined by actions[self.type] until self notices the player.
        wanderingMethods = {'brokenTurret': skip, 'flamingRobot': skip, 'robotBodyguard': skip,
                            'tougherShipMiniboss': skip, 'hellhound': skip,
                            'desertCaveLargeFly': self.progressAnimation,
                            'desertCaveSmallFly': self.progressAnimation,
                            'desertCaveFlyMiniboss': self.progressAnimation}

        # Continue initializing attributes. self.wanderingMethod defaults to being self.actAsGenericWanderingFoe
        try:
            self.wanderingMethod = wanderingMethods[name]

        except KeyError:
            self.wanderingMethod = self.actAsGenericWanderingFoe

        self.action = actions[self.type]
        self.room = list(room)
        self.animationFrame = 0
        self.dependentFoes = dependentFoes
        self.aggressionRadius = 225
        self.turnCooldownWhileWandering = 0
        self.initialRoom = list(self.room).copy()
        self.loot = []
        self.stun = 0

        # self.movementModifiers will modify self's movement temporarily. Each element in this list should be a list
        # \where the first element is the horizontal modifier, the second element is the vertical modifier, and the
        # third element is the duration.
        self.movementModifiers = []

        # If self.unusualTarget is None, self will attack pro. Otherwise, self will attack self.unusualTarget.
        self.unusualTarget = unusualTarget

        # self.specialSong determines what, if any, any special song should play when self is around.
        self.specialSong = None

        match name:
            case 'brokenTurret':
                self.hp = 10
                self.sprite = 'brokenTurret.png'
                self.damage = 26
                self.rotated = True
                self.fireCooldown = 0
                self.aggressionRadius = float('inf')
                self.deathAnimation = [f'brokenTurretDestruction{i}.png' for i in range(1, 9) for j in range(60)]
    
            case 'flamingRobot':
                self.hp = 5
                self.sprite = 'flamingRobotTemporarySprite.png'
                self.damage = 26
                self.accelerationCooldown = 0
                self.fireCooldown = 0
                self.aggressionRadius = float('inf')
    
            case 'robotBodyguard':
                self.hp = 15
                self.sprite = 'newRobotBodyguard.png'
                self.deathAnimation = [f'robotBodyguardDestruction{i}.png' for i in range(1, 10) for j in range(30)]
                self.damage = 26
                self.modeDuration = random.randint(100, 1400)
                self.mode = 'chasing'
                self.aggressionRadius = float('inf')
                self.hasFullHitbox = False
                widthOfSprite = IMAGES[self.sprite].get_width()
                heightOfSprite = IMAGES[self.sprite].get_height()
                pygameRect = pygame.Rect(-widthOfSprite / 2, heightOfSprite / 11, widthOfSprite,
                                         heightOfSprite * 9 / 22)
                self.hitboxOnSelf = rect(pygameRect)
    
            case 'antlionLarva':
                self.hp = 3
                self.sprite = 'desertCaveAntlionLarvaFrame1.png'
                self.animation = [f'desertCaveAntlionLarvaFrame{i}.png' for i in [1, 2] for j in range(20)]
                self.rotated = True
                self.damage = 45
                self.spawnDelay = 100
                self.cooldownPerRoomSwitch = 125
    
            case 'desertCaveExplosiveFoe':
                self.hp = 3
                self.sprite = 'meleeBlob.png'
                self.damage = 30
                self.duration = 1000
    
            case 'desertCaveSummoner':
                self.hp = 23
                self.sprite = 'desertCaveSummonerFrame2.png'
                self.animation = [f'desertCaveSummoner2Frame{i}.png' for i in range(1, 4) for j in range(30)]
                self.damage = 0
                self.fireCooldown = 500
                self.altFireCooldown = 1000
                self.thirdFireCooldown = 1500
                self.spawnDelay = random.randint(50, 500)
                self.cooldownPerRoomSwitch = 0
    
            case 'desertCaveSpittingGrub':
                self.hp = 2
                self.damage = 20
                self.spawnDelay = random.randint(10, 100)
                self.sprite = 'blobSummon.png'
    
            case 'desertCaveJellyfish':
                self.hp = 5
                self.rotated = True
                self.angle = 0
                self.damage = 40
                self.sprite = 'desertCaveJellyfishFrame1.png'
                self.momentum = 1
                self.fireCooldown = 0
                self.animation = [f'desertCaveJellyfishFrame{i}.png' for i in range(1, 5) for j in range(50)]
                self.deathAnimation = [f'desertCaveJellyfishDeathFrame{i}.png' for i in [1, 2] for j in range(60)]
                self.loot = [[droppedItem(self.x, self.y, 'lumisInInventory.png',
                                          item('lumis', 'lumisInInventory.png')), 100],
                             [droppedItem(self.x, self.y, 'desertCaveJellyfishFrame1.png',
                                          item('jellyfish', 'desertCaveJellyfishFrame1.png',
                                               'Throws a jellyfish.', stackSize=1,
                                               animation=self.animation)), 100]]
    
            case 'desertCaveLargeFly':
                self.hp = 15
                self.damage = 20
                self.sprite = 'largeFlyFrame1.png'
                self.summonsAsDesertCaveLargeFly = {'left': None, 'top': None, 'right': None}
                self.cooldownPerRoomSwitch = float('inf')
                self.animation = [f'largeFlyFrame{i}.png' for i in [1, 2] for j in range(45)]
                self.deathAnimation = [f'desertCaveLargeFlyDeathFrame{i}.png' for i in [1, 2] for j in range(150)]
                self.loot = [[droppedItem(self.x, self.y, 'lumisInInventory.png',
                                          item('lumis', 'lumisInInventory.png',
                                               qty=random.randint(1, 2))), 100]]
                self.hasFullHitbox = False
                widthOfInitialSprite = IMAGES[self.sprite].get_width()
                heightOfFrameTwo = IMAGES[self.animation[45]].get_height()
                pygameRect = pygame.Rect(-widthOfInitialSprite * 31 / 150, -heightOfFrameTwo * 29 / 73,
                                        widthOfInitialSprite * 2 / 5, heightOfFrameTwo * 77 / 146)
                self.hitboxOnSelf = rect(pygameRect)

            case 'desertCaveSmallFly':
                self.hp = 1
                self.damage = 20
                self.sprite = 'desertCaveSmallFlyFrame1.png'
                self.animation = [f'desertCaveSmallFlyFrame{i}.png' for i in [1, 2] for j in range(15)]
                self.currentDuration = 0
                self.cooldownPerRoomSwitch = float('inf')
                self.aggressionRadius = float('inf')
                self.deathAnimation = [f'desertCaveSmallFlyDeathFrame{i}.png' for i in [1, 2] for j in range(100)]
                self.hasFullHitbox = False
                widthOfInitialSprite = IMAGES[self.sprite].get_width()
                heightOfFrameTwo = IMAGES[self.animation[15]].get_height()
                pygameRect = pygame.Rect(-widthOfInitialSprite * 4 / 57, -heightOfFrameTwo * 7 / 58,
                                         widthOfInitialSprite / 6, heightOfFrameTwo * 11 / 116)
                self.hitboxOnSelf = rect(pygameRect)
    
            case 'desertCaveSpider':
                self.hp = 30
                self.damage = 50
                self.sprite = 'desertCaveSpider.png'
                self.altFireCooldown = float('inf')
                self.cooldownPerRoomSwitch = 50
                self.aggressionRadius = float('inf')
                self.loot = [[droppedItem(self.x, self.y, 'lumisInInventory.png',
                                          item('lumis', 'lumisInInventory.png',
                                               qty=random.randint(5, 10))), 100]]
    
            case 'desertCaveMoth':
                self.hp = 20
                self.damage = 50
                self.sprite = 'desertCaveMoth1.png'
                self.animation = [f'desertCaveMoth{i}.png' for i in [1, 2] for j in range(15)]
                self.fireCooldown = 10
                self.altFireCooldown = 60
                self.movementCode = 'pass'
                self.t = 0
                self.deltaTSign = -1
                self.loot = [[droppedItem(self.x, self.y, 'desertCaveMothProjectile1.png',
                                          item('moth dust', 'desertCaveMothProjectile1.png',
                                               qty=random.randint(5, 10))), 100]]

                # self.hitbox should remain centered on self and at a constant size.
                self.hitboxOnSelf = rect(IMAGES[self.animation[15]].get_rect(center=(0, 0)))
                self.hasFullHitbox = False
    
            case 'desertCaveFlyMiniboss':
                self.hp = 200
                self.damage = 50
                self.sprite = 'desertCaveFlyMiniboss1.png'
                self.animation = [f'desertCaveFlyMiniboss{i}.png' for i in [1, 2] for j in range(30)]
                self.fireCooldown = 0
                self.altFireCooldown = 1999
                self.movementCode = 'pass'
                self.t = 0
                self.deltaTSign = -1
                self.summonCooldown = 0
                self.thirdFireCooldown = float('inf')
                self.fourthFireCooldown = 0
                self.mode = 'summoning'
                self.summonsNext = False
                self.showsHp = True
                self.locksRoomOnAggression = True
                self.specialSong = 'motherFly.mp3'
    
            case 'tougherShipMiniboss':
                self.hp = 500
                self.sprite = 'watchdogIdle1.png'
                self.animation = [f'watchdogIdle{i}.png' for i in [1, 2] for j in range(30)]
                self.damage = 26
                self.modeDuration = 2200
                self.standardModeDuration = 2200
                self.altFireCooldown = 0
                self.mode = 'standard'
                self.standardMode = 'randomMovement'
                self.accelerationCooldown = 0
                self.showsHp = True
                self.altFireCooldown = 0
                self.laserAngle = 0
                self.pause = 0
                self.laser2Angle = 0
                self.enraged = False
                self.thirdFireCooldown = 0
                widthOfFireball = IMAGES['watchdogFireball.png'].get_width()
                heightOfFireball = IMAGES['watchdogFireball.png'].get_height()
                widthOfBigFireball = IMAGES['watchdogLargeFireball.png'].get_width()
                heightOfBigFireball = IMAGES['watchdogLargeFireball.png'].get_height()
                widthOfFireballFragment = IMAGES['watchdogFireballFragment.png'].get_width()
                heightOfFireballFragment = IMAGES['watchdogFireballFragment.png'].get_height()
                widthOfPulledFireball = IMAGES['watchdogPulledFireball.png'].get_width()
                heightOfPulledFireball = IMAGES['watchdogPulledFireball.png'].get_height()
                self.hitboxForFireballs = rect(pygame.Rect(-widthOfFireball * 49 / 112, -heightOfFireball * 9 / 51,
                                                          widthOfFireball * 45 / 56, heightOfFireball * 13 / 51))
                self.hitboxForBigFireballs = rect(pygame.Rect(-widthOfBigFireball * 5 / 52,
                                                              -heightOfBigFireball * 8 / 79,
                                                              widthOfBigFireball * 41 / 156,
                                                              heightOfBigFireball * 29 / 158))
                self.hitboxForFireballFragments = rect(pygame.Rect(-widthOfFireballFragment * 18 / 79,
                                                              -heightOfFireballFragment * 9 / 77,
                                                              widthOfFireballFragment * 23 / 79,
                                                              heightOfFireballFragment * 15 / 77))
                self.hitboxForPulledFireballs = rect(pygame.Rect(-widthOfPulledFireball / 9,
                                                                 -heightOfPulledFireball / 8,
                                                            widthOfPulledFireball * 13 / 45,
                                                            heightOfPulledFireball * 25 / 104))

            case 'shipMiniboss':
                self.hp = 500
                self.sprite = 'watchdog2.png'
                self.damage = 26
                self.modeDuration = 1000
                self.mode = 'chasing'
                self.summonCooldown = 18000
                self.dashing = False
                self.showsHp = True
    
            case 'temporaryBrokenTurret':
                self.hp = float('inf')
                self.duration = 2000
                self.sprite = 'brokenTurret.png'
                self.damage = 26
                self.rotated = True
    
            case 'hellhound':
                self.hp = 1250
                self.sprite = 'hellhoundIdle1.png'
                self.animation = [f'hellhoundIdle{i}.png' for i in [1, 2] for j in range(50)]
                self.mode = 'standard'
                self.modeDuration = 1900
                self.damage = 26
                self.altFireCooldown = 100
                self.dashing = False
                self.hpBarTop = height / 20
                self.showsHp = True
                self.enraged = False
                self.pause = 0

            case 'scary':
                self.delayAnimation = [f'scaryDelayAnimation{i}.png' for i in range(1, 36) for j in range(22)]
                self.sprite = 'scary1.png'
                self.animation = [f'scary{i}.png' for i in [1, 2] for j in range(60)]
                self.duration = 4380
                self.hp = 25
                self.aggressionRadius = float('inf')
                self.damage = 0
                self.fireCooldown = 0
                self.modeDuration = 550
                self.altFireCooldown = 0
                self.thirdFireCooldown = 0
                self.mode = 'fireRandomly'
                self.aggressive = False
                self.searchAnimation = [f'scarySearch{i}.png' for i in range(1, 26) for j in range(30)]
                self.teleportAnimation = [f'scaryTeleport{i}.png' for i in range(1, 23) for j in range(15)]
                self.fastTeleportAnimation = [f'scaryTeleport{i}.png' for i in range(1, 23) for j in range(5)]
                self.theta = 0
                self.acted = False

        if hasattr(self, 'animation'):
            self.idleAnimation = self.animation.copy()

        self.place = IMAGES[self.sprite].get_rect(center=(centerx, centery))
        self.hitbox = rect(self.place)
        self.initialHp = self.hp

        for enemy in self.dependentFoes:
            enemy.dependentFoes.append(self)
            self.newFoes.append(enemy)

        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')

    def progressAnimation(self, *args):
        """Update self's sprite."""

        # Update self.animationFrame
        self.animationFrame += GAMESPEED

        # If self.animationFrame is too large, take self to the start of self's idle animation.
        try:
            self.sprite = self.animation[int(self.animationFrame)]

        except IndexError:
            self.animationFrame = 0
            self.animation = self.idleAnimation.copy()
            self.sprite = self.animation[0]

        # Ensure that self remains centered on the right point.
        self.place = IMAGES[self.sprite].get_rect(center=(self.x, self.y))

    def actAsBrokenTurret(self, target, *args):
        # Rotate self.
        self.angle += 0.015 * GAMESPEED
        self.place = IMAGES[self.sprite].get_rect(center=(self.x, self.y))

        # Reduce self's cooldown.
        self.fireCooldown -= GAMESPEED

        # If self is ready to do so, fire a projectile and set self's delay before firing again.
        if self.fireCooldown <= 0:
            self.newBullets.append(bullet(math.cos(self.angle) * 2, math.sin(self.angle) * 2, 26,
                                   'brokenTurretFireball.png', self.x, self.y))
            self.fireCooldown = random.randint(27, 50)

    def actAsTemporaryBrokenTurret(self, target, *args):
        # Attack like a normal broken turret.
        self.actAsBrokenTurret(target)

        # Reduce self's remaining lifespan.
        self.reduceDuration()

    def estimatePredictivePath(self, target, speed, *args):
        """self.estimatePredictivePath(x, y, z) returns a list of an estimate of the horizontal and vertival movement
        of a projectile that starts at self's center, moves at speed z, and will hit the player unless the its hr
        or vr changes. The target argument should be pro."""
        delay = pointDistance((self.x, self.y), (target.x, target.y)) / speed
        newTargetX = lesser(greater(target.x + target.hr * delay, 0), width)
        newTargetY = lesser(greater(target.y + target.vr * delay, 0), height)
        return getPath(speed, (self.x, self.y), (newTargetX, newTargetY))

    def handleKnockback(self, displayVars, room):
        """Make self move in response to knockback."""

        # This function only needs to be called if self is being knocked back.
        if self.movementModifiers:
            # Keep track of where self currently is.
            oldX = self.x
            oldY = self.y

            # Move self.
            for modifier in self.movementModifiers:
                self.x += modifier[0] * GAMESPEED * MOVESPEED
                self.y += modifier[1] * GAMESPEED * MOVESPEED

            # Define collision to determine if self hit a wall.
            collision = False

            # If self is out of bounds, make self switch directions and go back into bounds and modify the collision
            # variable.
            if self.hitbox.left < self.leftXBoundary or self.hitbox.right > self.rightXBoundary:
                self.x = oldX
                collision = True

                for modifier in self.movementModifiers:
                    modifier[0] *= -1 / 3

            if self.hitbox.top < self.yBoundary or self.hitbox.bottom > self.bottomYBoundary:
                self.y = oldY
                collision = True

                for modifier in self.movementModifiers:
                    modifier[1] *= -1 / 3

            # If self hit a wall, execute the following block,
            if collision:
                # Calculate self's current movement speed.
                speed = sqrt((sum([modifier[0] for modifier in self.movementModifiers]) + self.hr) ** 2 +
                             (sum([modifier[1] for modifier in self.movementModifiers]) + self.vr) ** 2)

                # Briefly pause the game.
                time.sleep(lesser(0.01 * speed, 0.1))
                displayVars.screenShakeDuration = greater(displayVars.screenShakeDuration, lesser(25, speed * 5))

                # Move self backward.
                for modifier in self.movementModifiers:
                    self.x += modifier[0] * GAMESPEED * MOVESPEED * 2
                    self.y += modifier[1] * GAMESPEED * MOVESPEED * 2

                # Hurt self if self is moving quickly enough.
                if speed > 2:
                    # Inflict damage based on how quickly self is moving.
                    self.hp -= speed * 3

                    # Stun self based on  how quickly self is moving.
                    self.stun = speed * 60

                    # Create a death animation if self is dead.
                    if self.hp <= 0:
                        self.deathAnimation = [f'spearExplosion{i}.png' for i in range(1, 8) for j in range(20)]

    def moveWithoutWallCollision(self, *args):
        """self.moveWithoutWallCollision makes self move based on self.hr and self.vr without keeping self within
        boundaries or out of objects."""
        speedModifier = GAMESPEED * MOVESPEED * self.speed
        xMovement = self.hr * speedModifier
        yMovement = self.vr * speedModifier
        self.x += xMovement
        self.y += yMovement
        self.hitbox.move(xMovement, yMovement)
        self.place.centerx = self.x
        self.place.centery = self.y
        self.hitbox.getEnds()

    def moveNormally(self, *args):
        """Make self move and stay in boundaries. Return True if self hit the boundaries. Otherwise, return False."""

        # Make self move.
        self.moveWithoutWallCollision()

        # wallCollision defaults to False.
        wallCollision = False

        # If self is out of boundaries, put self back in the boundaries and set wallCollision to True.
        if self.hitbox.left < self.leftXBoundary:
            self.hitbox.move(self.leftXBoundary - self.hitbox.left, 0)
            self.place.left = self.leftXBoundary
            self.x = self.place.centerx
            wallCollision = True

        elif self.hitbox.right > self.rightXBoundary:
            self.hitbox.move(self.rightXBoundary - self.hitbox.right, 0)
            self.place.right = self.rightXBoundary
            self.x = self.place.centerx
            wallCollision = True

        if self.hitbox.top < self.yBoundary:
            self.place.y += self.yBoundary - self.hitbox.top
            self.hitbox.move(0, self.yBoundary - self.hitbox.top)
            self.y = self.place.centery
            wallCollision = True

        elif self.hitbox.bottom > self.bottomYBoundary:
            self.hitbox.move(0, self.bottomYBoundary - self.hitbox.bottom)
            self.place.bottom = self.bottomYBoundary
            self.y = self.place.centery
            wallCollision = True

        # If self hit the boundaries, return True. Otherwise, return False.
        return wallCollision

    def actAsFlamingRobot(self, target, *args):
        """This function should be used by flaming robots on each turn of theirs."""

        # Reduce cooldowns.
        self.accelerationCooldown -= GAMESPEED
        self.fireCooldown -= GAMESPEED

        # If needed, make self switch directions and set a cooldown until self switches directions again.
        if self.accelerationCooldown <= 0:
            self.setMovementNearTarget(target, 1.2, 30)
            self.accelerationCooldown = 300

        # If needed, make self create a fire and set a cooldown until self creates another fire.
        if self.fireCooldown <= 0:
            self.newBullets.append(bullet(0, 0, 26, 'flamingRobotFireTrail.png', self.x, self.y))
            self.fireCooldown = 100

        # Make self move, and switch directions if self collided with a wall this time.
        if self.moveNormally():
            self.setMovementNearTarget(target, 1.2, 30)
            self.accelerationCooldown = 300

    def actAsRobotBodyguard(self, target, *args):
        """This function should be used by robot bodyguards on each turn of theirs."""

        if self.mode == 'chasing':
            # Move straight to the player.
            self.setMovementToTarget(target, 0.9)
            self.moveNormally()

        else:
            # Reduce the cooldown for self firing.
            self.fireCooldown -= GAMESPEED

            # If self is ready to fire, make self fire and set a cooldown until self can fire again.
            if self.fireCooldown <= 0:
                self.basicStraightShot(2.1, 'brokenTurretFireball.png', 26, target)
                self.fireCooldown = 90

        self.modeDuration -= GAMESPEED

        # Switch self.mode and set a cooldown until self's mode changes again.
        if self.modeDuration <= 0:
            if self.mode == 'chasing':
                self.mode = 'firing'
                self.modeDuration = 1000

            else:
                self.mode = 'chasing'
                self.modeDuration = random.randint(2000, 4000)

    def actAsAntlionLarva(self, target, *args):
        """This function should be used by antlion larvae on each turn of theirs."""

        # Rotate to face the player.
        self.angle = getRadians(target.x - self.x, self.y - target.y)

        # Move towards the player.
        self.setMovementToTarget(target, 0.6)
        self.moveNormally()

        # Progress self's animation.
        self.progressAnimation()

    def actAsDesertCaveExplosiveFoe(self, target, *args):
        """This function should be used by desert cave explosive foes on each turn of theirs."""

        # Reduce self.duration.
        self.duration -= GAMESPEED

        # Self moves at an angle of self.angle.
        # Calculate how much self.angle would have to increase or decrease for self to move directly towards the player.
        angleIncNeeded = 2 * math.pi - (self.angle - getRadians(target.x - self.x, self.y - target.y)) % (2 * math.pi)
        angleDecNeeded = (self.angle - getRadians(target.x - self.x, self.y - target.y)) % (2 * math.pi)

        # Rotate towards the player.
        if angleIncNeeded > angleDecNeeded:
            self.angle -= 1 / 20

        else:
            self.angle += 1 / 20

        # Set self.hr and self.vr. Self should shake a bit if self.duration is low enough.
        self.hr = math.cos(self.angle) * 2
        self.vr = math.sin(self.angle) * 2

        if self.duration <= 400:
            self.hr += random.randint(-1, 1)
            self.vr += random.randint(-1, 1)

        # Make self move. If self hits a wall, set self.angle to be the direction to the player.
        if self.moveNormally():
            self.angle = getRadians(target.x - self.x, self.y - target.y)

        # If self.duration <= 0, make self create a fire and die.
        if self.duration <= 0:
            self.newBullets.append(bullet(0, 0, 65, 'aLargerFire.png', self.x, self.y,
                                          dissappearsAtEdges=0, piercing=float('inf')))
            self.hp = 0

    def actAsDesertCaveSpittingGrub(self, target, *args):
        """This function should be used by desert cave spitting grubs on each turn of theirs."""

        # Decrease the time until self fires.
        self.fireCooldown -= GAMESPEED

        # If self.fireCooldown <= 0, make self fire at the player, and set a cooldown until self fires again.
        if self.fireCooldown <= 0:
            self.basicStraightShot(1.5, 'brokenTurretFireball.png', 15, target)
            self.fireCooldown = 500

    def actAsDesertCaveJellyfish(self, target, *args):
        """This function should be used by desert cave jellyfish on each turn of theirs."""

        # Reduce self.fireCooldown.
        self.fireCooldown -= GAMESPEED

        # Reduce self.momentum, effectively slowing self down.
        self.momentum -= 0.005 * GAMESPEED

        # Progress self's animation.
        self.progressAnimation()

        # Make self move at an angle of self.angle.
        # The speed at which self moves should be proportional to self.momentum.
        self.hr = math.cos(self.angle) * self.momentum * 3
        self.vr = math.sin(self.angle) * self.momentum * 3

        # Make self move. If self hits a wall, set self.fireCooldown to 0.
        if self.moveNormally():
            self.fireCooldown = 0

        # If self.fireCooldown <= 0, make self start dashing to the player, and set self.fireCooldown.
        if self.fireCooldown <= 0:
            self.angle = getRadians(target.x - self.x, self.y - target.y)
            self.momentum = 1
            self.fireCooldown = 200

    def actAsDesertCaveLargeFly(self, target, *args):
        """This function should be used by desert cave large flies on each turn of theirs."""

        # Reduce self.fireCooldown, and progress self's animation.
        self.fireCooldown -= GAMESPEED
        self.progressAnimation()

        # If self.fireCooldown <= 0, enact the proper procedure.
        if self.fireCooldown <= 0:
            # Set self.fireCooldown.
            self.fireCooldown = 500

            # Self can have one assistant right above self, one right to the left, and one right to the right.
            # If there is space for an assistant, create one where there is space.
            if self.summonsAsDesertCaveLargeFly['top'] is None or self.summonsAsDesertCaveLargeFly['top'].hp <= 0:
                self.newFoes.append(foe('desertCaveSmallFly', self.x, self.y, self.room,
                                        unusualTarget=self.unusualTarget, vr=-0.3))
                self.summonsAsDesertCaveLargeFly['top'] = self.newFoes[-1]

            elif self.summonsAsDesertCaveLargeFly['left'] is None or self.summonsAsDesertCaveLargeFly['left'].hp <= 0:
                self.newFoes.append(foe('desertCaveSmallFly', self.x, self.y, self.room,
                                        unusualTarget=self.unusualTarget, hr=-0.3))
                self.summonsAsDesertCaveLargeFly['left'] = self.newFoes[-1]

            elif self.summonsAsDesertCaveLargeFly['right'] is None or self.summonsAsDesertCaveLargeFly['right'].hp <= 0:
                self.newFoes.append(foe('desertCaveSmallFly', self.x, self.y, self.room,
                                        unusualTarget=self.unusualTarget, hr=0.3))
                self.summonsAsDesertCaveLargeFly['right'] = self.newFoes[-1]

            self.summons = [value for value in self.summonsAsDesertCaveLargeFly.values() if value is not None and \
                            value.hp > 0]

    def actAsDesertCaveSmallFly(self, target, *args):
        """This function should be used by desert cave small flies on each turn of theirs."""

        # Reduce self.fireCooldown, and increase self.currentDuration.
        self.fireCooldown -= GAMESPEED
        self.currentDuration += GAMESPEED

        # Progress self's animation.
        self.progressAnimation()

        # If self.currentDuration is low enough, move. self.hr and self.vr should have been given as keyword arguments
        # when self was created.
        if self.currentDuration < 200:
            self.moveWithoutWallCollision()

        # If self.fireCooldown <= 0, fire towards the target and set self.fireCooldown.
        if self.fireCooldown <= 0:
            self.basicStraightShot(4, 'brokenTurretFireball.png', 3 if type(target) is foe else 60,
                                   target, unusualTargets=[self.unusualTarget])
            self.fireCooldown = 200

    def setMovementInSemicircleTowardsTarget(self, target, radius):
        """self.setMovementInSemicircleTowardsTarget(x, y) sets self.deltaTSign and sets self.movementCode so that
        repeatedly modifying self.t by a number of sign self.deltaTSign and calling exec(self.movementCode) causes
        self to move along a circle with radius y such that the point across self's coordinate from the radius of the
        circle, along with self's coordinate, forms line that has x's current coordinate."""

        path = getPath(radius * 2, (self.x, self.y), (target.x, target.y))
        destinationPoint = (self.x + path[0], self.y + path[1])
        self.t = -getRadians((self.x - destinationPoint[0]), (self.y - destinationPoint[1]))
        self.movementCode = (f'self.x, self.y = {radius} * math.cos(self.t) + (self.x + {destinationPoint[0]}) / 2 '
                             f'+ {self.x - (radius * math.cos(self.t) + (self.x + destinationPoint[0]) / 2)}, '
                             f'{radius} * math.sin(self.t) + (self.y + {destinationPoint[1]}) / 2 + '
                             f'{self.y - (radius * math.sin(self.t) + (self.y + destinationPoint[1]) / 2)}')
        self.deltaTSign = 1 if (self.y > height / 2 and self.x < target.x) or \
                               (self.y < height / 2 and self.x > target.x) else -1

    def actAsDesertCaveMoth(self, target, room, *args):
        """This function should be used by desert cave moths on each turn of theirs."""

        # Reduce cooldowns.
        self.fireCooldown -= GAMESPEED
        self.altFireCooldown -= GAMESPEED

        # Progress self.animation.
        self.progressAnimation()

        # Once self should move, move self.
        exec(self.movementCode)

        # Update self.t. self.t will be used to calculate self.x and self.y.
        self.t += math.pi / 600 * self.deltaTSign * GAMESPEED

        # Make self turn around if it hits an object.
        for thing in room.environmentObjects:
            if thing.hitbox.checkCollision(self.hitbox):
                self.deltaTSign *= -1

                while thing.hitbox.checkCollision(self.hitbox):
                    self.t += math.pi / 600 * self.deltaTSign * GAMESPEED
                    exec(self.movementCode)
                    self.hitbox = copy.deepcopy(self.hitboxOnSelf)
                    self.hitbox.move(self.x, self.y)

        # If self.fireCooldown <= 0, fire a cluster of projectiles and set self.fireCooldown.
        if self.fireCooldown <= 0:
            self.basicClusterShot(3, 30, target, 4, 'desertCaveMothProjectile1.png',
                                 50, unusualTargets=[self.unusualTarget],
                                 animation=[f'desertCaveMothProjectile{i}.png' for i in [1, 2] for j in range(15)])
            self.fireCooldown = random.randint(30, 600)

        # If self.altFireCooldown <= 0, enact the proper procedure.
        elif self.altFireCooldown <= 0:
            # Set self.movement code so that self will move in a semicircular motion.
            self.setMovementInSemicircleTowardsTarget(target, width / 20)

            # Set self.altFireCooldown.
            self.altFireCooldown = 600

    def actAsDesertCaveSummoner(self, target, *args):
        """This function should be used by desert cave summoners on each turn of theirs."""

        # Reduce cooldowns.
        self.fireCooldown -= GAMESPEED
        self.altFireCooldown -= GAMESPEED
        self.thirdFireCooldown -= GAMESPEED

        # Progress self's animation.
        self.progressAnimation()

        # If self.fireCooldown <= 0, summon a desert cave explosive foe near self, and set self.fireCooldown.
        if self.fireCooldown <= 0:
            self.newFoes.append(foe('desertCaveExplosiveFoe',
                                    self.x + random.randint(-int(width / 10), int(width / 10)),
                                    self.y + random.randint(-int(height / 10), int(height / 10)), self.room,
                                    angle=getRadians(target.x - self.x, self.y - target.y), spawnDelay=250))

            self.fireCooldown = 1500

        # If self.altFireCooldown <= 0, fire a group of projectiles aimed near to the player,
        # and set self.altFireCooldown.
        elif self.altFireCooldown <= 0:
            self.basicSpreadShot(7, math.pi * 2 / 3, target, 1.2,
                                 'bouncySplittingProjectileFromWatchdog.png', 45)
            self.altFireCooldown = 1500

        # If self.thirdFireCooldown <= 0, teleport to a random location, and set self.thirdFireCooldown.
        elif self.thirdFireCooldown <= 0:
            self.teleportRandomly(250)
            self.thirdFireCooldown = 1500

    def actAsDesertCaveSpider(self, target, *args):
        """This function should be used by desert cave spiders on each turn of theirs."""

        # Reduce cooldowns.
        self.fireCooldown -= GAMESPEED
        self.altFireCooldown -= GAMESPEED

        # Move. If self hits a wall, assign 0 to self.altFireCooldown. This will make self stop moving and fire.
        if self.moveNormally():
            self.altFireCooldown = 0

        # If self.fireCooldown <= 0, set self's movement to be headed near the player, and set self's cooldowns.
        if self.fireCooldown <= 0:
            self.setMovementNearTarget(target, 2.5, 30)

            # self.fireCooldown will be infinite until self.altFireCooldown <= 0.
            self.fireCooldown = float('inf')
            self.altFireCooldown = random.randint(25, 175)

        # If self.altFireCooldown <= 0, stop self's movement, set self's cooldowns, and fire a group of projectiles
        # headed near the player.
        elif self.altFireCooldown <= 0:
            self.hr = 0
            self.vr = 0

            # self.unusualTarget may be a large fly.
            self.basicSpreadShot(3, math.pi / 6, target, 3, 'spiderProjectile1.png', 60, 
                                 animation=[f'spiderProjectile{i}.png' for i in [1, 2] for j in range(30)],
                                 unusualTargets=[self.unusualTarget] + list(self.unusualTarget.summons if \
                                                                                self.unusualTarget is not None else []))

            # self.altFireCooldown will be infinite until self.fireCooldown <= 0.
            self.altFireCooldown = float('inf')
            self.fireCooldown = random.randint(15, 150)

    def actAsDesertCaveFlyMiniboss(self, target, *args):
        """This function should be used by the desert cave fly miniboss on each of its turns."""

        # Reduce cooldowns.
        self.fireCooldown -= GAMESPEED
        self.altFireCooldown -= GAMESPEED
        self.thirdFireCooldown -= GAMESPEED
        self.fourthFireCooldown -= GAMESPEED

        # Progress self's animation.
        self.progressAnimation()

        # Define a class, point, to hold attriubtes called x and y. The point class lets self more easily target
        # projectiles at points other than the player's center.
        class point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        # If self.altFireCooldown <= 0, enact the proper procedure.
        if self.altFireCooldown <= 0:
            # Set self.vr to 0. It is important to do so so that self stops moving up at the end of the slam attack.
            self.vr = 0

            # Decrease self.summonCooldown.
            self.summonCooldown -= 1

            # Set self.fireCooldown to 0.
            self.fireCooldown = 0

            # Modify self.mode.
            if self.mode == 'moving':
                self.altFireCooldown = 1199

                if self.summonCooldown <= 0:
                    self.mode = 'summoning'
                    self.summonsNext = False
                    self.summonCooldown = 8

                else:
                    self.mode = random.choice(['slam', 'laser', 'spit'])
                    self.summonsNext = True

            else:
                self.altFireCooldown = 299
                self.mode = 'moving'

        # Enact the proper procedure based on self.mode.
        if self.mode == 'moving':
            # Set self.x and self.y.
            exec(self.movementCode)

            # Modify self.t.
            self.t += math.pi / 300 * self.deltaTSign * GAMESPEED

            # If self.fireCooldown <= 0, set self.movementCode and self.fireCooldown.
            if self.fireCooldown <= 0:
                self.setMovementInSemicircleTowardsTarget(target, width / 20)
                self.fireCooldown = 300

        elif self.mode == 'slam':
            # Make self move. Self may move up and down if self.mode == 'slam'.
            self.moveNormally()

            # If self.fireCooldown <= 0, enact the proper procedure.
            if self.fireCooldown <= 0:
                # Set self.animation.
                self.animation = [f'desertCaveFlyMinibossSlam{i}.png' for i in range(1, 26) for j in range(15)]

                # Create projectiles that will wait for many frames to appear, move, or check collision.
                self.basicSpreadShot(25, math.pi * 2, target, 5,
                                     'desertCaveFlyMinibossLargeProjectile1.png', 60,
                                     animation=[f'desertCaveFlyMinibossLargeProjectile{i}.png' for i in \
                                                range(1, 6) for j in range(15)], delay=165,
                                     delayedSprite='invisiblePixels.png', center=(self.x, self.y + height / 15))

                # Set self.fireCooldown and self.vr.
                self.fireCooldown = 400
                self.vr = 0

            # Determine self.vr based on self.fireCooldown.
            if self.fireCooldown > 250:
                self.vr = 0

            elif self.fireCooldown > 220:
                self.vr = 1

            elif self.fireCooldown > 115:
                self.vr = 0

            elif self.fireCooldown > 25:
                self.vr = -5 / 21

        elif self.mode == 'laser':
            if self.fireCooldown <= 0:
                # Set self.animation.
                self.animation = [f'desertCaveFlyMinibossLaser{i}.png' for i in range(1, 11) for j in range(15)] + \
                                 ['desertCaveFlyMinibossLaser9.png'] * 150

                # Fire a laser that will wait for many frames before appearing or checking collision.
                angle = getRadians(target.x - self.x, target.y - self.y)
                self.fireLaserToAngle(angle, 'desertCaveFlyMinibossLaserProjectile1.png', 60,
                                      animation=[f'desertCaveFlyMinibossLaserProjectile{i}.png' for i in range(1, 4) \
                                                 for j in range(30)], delay=120,
                                      linger=165, delaysprite='invisiblePixels.png')

                # Set self.fireCooldown.
                self.fireCooldown = 300

        elif self.mode == 'summoning':
            if self.fireCooldown <= 0:
                self.fireCooldown = float('inf')
                self.thirdFireCooldown = 120
                self.animation = [f'desertCaveFlyMinibossSummon{i}.png' for i in range(1, 10) for j in range(30)]

            if self.thirdFireCooldown <= 0:
                self.thirdFireCooldown = float('inf')

                # Summon two moths near self.
                for i in range(2):
                    self.newFoes.append(foe('desertCaveMoth', self.x + random.randint(-int(width / 10),
                                                                                      int(width / 10)),
                                            self.y + random.randint(-int(height / 10), int(height / 10)), self.room,
                                            spawnDelay=100))

                # Summon six flies near self.
                for i in range(6):
                    self.newFoes.append(foe('desertCaveSmallFly', self.x + random.randint(-int(width / 10),
                                                                                          int(width / 10)),
                                            self.y + random.randint(-int(height / 10), int(height / 10)), self.room,
                                            spawnDelay=100))

        elif self.mode == 'spit':
            # Create a point to target that is directly below self.
            pointUsed = point(self.x, self.y + 1)

            if self.fireCooldown <= 0:
                self.animation = [f'desertCaveFlyMinibossSpit{i}.png' for i in range(1, 19) for j in range(66)]
                self.fireCooldown = 1200
                self.thirdFireCooldown = 396

            if self.thirdFireCooldown <= 0:
                # Fire two projectiles that, with self, form an angle that a vertical line through self.x bisects.
                self.basicSpreadShot(2, (self.fireCooldown - 804) * math.pi / 201,
                                     pointUsed, 6, 'desertCaveFlyMinibossLargeProjectile1.png', 60,
                                     animation=[f'desertCaveFlyMinibossLargeProjectile{i}.png' for i in range(1, 6) \
                                                for j in range(60)])

                # Set self.thirdFireCooldown.
                self.thirdFireCooldown = 15

    def basicSpreadShot(self, qty, totalAngle, target, speed, sprite, damage, center=None, hitbox=None, **kwargs):
        """self.basicSpreadShot(a, b, c, d, e, f, g, h, i, j) fires a projectiles that have sprite e,
        damage f, animation g, delay h, delayedSprite i, and center j and move at speed d where the outer projectiles
        form an angle, which is bisected by a line from self to c, of b radians"""
        indivisualAngle = totalAngle / (qty - 1)
        radians = getRadians(target.x - self.x, self.y - target.y)

        if center is None:
            center = (self.x, self.y)

        for i in range(qty):
            angle = radians - totalAngle / 2 + indivisualAngle * i

            # Fire a projectile. I use copy.deepcopy so that changes to one projectile's hitbox do not modify the
            # other projectiles' hitboxes.
            self.newBullets.append(bullet(math.cos(angle) * speed, math.sin(angle) * speed,
                                              damage, sprite, center[0], center[1],
                                          hitboxOnProjectile=copy.deepcopy(hitbox), **kwargs))

        pygame.display.flip()

    def basicClusterShot(self, qty, maxAngleInDegrees, target, speed, sprite, damage, **kwargs):
        """self.basicClusterShot(a, b, c, d, e, f, g) fires projectiles that have sprite e,
        damage f, and animation g and move at speed d where the projectiles are fired at an angle that is within b / 2
        degrees of the angle from self to c."""
        angleToPro = -getRadians(target.x - self.x, target.y - self.y)

        for i in range(qty):
            angle = angleToPro + random.randint(int(-maxAngleInDegrees),
                                                int(maxAngleInDegrees)) * math.pi / 360
            # Fire a projectile.
            self.newBullets.append(bullet(speed * math.cos(angle), speed * math.sin(angle), damage, sprite, self.x,
                                          self.y, **kwargs))

    def basicStraightShot(self, speed, sprite, damage, target, **kwargs):
        """self.basicStraightShot(a, b, c, d) fires a projectile that has sprite b and
        damage c, moves at speed a, and moves in a line from self to d."""
        path = getPath(speed, (self.x, self.y), (target.x, target.y))
        self.newBullets.append(bullet(path[0], path[1], damage, sprite, self.x, self.y, **kwargs))

    def basicRandomShot(self, speed, sprite, damage, **kwargs):
        """Fires a projectile in a random direction."""
        angle = random.randint(0, 360) * math.pi / 180
        self.newBullets.append(bullet(speed * math.cos(angle), speed * math.sin(angle), damage, sprite, self.x, self.y,
                                      **kwargs))

    def fireBouncySplittingProjectile(self, target, speed, damage, sprite, splitBulletsQty, splitProjectileSprite,
                                      hitboxForFragments=None, **kwargs):
        """Fires a bouncy projectile that, when destroyed, splits into a ring of projectiles that move outward."""
        path = getPath(speed, (self.x, self.y), (target.x, target.y))
        endEffect = f'for i in range({splitBulletsQty}): ' \
                    f'enemyBullets.append(bullet(1.5 * math.cos(i * 2 * math.pi / {splitBulletsQty}), ' \
                    f'1.5 * math.sin(i * 2 * math.pi / {splitBulletsQty}),' \
                    f' 26, "{splitProjectileSprite}", projectile.x, projectile.y, dissappearsAtEdges=0, ' \
                    f'hitboxOnProjectile=copy.deepcopy(projectile.hitboxForFragments)))'
        self.newBullets.append(bullet(path[0], path[1], damage, sprite, self.x, self.y, endEffect=endEffect, bounces=1,
                                      dissappearsAtEdges=0, hitboxForFragments=hitboxForFragments, **kwargs))

    def setMovementToTarget(self, target, speed):
        """Sets self's hr and vr so that self.moveNormally causes self to move straight towards the target's
        current coordinate."""
        path = getPath(speed, (self.x, self.y), (target.x, target.y))
        self.hr = path[0]
        self.vr = path[1]

    def setMovementNearTarget(self, target, speed, variation):
        """Sets self's hr and vr so that self.moveNormally causes self to move nearly straight towards the target's
        current coordinate."""
        path = getPartiallyRandomPath(speed, (self.x, self.y), (target.x, target.y), variation)
        self.hr = path[0]
        self.vr = path[1]

    def setMovementPredictively(self, target, speed, *args):
        """Sets self's hr and vr so that self.moveNormally causes self to move towards where the target is currently
        going."""
        path = self.estimatePredictivePath(target, speed)
        self.hr = path[0]
        self.vr = path[1]

    def fireBasicSemirandomLaserProjectile(self, target, angleVariation, sprite, damage, **kwargs):
        """Fires a laser at roughly the angle from self to the target."""
        radians = getRadians(target.x - self.x, target.y - self.y) + \
                  random.randint(-10, 10) * angleVariation / 20
        offset = [math.cos(radians) * diagonal / 2, -math.sin(radians) * diagonal / 2]
        self.newBullets.append(bullet(0, 0, damage, sprite, self.x + offset[0], self.y + offset[1],
                                      rotation=radians * 180 / math.pi, piercing=float('inf'), **kwargs))
        return radians

    def fireLaserToAngle(self, angle, sprite, damage, delaysprite='invisiblePixels.png', **kwargs):
        """Fires a laser to the specified angle."""
        offset = [math.cos(angle) * diagonal / 2, -math.sin(angle) * diagonal / 2]
        self.newBullets += [bullet(0, 0, damage, sprite, self.x + offset[0], self.y + offset[1],
                                   rotation=angle * 180 / math.pi, piercing=float('inf'),
                                   delayedSprite=delaysprite, **kwargs)]

    def checkLineOfSight(self, target, room):
        """Returns True if target is in self's line of sight else false."""
        angle = getRadians((target.x - self.x), (target.y - self.y))

        # Add an invisible laser to self.newBullets
        self.fireLaserToAngle(angle, 'invisibleLaser.png', 0, linger=0)

        # Remove the laser so that it is not added to enemyBullets in the main file, but store the laser in a variable.
        laser = self.newBullets.pop(-1)

        # Return False if the laser hits an environmental object that is nearer to self than target is.
        for i in room.environmentObjects:
            if laser.hitbox.checkCollision(i.hitbox) and \
                    pointDistance((self.x, self.y), (i.hitbox.centerx, i.hitbox.centery)) < \
                    pointDistance((self.x, self.y), (target.hitbox.centerx, target.hitbox.centery)):
                return False

        # Default to returning True.
        return True

    def fireLaserWithWarning(self, angle, sprite, damage, warningLinger, laserLinger, laserDelay, animation=None):
        """Fire a harmful laser with delay, and fire a harmless laser to show where the harmful laser will be."""
        self.fireLaserToAngle(angle, sprite, 0, animation=animation, linger=warningLinger,
                              checksCollisionWhen='False')
        self.fireLaserToAngle(angle, sprite, damage, animation=animation, linger=laserLinger, delay=laserDelay,
                              delaysprite='invisiblePixels.png')

    def actAsTougherWatchdogNotEnraged(self, target, *args):
        """This function should be used by the tougher ship miniboss on each of its turns when the
        hellhound is alive."""
        
        # Reduce cooldowns.
        self.modeDuration -= GAMESPEED
        self.fireCooldown -= GAMESPEED
        self.altFireCooldown -= GAMESPEED
        self.pause -= GAMESPEED
        
        # Progress self's animation.
        self.progressAnimation()

        # If self.pause <= 0, enact the proper procedure.
        if self.pause <= 0:

            # Enact the proper procedure based on self.mode.
            match self.mode:
                case 'standard':
                    # Reduce self.standardModeDuration.
                    self.standardModeDuration -= GAMESPEED

                    # Enact the proper procedure based on self.standardMode.
                    match self.standardMode:
                        case 'randomMovement':
                            # Reduce self.accelerationCooldown.
                            self.accelerationCooldown -= GAMESPEED

                            # Move. If self hits a wall, assign 0 t0 self.accelerationCooldown.
                            if self.moveNormally():
                                self.accelerationCooldown = 0

                            # If self.accelerationCooldown <= 0, set self.hr and self.vr so that self moves nearly
                            # straight towards the target and set self.accelerationCooldown.
                            if self.accelerationCooldown <= 0:
                                self.setMovementNearTarget(target, 0.6, 57)
                                self.accelerationCooldown = 100

                            # If self.fireCooldown <= 0, fire at the player and set self.fireCooldown.
                            if self.fireCooldown <= 0:
                                # Fire.
                                self.basicStraightShot(5, 'watchdogFireball.png', 26, target,
                                                       hitboxOnProjectile=copy.deepcopy(self.hitboxForFireballs))

                                # Set self.fireCooldown.
                                self.fireCooldown = 150
    
                        case 'spreadShotWithMovement':
                            # Move straight towards the target.
                            self.setMovementToTarget(target, 0.4)
                            self.moveNormally()

                            # If self.fireCooldown <= 0, fire a group of projectiles at the player and set
                            # self.fireCooldown.
                            if self.fireCooldown <= 0:
                                # Fire.
                                self.basicSpreadShot(5, math.pi / 3, target, 3,
                                                     'watchdogFireball.png', 26,
                                                     hitbox=copy.deepcopy(self.hitboxForFireballs))

                                # Set self.fireCooldown.
                                self.fireCooldown = 350
    
                        case 'spreadShotWithTeleportation':
                            # If self.fireCooldown <= 0, fire a group of projectiles at the player, set
                            # self.fireCooldown, and set self.altFireCooldown.
                            if self.fireCooldown <= 0:
                                # Fire.
                                self.basicSpreadShot(5, math.pi / 3, target, 3,
                                                     'watchdogFireball.png', 26,
                                                     hitbox=copy.deepcopy(self.hitboxForFireballs))
                                self.fireCooldown = 145
                                self.altFireCooldown = 100

                            # If self.altFireCooldown <= 0, teleport to a random place and set self.altFireCooldown.
                            elif self.altFireCooldown <= 0:
                                self.teleportRandomly(animation=watchdogTeleportAnimation)
                                self.altFireCooldown = 145

                    # If self.standardModeDuration <= 0, enact the proper procedure.
                    if self.standardModeDuration <= 0:
                        # Set self.standardModeDuration and self.pause.
                        self.standardModeDuration = 1100
                        self.pause = 200

                        # Based on self.standardMode, set self.standardMode and prepare self for self's next mode.
                        match self.standardMode:
                            case 'randomMovement':
                                self.standardMode = 'spreadShotWithMovement'

                            case 'spreadShotWithMovement':
                                self.standardMode = 'spreadShotWithTeleportation'
                                self.fireCooldown = 145
                                self.altFireCooldown = 195

                            case 'spreadShotWithTeleportation':
                                self.basicSpreadShot(5, math.pi / 3, target, 3,
                                                     'watchdogFireball.png',26,
                                                     hitbox=copy.deepcopy(self.hitboxForFireballs))
                                self.standardMode = 'randomMovement'

                case 'randomLasers':
                    if self.fireCooldown <= 0 and self.modeDuration >= 140:
                        # Fire two harmless lasers near the player and two delayed, harmful lasers in the same places
                        # as the harmless ones.
                        for i in range(2):
                            angle = getRadians(target.x - self.x, target.y - self.y) + random.randint(-20, 20) / 100
                            self.fireLaserWithWarning(angle, 'watchdogLaser1.png', 26, 100,
                                                      40, 124, animation=watchdogLaserAnim)
                            self.fireCooldown = 149
    
                case 'bouncySplittingProjectiles':
                    if self.fireCooldown <= 0:
                        # Fire a bouncy, splitting projectile.
                        self.fireBouncySplittingProjectile(target, 2, 26,
                                                           'watchdogLargeFireball.png', 15,
                                                           "watchdogFireballFragment.png",
                                                           hitboxForFragments= \
                                                               copy.deepcopy(self.hitboxForFireballFragments),
                                                           hitboxOnProjectile=copy.deepcopy(self.hitboxForBigFireballs))

                        # Set self.fireCooldown and self.altFireCooldown.
                        self.fireCooldown = 241
                        self.altFireCooldown = 50
    
                    elif self.altFireCooldown <= 0:
                        # Teleport to a random location and set self.altFireCooldown.
                        self.teleportRandomly(animation=watchdogTeleportAnimation)
                        self.altFireCooldown = 241
    
                case 'ringsOfProjectiles':
                    if self.fireCooldown <= 0:
                        # Fire a ring of projectiles and set self.fireCooldown.
                        self.basicSpreadShot(21, 2 * math.pi, target, 4, 'watchdogFireball.png',
                                             26, hitbox=self.hitboxForFireballs)
                        self.fireCooldown = 250
    
                case 'closingLasers':
                    if self.altFireCooldown <= 0:
                        # Set the angles that self should fire lasers at.
                        self.laserAngle = getRadians(target.x - self.x, target.y - self.y) - math.pi / 4
                        self.laser2Angle = getRadians(target.x - self.x, target.y - self.y) + math.pi / 4

                        # Fire two lasers.
                        self.fireLaserToAngle(self.laserAngle, 'watchdogLaser1.png', 26,
                                              animation=watchdogLaserAnim,
                                              checksCollisionWhen='False', linger=12)
                        self.fireLaserToAngle(self.laser2Angle, 'watchdogLaser1.png', 26,
                                              animation=watchdogLaserAnim,
                                              checksCollisionWhen='False', linger=12)

                        # Set self.fireCooldown and self.altFireCooldown.
                        self.fireCooldown = 75
                        self.altFireCooldown = 2400
    
                    if self.fireCooldown <= 0:
                        # Change the angles that the lasers will be fired at.
                        self.laserAngle += math.pi / 120
                        self.laser2Angle -= math.pi / 120

                        # Fire two lasers.
                        self.fireLaserToAngle(self.laserAngle, 'watchdogLaser1.png', 26,
                                              animation=watchdogLaserAnim,
                                              linger=16)
                        self.fireLaserToAngle(self.laser2Angle, 'watchdogLaser1.png', 26,
                                              animation=watchdogLaserAnim,
                                              linger=16)

                        # Set self.fireCooldown.
                        self.fireCooldown = 10
    
                case 'pillarsOfFire':
                    if self.fireCooldown <= 0:
                        # Create projectiles.
                        self.putProjectilesRandomlyInHypotheticalCells(5, 5,
                                                                       'watchdogFirePillar8.png', 26,
                                                                       417, height * 39 / 225,
                                                                       delayedAnimation=watchdogFirePillarAnim)

                        # Set self.fireCooldown.
                        self.fireCooldown = 667
    
                case 'pulledFires':
                    if self.fireCooldown <= 0:
                        self.fireCooldown = float('inf')
                        
                        # Create projectiles that will move towards self.
                        self.putProjectilesInHypotheticalCellsAndPull(6, 6,
                                                                      'watchdogPulledFireball.png', 26,
                                                                      550, height * 34 / 225, 400,
                                                                      hitbox=\
                                                                          copy.deepcopy(self.hitboxForPulledFireballs))

        if self.modeDuration <= 0:
            # Set cooldowns, set self.mode, and prepare for self's next attack.

            self.fireCooldown = 0
            self.altFireCooldown = 0
            self.pause = 200

            if self.mode == 'standard':
                self.modeDuration = 2400

                match random.choice([1, 6]):
                    case 0:
                        self.mode = 'turretSummoning'
    
                        # Set self.pause so that self will be idle while its turrets are around.
                        self.pause = 2400
    
                        # Create turrets.
                        self.newFoes += [foe('temporaryBrokenTurret', width * 3 / 4, height / 4, self.room,
                                             spawnDelay=100, duration=2300),
                                         foe('temporaryBrokenTurret', width * 3 / 4, height * 3 / 4,
                                             self.room, spawnDelay=100, duration=2300),
                                         foe('temporaryBrokenTurret', width / 4, height * 3 / 4, self.room,
                                             spawnDelay=100, duration=2300),
                                         foe('temporaryBrokenTurret', width / 4, height / 4, self.room,
                                             spawnDelay=100, duration=2300)]
    
                        # Teleport to the center of the display.
                        self.teleportToPoint(width / 2, height / 2, animation=watchdogTeleportAnimation)
    
                    case 1:
                        self.mode = 'bouncySplittingProjectiles'
                        self.fireCooldown = 251
                        self.altFireCooldown = 301
    
                    case 2:
                        self.mode = 'randomLasers'
                        self.fireCooldown = 200
                        self.altFireCooldown = 326
                        self.teleportToPoint(width / 2, height / 2, animation=watchdogTeleportAnimation)
    
                    case 3:
                        self.mode = 'ringsOfProjectiles'
    
                    case 4:
                        self.mode = 'closingLasers'
                        self.teleportToPoint(width / 2, height / 2, animation=watchdogTeleportAnimation)
                        self.fireCooldown = 200
                        self.altFireCooldown = 200
                        self.modeDuration = 700
    
                    case 5:
                        self.mode = 'pillarsOfFire'
    
                    case 6:
                        self.mode = 'pulledFires'
                        self.modeDuration = 1600

            else:
                self.mode = 'standard'
                self.modeDuration = 1100

        # If the hellhound is dead, set self.enraged so that self will act differently and set cooldowns.
        if self.dependentFoes[0].hp <= 0:
            self.enraged = True
            self.fireCooldown = 0
            self.altFireCooldown = 0
            self.modeDuration = 0

    def actAsTougherWatchdogEnraged(self, target, *args):
        """This function should be used by the tougher ship miniboss on each of its turns when the hellhound is dead.
        This function is not finished."""

        # TODO finish this function.
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
                                      animation=watchdogLaserAnim, checksCollisionWhen='False', linger=100)
                self.fireLaserToAngle(self.laser2Angle, 'watchdogLaser1.png', 0,
                                      animation=watchdogLaserAnim, checksCollisionWhen='False', linger=100)
            else:
                if self.fireCooldown <= 0:
                    self.laserAngle += math.pi / 70
                    self.laser2Angle -= math.pi / 70
                    self.fireLaserToAngle(self.laserAngle, 'watchdogLaser1.png', 26,
                                          animation=watchdogLaserAnim, linger=10)
                    self.fireLaserToAngle(self.laser2Angle, 'watchdogLaser1.png', 26,
                                          animation=watchdogLaserAnim, linger=10)
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
                                                              26, 750, delayedAnimation=watchdogFirePillarAnim)
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

    def actAsTougherWatchdog(self, target, *args):
        """This function should be used by the tougher ship miniboss on each of its turns."""

        # Use a different function based on self.enraged, which will be True if the hellhound is alive and False
        # otherwise.
        if self.enraged:
            self.actAsTougherWatchdogEnraged(target)

        else:
            self.actAsTougherWatchdogNotEnraged(target)

    def teleportToTarget(self, target, animation=None, spawnDelay=250):
        """Make self teleport to target's location."""

        if animation is not None:
            # Create a harmless projectile where self is before teleporting.
            self.newBullets.append(bullet(0, 0, 0, animation[0], self.x, self.y, animation=animation,
                                          linger=250, checksCollisionWhen='False'))

        # Teleport to target's location.
        self.x, self.y = target.x, target.y
        self.spawnDelay = spawnDelay
        self.place.centerx, self.place.centery = self.x, self.y
        self.hitbox = rect(self.place)

    def createRingOfSpiralingBullets(self, speed, radiusToTheta, qty, damage, sprite, x=None,
                                     y=None, **kwargs):
        """"""

        # By default, the projectiles should be created at self's location.
        if x is None:
            x = self.x

        if y is None:
            y = self.y

        thetaIncreaseRate = f'{speed} / sqrt(self.radius ** 2 + {radiusToTheta ** 2})'
        radiusIncreaseRate = f'{speed * radiusToTheta} / sqrt(self.radius ** 2 + {radiusToTheta ** 2})'

        # Create projectiles.
        for i in range(qty):
            self.newBullets.append(bullet(0, 0, damage, sprite, x, y,
                                          polarMovement=f'({radiusIncreaseRate}, {thetaIncreaseRate})',
                                          dissappearsAtEdges=0, theta=2 * i * math.pi / qty, **kwargs))

    def createStillBulletRandomlyInSpace(self, xMin, xMax, yMin, yMax, sprite, damage, linger, delay=250,
                                         **kwargs):
        """Create a still bullet in a random part of a specified area."""
        
        # Determine where the bullet should go.
        centerx = random.randint(int(xMin), int(xMax))
        centery = random.randint(int(yMin), int(yMax))
        
        # Create the bullet.
        self.newBullets.append(bullet(0, 0, damage, sprite, centerx, centery, linger=linger, delay=delay,
                                      dissappearsAtEdges=0, **kwargs))

    def putProjectilesRandomlyInHypotheticalCells(self, qtyPerRow, qtyPerColumn, sprite, damage, linger,
                                                                  topYBoundary, delay=250, hitbox=None, **kwargs):
        """Divide the room into cells and put a still projectile in each cell."""

        # Get a rectangle to fit the sprite.
        rectangleForSprite = IMAGES[sprite].get_rect()

        # Determine the minimum and maximum x and y coordinates where projectiles may appear.
        minX = self.leftXBoundary + rectangleForSprite.width / 2
        minY = topYBoundary + rectangleForSprite.height / 2

        # Determine the length and width of the area where projectiles may appear.
        totalWidth = self.rightXBoundary  - rectangleForSprite.width / 2 - minX
        totalHeight = self.bottomYBoundary - rectangleForSprite.height / 2 - minY

        # Get a list of the x boundaries and y boundaries of cells to divide the room.
        xBoundariesList = [minX + totalWidth * i / (qtyPerRow) for i in range(qtyPerRow + 1)]
        yBoundariesList = [minY + totalHeight * i / (qtyPerColumn) for i in range(qtyPerColumn + 1)]

        # Create a projectile in each cell.
        for i in range(qtyPerRow):
            for j in range(qtyPerColumn):
                self.createStillBulletRandomlyInSpace(xBoundariesList[i], xBoundariesList[i + 1], yBoundariesList[j],
                                                      yBoundariesList[j + 1], sprite, damage, linger, delay=delay,
                                                      hitboxOnProjectile=copy.deepcopy(hitbox), **kwargs)

    def putProjectilesInHypotheticalCellsAndPull(self, qtyPerRow, qtyPerColumn, sprite, damage, linger, topYBoundary,
                                                 timeToReachSelf, delayBeforePulling=150, delay=250, hitbox=None,
                                                 **kwargs):
        """Divide the room into cells and put a projectile in each cell. After a delay, each projectile will move
        towards self's current location."""

        # Create projectiles.
        self.putProjectilesRandomlyInHypotheticalCells(qtyPerRow, qtyPerColumn, sprite, damage, linger, topYBoundary,
                                                       delay=delay, hitbox=hitbox, **kwargs)

        # Determine how the projectiles will move.
        for i in range(qtyPerRow * qtyPerColumn):
            projectile = self.newBullets[-i]
            path = getPath(pointDistance((projectile.x, projectile.y), (self.x, self.y)) / timeToReachSelf,
                           (projectile.x, projectile.y), (self.x, self.y))
            projectile.movementByDuration = (f'[0, 0] if self.currentDuration <= {delayBeforePulling} else '
                                                      f'{path}')

    def pullProjectileTowardsSelf(self, projectile, speed):
        """Sets projectile's hr and vr so that projectile will move towards self's current location."""

        path = getPath(speed, (projectile.x, projectile.y), (self.x, self.y))
        (projectile.hr, projectile.vr) = path

    def fireAndPullProjectileInSpace(self, xMin, xMax, yMin, yMax, sprite, damage, speed, delayBeforePulling, delay=250,
                                     **kwargs):
        """Create a projectile that will move towards self in a random part of a specified area."""
        
        # Determine where to put the projectile.
        centerx = random.randint(xMin, xMax)
        centery = random.randint(yMin, yMax)
        
        # Determine how the projectile should move.
        path = getPath(speed, (centerx, centery), (self.x, self.y))
        movement = f'([0, 0] if self.currentDuration <= {delayBeforePulling} else [{path[0]}, {path[1]}])'
        
        # Create the projectile.
        self.newBullets.append(bullet(path[0], path[1], damage, sprite, centerx, centery, delay=delay, 
                                      durationBasedMovement=movement, **kwargs))

    def teleportRandomly(self, spawnDelay=250, animation=None):
        """Make self teleport to a random location."""
        
        if animation is not None:
            # Create a harmless projectile where self is before teleporting.
            self.newBullets.append(bullet(0, 0, 0, animation[0], self.x, self.y, animation=animation,
                                          linger=250))

        # Make self teleport.
        self.x = random.randint(int(self.leftXBoundary + self.place.width / 2),
                                int(self.rightXBoundary - self.place.width / 2))
        self.y = random.randint(int(self.yBoundary + self.place.height / 2),
                                int(self.bottomYBoundary - self.place.height / 2))
        self.spawnDelay = spawnDelay
        self.place.centerx, self.place.centery = self.x, self.y
        self.hitbox = rect(self.place)

    def teleportToPoint(self, x, y, animation=None, spawnDelay=250):
        # Make self teleport to a specified point.
        
        if animation is not None:
            # Create a harmless projectile where self is before teleporting.
            self.newBullets.append(bullet(0, 0, 0, animation[0], self.x, self.y, animation=animation,
                                          linger=spawnDelay))

        # Make self teleport.
        self.x, self.y = x, y
        self.spawnDelay = spawnDelay
        self.place.centerx, self.place.centery = self.x, self.y
        self.hitbox = rect(self.place)

    def teleportPredictively(self, target, animation=None, spawnDelay=250):
        """Make self teleport to where target is predicted to be when self reappears."""

        # Predict where target will be.
        destinationX = greater(lesser(target.x + target.hr * spawnDelay, width), 0)
        destinationY = greater(lesser(target.y + target.vr * spawnDelay, height), height * 0.17)
        
        # Teleport to where target is predicted to be.
        self.teleportToPoint(destinationX, destinationY, animation=animation, spawnDelay=spawnDelay)

    def actAsHellhound(self, target, *args):
        """This function should be used by the hellhound on each of its turns."""
        
        # Reduce cooldowns.
        self.modeDuration -= GAMESPEED
        self.fireCooldown -= GAMESPEED
        self.altFireCooldown -= GAMESPEED
        self.pause -= GAMESPEED
        
        # Set self.delaySprite because it will sometimes be changed right before self teleports.
        self.delaySprite = 'hellhoundFootstep.png'
        
        # Progress self's animation.
        self.progressAnimation()

        # If self.pause <= 0, perform the proper actions based on self.mode.
        if self.pause <= 0:
            match self.mode:
                case 'standard':
                    if pointDistance((self.x, self.y), (target.x, target.y)) > diagonal / 10:
                        # Make self move quickly to the target.
                        self.setMovementToTarget(target, 2.4)

                    else:
                        # Make self move to the target at a slower pace.
                        self.setMovementToTarget(target, 0.6)

                        # If self.fireCooldown <= 0, fire and set self.fireCooldown.
                        if self.fireCooldown <= 0:
                            self.basicStraightShot(1.6, 'hellhoundSlash.png', 26, target, linger=200)
                            self.fireCooldown = 250

                    # Move.
                    self.moveNormally()

                    # If self.altFireCooldown <= 0, teleport randomly and set self.altFireCooldown.
                    if self.altFireCooldown <= 0:
                        self.teleportRandomly(animation=hellhoundTeleportAnimation)
                        self.altFireCooldown = 1000

                case 'flamingRobot':
                    # Move. if self hits a wall, enact the proper procedure.
                    if self.moveNormally():
                        # Self cannot switch modes while self.dashing.
                        self.dashing = False

                        # If I didn't check if self.moveDuration > 0, self would be unable to switch modes again.
                        if self.modeDuration > 0:
                            # Set self's hr and vr so that self moves to the target's current location.
                            self.setMovementToTarget(target, 3)

                            # self.dashing should be set to one so that self cannot switch modes until hitting a wall again.
                            self.dashing = True

                            # Move.
                            self.moveNormally()

                    # If self.fireCooldown <= 0, fire a still projectile and set self.fireCooldown.
                    if self.fireCooldown <= 0:
                        self.newBullets.append(bullet(0, 0, 26, 'hellhoundFootstep.png', self.x,
                                                      self.y))

                        self.fireCooldown = 50

                case 'dashingAndFiring':
                    if self.fireCooldown <= 0:
                        # Fire a still projectile and set self.fireCooldown.
                        self.newBullets.append(bullet(0, 0, 26, 'hellhoundFootstep.png', self.x,
                                                      self.y))
                        self.fireCooldown = 40

                    if self.altFireCooldown <= 0:
                        # Fire two projectiles that move perpendicularly to self. Set self.altFireCooldown.
                        self.newBullets.append(bullet(-self.vr * 2, self.hr * 2, 26,
                                                      'watchdogFireball.png', self.x, self.y))
                        self.newBullets.append(bullet(self.vr * 2, -self.hr * 2, 26,
                                                      'watchdogFireball.png', self.x, self.y))
                        self.altFireCooldown = 40

                    # Move. If self hits a wall, enact the proper procedure.
                    if self.moveNormally():
                        # Fire a ring of projectiles.
                        self.basicSpreadShot(45, 2 * math.pi, target, 4, 'watchdogFireball.png',
                                             26)

                        # Set self.modeDuration so that self will immediately switch modes.
                        self.modeDuration = 0

                case 'dashingAndSwiping':
                    # The next block of code functions just like the first block of the case 'flamingRobot' block.
                    if self.moveNormally():
                        self.dashing = False

                        if self.modeDuration > 0:
                            self.dashing = True
                            self.setMovementToTarget(target, 3)

                    # If self.fireCooldown <= 0 and self is close enough to target, fire and set self.fireCooldown.
                    if pointDistance((self.x, self.y), (target.x, target.y)) < diagonal / 5 and \
                            self.fireCooldown <= 0:
                        self.basicStraightShot(2.5, 'hellhoundSlash.png', 26, target, linger=200)
                        self.fireCooldown = 250

                case 'hidingInFire':
                    # Move. If self hits a wall, set self.fireCooldown.
                    if self.moveNormally():
                        self.fireCooldown = 15

                    # If self.fireCooldown <= 0, enact the proper procedure.
                    if self.fireCooldown <= 0:
                        # Create 36 still projectiles.
                        self.putProjectilesRandomlyInHypotheticalCells(6, 6,
                                                                       'hellhoundDisguiseFire.png', 26,
                                                                       417, height * 4 / 25)

                        # Set self.delaySprite so that self will be invisible while delayed.
                        self.delaySprite = 'invisiblePixels.png'

                        # Teleport to a random location.
                        self.teleportRandomly(spawnDelay=417, animation=hellhoundTeleportAnimation)

                        # Create a projectile at self's location. This projectile will move in loops.
                        self.newBullets.append(bullet(0, 0, 26, 'hellhoundDisguiseFire.png',
                                                      self.x,
                                                      self.y, delay=250, linger=167,
                                                      durationBasedPlace=f'({self.x} + math.cos(self.currentDuration '
                                                                         f'/ 5) * 5,'
                                                      f'{self.y} + math.sin(self.currentDuration / 5) * 5)'))

                        # Set self.fireCooldown.
                        self.fireCooldown = 500

                        # Set self's movement predictively. Once self stops being delayed, it will dash at the player.
                        self.setMovementPredictively(target, 6)

                case 'dashingFromWalls':
                    # Move. If self hits a wall, enact the proper procedure.
                    # This block functions much like the case 'dashingAndSwiping' and case 'flamingRobot' blocks.
                    if self.moveNormally():
                        # This block functions much like the
                        self.dashing = False

                        if self.modeDuration > 0:
                            self.dashing = True

                            # Set self.pause.
                            self.pause = 75

                            # Set self's movement predictively so that self dashes at the player once self.pause <= 0.
                            self.setMovementPredictively(target, 15)

                            # Fire a laser to show where self will dash.
                            self.fireLaserToAngle(getRadians(self.hr, self.vr), 'watchdogLaser1.png', 0,
                                                  animation=watchdogLaserAnim, linger=75, checksCollisionWhen='False')
                        
        # If appropriate, teleport, switch modes and prepare act according to the new mode.
        if self.modeDuration <= 0 and not self.dashing:
            # Set self.fireCooldown and self.altFireCooldown.
            self.fireCooldown = 0
            self.altFireCooldown = 0
            
            # Teleport randomly.
            self.teleportRandomly(animation=hellhoundTeleportAnimation)

            if self.mode == 'standard':
                match random.randint(0, 4):
                    case 0:
                        self.mode = 'flamingRobot'
                        self.modeDuration = 2900
                        
                        # Begin dashing at the target.
                        self.dashing = True
                        self.setMovementToTarget(target, 2)
    
                    case 1:
                        self.mode = 'dashingAndFiring'
                        
                        # Self.modeDuration will be set to 0 once self hits a wall.
                        self.modeDuration = float('inf')
                        
                        # Begin dashing at the target.
                        self.setMovementToTarget(target, 2.5)
    
                    case 2:
                        self.mode = 'dashingAndSwiping'
                        self.modeDuration = 2900
                        
                        # Begin dashing at the target.
                        self.setMovementToTarget(target, 2.3)
                        self.dashing = True
    
                    case 3:
                        self.mode = 'hidingInFire'
                        self.modeDuration = 599
    
                    case 4:
                        self.mode = 'dashingFromWalls'
                        self.modeDuration = 2900
                        
                        # Begin dashing at the target.
                        self.dashing = True
                        self.setMovementToTarget(target, 3)

            else:
                self.mode = 'standard'
                self.modeDuration = 1450

    def actAsWatchdogMeleeSummon(self, target, *args):
        # TODO Delete this Function.
        self.setMovementToTarget(target, 0.3)
        self.moveNormally()

    def actAsWatchdogRangedSummon(self, target, *args):
        # TODO Delete this function.
        self.fireCooldown -= GAMESPEED

        if self.fireCooldown <= 0:
            path = getPath(0.5, (self.x, self.y), (target.x, target.y))
            self.newBullets.append(bullet(path[0], path[1], 26, 'brokenTurretFireball.png', self.x, self.y,
                                          linger=1800))
            self.fireCooldown = 1000

    def actAsShipMiniboss(self, target, *args):
        """This function should be used by the ship miniboss on each of its turns. This function is not finished."""

        # TODO finish this function.
        self.modeDuration -= GAMESPEED
        self.summonCooldown -= GAMESPEED

        if self.mode == 'chasing':
            self.setMovementToTarget(target, 2)
            self.moveNormally()

        elif self.mode == 'firingInSpread':
            self.fireCooldown -= GAMESPEED

            if self.fireCooldown <= 0:
                radians = getRadians(target.x - self.x, self.y - target.y)

                if self.hp > 250:
                    self.basicSpreadShot(random.randint(4, 5), random.randint(45, 75) * math.pi / 180,
                                         target, 4, 'brokenTurretFireball.png',
                                         26)

                    self.fireCooldown = random.randint(50, 100)

                else:
                    for i in range(32):
                        angle = radians + i * math.pi / 16
                        self.newBullets.append(bullet(5 * math.cos(angle),
                                                      5 * math.sin(angle),
                                                      26, 'brokenTurretFireball.png', self.x, self.y))

                    self.fireCooldown = 80

        elif self.mode == 'firing':
            self.fireCooldown -= GAMESPEED

            if self.fireCooldown <= 0:
                path = getPath(6, (self.x, self.y), (target.x, target.y))
                self.newBullets.append(bullet(path[0], path[1], 26, 'brokenTurretFireball.png', self.x,
                                              self.y,
                                              linger=400))
                self.fireCooldown = 20

        elif self.mode == 'hasSummons':
            if pointDistance((self.x, self.y), (width / 2, height / 2)) > height / 300:
                self.setMovementToTarget(target, 1)
                self.moveNormally()

            else:
                self.fireCooldown -= GAMESPEED

                if self.fireCooldown <= 0:
                    path = getPath(2, (self.x, self.y), (target.x, target.y))
                    self.newBullets.append(bullet(path[0], path[1], 26, 'brokenTurretFireball.png',
                                                  self.x, self.y))
                    self.fireCooldown = 600

        elif self.mode == 'flamingRobot':
            if self.moveNormally():
                self.dashing = False

                if self.modeDuration > 0:
                    self.setMovementToTarget(target, 3)
                    self.dashing = True
                    self.moveNormally()

            self.fireCooldown -= GAMESPEED

            if self.fireCooldown <= 0:
                self.newBullets.append(bullet(0, 0, 26, 'flamingRobotFireTrail.png', self.x,
                                              self.y))
                self.fireCooldown = 25

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
                    self.modeDuration = random.randint(300, 300)

                else:
                    self.mode = 'flamingRobot'
                    self.setMovementToTarget(target, 2)
                    self.dashing = True
                    self.moveNormally()
                    self.modeDuration = random.randint(4000, 6000)

            elif self.mode == 'hasSummons':
                self.mode = 'chasing'
                self.modeDuration = random.randint(300, 300)

            elif self.mode == 'flamingRobot':
                self.mode = 'chasing'
                self.modeDuration = random.randint(300, 300)

    def reduceDuration(self):
        """This function reduces self's remaining duration."""

        # Reduce self.duration.
        self.duration -= GAMESPEED

        # Set self.hp to 0 if needed.
        if self.duration < 0:
            self.hp = 0

    def createProjectilesThatMoveInwardsFromWalls(self, damage, sprite, qtyPerSide, speed, delay=100, **kwargs):
        """Creates projectiles that move to the opposite end of the room on each wall."""

        for i in range(qtyPerSide):
            self.newBullets.append(bullet(speed, 0, damage, sprite,
                                          0, height * i / (qtyPerSide - 1), delay=delay, **kwargs))
            self.newBullets.append(bullet(-speed, 0, damage, sprite,
                                          width, height * i / (qtyPerSide - 1), delay=delay, **kwargs))
            self.newBullets.append(bullet(0, speed, damage, sprite,
                                          width * i / (qtyPerSide - 1), 0, delay=delay, **kwargs))
            self.newBullets.append(bullet(0, -speed, damage, sprite,
                                          width * i / (qtyPerSide - 1), height, delay=delay, **kwargs))

    def giveProjectileHoming(self, projectile, minimumDistanceForHoming=float('inf')):
        """Makes a projectile move straight to the player if it gets close enough to the projectile."""

        projectile.conditionalEffects = {'pointDistance((projectile.x, projectile.y), '
                                                             f'(pro.x, pro.y)) < {minimumDistanceForHoming}':
                                                                 "(projectile.hr, projectile.vr) = "
                                                                 "tuple(getPath(sqrt(projectile.hr ** 2 + "
                                                                 "projectile.vr ** 2), (projectile.x, projectile.y), "
                                                                 "(pro.x, pro.y))); projectile.rotation = 0 if "
                                                                 "projectile.hr == projectile.vr == 0 else "
                                                                 "getDegrees(projectile.hr, projectile.vr)"}

    def teleportNearToTarget(self, target, xVariation, yVariation, spawnDelay=250, minX=None, maxX=None, minY=None,
                             maxY=None):
        """Teleport within a specified distance horizontally and vertically from target."""
        maxXDis = int(xVariation / 2)
        maxYDis = int(yVariation / 2)

        # minX, maxX, minY, and maxY should all have acceptable default values.
        minX = self.place.width / 2 if minX is None else minX
        maxX = width - self.place.width / 2 if maxX is None else maxX
        minY = self.yBoundary if minY is None else minY
        maxY = height - self.place.height / 2 if maxY is None else maxY

        # Determine where to go. Make sure not to go out of boundaries.
        destination = [lesser(greater(target.x + random.randint(-maxXDis, maxXDis),
                                      minX), maxX),
                       greater(lesser(target.y + random.randint(-maxYDis, maxYDis),
                                      minY), maxY)]

        # Teleport.
        self.teleportToPoint(destination[0], destination[1], spawnDelay=spawnDelay)

    def actAsScary(self, target, room, *args):
        """This function should be used by the scary on each of its turns."""

        # The next block is for a feature that is not implemented yet.
        if not self.acted:
            self.newBullets = [bullet(0, 0, 0, 'scaryDarkFilterPng.png', 0, 0,
                                      linger=float('inf'), checksCollisionWhen='False', firer=self, target=target,
                                      causeAndEffect={'projectile.firer.hp <= 0': 'projectile.linger = 0'},
                                      dissappearsAtEdges=False, piercing=float('inf'),
                                      durationBasedPlace='(self.target.x, self.target.y)')]
            self.newBullets = []
            self.acted = True

        # Progress self's animation.
        self.progressAnimation()

        # Reduce self's cooldowns.
        self.duration -= GAMESPEED
        self.fireCooldown -= GAMESPEED
        self.modeDuration -= GAMESPEED
        self.altFireCooldown -= GAMESPEED
        self.thirdFireCooldown -= GAMESPEED

        # If self.aggressive but self.mode is not one that should be used if self.aggressive, enact the proper
        # procedure. Self should only execute the following block once.
        if self.aggressive and self.mode in ['fireRandomly', 'search', 'grid', 'investigating']:
            self.mode = 'dashing'
            self.fireCooldown = 90
            self.modeDuration = 550
            self.animation = self.idleAnimation.copy()

            # Destroy the room's environmental objects. They will come back once the player dies.
            room.environmentObjects = []

            # Self will inflict damage on contact now.
            self.damage = target.maxHp * 0.3

        # Enact the proper procedure based on self.mode.
        match self.mode:
            case 'fireRandomly':
                if self.fireCooldown <= 0:
                    # Fire randomly. The projectile that self fires should make self move to the projectile's current
                    # location, set self.modeDuration, reduce the player's oxygen, set self.mode to
                    # 'investigating' if self.mode is not 'searching', increase self.duration, and set self.animation
                    # upon hitting the player.
                    self.basicRandomShot(3, 'spiderProjectile1.png', 0,
                                         firer=self,
                                         playerContactEffect="(projectile.firer.hr, projectile.firer.vr) = "
                                                             "tuple(getPath(2, (projectile.firer.x, "
                                                             "projectile.firer.y),"
                                                             "(projectile.x, projectile.y))); "
                                                             "projectile.firer.modeDuration = "
                                                             "pointDistance((projectile.firer.x, projectile.firer.y), "
                                                             "(projectile.x, projectile.y)) / 2 if "
                                                             "projectile.firer.mode"
                                                             " not in ['search', 'investigating'] else "
                                                             "projectile.firer.modeDuration; pro.oxygen -= 30;"
                                                             "projectile.firer.mode = 'investigating' if "
                                                             "projectile.firer.mode != 'searching' else 'searching';"
                                                             "projectile.firer.duration += 1000;"
                                                             "projectile.firer.animation = "
                                                             "projectile.firer.idleAnimation.copy() "
                                                             )

                    # Set self.fireCooldown.
                    self.fireCooldown = 10

                    # If self.duration is low enough, give the projectile that self last fired homing.
                    if self.duration <= 2690:
                        self.giveProjectileHoming(self.newBullets[-1], diagonal / 7)

            case 'search':
                # If self.fireCooldown <= 0 and the player is in self's sight, set self.aggressive and
                # self.modeDuration.
                if self.fireCooldown <= 0 and self.checkLineOfSight(target, room):
                    self.aggressive = True
                    
                    # Set self.modeDuration to 1 so that self cannot immediately teleport.
                    self.modeDuration = 1

            case 'grid':
                if self.fireCooldown <= 0:
                    # Create projectiles that move in from the walls. The projectile that self fires should make self 
                    # move to the projectile's current location, set self.modeDuration, reduce the player's oxygen, 
                    # set self.mode to 'investigating' if self.mode is not 'searching', increase self.duration, and set 
                    # self.animation upon hitting the player.
                    self.createProjectilesThatMoveInwardsFromWalls(0, 'spiderProjectile1.png',
                                                               random.randint(5, 10), 7, firer=self,
                                       playerContactEffect="(projectile.firer.hr, projectile.firer.vr) = "
                                                           "tuple(getPath(2, (projectile.firer.x, projectile.firer.y),"
                                                           "(projectile.x, projectile.y))); "
                                                           "projectile.firer.modeDuration = "
                                                           "pointDistance((projectile.firer.x, projectile.firer.y), "
                                                           "(projectile.x, projectile.y)) / 2 if projectile.firer.mode "
                                                           "not in ['search', 'investigating'] else "
                                                           "projectile.firer.modeDuration; pro.oxygen -= 30;"
                                                           "projectile.firer.mode = 'investigating' if "
                                                           "projectile.firer.mode != 'searching' else 'searching';"
                                                           "projectile.firer.duration += 1000;"
                                                           "projectile.firer.animation = "
                                                           "projectile.firer.idleAnimation.copy() ")

                    # Set self.fireCooldown.
                    self.fireCooldown = 120

            case 'investigating':
                # self.mode will only be 'investigating' in response to the player getting hit.
                # Move. If self hits a wall, set self.modeDuration to 0. Self.hr and self.vr should have been set by
                # the same exec function call that set self.mode to 'investigating'.
                if self.moveNormally():
                    self.modeDuration = 0

                # If self hits an environmental object, set self.modeDuration to 0.
                else:
                    for i in room.environmentObjects:
                        if i.hitbox.checkCollision(self.hitbox):
                            self.modeDuration = 0
                            break

            case 'dashing':
                if self.altFireCooldown <= 0:
                    # Teleport near to the player.
                    self.teleportNearToTarget(target, width / 4, height / 4, minX=width * 79 / 800,
                                              maxX=width * 721 / 800,
                                              minY=height * 78 / 225, maxY=height * 731 / 900, spawnDelay=110)

                    # Set self.delayFrame and self.delayAnimation.
                    self.delayFrame = 0
                    self.delayAnimation = self.fastTeleportAnimation.copy()

                    # Set cooldowns.
                    self.fireCooldown = 50
                    self.altFireCooldown = 100
                    self.thirdFireCooldown = 1

                elif self.thirdFireCooldown <= 0:
                    # Make self move predictively to the target.
                    self.setMovementPredictively(target, 15)

                    # Fire a laser to show where self will dash.
                    angle = getRadians(self.hr, self.vr)
                    self.fireLaserToAngle(angle, 'desertCaveFlyMinibossLaserProjectile1.png', 0,
                                          animation=[f'desertCaveFlyMinibossLaserProjectile{i}.png' for i in \
                                                     range(1, 4) for j in range(30)], linger=50,
                                          checksCollisionWhen='False')

                    # Set self.thirdFireCooldown so that self will wait until teleporting to execute this block again.
                    self.thirdFireCooldown = float('inf')

                elif self.fireCooldown <= 0:
                    # This block does not set self.fireCooldown.
                    # Move. Set self.altFireCooldown if self hits a wall.
                    if self.moveNormally():
                        self.altFireCooldown = 0

                    # If target is vulnerable and self is colliding with target, execute the next block.
                    if self.hitbox.checkCollision(target.hitbox) and target.invincibility <= 0:
                        # Reduce target's oxygen.
                        target.oxygen -= 30

                        # Hurt the target here to avoid unnecessary checks for collision.
                        target.hurt(0.3 * target.maxHp)

            case 'circling':
                if pointDistance((self.x, self.y), (target.x, target.y)) < diagonal / 6 and \
                        self.thirdFireCooldown <= 0:
                    # Self will circle around the player when self.thirdFireCooldown == float('inf').
                    # Set cooldowns.
                    self.thirdFireCooldown = float('inf')
                    self.altFireCooldown = 400
                    self.fireCooldown = 130

                    # Set self.hr and self.vr to 0 since they will be useless for now.
                    self.hr = self.vr = 0

                    # Get the angle from self to target so that self can start rotating around target without sudden
                    # movement.
                    self.theta = getRadians(target.x - self.x, target.y - self.y)

                if self.thirdFireCooldown == float('inf'):
                    # Increase the angle from target to self.
                    self.theta += math.pi / 50

                    # Set self.x and self.y.
                    self.x, self.y = (target.x - diagonal / 5 * math.cos(self.theta),
                                      target.y + diagonal / 5 * math.sin(self.theta))

                if self.altFireCooldown <= 0:
                    # Set cooldowns. While self.thirdFireCooldown is not infinity, self should stop circling.
                    self.altFireCooldown = float('inf')
                    self.thirdFireCooldown = 100
                    self.fireCooldown = float('inf')
                    self.setMovementToTarget(target, 4)

                if self.fireCooldown <= 0:
                    # This block should repeatedly execute while self is circling.
                    self.fireCooldown = 65

                    # Fire a projectile that takes away oxygen upon colliding with the player.
                    self.basicStraightShot(5, 'spiderProjectile1.png', target.maxHp * 0.3, target,
                                           playerContactEffect="pro.oxygen -= 30")

                # If self.thirdFireCooldown <= 0, self should do nothing but continuously move towards the target.
                if self.thirdFireCooldown <= 0:
                    self.setMovementToTarget(target, 12)

                if self.hr or self.vr:
                    self.moveNormally()

            case 'teleportingAndFiringInRings':
                if self.fireCooldown <= 0:
                    # Set cooldowns. Self.altFireCooldown is set to 1 so that self will wait until just after
                    # teleporting to fire.
                    self.altFireCooldown = 1
                    self.fireCooldown = 100

                    # Set self's animation while delayed.
                    self.delayFrame = 0
                    self.delayAnimation = self.fastTeleportAnimation.copy()

                    # Teleport predictively.
                    self.teleportPredictively(target, spawnDelay=110)

                elif self.altFireCooldown <= 0:
                    # Fire a ring of projectiles.
                    self.basicSpreadShot(20, 2 * math.pi, target, 4, 'spiderProjectile1.png',
                                         target.maxHp * 0.3)

                    # Set self.altFireCooldown. Self should only fire right after teleporting.
                    self.altFireCooldown = float('inf')

        # If self.modeDuration <= 0, execute the following block.
        if self.modeDuration <= 0:
            # Fire a harmless bullet that replenishes oxygen and goes away upon colliding with target.
            self.newBullets.append(bullet(0, -0.2, 0, 'nanotechRevolverBulletImpactFrame1.png',
                                          self.x, self.y, piercing=float('inf'),
                                          playerContactEffect='pro.oxygen = lesser(pro.maxOxygen, pro.oxygen + 7); '
                                                              'projectile.linger = 0',
                                          alwaysChecksCollisionWithPro=True))

            # If not self.aggressive and self is not investigating, execute the next block.
            if self.mode != 'investigating' and not self.aggressive:
                # If self.duration < 0, make self die.
                if self.duration < 0:
                    self.hp = 0

                # Otherwise, set self's animation while delayed and teleport.
                else:
                    self.delayFrame = 0
                    self.delayAnimation = self.teleportAnimation.copy()
                    self.teleportRandomly(spawnDelay=330)

            # Modify self.mode and prepare for self's next action.
            if self.aggressive:
                match self.mode:
                    case 'dashing':
                        self.fireCooldown = 0
                        self.mode = 'teleportingAndFiringInRings'
                        self.modeDuration = 390

                    case 'teleportingAndFiringInRings':
                        self.modeDuration = 1100
                        self.thirdFireCooldown = 0
                        self.mode = 'circling'

                    case 'circling':
                        self.modeDuration = 550
                        self.fireCooldown = 90
                        self.altFireCooldown = 0
                        self.mode = 'dashing'

            else:
                match self.mode:
                    case 'search':
                        self.mode = 'fireRandomly'
                        self.modeDuration = 350

                    case 'fireRandomly':
                        self.mode = 'grid'
                        self.modeDuration = 550

                    case 'grid':
                        self.mode = 'search'
                        self.modeDuration = 750
                        self.fireCooldown = 300
                        self.animation = self.searchAnimation.copy()
                        self.animationFrame = 0

                    case 'investigating':
                        self.mode = 'search'
                        self.modeDuration = 750
                        self.fireCooldown = 300
                        self.animation = self.searchAnimation.copy()
                        self.animationFrame = 0

    def actAsGenericWanderingFoe(self, rooms, *args):
        """This function is the default function for foes to use while wandering."""

        # Reduce the wait until self turns.
        self.turnCooldownWhileWandering -= GAMESPEED

        # If self has an animation, progress self's animation.
        try:
            self.progressAnimation()

        except AttributeError:
            pass

        # If self.turnCooldownWhileWandering <= 0, execute the following block.
        if self.turnCooldownWhileWandering <= 0:
            # Set self.hr and self.vr. Self's speed should remain constant.
            angle = random.randint(0, 360) * math.pi / 180
            self.hr, self.vr = math.cos(angle) / 4, math.sin(angle) / 4

            # Set self.turnCooldownWhileWandering.
            self.turnCooldownWhileWandering = 350

        # Move. Turn around if self hits a wall.
        if self.moveNormally():
            self.hr = -self.hr
            self.vr = -self.vr

        # If self.rotated, set self.angle to be the angle that self is moving at.
        if self.rotated:
            self.angle = getRadians(self.hr, -self.vr)

    def showHp(self, offset=(0, 0)):
        """Displays self's hp."""
        hpGoneRect = pygame.Rect(width * 4 / 5, self.hpBarTop, width * 1 / 6, height / 70)
        hpRect = pygame.Rect(width * 4 / 5, self.hpBarTop,
                             width * 1 / 6 * self.hp / self.initialHp, height / 70)
        fillWithOffset('#1abdbd', hpGoneRect, offset)
        fillWithOffset('#cd300e', hpRect, offset)

    def updateStats(self):
        """Update self's stats every frame."""
        self.speed = 1

        # Reduce the duration of modifications to self's movement and remove them as needed.
        for modifier in self.movementModifiers:
            modifier[2] -= 1

            if modifier[2] <= 0:
                self.movementModifiers.remove(modifier)

        # Execute the effects of any debuffs that self has and reduce their durations.
        for debuff in self.debuffs:
            exec(debuff.effect)
            debuff.duration -= GAMESPEED

            if debuff.duration <= 0:
                self.debuffs.remove(debuff)

    def updateHitbox(self):
        """Update's self's hitbox to be consistent with self.x and self.y."""

        # If self.hasFullHitbox, execute the next block.
        if self.hasFullHitbox:
            # Set self.hitbox. If self.rotated, self's hitbox should be rotated.

            if self.rotated:
                self.hitbox = rect(IMAGES[self.sprite].get_rect(center=(self.x, self.y)), -self.angle)

            else:
                self.hitbox = rect(IMAGES[self.sprite].get_rect(center=(self.x, self.y)))

        # If self.hitboxOnSelf exists, execute the next block.
        elif hasattr(self, 'hitboxOnSelf'):
            # Set self.hitbox to a copy of self.hitboxOnSelf.
            self.hitbox = copy.deepcopy(self.hitboxOnSelf)

            # Move self.hitbox to be in the right position.
            self.hitbox.move(self.x, self.y)

    def actAsFoe(self, target, rooms, room, displayVars, *args):
        """Every foe that has noticed the player should use this function each frame. """

        self.updateStats()

        if self.spawnDelay <= 0:
            # Keep track of where self was at the start of this function.
            oldX = self.x
            oldY = self.y

            # Perform the proper action for self. Attack self.unusualTarget if it's not None. Otherwise, attack pro.
            if self.stun > 0:
                self.stun -= GAMESPEED

            else:
                self.action(target if self.unusualTarget is None else self.unusualTarget, room, *args)

            # Make self.place to be centered around self.x, self.y
            self.place.centerx, self.place.centery = self.x, self.y

            # Handle knockback.
            self.handleKnockback(displayVars, room)

            # Update self's hitbox.
            self.updateHitbox()

            # If not self.goesThroughObjects and self is colliding with an environmental object, execute the next block.
            if not self.goesThroughObjects:
                if [obj for obj in rooms.rooms[tuple(self.room)].environmentObjects if \
                            obj.hitbox.checkCollision(self.hitbox)]:
                    # Take self.x and self.y back to what they were at the start of this function.
                    self.x = oldX
                    self.y = oldY

                    # Update self.place.
                    self.place.centerx = self.x
                    self.place.centery = self.y

                    # If self.hasFullHitbox, update self.hitbox.
                    if self.hasFullHitbox:
                        if self.rotated:
                            self.hitbox = rect(IMAGES[self.sprite].get_rect(center=(self.x, self.y)), -self.angle)

                        else:
                            self.hitbox = rect(IMAGES[self.sprite].get_rect(center=(self.x, self.y)))

        else:
            self.spawnDelay -= GAMESPEED

    def chaseThroughRooms(self, target, axis, rooms, *args):
        """Chase the player through rooms."""

        if hasattr(self, 'movementCode'):
            # self.movementCode should be repeatedly executed to move self.
            self.movementCode = 'pass'

        # Reduce self.cooldownPerRoomSwitch.
        self.cooldownPerRoomSwitch -= GAMESPEED
        self.room = list(self.room)

        # Record what self.x, self.y, and self.room were at the start of this function.
        initialX = self.x
        initialY = self.y
        oldRoom = self.room.copy()

        # Execute the next block if self.cooldownPerRoomSwitch <= 0.
        if self.cooldownPerRoomSwitch <= 0:
            # Set self.cooldownPerRoomSwitch and self.delay.
            self.cooldownPerRoomSwitch = 525
            self.spawnDelay = 50

            # Change self.room and go to the right edge of the new room.
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

            # If self should not be where self is, execute the next block.
            if tuple(self.room) not in rooms.rooms.keys() or rooms.rooms[tuple(self.room)].isSafe:
                # Set self.room, self.x, and self.y to what they were at the start of this function.
                self.room = oldRoom
                self.x = initialX
                self.y = initialY

            # Otherwise, update self.place and self.hitbox.
            else:
                self.place.centerx = self.x
                self.place.centery = self.y
                self.hitbox.move(self.x - initialX, self.y - initialY)

    def getUpdate(self):
        """Give self any attributes that self is missing. They may have been added after self was created."""

        # Create a foe of the same type as self.
        comparison = foe(self.type, 0, 0, [0, 0, 0])

        # Get a dictionary of the attributes of comparison.
        stats = vars(comparison)

        # Give self any attributes that comparison has but self does not.
        for key in list(stats.keys()):
            if not hasattr(self, key):
                self.__setattr__(key, stats[key])
