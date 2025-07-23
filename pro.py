import math
import random
import pygame
import worldFile
import copy

from variables import (IMAGES, GAMESPEED, display, MOVESPEED, width, height, recipes, fullscreenRect,
                       descriptionsPerCritter, descriptionsPerItem)
from definitions import getDirection, lesser, getPath, draw, checkMouseCollision, loadWithPickle, saveWithPickle, \
    greater, getRadians, blitWithOffset, fillWithOffset, camelCaseToNormalText, normalTextToCamelCase, getEvents, \
    temporarilyPlay, playSoundEffect
from rects import rect
from bullets import bullet
from item import item
from word import word
from plainSprites import plainSprite
from debuff import debuff
from textBox import textBox
import traceback

nanotechBulletImplosionAnimation = [f'nanotechRevolverBulletImpactFrame{i}.png' for i in range(1, 7) for j in
                                    range(10)]
craftingBox = plainSprite('craftingBox.png', width * 7 / 8, height * 9 / 20)
craftButton = plainSprite('startButton.png', width * 7 / 8, height * 7 / 10)


class player:
    def __init__(self, **extra):
        self.startingRoom = [0, 0, 10]
        self.startingCoord = [width / 2, height / 2]
        self.maxHp = 130
        self.hp = 130
        self.fireCooldown = 0
        self.inventoryShown = 0
        self.room = [0, 0, 10]
        self.bullets = []
        self.sprinting = 0
        self.sprite = 'newWalkingAnimation_s1.png'
        self.place = IMAGES[self.sprite].get_rect(center=(display.get_size()[0] / 2, display.get_size()[1] / 2))
        self.x = self.place.centerx
        self.y = self.place.centery
        self.hitbox = rect(pygame.Rect(self.place.left + width / 320, self.place.top + height / 45,
                                       self.place.width - width / 160, self.place.height - height / 45))
        self.hitboxForObjectCollision = rect(pygame.Rect(self.place.left, self.place.top + height * 16 / 225,
                                                         height * 4 / 225, self.place.width))
        self.aggressiveFoes = []

        self.idleAnimation = {'w': ['newWalkingAnimation_w1.png'],
                              's': ['newWalkingAnimation_s1.png'],
                              'd': ['newWalkingAnimation_d1.png'],
                              'a': ['newWalkingAnimation_a1.png']}

        self.walkingAnimation = {'w': [],
                                 'a': [],
                                 's': [],
                                 'd': []}

        for letter in ['w', 'a', 's', 'd']:
            for i in range(1, 5):
                for j in range(95):
                    self.walkingAnimation[letter].append(f'newWalkingAnimation_{letter}{i}.png')

        self.hr = 0
        self.vr = 0
        self.forcedHr = 0
        self.forcedVr = 0
        self.animation = self.idleAnimation['s'].copy()
        self.directionlessAnimation = self.idleAnimation
        self.animationFrame = 0
        self.direction = 's'
        self.slideTime = 0
        self.mapShown = 0
        self.stamina = 100
        self.file = None
        self.hpRect = pygame.Rect(width / 160, height / 90, width * 61 / 400 * self.hp / self.maxHp, height * 9 / 450)
        self.bullets = []
        self.invincibility = 0
        self.speed = 1
        self.itemFunctions = {'nanotechRevolver': self.useNanotechRevolver,
                              'lumisFlamethrower': self.useLumisFlamethrower, 'jellyfish': self.useJellyfish,
                              'lumiswoodBow': self.useLumisWoodBow, 'bagOfSand': self.useBagOfSand}
        self.altItemFunctions = {'lumisFlamethrower': self.useLumisFlamethrowerAlt,
                                 'lumiswoodBow': self.useLumisWoodBowAlt, 'bagOfSand': self.useBagOfSandAlt}
        self.inventory = [item('empty', 'invisiblePixels.png', stackSize=1) for i in range(101)]
        self.activeItem = self.inventory[0]
        self.activeItemSlot = 0
        self.inventoryBoxes = []
        boxWidth = IMAGES['inventoryBox.png'].get_width()
        boxHeight = IMAGES['inventoryBox.png'].get_height()
        self.emptySlots = []
        self.maxOxygen = 100
        self.oxygen = 100
        self.scaryCooldown = 1
        self.timeSincePressingSpace = float('inf')
        self.maxPotions = 2
        self.potions = 2
        self.potionRechargeProgress = 0
        self.hpBar = plainSprite("hpBar.png", width * 33 / 400, height / 50)
        self.hpGoneSprite = plainSprite('hpGone.png', width * 33 / 400, height / 50)
        self.staminaBar = plainSprite("staminaBar.png", width * 33 / 400, height * 13 / 180)
        self.staminaGoneSprite = plainSprite("staminaGone.png", width * 33 / 400, height * 13 / 180)
        self.potionSprites = [plainSprite('healthPotion.png', width / 25, height * 4 / 5),
                              plainSprite('healthPotion.png', width * 3 / 25, height * 4 / 5)]
        self.potionsFilledBar = plainSprite("potionFilledBar.png", width / 25, height * 71 / 90)
        self.song = 'Crashed.mp3'
        self.cooldownForControlledMovement = 0
        self.walkingSoundCooldown = 0

        # self.healingCooldown exists so that two of the healing sound effect cannot overlap.
        self.healingCooldown = 0

        # self.journalInfo lists what entries the player has for certain categories and what the entries are.
        self.journalInfo = {'creatures': {}, 'items': {},
                            'biomes': {'ship': 'The ship is your crashed ship, which no longer functions.'},
                            'protagonist': {'healing': 'To heal, you drink potions. Inflicting sufficient damage to '
                                                       'enemies gives you another potion unless you are holding the '
                                                       'most potions that you can or have regenerated a potion since '
                                                       'last using one.'}}

        for i in range(3):
            for j in range(10):
                self.inventoryBoxes.append(plainSprite(
                    'inventoryBox.png', j * boxWidth * 2 + width * 1 / 30 + boxWidth / 2,
                                        i * 3 * boxHeight + height * 7 / 30 + boxHeight / 2))

        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')

    def switchAnimation(self, animation):
        """The switchAnimation function should change your animation and directionlessAnimation and take you
        to the start of your new animation."""
        self.directionlessAnimation = animation
        self.animationFrame = 0

    def gainItem(self, itemGained):
        """Adds as much as possible of itemGained to the player's inventory. Returns however much of itemGained could
        not be added to the inventory."""

        activeItemNumber = self.inventory.index(self.activeItem)

        # qtyLeft represents how much of itemGained has not yet been added to the player's inventory.
        qtyLeft = itemGained.qty

        # The following loop will end with a return statement if not all of itemGained can be picked up.
        while qtyLeft > 0:
            self.emptySlots = [i for i in self.inventory[0:30] if i.name == 'empty']

            # similarSlots is a list of self's items of the same type as itemGained to which itemGained can be added.
            similarSlots = [i for i in self.inventory[0:30] if i.name == itemGained.name and i.qty < i.stackSize]

            # Do some stuff if similarSlots is empty.
            if not similarSlots:
                # If the player has at least 30 slots full of items, then itemGained cannot be picked up.
                if len([i for i in self.inventory if i.name != 'empty']) >= 30:
                    return qtyLeft

                # Otherwise, itemGained will be put in an empty slot.
                newItem = self.inventory[self.inventory.index(self.emptySlots[0])] = copy.copy(itemGained)
                qtyLeft = 0

                # Switch self.activeItem to be itemGained if itemGained was put in the active item slot.
                if self.inventory.index(newItem) == activeItemNumber:
                    self.activeItem = newItem

                # If possible, add the journal entry for the new item to the player's journal.
                try:
                    self.journalInfo['items'][newItem.name] = descriptionsPerItem[newItem.name]

                except KeyError:
                    pass

            # Do other stuff otherwise.
            else:
                # Add some of itemGained to an item of the same type in the player's inventory.
                similarSlot = random.choice(similarSlots)
                qtyAdded = lesser(qtyLeft, similarSlot.stackSize - similarSlot.qty)
                similarSlot.qty += qtyAdded

                # Adjust qtyLeft.
                qtyLeft -= qtyAdded

        return 0

    def updateHpRect(self):
        self.hpRect = pygame.Rect(width / 160, height / 90, width * 61 / 400 * self.hp / self.maxHp, height * 9 / 450)

    def hurt(self, damage, givesInvincibility=True, playHurtSound=True):
        """self.hurt(damage) reduces the player's hp by damage, makes the player temporarily invincible, and update's
        the display that shows the player's hp."""

        if damage:
            self.hp -= damage
            self.invincibility = greater(250 if givesInvincibility else 0, self.invincibility)
            self.updateHpRect()

        if playHurtSound:
            playSoundEffect('hurt.wav', volume=0.4)


    def heal(self, hp):
        """Heal self by hp hp."""

        self.hp = lesser(self.maxHp, self.hp + hp)
        self.updateHpRect()

    def progressAnimation(self):
        """The progressAnimation changes your animation, directionlessAnimation, and sprite as appropriate."""
        # If you are firing, the next three lines of code make you turn to face where you are firing.

        if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
            self.direction = getDirection(pygame.mouse.get_pos()[0] - self.x,
                                          pygame.mouse.get_pos()[1] - self.y)

        # If you are moving but not firing, the next two lines of code make you turn based on how you are moving.

        elif self.hr != 0 or self.vr != 0:
            self.direction = getDirection(self.hr, self.vr)

        self.animationFrame += GAMESPEED

        if self.directionlessAnimation == self.idleAnimation and abs(self.vr) + abs(self.hr) > 0:
            self.switchAnimation(self.walkingAnimation)

        elif self.directionlessAnimation == self.walkingAnimation and self.hr == self.vr == 0:
            self.switchAnimation(self.idleAnimation)

        if self.animationFrame > len(self.animation) - 1:
            self.animationFrame = 0

        self.animation = self.directionlessAnimation[self.direction]
        self.sprite = self.animation[int(self.animationFrame)]

    def slide(self):
        if self.stamina >= 200 and self.slideTime <= 0:
            self.slideTime = GAMESPEED + 1
            self.stamina -= 200
            self.invincibility = 2

    def dash(self):
        if self.stamina >= 300 and self.slideTime <= 0:
            self.slideTime = 40
            self.stamina -= 300
            self.invincibility = 60
            playSoundEffect('dashing2.wav', volume=0.4)

    def usePotion(self):
        """Makes the player use a potion."""

        if self.potions and self.healingCooldown <= 0:
            self.potions -= 1
            self.hp = lesser(self.hp + 70, self.maxHp)
            self.potionRechargeProgress = 0
            self.updateHpRect()
            playSoundEffect('healing.wav')
            self.healingCooldown = 240

    def getPotion(self):
        "Gives the player a potion."

        self.potions = lesser(self.potions + 1, self.maxPotions)
        playSoundEffect('gettingPotion.wav')

    def useActiveItem(self, offset=(0, 0)):
        """Makes the player use their active item as appropriate."""

        if self.fireCooldown <= 0 and not self.sprinting and self.slideTime <= 0 and self.activeItem.cooldown <= 0:
            if pygame.mouse.get_pressed()[0] and self.activeItem.standardCooldown <= 0:
                try:
                    self.itemFunctions[self.activeItem.name](offset=offset)
                    return 1

                except KeyError:
                    # TODO Replace the next line with pass.
                    pass

            elif pygame.mouse.get_pressed()[2] and self.activeItem.altCooldown <= 0:
                try:
                    self.altItemFunctions[self.activeItem.name](offset=offset)
                    return 1

                except KeyError:
                    pass

    def fireToMouse(self, damage, sprite, speed, knockbackStrength=0, knockbackDuration=50, **kwargs):
        """Fire a projectile towards the mouse."""

        # Find the hr and vr that the projectile must have.
        path = getPath(speed, (self.x, self.y), pygame.mouse.get_pos())

        # Determine the knockback.
        knockback = [(knockbackStrength * path[0]) / speed, (knockbackStrength * path[1]) / speed,
                     knockbackDuration] if knockbackStrength \
            else None

        # Fire a projectile.
        self.bullets.append(bullet(path[0], path[1], damage, sprite, self.x, self.y, firer=self, knockback=knockback,
                                   **kwargs))

    def fireInConsistentSpread(self, damage, sprite, speed, qty, totalAngleInRadians, animation=None,
                               impactAnimation=None, linger=1600, knockbackStrength=0, knockbackDuration=50, **kwargs):
        """Fire a spread of projectiles centered on the mouse."""

        # Calculate the angle between each projectile.
        angleChangePerProjectile = totalAngleInRadians / (qty - 1)

        # Calculate the angle from self to the center of the spread.
        mousePosition = pygame.mouse.get_pos()
        centerAngle = -getRadians(mousePosition[0] - self.x, mousePosition[1] - self.y)

        # Fire projectiles.
        for i in range(qty):
            # Determine the angle at which to fire.
            angle = centerAngle - totalAngleInRadians / 2 + \
                    i * angleChangePerProjectile

            # Store the sine and cosine of angle because they will be used repeatedly.
            sine = math.sin(angle)
            cosine = math.cos(angle)

            # Deterimine the knockback.
            knockback = [cosine * knockbackStrength, sine * knockbackStrength, knockbackDuration]

            # Fire a projectile.
            self.bullets.append(bullet(speed * cosine, speed * sine, damage, sprite, self.x,
                                       self.y, animation=animation, impactAnimation=impactAnimation, linger=linger,
                                       firer=self, knockback=knockback, **kwargs))

    def fireInRandomSpread(self, damage, sprite, speed, qty, maxAngleInDegrees, animation=None, impactAnimation=None,
                           timeBeforeStop=1600, piercing=1):
        mousePosition = pygame.mouse.get_pos()
        angleToMouse = -getRadians(mousePosition[0] - self.x, mousePosition[1] - self.y)

        for i in range(qty):
            angle = angleToMouse + random.randint(-maxAngleInDegrees, maxAngleInDegrees) * math.pi / 360
            self.bullets.append(bullet(speed * math.cos(angle), speed * math.sin(angle), damage, sprite, self.x,
                                       self.y, animation=animation, impactAnimation=impactAnimation,
                                       timeBeforeStop=timeBeforeStop, piercing=piercing, firer=self))

    def attatchProjectileToSelf(self, bullet, connectorSprite, offset=(0, 0)):
        """Connect bullet to self using connectorSprite. For this function to work, bullet.firer must be self"""
        bullet.additionalMethods = {bullet.visuallyConnectToFirer: (connectorSprite, offset,)}

    def makeProjectilePullSelfUponHittingFoe(self, bullet, speed, givesInvincibility=True):
        """Make bullet pull self towards bullet upon hitting a foe. The speed paramater determines the speed at which
        self will be pulled."""
        bullet.foeContactEffect = (f'[projectile.firer.forcedHr, projectile.firer.forcedVr] = getPath({speed}, '
                                   f'(pro.x, pro.y), (foe.x, foe.y)); '
                                   f'pro.cooldownForControlledMovement = '
                                   f'pointDistance((pro.x, pro.y), '
                                   f'(foe.x, foe.y)) / {speed}')

        if givesInvincibility:
            bullet.foeContactEffect += (f'; projectile.firer.invincibility = '
                                        f'pro.cooldownForControlledMovement + 180')

    def destroyFoes(self):
        for i in self.proRoom().foes:
            i.hp = 0

    def useNanotechRevolver(self, **kwargs):
        """The useNanotechRevolver function will be your attack while your active item is the nanotechRevolver."""
        self.fireToMouse(1, 'basicRangeProjectile_d.png', 6.5,
                         impactAnimation=nanotechBulletImplosionAnimation)
        self.fireCooldown = 60
        playSoundEffect('nanotechRevolver.wav')

    def useLumisFlamethrower(self, **kwargs):
        self.fireInConsistentSpread(0.3, 'spiderProjectile1.png', 8, 5, math.pi / 8,
                                    animation=[f'spiderProjectile{i}.png' for i in [1, 2] for j in range(30)],
                                    linger=100)
        self.fireCooldown = 45

    def useLumisFlamethrowerAlt(self, **kwargs):
        for i in range(5):
            self.fireInRandomSpread(0.002, 'desertCaveMothProjectile1.png', 2 + i / 4, 18,
                                    60,
                                    animation=[f'desertCaveMothProjectile{i}.png' for i in [1, 2] for j in range(15)],
                                    timeBeforeStop=100, piercing=200000)
        self.fireCooldown = 100

    def useJellyfish(self, **kwargs):
        self.fireToMouse(10, 'desertCaveJellyfishFrame1.png', 7.5,
                         animation=[f'desertCaveJellyfishFrame{i}.png' for i in range(1, 5) for j in range(20)],
                         debuffInflictions=[debuff('nanotechRevolverBulletImpactFrame1.png',
                                                   'self.speed *= 2 / 3; self.hp -= GAMESPEED / 100',
                                                   5400,
                                                   effectUponEnding='debuff.source.source.cooldown = 900')],
                         source=self.activeItem,
                         foeContactEffect='projectile.source.cooldown = 5400;')
        self.bullets[-1].debuffInflictions[0].source = self.bullets[-1]
        self.activeItem.cooldown = 900
        playSoundEffect('jellyfishThrown.wav')

    def useLumisWoodBow(self, **kwargs):
        self.fireToMouse(2.5, 'spiderProjectile1.png', 10)
        self.fireCooldown = 100

    def useLumisWoodBowAlt(self, offset=(0, 0), **kwargs):
        self.fireToMouse(3, 'desertCaveFlyMinibossLargeProjectile1.png', 8)
        self.attatchProjectileToSelf(self.bullets[-1], 'desertCaveFlyMinibossLaserProjectile1.png',
                                     offset=offset)
        self.makeProjectilePullSelfUponHittingFoe(self.bullets[-1], 7.5)
        self.activeItem.cooldown = 1260

    def useBagOfSand(self, **kwargs):
        """Use the bag of sand's standard attack method."""

        # Fire projectiles.
        self.fireInConsistentSpread(0, 'desertCaveMothProjectile1.png', 3, 5, math.pi / 6,
                                    piercing=float('inf'), stun=360)

        # Make each projectile slow down over time.
        for i in range(-5, 0):
            # Store a projectile's hr and vr.
            initialHr = self.bullets[i].hr
            initialVr = self.bullets[i].vr

            # Make the projectile slow down over time.
            self.bullets[i].movementByDuration = (f"[{initialHr} * math.e ** (-self.currentDuration / 180),"
                                                  f"{initialVr} * math.e ** (-self.currentDuration / 180)]")

        # Set the bag of sand's standard cooldown.
        self.activeItem.standardCooldown = 3600

    def useBagOfSandAlt(self, **kwargs):
        """Use the bag of sand's alternate attack method."""

        # Fire a projectile.
        self.fireToMouse(0, 'largerWraithSwing.png', 7, piercing=float('inf'), linger=60,
                         timeBeforeStop=40)

        # Store the projectile's movement.
        hr = self.bullets[-1].hr
        vr = self.bullets[-1].vr

        # Make the projectile knock back enemies, make the screen shake, and pause the game upon contact with stunned
        # foes.
        self.bullets[-1].foeContactEffect = (
            f"if foe.stun > 0: foe.movementModifiers.append([{hr / 2}, {vr / 2}, 360]);"
            f" displayVars.screenShakeDuration = "
            f"greater(displayVars.screenShakeDuration, 50); time.sleep(0.03)")

        # Set self.fireCooldown.
        self.fireCooldown = 180

    def startSprinting(self):
        self.sprinting = 1
        self.updateSpeed()

        if 30 < self.timeSincePressingSpace < 60 and self.speed <= 5:
            self.speed += 1

        self.timeSincePressingSpace = 0

    def getInput(self):
        """The getInput function will perform actions based on the player's input."""

        if self.slideTime > 0:
            self.sprinting = 0

        if self.inventoryShown:
            self.updateInventory()

        if pygame.mouse.get_pressed()[0]:
            pass

        for event in pygame.event.get(pygame.KEYDOWN):
            if event.key == pygame.K_a:
                self.hr -= 2

            elif event.key == pygame.K_d:
                self.hr += 2

            elif event.key == pygame.K_w:
                self.vr -= 2

            elif event.key == pygame.K_s:
                self.vr += 2

            elif event.key == pygame.K_SPACE:
                self.startSprinting()

            elif event.key == pygame.K_h:
                self.usePotion()

            elif event.key == pygame.K_l:
                if self.inventoryShown:
                    self.inventoryShown = 0

                else:
                    self.inventoryShown = 1
                    self.updateItemPositions()

            elif event.key == pygame.K_z and not (self.proRoom().locks and self.proRoom().foes):
                try:
                    self.room = self.proRoom().roomThatCanBeManuallyTeleportedTo.coordinate

                except AttributeError:
                    pass

            elif event.key == pygame.K_t:
                try:
                    exec(input('Type your command:'))

                except:
                    print('Invalid command')

            elif event.key == pygame.K_m:
                if self.mapShown:
                    self.mapShown = 0

                else:
                    self.mapShown = 1

            elif event.key == pygame.K_j:
                self.showMainJournal()

            elif event.key == pygame.K_0:
                self.activeItem = self.inventory[9]
                self.activeItemSlot = 9

            elif pygame.key.get_mods() & pygame.KMOD_CTRL and not self.sprinting:
                self.slide()

            elif pygame.key.get_mods() & pygame.KMOD_SHIFT and not self.sprinting:
                self.dash()

            elif event.key == pygame.K_k:
                self.destroyFoes()

            else:
                for i in range(9):
                    exec(f'if event.key == pygame.K_{i + 1}: self.activeItem = self.inventory[{i}]')
                    exec(f'if event.key == pygame.K_{i + 1}: self.activeItemSlot = {i}')

        for event in pygame.event.get(pygame.KEYUP):
            if event.key == pygame.K_a:
                self.hr += 2

            elif event.key == pygame.K_d:
                self.hr -= 2

            elif event.key == pygame.K_w:
                self.vr += 2

            elif event.key == pygame.K_s:
                self.vr -= 2

            elif event.key == pygame.K_SPACE:
                self.sprinting = 0

    def updateSpeed(self):
        if self.slideTime <= 0:
            if self.sprinting:
                self.speed = greater(1.6, self.speed - 0.0036 * GAMESPEED)

            else:
                self.speed = greater(0.7, self.speed - 0.036 * GAMESPEED)

        else:
            self.speed = 4

    def updateJournalEntriesForCritters(self):
        """Adds critters in the current room to the journal."""

        for enemy in self.proRoom().foes:
            try:
                self.journalInfo['creatures'][enemy.type] = descriptionsPerCritter[enemy.type]

            except KeyError:
                pass

        for critter in self.proRoom().passiveCritters:
            try:
                self.journalInfo['creatures'][critter.type] = descriptionsPerCritter[critter.type]

            except KeyError:
                pass

    def updateStats(self):
        """The updateStats method should modify your attributes each frame."""

        self.slideTime -= GAMESPEED
        self.stamina = lesser(self.stamina + GAMESPEED, 500)
        self.fireCooldown -= GAMESPEED
        self.invincibility -= GAMESPEED
        self.timeSincePressingSpace += GAMESPEED
        currentRoom = self.proRoom()
        self.cooldownForControlledMovement -= GAMESPEED
        self.hurt(self.proRoom().constantDamage, givesInvincibility=False, playHurtSound=False)
        self.walkingSoundCooldown -= GAMESPEED
        self.healingCooldown -= GAMESPEED

        for i in self.inventory[0: 30]:
            i.cooldown -= GAMESPEED
            i.standardCooldown -= GAMESPEED
            i.altCooldown -= GAMESPEED

        if currentRoom.oxygenLoss:
            self.oxygen -= currentRoom.oxygenLoss

            if self.oxygen <= 0:
                self.hp = 0

        else:
            self.oxygen = self.maxOxygen

        self.updateSpeed()

        # Add creatures to the journal as needed.
        self.updateJournalEntriesForCritters()

    def updateItemPositions(self):
        for i in range(30):
            thing = self.inventory[i]
            box = self.inventoryBoxes[i]
            thing.dragged = 0
            thing.place.centerx, thing.place.centery = box.place.centerx, box.place.centery
            thing.updateHitbox()

    def showInventory(self, offset=(0, 0)):
        for box in self.inventoryBoxes:
            draw(box, offset=offset)

        for thing in self.inventory:
            thing.progressAnimation()

            if thing.name != 'empty':
                draw(thing, offset=offset)

                index = self.inventory.index(thing)

                if (index < 30 or index == 100) and checkMouseCollision(thing.hitbox) and not thing.dragged:
                    thing.textBox.draw(offset=offset)

                if thing.qty > 1:
                    word(thing.hitbox.centerx, thing.hitbox.bottom, str(thing.qty),
                         'finalNumber').draw(offset=offset)

        draw(craftingBox, offset=offset)
        draw(craftButton, offset=offset)

    def showHotbar(self, offset=(0, 0)):
        """Show self's hotbar."""

        for i in range(10):
            place = pygame.Rect(width * ((i + 1) / 11 - 3 / 160), height * 14 / 15, width * 3 / 80, height / 15)
            blitWithOffset(IMAGES[self.inventoryBoxes[i].sprite], place, offset)
            itemShown = self.inventory[i]
            slotNumberMarker = word(place.left - width / 160, place.top - height / 90, str(i + 1 if i < 9 else 0),
                                    'finalNumber')
            slotNumberMarker.draw(offset=offset)

            # If self.inventoryShown, then itemShown will progress its animation in self.showInventory.
            if not self.inventoryShown:
                itemShown.progressAnimation()

            # Draw the item.
            if itemShown.name != 'empty':
                blitWithOffset(IMAGES[itemShown.sprite], place, offset=offset)

            # Show the item's cooldowns.
            if itemShown.cooldown > 0:
                cooldownMarker = word(place.left, place.centery, str(int(itemShown.cooldown / 180) + 1),
                                      'finalNumber')
                cooldownMarker.draw(offset=offset)

            if itemShown.standardCooldown > 0:
                cooldownMarker = word(place.left + height / 45, place.centery,
                                      str(int(itemShown.standardCooldown / 180) + 1), 'finalNumber')
                cooldownMarker.draw(offset=offset)

            if itemShown.altCooldown > 0:
                cooldownMarker = word(place.left - height / 45, place.centery,
                                      str(int(itemShown.altCooldown / 180) + 1), 'finalNumber')
                cooldownMarker.draw(offset=offset)

    def showInfo(self, offset=(0, 0)):
        draw(self.hpGoneSprite, offset=offset)
        fillWithOffset("#f20cc6", self.hpRect, offset)
        draw(self.hpBar, offset=offset)
        staminaRect = pygame.Rect(width / 160, height * 56 / 900, width * 31 / 100000 * self.stamina, height / 50)
        draw(self.staminaGoneSprite, offset=offset)
        fillWithOffset("#10efe6", staminaRect, offset)
        draw(self.staminaBar, offset=offset)

        for i in range(self.potions):
            draw(self.potionSprites[i], offset=offset)

        if self.proRoom().oxygenLoss:
            oxygenGoneRect = pygame.Rect(width / 100, height / 10, width / 100, height / 10)
            oxygenRect = pygame.Rect(width / 100, height / 10, width / 100,
                                     height * self.oxygen / self.maxOxygen / 10)
            fillWithOffset("#6304b6ff", oxygenGoneRect, offset)
            fillWithOffset("#06d3ffff", oxygenRect, offset)

        if 30 < self.timeSincePressingSpace < 60:
            totalTimeToSprintRect = pygame.Rect(width / 40, height / 10, width / 100, height / 10)
            timeToSprintRect = pygame.Rect(width / 40, height / 10, width / 100,
                                           height * (60 - self.timeSincePressingSpace) / 300)
            fillWithOffset("#1abdbd", totalTimeToSprintRect, offset)
            fillWithOffset("#cd300e", timeToSprintRect, offset)

    def updateInventory(self):
        self.activeItem = self.inventory[self.activeItemSlot]
        dragging = 0

        for i in range(30):
            thing = self.inventory[i]
            box = self.inventoryBoxes[i]

            if not thing.dragged:
                thing.place.centerx, thing.place.centery = box.place.centerx, box.place.centery

            thing.updateHitbox()

        for thing in self.inventory:
            if thing.dragged:
                draggedItem = thing
                dragging = 1
                thing.place.centerx, thing.place.centery = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                thing.updateHitbox()
                break

        if not dragging:
            self.inventory[100].dragged = 1
            dragging = 1
            draggedItem = self.inventory[100]

        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN, pump=False):
            if checkMouseCollision(craftingBox.hitbox):
                try:
                    availableSlots = [i for i in range(30, 100) if self.inventory[i].name == 'empty']
                    draggedItemIndex = self.inventory.index(draggedItem)
                    self.inventory[availableSlots[0]] = draggedItem
                    draggedItem.dragged = 0
                    self.inventory[draggedItemIndex] = item('empty', 'invisiblePixels.png', stackSize=1)

                except (ValueError, IndexError):
                    pass

            elif checkMouseCollision(craftButton.hitbox):
                self.craft()

            for thing in self.inventory[:30]:
                if thing.dragged == 0 and checkMouseCollision(thing.hitbox):
                    if pygame.mouse.get_pressed()[0]:
                        if thing.name == draggedItem.name:
                            qtyAdded = lesser(draggedItem.qty, thing.stackSize - thing.qty)
                            thing.qty += qtyAdded
                            draggedItem.qty -= qtyAdded

                            if draggedItem.qty == 0:
                                self.inventory[self.inventory.index(draggedItem)] = item('empty',
                                                                                         'invisiblePixels.png',
                                                                                         stackSize=1)

                        else:
                            thing.dragged = 1
                            draggedItemIndex = self.inventory.index(draggedItem)
                            thingIndex = self.inventory.index(thing)
                            self.inventory[thingIndex] = draggedItem
                            self.inventory[draggedItemIndex] = thing
                            box = self.inventoryBoxes[thingIndex]
                            draggedItem.dragged = 0
                            draggedItem.place.centerx, draggedItem.place.centery = box.place.centerx, box.place.centery
                            draggedItem.updateHitbox()

                    elif pygame.mouse.get_pressed()[2]:
                        if thing.name == draggedItem.name and draggedItem.qty < draggedItem.stackSize:
                            draggedItem.qty += 1
                            thing.qty -= 1

                            if thing.qty == 0:
                                self.inventory[self.inventory.index(thing)] = item('empty',
                                                                                   'invisiblePixels.png',
                                                                                   stackSize=1)

                        elif draggedItem.name == 'empty':
                            if thing.qty:
                                thing.qty -= 1
                                self.inventory[self.inventory.index(draggedItem)] = \
                                    item(thing.name, thing.sprite, escription=thing.description, qty=1,
                                         stackSize=thing.stackSize)

                                if thing.qty == 0:
                                    self.inventory[self.inventory.index(thing)] = item('empty',
                                                                                       'invisiblePixels.png',
                                                                                       stackSize=1)

    def craft(self):
        items = [i for i in self.inventory[30: 100] if i.name != 'empty']
        itemNames = []

        for i in items:
            itemNames += [i.name] * i.qty

        try:
            itemGained = eval(recipes[tuple(sorted(itemNames))])
            self.gainItem(itemGained)

            for thing in items:
                self.inventory[self.inventory.index(thing)] = item('empty', 'invisiblePixels.png',
                                                                   stackSize=1)

        except KeyError:
            for thing in items:
                self.inventory[self.inventory.index(thing)] = item('empty', 'invisiblePixels.png',
                                                                   stackSize=1)

            for thing in items:
                self.gainItem(thing)

    def showMap(self, offset=(0, 0)):
        fillWithOffset((0, 0, 0), fullscreenRect, offset)
        for coordinate in list(rooms.rooms.keys()):
            if coordinate[2] == self.room[2] and (abs(self.room[1] - coordinate[1]) < 3 \
                    and abs(self.room[0] - coordinate[0]) < 3 or True):
                blitWithOffset(IMAGES[rooms.rooms[coordinate].mapMarker],
                               pygame.Rect(width * (311 / 640 + (coordinate[0] - self.room[0]) * 47 / 1600),
                                           height * (434 / 900 - (coordinate[1] - self.room[1]) * 17 / 450),
                                           9 * width / 320, 8 * height / 225), offset)

                if 5 > rooms.rooms[coordinate].difficulty > -1:
                    blitWithOffset(IMAGES['blobSummon.png'],
                                   pygame.Rect(width * (311 / 640 + (coordinate[0] - self.room[0]) * 47 / 1600),
                                               height * (434 / 900 - (coordinate[1] - self.room[1]) * 17 / 450),
                                               9 * width / 320, 8 * height / 225), offset)

                if coordinate == tuple(self.room):
                    blitWithOffset(IMAGES['playerRoomMapImage.png'],
                                   pygame.Rect(
                                       width * 311 / 640, height * 434 / 900,
                                       9 * width / 320, 8 * height / 225), offset)

    def showMainJournal(self):
        """Shows the journal's main categories."""

        # The next loop will be exited with a return statement.
        while True:
            # Color the whole display light yellow.
            display.fill((255, 246, 180), fullscreenRect)

            # Assign boxes. We need to keep track of boxes drawn because each one must be able to check collision.
            boxes = []

            # Draw a box for each main category of journal entries. Save boxes to the boxes variable.
            for i in range(len(self.journalInfo.keys())):
                # I'd rather not draw camel case for the player.
                box = textBox(camelCaseToNormalText(list(self.journalInfo.keys())[i]), 'newLetter',
                              'invisiblePixels.png', 0, height * i / 10, width)
                boxes.append(box)
                box.draw()

            # Handle MOUSEBUTTONDOWN events.
            if pygame.mouse.get_pressed()[0] and getEvents({pygame.MOUSEBUTTONDOWN: None}):
                # If the player pressed the mouse and the left button is pressed, check collisions with boxes.
                for box in boxes:
                    # If the player clicked on a box, go to the coresponding section of the journal.
                    if checkMouseCollision(box.hitbox):
                        # We converted the boxes' text to normal text, so it must be turned back to camel case.
                        self.showOptionsInCategory(normalTextToCamelCase(box.text))

            # Exit if the escape key was pressed.
            if getEvents({pygame.KEYDOWN: [pygame.K_ESCAPE]}):
                return

            # Update the display.
            pygame.display.flip()

    def showOptionsInCategory(self, category):
        """Show options for entries on a given category in the journal."""

        # verticalOffset will determine where boxes should be. It is used so that the player can scroll.
        verticalOffset = 0

        # The next loop will be exited with a return statement.
        while True:
            # Color the whole display light yellow.
            display.fill((255, 246, 180), fullscreenRect)

            # Do other things.
            if list(self.journalInfo[category].keys()):
                # Assign boxes. We need to keep track of boxes drawn because each one must be able to check collision.
                boxes = []

                # Draw a box for each main category of journal entries. Save boxes to the boxes variable.
                for i in range(len(self.journalInfo[category].keys())):
                    # I'd rather not show the text in camel case.
                    box = textBox(camelCaseToNormalText(list(self.journalInfo[category].keys())[i]), 'newLetter',
                                  'invisiblePixels.png', 0, height * i / 10 + verticalOffset, width)
                    boxes.append(box)
                    box.draw()

                # bottomOfBottomBox is used to determine how far the player can scroll.
                if boxes:
                    bottomOfBottomBox = boxes[-1].place.bottom - verticalOffset

                # Handle MOUSEBUTTONDOWN events.
                if pygame.mouse.get_pressed()[0] and getEvents({pygame.MOUSEBUTTONDOWN: None}):
                    for box in boxes:
                        # If the player clicked on a box, go to the coresponding section of the journal.
                        if checkMouseCollision(box.hitbox):
                            # Since we converted the boxes' text to normal text, it must be turned back to camel case.
                            self.showJournalEntry(category, normalTextToCamelCase(box.text))

                # Handle KEYDOWN events.
                for event in getEvents({pygame.KEYDOWN: [pygame.K_ESCAPE, pygame.K_DOWN, pygame.K_UP]}):
                    match event.key:
                        # Return to the main journal if escape was pressed.
                        case pygame.K_ESCAPE:
                            return

                        # Scroll down if the down arrow was pressed.
                        case pygame.K_DOWN:
                            verticalOffset = lesser(greater(verticalOffset - height, height - bottomOfBottomBox), 0)

                        # Scroll up if the up arrow was pressed.
                        case pygame.K_UP:
                            verticalOffset = lesser(greater(verticalOffset + height, height - bottomOfBottomBox), 0)

            # If there are no entries to show, then just exit if the escape key was pressed.
            else:
                if getEvents({pygame.KEYDOWN: [pygame.K_ESCAPE]}):
                    return

            # Update the display.
            pygame.display.flip()

    def showJournalEntry(self, category, entry):
        """Shows a given journal entry."""

        # The next loop will be exited with a return statement.
        while True:
            # Color the whole display light yellow.
            display.fill((255, 246, 180), fullscreenRect)

            # Show the entry.
            box = textBox(self.journalInfo[category][entry], 'newLetter', 'invisiblePixels.png', 0,
                          0, width, height / 20)
            box.draw()

            # Return to the options for the current category if the escape key was pressed..
            if getEvents({pygame.KEYDOWN: [pygame.K_ESCAPE]}):
                return

            # Update the display.
            pygame.display.flip()

    def updateHitbox(self):
        """Updates the player's hitbox."""
        self.hitbox = rect(pygame.Rect(self.place.left, self.place.top + 20, self.place.width,
                                       self.place.height - height / 80))
        self.hitboxForObjectCollision = rect(pygame.Rect(self.place.left, self.place.top + height / 15,
                                                         self.place.width, height * 11 / 450))

    def move(self):
        """The move function makes the player move."""
        oldX = self.x
        oldY = self.y
        (hr, vr) = (self.hr * self.speed, self.vr * self.speed) if self.cooldownForControlledMovement <= 0 else \
            (self.forcedHr, self.forcedVr)
        self.x += hr * GAMESPEED * MOVESPEED
        self.y += vr * GAMESPEED * MOVESPEED
        self.slideTime -= GAMESPEED
        self.place.centerx = self.x
        self.place.centery = self.y
        self.updateHitbox()
        self.proRoom()

        for thing in self.proRoom().environmentObjects:
            if thing.hitbox.checkCollision(self.hitboxForObjectCollision):
                self.x = oldX
                self.y = oldY
                self.place.centerx = self.x
                self.place.centery = self.y
                self.updateHitbox()

            if thing.hitbox.checkCollision(self.hitboxForObjectCollision):
                thing.hp = 0

        if self.place.left < self.proRoom().leftXBoundary:
            if (self.room[0] - 1, self.room[1], self.room[2]) in list(rooms.rooms.keys()):
                if (self.proRoom().locks and self.proRoom().foes) or self.proRoom().disconnected or not \
                        self.proRoom().playerXRangeToGoLeft[0] <= self.y <= self.proRoom().playerXRangeToGoLeft[1]:
                    self.place.left = self.proRoom().leftXBoundary

                else:
                    self.room[0] -= 1
                    self.place.right = self.proRoom().rightXBoundary

            else:
                self.place.left = self.proRoom().leftXBoundary

            self.x = self.place.centerx

        elif self.place.right > self.proRoom().rightXBoundary:
            if (self.room[0] + 1, self.room[1], self.room[2]) in list(rooms.rooms.keys()):
                if (self.proRoom().locks and self.proRoom().foes) or self.proRoom().disconnected or not \
                        self.proRoom().playerXRangeToGoRight[0] <= self.y <= self.proRoom().playerXRangeToGoRight[1]:
                    self.place.right = self.proRoom().rightXBoundary

                else:
                    self.room[0] += 1
                    self.place.left = self.proRoom().leftXBoundary

            else:
                self.place.right = self.proRoom().rightXBoundary

            self.x = self.place.centerx

        if self.place.top < self.proRoom().yBoundaries:
            if (self.room[0], self.room[1] + 1, self.room[2]) in list(rooms.rooms.keys()):
                if (self.proRoom().locks and self.proRoom().foes) or self.proRoom().disconnected or not \
                        self.proRoom().playerXRangeToGoUp[0] <= self.x <= self.proRoom().playerXRangeToGoUp[1]:
                    self.place.top = self.proRoom().yBoundaries

                else:
                    self.room[1] += 1
                    self.place.bottom = self.proRoom().bottomYBoundary

            else:
                self.place.top = self.proRoom().yBoundaries

            self.y = self.place.centery

        elif self.place.bottom > self.proRoom().bottomYBoundary:
            if (self.room[0], self.room[1] - 1, self.room[2]) in list(rooms.rooms.keys()):
                if (self.proRoom().locks and self.proRoom().foes) or self.proRoom().disconnected or not \
                        self.proRoom().playerXRangeToGoDown[0] <= self.x <= self.proRoom().playerXRangeToGoDown[1]:
                    self.place.bottom = self.proRoom().bottomYBoundary

                else:
                    self.room[1] -= 1
                    self.place.top = self.proRoom().yBoundaries

            else:
                self.place.bottom = self.proRoom().bottomYBoundary

            self.y = self.place.centery

        self.updateHitbox()

        if (self.hr or self.vr) and self.walkingSoundCooldown <= 0 and self.slideTime <= 0:
            playSoundEffect('running.wav' if self.sprinting else 'walking.wav', volume=0.3 if self.sprinting else 1)
            self.walkingSoundCooldown = 50 if self.sprinting else 100

        if self.sprinting or self.slideTime > 0:
            return 1

    def foeStats(self):
        print([vars(foe) for foe in self.proRoom().foes])

    def loadRooms(self, file):
        """The loadGame function should load the player info and the world info."""
        global rooms

        try:
            rooms = loadWithPickle(f'worldSave{file}.pickle')
            return rooms

        except FileNotFoundError:
            pass

    def resetRooms(self):
        global rooms
        rooms = worldFile.reset()
        return rooms

    def saveGame(self):
        """The saveGame function should save the player info and the world info."""
        saveWithPickle(f'playerSave{self.file}.pickle', self)

    def actions(self, offset=(0, 0)):
        """The actions function will perform all the player's actions."""
        self.getInput()
        self.updateStats()
        self.progressAnimation()
        returnedValues = []

        if self.useActiveItem(offset=offset):
            self.move()

            for foe in [foe for foe in self.proRoom().foes if foe.type == 'scary' and not foe.aggressive]:
                foe.aggressive = True

            return 1

        elif self.move():
            return 1

    def proRoom(self):
        return rooms.rooms[tuple(self.room)]

    def getRidOfAllFoes(self):
        for foes in [i.foes for i in rooms.rooms.values()]:
            for i in foes:
                i.hp = 0

    def getUpdate(self):
        comparison = player()
        stats = vars(comparison)

        for key in stats.keys():
            if not hasattr(self, key):
                self.__setattr__(key, stats[key])

    def test(self, method):
        try:
            method()

        except Exception as error:
            print("Caught an exception:", error)
            print("Exception type:", type(error))
            print("Traceback:", traceback.format_exc())
