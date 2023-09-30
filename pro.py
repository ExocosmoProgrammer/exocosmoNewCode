import keyboard
import pygame
from world import rooms
from variables import IMAGES, GAMESPEED, display, FILE, MOVESPEED
from definitions import getDirection, lesser, getPath, draw, checkMouseCollision, loadWithPickle, saveWithPickle
from rects import rect
from bullets import bullet
from item import item
from plainSprites import plainSprite


class player:
    def __init__(self, **extra):
        self.maxHp = 130
        self.hp = 130
        self.fireCooldown = 0
        self.inventoryShown = 0
        self.sprite = 'newWalkingAnimation_s1.png'
        self.place = IMAGES[self.sprite].get_rect(center=(display.get_size()[0] / 2, display.get_size()[1] / 2))
        self.room = [0, 0, 10]

        # I use self.x and self.y as coordinates so the bullet's coordinates will be tracked more precisely,
        # since the player's place's coordinates are rounded each frame.

        self.x = self.place.centerx
        self.y = self.place.centery
        self.bullets = []
        self.hitbox = rect(pygame.Rect(self.place.left, self.place.top + 20, self.place.width,
                                       self.place.height - 20), 0)

        # The animations are dictionaries with each key representing a direction and the key's value being an
        # animation for if you face the direction the key represents.

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

        # hr and vr represent horizontal movement per frame and vertical movement per frame.

        self.hr = (keyboard.is_pressed('d') - keyboard.is_pressed('a')) * GAMESPEED
        self.vr = (keyboard.is_pressed('s') - keyboard.is_pressed('w')) * GAMESPEED

        # When you turn to face a different way, your animation is set to your directionlessAnimation's
        # value corresponding to your direction.

        self.animation = self.idleAnimation['s'].copy()
        self.directionlessAnimation = self.idleAnimation
        self.animationFrame = 0
        self.direction = 's'
        self.slideTime = 0
        self.mapShown = 0
        self.stamina = 100
        self.hpRect = pygame.Rect(0, 3, display.get_width() / 10, display.get_height() / 90)
        self.hpGoneRect = pygame.Rect(0, 3, display.get_width() / 10, display.get_height() / 90)
        self.bullets = []
        self.invincibility = 0
        self.speed = 0.5
        self.itemFunctions = {'nanotechRevolver': self.useNanotechRevolver}
        self.inventory = []
        self.inventoryBoxes = []
        boxWidth = IMAGES['inventoryBox.png'].get_width()
        boxHeight = IMAGES['inventoryBox.png'].get_height()
        self.emptySlots = []

        for i in range(3):
            for j in range(10):
                self.inventoryBoxes.append(plainSprite(
                    'inventoryBox.png', j * boxWidth * 2 + display.get_width() * 13 / 80 + boxWidth / 2,
                    i * 3 * boxHeight + display.get_height() * 7 / 30 + boxHeight / 2))

        for i in range(100):
            self.inventory.append(item('empty', 'invisiblePixels.png'))

        self.activeItem = self.inventory[0]

        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')

    def switchAnimation(self, animation):
        """The switchAnimation function should change your animation and directionlessAnimation and take you
        to the start of your new animation."""
        self.directionlessAnimation = animation
        self.animationFrame = 0

    def gainItem(self, itemGained):
        self.emptySlots = [i for i in self.inventory[0:30] if i.name == 'empty']
        self.inventory[self.inventory.index(self.emptySlots[0])] = itemGained

    def hurt(self, damage):
        self.hp -= damage
        self.invincibility = 250
        self.hpRect = pygame.Rect(0, 3, self.hp * display.get_width() / (10 * self.maxHp), display.get_height() / 90)

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

        elif self.directionlessAnimation == self.walkingAnimation and self.vr == self.hr == 0:
            self.switchAnimation(self.idleAnimation)

        elif self.animationFrame > len(self.animation) - 1:
            self.animationFrame = 0

        self.animation = self.directionlessAnimation[self.direction]
        self.sprite = self.animation[int(self.animationFrame)]

    def slide(self):
        """Later, the slide function should take away stamina but temporarily increase your speed. My brother wanted
        the ability to slide in this game."""
        if self.stamina >= 25 and self.slideTime <= 0:
            self.slideTime = 50
            self.stamina -= 100
            self.invincibility = 2

    def dash(self):
        if self.stamina == 500 and self.slideTime <= 0:
            self.slideTime = 150
            self.stamina = 0
            self.invincibility = 250

    def useActiveItem(self):
        if pygame.mouse.get_pressed()[0] and self.fireCooldown <= 0:
            try:
                self.itemFunctions[self.activeItem.name]()

            except KeyError:
                pass

    def useNanotechRevolver(self):
        """The useNanotechRevolver function will be your attack while your active item is the nanotechRevolver."""
        path = getPath(GAMESPEED * 3, (self.x, self.y), pygame.mouse.get_pos())
        self.bullets.append(bullet(path[0], path[1], 1, 'basicRangeProjectile_d.png', self.x, self.y))
        self.fireCooldown = 100

    def getInput(self):
        """The getInput function will have actions being performed based on player input."""
        self.hr = (keyboard.is_pressed('d') - keyboard.is_pressed('a'))
        self.vr = (keyboard.is_pressed('s') - keyboard.is_pressed('w'))

        if self.inventoryShown:
            self.updateInventory()

        if pygame.mouse.get_pressed()[0]:
            pass

        for event in pygame.event.get(pygame.KEYDOWN):

            if event.key == pygame.K_l:
                print('shown')
                if self.inventoryShown:
                    self.inventoryShown = 0

                else:
                    self.inventoryShown = 1
                    self.updateItemPositions()

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

            elif pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.slide()

            elif pygame.key.get_mods() & pygame.KMOD_SHIFT:
                self.dash()

            else:
                for i in range(10):
                    exec(f'if event.key == pygame.K_{i}: self.activeItem = self.inventory[{i}]')

    def updateStats(self):
        """The updateStats function should modify your attributes each frame."""
        self.slideTime -= GAMESPEED
        self.stamina = lesser(self.stamina + GAMESPEED, 500)
        self.fireCooldown -= GAMESPEED
        self.invincibility -= 1

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
            if thing.name != 'empty':
                draw(thing)

    def showInfo(self):
        display.fill("#1abdbd", self.hpGoneRect)
        display.fill("#cd300e", self.hpRect)
        display.fill('#90b133', pygame.Rect(0, display.get_height() / 20, display.get_width() / 10,
                                  display.get_height() / 90))
        staminaRect = pygame.Rect(0, display.get_height() / 20, display.get_width() * self.stamina / 5000,
                                  display.get_height() / 90)
        display.fill("#1abdbd", staminaRect)

    def updateInventory(self):
        dragging = 0

        for thing in self.inventory:
            if thing.dragged:
                draggedItem = thing
                dragging = 1
                thing.place.centerx, thing.place.centery = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                thing.updateHitbox()
                break

        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN, pump=False):
            for thing in self.inventory:
                if thing.dragged == 0 and checkMouseCollision(thing.hitbox):
                    if pygame.mouse.get_pressed()[0]:
                        thing.dragged = 1

                        if dragging:
                            draggedItemIndex = self.inventory.index(draggedItem)
                            thingIndex = self.inventory.index(thing)
                            self.inventory[thingIndex] = draggedItem
                            self.inventory[draggedItemIndex] = thing
                            box = self.inventoryBoxes[thingIndex]
                            draggedItem.dragged = 0
                            draggedItem.place.centerx, draggedItem.place.centery = box.place.centerx, box.place.centery
                            draggedItem.updateHitbox()

    def showMap(self):
        display.fill((0, 0, 0))

        for coordinate in list(rooms.rooms.keys()):
            if coordinate[2] == self.room[2] and abs(self.room[1] - coordinate[1]) < 6 \
                    and abs(self.room[0] - coordinate[0]) < 6:
                print(coordinate)
                display.blit(IMAGES[rooms.rooms[coordinate].mapMarker],
                             pygame.Rect(display.get_width() * (311 / 640 + (coordinate[0] - self.room[0]) * 47 / 1600),
                                         display.get_height() * (434 / 900 - (coordinate[1] - self.room[1]) * 17 / 450),
                                         9 * display.get_width() / 320, 8 * display.get_height() / 225))

                if coordinate == tuple(self.room):
                    display.blit(IMAGES['playerRoomMapImage.png'],
                                 pygame.Rect(
                                     display.get_width() * 311 / 640, display.get_height() * 434 / 900,
                                     9 * display.get_width() / 320, 8 * display.get_height() / 225))

    def move(self):
        """The move function makes the player move."""
        if self.slideTime < 0:
            self.x += self.hr * GAMESPEED * self.speed * MOVESPEED
            self.y += self.vr * GAMESPEED * self.speed * MOVESPEED

        else:
            self.x += self.hr * GAMESPEED * 4 * MOVESPEED
            self.y += self.vr * GAMESPEED * 4 * MOVESPEED
            self.slideTime -= GAMESPEED

        self.hitbox.move(self.hr * GAMESPEED * MOVESPEED, self.vr * GAMESPEED * MOVESPEED)
        self.place.centerx = self.x
        self.place.centery = self.y
        self.hitbox = rect(pygame.Rect(self.place.left, self.place.top + 20, self.place.width, self.place.height - 20), 0)
        # The next twelve lines of code should make the display's edges act as boundaries.

        if self.place.left < 0:
            if (self.room[0] - 1, self.room[1], self.room[2]) in list(rooms.rooms.keys()):
                if rooms.rooms[tuple(self.room)].locks and rooms.rooms[tuple(self.room)].foes:
                    self.place.left = 0

                else:
                    self.place.right = display.get_width()
                    self.room[0] -= 1

            else:
                self.place.left = 0
            self.x = self.place.centerx

        elif self.place.right > display.get_width():
            if (self.room[0] + 1, self.room[1], self.room[2]) in list(rooms.rooms.keys()):
                if rooms.rooms[tuple(self.room)].locks and rooms.rooms[tuple(self.room)].foes:
                    self.place.right = display.get_width()

                else:
                    self.place.left = 0
                    self.room[0] += 1

            else:
                self.place.right = display.get_width()
            self.x = self.place.centerx

        if self.place.top < rooms.rooms[tuple(self.room)].yBoundaries[0]:
            if (self.room[0], self.room[1] + 1, self.room[2]) in list(rooms.rooms.keys()):
                if rooms.rooms[tuple(self.room)].locks and rooms.rooms[tuple(self.room)].foes:
                    self.place.top = rooms.rooms[tuple(self.room)].yBoundaries[0]

                else:
                    self.place.bottom = display.get_height()
                    self.room[1] += 1

            else:
                self.place.top = rooms.rooms[tuple(self.room)].yBoundaries[0]
            self.y = self.place.centery

        elif self.place.bottom > display.get_height():
            if (self.room[0], self.room[1] - 1, self.room[2]) in list(rooms.rooms.keys()):
                if rooms.rooms[tuple(self.room)].locks and rooms.rooms[tuple(self.room)].foes:
                    self.place.bottom = display.get_height()

                else:
                    self.place.top = rooms.rooms[tuple(self.room)].yBoundaries[0]
                    self.room[1] -= 1

            else:
                self.place.bottom = display.get_height()
            self.y = self.place.centery

    def loadGame(self):
        """The loadGame function should load the player info and the world info."""
        global pro, rooms

        pro = loadWithPickle(f'playerSave{FILE}.pickle')
        rooms = loadWithPickle(f'worldSave{FILE}.pickle')

    def saveGame(self):
        """The saveGame function should save the player info and the world info."""
        saveWithPickle(f'playerSave{FILE}.pickle', player)
        saveWithPickle(f'worldSave{FILE}.pickle', rooms)

    def actions(self):
        """The actions function will perform all the player's actions."""
        self.getInput()
        self.updateStats()
        self.move()
        self.progressAnimation()
        self.useActiveItem()