import math
import random
import pygame
import worldFile
import copy

from variables import IMAGES, GAMESPEED, display, MOVESPEED, width, height, recipes
from definitions import getDirection, lesser, getPath, draw, checkMouseCollision, loadWithPickle, saveWithPickle, \
    greater, getRadians
from rects import rect
from bullets import bullet
from item import item
from word import word
from plainSprites import plainSprite
from debuff import debuff

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
                              'lumiswood bow': self.useLumisWoodBow}
        self.altItemFunctions = {'lumisFlamethrower': self.useLumisFlamethrowerAlt,
                                 'lumiswood bow': self.useLumisWoodBowAlt}
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
        self.canRechargePotion = True
        self.hpBar = plainSprite("hpBar.png", width * 33 / 400, height / 50)
        self.hpGoneSprite = plainSprite('hpGone.png', width * 33 / 400, height / 50)
        self.staminaBar = plainSprite("staminaBar.png", width * 33 / 400, height * 13 / 180)
        self.staminaGoneSprite = plainSprite("staminaGone.png", width * 33 / 400, height * 13 / 180)
        self.potionSprites = [plainSprite('healthPotion.png', width / 25, height * 4 / 5),
                              plainSprite('healthPotion.png', width * 3 / 25, height * 4 / 5)]
        self.potionsFilledBar = plainSprite("potionFilledBar.png", width / 25, height * 71 / 90)
        self.song = 'Crashed.mp3'
        self.cooldownForControlledMovement = 0

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
        """self.gainItem(itemGained) adds itemGained to the player's inventory."""
        activeItemNumber = self.inventory.index(self.activeItem)
        qtyLeft = itemGained.qty

        while qtyLeft > 0:
            self.emptySlots = [i for i in self.inventory[0:30] if i.name == 'empty']
            similarSlots = [i for i in self.inventory[0:30] if i.name == itemGained.name and i.qty < i.stackSize]

            if not similarSlots:
                if len([i for i in self.inventory if i.name != 'empty']) >= 30:
                    return qtyLeft

                newItem = self.inventory[self.inventory.index(self.emptySlots[0])] = copy.copy(itemGained)
                qtyLeft = 0

                if self.inventory.index(newItem) == activeItemNumber:
                    self.activeItem = newItem

                return 0

            else:
                similarSlot = random.choice(similarSlots)
                qtyAdded = lesser(qtyLeft, similarSlot.stackSize - similarSlot.qty)
                similarSlot.qty += qtyAdded
                qtyLeft -= qtyAdded

        return 0

    def updateHpRect(self):
        self.hpRect = pygame.Rect(width / 160, height / 90, width * 61 / 400 * self.hp / self.maxHp, height * 9 / 450)

    def hurt(self, damage):
        """self.hurt(damage) reduces the player's hp by damage, makes the player temporarily invincible, and update's
        the display that shows the player's hp."""

        if damage:
            self.hp -= damage
            self.invincibility = 250
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
        if self.stamina >= 250 and self.slideTime <= 0:
            self.slideTime = 40
            self.stamina -= 250
            self.invincibility = 160

    def usePotion(self):
        if self.potions:
            self.potions -= 1
            self.hp = lesser(self.hp + 70, self.maxHp)
            self.potionRechargeProgress = 0
            self.canRechargePotion = True
            self.updateHpRect()

    def useActiveItem(self):
        """Makes the player use their active item as appropriate."""

        if self.fireCooldown <= 0 and not self.sprinting and self.slideTime <= 0 and self.activeItem.cooldown <= 0:
            if pygame.mouse.get_pressed()[0]:
                try:
                    self.itemFunctions[self.activeItem.name]()
                    return 1

                except KeyError:
                    # TODO Replace the next line with pass.
                    pass

            elif pygame.mouse.get_pressed()[2]:
                try:
                    self.altItemFunctions[self.activeItem.name]()

                except KeyError:
                    pass


    def fireToMouse(self, damage, sprite, speed, **kwargs):
        path = getPath(speed, (self.x, self.y), pygame.mouse.get_pos())
        self.bullets.append(bullet(path[0], path[1], damage, sprite, self.x, self.y, firer=self, **kwargs))

    def fireInConsistentSpread(self, damage, sprite, speed, qty, totalAngleInRadians, animation=None,
                              impactAnimation=None, linger=1600):
        angleChangePerProjectile = totalAngleInRadians / (qty - 1)

        for i in range(qty):
            mousePosition = pygame.mouse.get_pos()
            angle = -getRadians(mousePosition[0] - self.x, mousePosition[1] - self.y) - totalAngleInRadians / 2 + \
                    i * angleChangePerProjectile
            self.bullets.append(bullet(speed * math.cos(angle), speed * math.sin(angle), damage, sprite, self.x,
                                       self.y, animation=animation, impactAnimation=impactAnimation, linger=linger))

    def fireInRandomSpread(self, damage, sprite, speed, qty, maxAngleInDegrees, animation=None, impactAnimation=None,
                           timeBeforeStop=1600, piercing=1):
        mousePosition = pygame.mouse.get_pos()
        angleToMouse = -getRadians(mousePosition[0] - self.x, mousePosition[1] - self.y)

        for i in range(qty):
            angle = angleToMouse + random.randint(-maxAngleInDegrees, maxAngleInDegrees) * math.pi / 360
            self.bullets.append(bullet(speed * math.cos(angle), speed * math.sin(angle), damage, sprite, self.x,
                                       self.y, animation=animation, impactAnimation=impactAnimation,
                                       timeBeforeStop=timeBeforeStop, piercing=piercing))

    def attatchProjectileToSelf(self, bullet, connectorSprite):
        """Connect bullet to self using connectorSprite. For this function to work, bullet.firer must be self"""
        bullet.additionalMethods = {bullet.visuallyConnectToFirer: (connectorSprite,)}

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

    def useNanotechRevolver(self):
        """The useNanotechRevolver function will be your attack while your active item is the nanotechRevolver."""
        self.fireToMouse(1, 'basicRangeProjectile_d.png', 6.5,
                         impactAnimation=nanotechBulletImplosionAnimation)
        self.fireCooldown = 60

    def useLumisFlamethrower(self):
        self.fireInConsistentSpread(0.3, 'spiderProjectile1.png', 8, 5, math.pi / 8,
                                   animation=[f'spiderProjectile{i}.png' for i in [1, 2] for j in range(30)],
                                   linger=100)
        self.fireCooldown = 45

    def useLumisFlamethrowerAlt(self):
        for i in range(5):
            self.fireInRandomSpread(0.01, 'desertCaveMothProjectile1.png', 2 + i / 4, 18,
                                    60,
                                    animation=[f'desertCaveMothProjectile{i}.png' for i in [1, 2] for j in range(15)],
                                    timeBeforeStop=100, piercing=200000)
        self.fireCooldown = 100

    def useJellyfish(self):
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

    def useLumisWoodBow(self):
        self.fireToMouse(2.5, 'spiderProjectile1.png', 10)
        self.fireCooldown = 100

    def useLumisWoodBowAlt(self):
        self.fireToMouse(3, 'desertCaveFlyMinibossLargeProjectile1.png', 8)
        self.attatchProjectileToSelf(self.bullets[-1], 'desertCaveFlyMinibossLaserProjectile1.png')
        self.makeProjectilePullSelfUponHittingFoe(self.bullets[-1], 7.5)
        self.activeItem.cooldown = 1260

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

            elif event.key == pygame.K_0:
                self.activeItem = self.inventory[9]
                self.activeItemSlot = 9

            elif pygame.key.get_mods() & pygame.KMOD_CTRL and not self.sprinting:
                self.slide()

            elif pygame.key.get_mods() & pygame.KMOD_SHIFT and not self.sprinting:
                self.dash()

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

    def updateStats(self):
        """The updateStats method should modify your attributes each frame."""
        self.slideTime -= GAMESPEED
        self.stamina = lesser(self.stamina + GAMESPEED, 500)
        self.fireCooldown -= GAMESPEED
        self.invincibility -= GAMESPEED
        self.timeSincePressingSpace += GAMESPEED
        currentRoom = self.proRoom()
        self.cooldownForControlledMovement -= GAMESPEED

        for i in self.inventory[0: 30]:
            i.cooldown -= GAMESPEED

        if currentRoom.oxygenLoss:
            self.oxygen -= currentRoom.oxygenLoss

            if self.oxygen <= 0:
                self.hp = 0

        else:
            self.oxygen = self.maxOxygen

        self.updateSpeed()

    def updateItemPositions(self):
        for i in range(30):
            thing = self.inventory[i]
            box = self.inventoryBoxes[i]
            thing.dragged = 0
            thing.place.centerx, thing.place.centery = box.place.centerx, box.place.centery
            thing.updateHitbox()

    def showInventory(self):
        for box in self.inventoryBoxes:
            draw(box)

        for thing in self.inventory:
            thing.progressAnimation()

            if thing.name != 'empty':
                draw(thing)

                index = self.inventory.index(thing)

                if (index < 30 or index == 100) and checkMouseCollision(thing.hitbox) and not thing.dragged:
                    thing.textBox.draw()

                if thing.qty > 1:
                    word(thing.hitbox.centerx, thing.hitbox.bottom, str(thing.qty), 'finalNumber').draw()

        draw(craftingBox)
        draw(craftButton)

    def showHotbar(self):
        for i in range(10):
            place = pygame.Rect(width * ((i + 1) /11 - 3 / 160), height * 14 / 15, width * 3 / 80, height / 15)
            display.blit(IMAGES[self.inventoryBoxes[i].sprite], place)
            itemShown = self.inventory[i]
            slotNumberMarker = word(place.left - width / 160, place.top - height / 90, str(i + 1 if i < 9 else 0),
                                    'finalNumber')
            slotNumberMarker.draw()

            # If self.inventoryShown, then itemShown will progress its animation in self.showInventory.
            if not self.inventoryShown:
                itemShown.progressAnimation()

            if itemShown.name != 'empty':
                display.blit(IMAGES[itemShown.sprite], place)

            if self.inventory[i].cooldown > 0:
                cooldownMarker = word(place.left, place.centery, str(int(itemShown.cooldown / 180) + 1),
                                      'finalNumber')
                cooldownMarker.draw()

    def showInfo(self):
        draw(self.hpGoneSprite)
        display.fill("#f20cc6", self.hpRect)
        draw(self.hpBar)
        staminaRect = pygame.Rect(width / 160, height * 56 / 900, width * 31 / 100000 * self.stamina, height / 50)
        draw(self.staminaGoneSprite)
        display.fill("#10efe6", staminaRect)
        draw(self.staminaBar)

        for i in range(self.potions):
            draw(self.potionSprites[i])

        if self.proRoom().oxygenLoss:
            oxygenGoneRect = pygame.Rect(width / 100, height / 10, width / 100, height / 10)
            oxygenRect = pygame.Rect(width / 100, height / 10, width / 100,
                                     height * self.oxygen / self.maxOxygen / 10)
            display.fill("#6304b6ff", oxygenGoneRect)
            display.fill("#06d3ffff", oxygenRect)

        if 30 < self.timeSincePressingSpace < 60:
            totalTimeToSprintRect = pygame.Rect(width / 40, height / 10, width / 100, height / 10)
            timeToSprintRect = pygame.Rect(width / 40, height / 10, width / 100,
                                           height * (60 - self.timeSincePressingSpace) / 300)
            display.fill("#1abdbd", totalTimeToSprintRect)
            display.fill("#cd300e", timeToSprintRect)

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

    def showMap(self):
        display.fill((0, 0, 0))

        for coordinate in list(rooms.rooms.keys()):
            if coordinate[2] == self.room[2] and abs(self.room[1] - coordinate[1]) < 3 \
                    and abs(self.room[0] - coordinate[0]) < 3:
                display.blit(IMAGES[rooms.rooms[coordinate].mapMarker],
                             pygame.Rect(width * (311 / 640 + (coordinate[0] - self.room[0]) * 47 / 1600),
                                         height * (434 / 900 - (coordinate[1] - self.room[1]) * 17 / 450),
                                         9 * width / 320, 8 * height / 225))

                if 5 > rooms.rooms[coordinate].difficulty > -1:
                    display.blit(IMAGES['blobSummon.png'],
                                 pygame.Rect(width * (311 / 640 + (coordinate[0] - self.room[0]) * 47 / 1600),
                                             height * (434 / 900 - (coordinate[1] - self.room[1]) * 17 / 450),
                                             9 * width / 320, 8 * height / 225))

                if coordinate == tuple(self.room):
                    display.blit(IMAGES['playerRoomMapImage.png'],
                                 pygame.Rect(
                                     width * 311 / 640, height * 434 / 900,
                                     9 * width / 320, 8 * height / 225))

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
                if (self.proRoom().locks and self.proRoom().foes) or self.proRoom().disconnected:
                    self.place.left = self.proRoom().leftXBoundary

                else:
                    self.room[0] -= 1
                    self.place.right = self.proRoom().rightXBoundary

            else:
                self.place.left = self.proRoom().leftXBoundary

            self.x = self.place.centerx

        elif self.place.right > self.proRoom().rightXBoundary:
            if (self.room[0] + 1, self.room[1], self.room[2]) in list(rooms.rooms.keys()):
                if (self.proRoom().locks and self.proRoom().foes) or self.proRoom().disconnected:
                    self.place.right = self.proRoom().rightXBoundary

                else:
                    self.room[0] += 1
                    self.place.left = self.proRoom().leftXBoundary

            else:
                self.place.right = self.proRoom().rightXBoundary

            self.x = self.place.centerx

        if self.place.top < self.proRoom().yBoundaries:
            if (self.room[0], self.room[1] + 1, self.room[2]) in list(rooms.rooms.keys()):
                if (self.proRoom().locks and self.proRoom().foes) or self.proRoom().disconnected:
                    self.place.top = self.proRoom().yBoundaries

                else:
                    self.room[1] += 1
                    self.place.bottom = self.proRoom().bottomYBoundary

            else:
                self.place.top = self.proRoom().yBoundaries

            self.y = self.place.centery

        elif self.place.bottom > self.proRoom().bottomYBoundary:
            if (self.room[0], self.room[1] - 1, self.room[2]) in list(rooms.rooms.keys()):
                if (self.proRoom().locks and self.proRoom().foes) or self.proRoom().disconnected:
                    self.place.bottom = self.proRoom().bottomYBoundary

                else:
                    self.room[1] -= 1
                    self.place.top = self.proRoom().yBoundaries

            else:
                self.place.bottom = self.proRoom().bottomYBoundary

            self.y = self.place.centery

        self.updateHitbox()

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

    def actions(self):
        """The actions function will perform all the player's actions."""
        self.getInput()
        self.updateStats()
        self.progressAnimation()
        returnedValues = []

        if self.useActiveItem():
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
