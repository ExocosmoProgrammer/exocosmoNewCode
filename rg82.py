import math
import sys
import time
import datetime
import pygame
import copy

from definitions import draw, drawToFullScreen, lesser, checkMouseCollision, loadWithPickle, saveWithPickle,\
    greater, sign, pointDistance, percentChance, getPath, getDegrees, sqrt
from droppedItem import droppedItem
import random
from variables import display, IMAGES, width, height, GAMESPEED, diagonal
from button import button
from pro import player
from temporaryAnimation import temporaryAnimation
from bullets import bullet
from foe import foe

enemyBullets = []
pro = player()
startButton = button('whiteStartButton.png', width * 41 / 50, height * 7 / 12,
                     spriteWhenTouchingMouse='redStartButton.png')
exitButton = button('whiteExitButton.png', width * 41 / 50, height * 17 / 24,
                    spriteWhenTouchingMouse='redExitButton.png')
save1Button = button('whiteSave1Button.png', width * 41 / 50, height * 9 / 16,
                     spriteWhenTouchingMouse='redSave1Button.png')
save2Button = button('whiteSave2Button.png', width * 41 / 50, height * 11 / 16,
                     spriteWhenTouchingMouse='redSave2Button.png')
save3Button = button('whiteSave3Button.png', width * 41 / 50, height * 13 / 16,
                     spriteWhenTouchingMouse='redSave3Button.png')
menu = 'title'

file = None

while file is None:
    drawToFullScreen('exocosmoNewTitleScreen.bmp')

    if menu == 'title':
        startButton.draw()
        exitButton.draw()

        if pygame.event.get(pygame.MOUSEBUTTONDOWN, pump=False):

            if checkMouseCollision(startButton.hitbox):
                menu = 'saveSelection'

            elif checkMouseCollision(exitButton.hitbox):
                assert False

    elif menu == 'saveSelection':
        for i in range(1, 4):
            exec(f'save{i}Button.draw()')

        if pygame.event.get(pygame.MOUSEBUTTONDOWN, pump=False):
            for i in range(1, 4):
                exec(f"if checkMouseCollision(save{i}Button.hitbox): file = {i}")

    pygame.event.pump()
    pygame.display.flip()


def load():
    """load() should load the player's saved data."""
    global pro, rooms

    try:
        newRooms = pro.loadRooms(file)

        if newRooms is not None:
            rooms = newRooms

        pro = loadWithPickle(f'playerSave{file}.pickle')
        pro.aggressiveFoes = []
        pro.hr = 0
        pro.vr = 0

        for room in rooms.rooms.values():
            room.getUpdate()

            for enemy in room.foes:
                enemy.getUpdate()

        pro.getUpdate()

    except FileNotFoundError or EOFError:
        rooms = pro.resetRooms()
        pro = player()


load()


def proRoom():
    """proRoom() returns the room that the player is in."""
    return rooms.rooms[tuple(pro.room)]


currentRoom = proRoom()


def getNearbyFoes():
    foes = []

    for i in range(-3, 4):
        for j in range(-3, 4):
            try:
                foes += rooms.rooms[pro.room[0] + i, pro.room[1] + j, pro.room[2]].foes

            except KeyError:
                pass

    return foes


def save():
    """save() should save the game."""
    if True:
        saveWithPickle(f'playerSave{file}.pickle', pro)
        saveWithPickle(f'worldSave{file}.pickle', rooms)


def drawGame():
    """drawGame() draws every sprite and flips the display."""
    if not pro.mapShown:
        drawToFullScreen(currentRoom.background)

        for door in currentRoom.doors:
            draw(door)

        for sprite in currentRoom.plainSprites:
            draw(sprite)

        for member in currentRoom.teleporters:
            member.functionToGetSprite(pro, currentRoom.locks and currentRoom.foes)
            draw(member)

        for trap in currentRoom.damagingTraps:
            trap.progressAnimation()
            draw(trap)

        for item in currentRoom.droppedItems:
            draw(item)

        for critter in currentRoom.passiveCritters:
            draw(critter)

        for obj in currentRoom.environmentObjects:
            if obj.place.bottom <= pro.place.bottom:
                draw(obj)

        draw(pro)

        for enemy in currentRoom.foes:
            if enemy.spawnDelay <= 0:
                if enemy.rotated:
                    draw(enemy, enemy.angle * -180 / math.pi)

                else:
                    draw(enemy)

            else:
                if hasattr(enemy, 'delayAnimation'):
                    enemy.delayFrame += GAMESPEED

                    if int(enemy.delayFrame) > len(enemy.delayAnimation) - 1:
                        enemy.delayFrame = 0

                    enemy.delaySprite = enemy.delayAnimation[enemy.delayFrame]
                    enemy.place = IMAGES[enemy.delaySprite].get_rect(center=(enemy.x, enemy.y))

                display.blit(IMAGES[enemy.delaySprite], enemy.place)

        for projectile in pro.bullets:
            if projectile.delay <= 0:
                draw(projectile, projectile.rotation)

            else:
                display.blit(IMAGES[projectile.getSpriteWhenDelayed()], projectile.place)

        for projectile in enemyBullets:
            if projectile.delay <= 0:
                draw(projectile, projectile.rotation)

            else:
                display.blit(IMAGES[projectile.getSpriteWhenDelayed()], projectile.place)

        for obj in currentRoom.environmentObjects:
            if obj.place.bottom > pro.place.bottom:
                draw(obj)

        for animation in currentRoom.temporaryAnimations:
            draw(animation)

            if animation.progressAnimation():
                currentRoom.temporaryAnimations.remove(animation)

        for enemy in currentRoom.foes:
            if enemy.showsHp:
                enemy.showHp()

        if pro.inventoryShown:
            pro.showInventory()

        pro.showInfo()

    else:
        pro.showMap()

    pygame.display.flip()


def foeActions():
    """foeActions() should make foes act."""
    global enemyBullets

    for enemy in currentRoom.foes:
        if enemy not in pro.aggressiveFoes:
            if enemy.spawnDelay <= 0:
                enemy.wanderingMethod(rooms)

                if pointDistance((enemy.x, enemy.y), (pro.x, pro.y)) <= \
                        enemy.aggressionRadius * diagonal / 1836 and enemy in currentRoom.foes:
                    pro.aggressiveFoes.append(enemy)

                    if enemy.locksRoomOnAggression:
                        proRoom().locks = True

            else:
                enemy.spawnDelay -= GAMESPEED

    for enemy in pro.aggressiveFoes:
        if enemy.room[2] == pro.room[2]:
            if enemy not in currentRoom.foes:
                axisChoices = ['x', 'y']

                if enemy.room[0] == pro.room[0] or (enemy.room[0] + sign(pro.room[0] - enemy.room[0]),
                                                    enemy.room[1], enemy.room[2]) not in rooms.rooms:
                    axisChoices.remove('x')

                if enemy.room[1] == pro.room[1] or (enemy.room[0], enemy.room[1] + sign(pro.room[1] - enemy.room[1]),
                                                    enemy.room[2]) not in rooms.rooms:
                    axisChoices.remove('y')

                if axisChoices:
                    try:
                        rooms.rooms[tuple(enemy.room)].foes.remove(enemy)

                    except ValueError:
                        pass

                    axis = random.choice(axisChoices)
                    enemy.chaseThroughRooms(pro, axis, rooms)
                    rooms.rooms[tuple(enemy.room)].foes.append(enemy)

            else:
                enemy.actAsFoe(pro, rooms, currentRoom)
                enemyBullets += enemy.newBullets
                currentRoom.foes += enemy.newFoes
                enemy.newFoes = []
                enemy.newBullets = []


def passiveCritterActions():
    for critter in currentRoom.passiveCritters:
        critter.action()


def clearBullets():
    global enemyBullets
    enemyBullets = []
    pro.bullets = []


def moveBullets():
    """moveBullets() should move every bullet."""
    for projectile in pro.bullets:
        if projectile.delay <= 0:
            projectile.move()

            for key in projectile.conditionalEffects.keys():
                if eval(key):
                    exec(projectile.conditionalEffects[key])

        else:
            projectile.delay -= GAMESPEED

    for projectile in enemyBullets:
        if projectile.delay <= 0:
            projectile.move()

            for key in projectile.conditionalEffects.keys():
                if eval(key):
                    exec(projectile.conditionalEffects[key])

        else:
            projectile.delay -= GAMESPEED


# Separating checkCollision into the next two functions helps me prevent many things  from damaging the player in
# one tick. I do this by returning one in the next function when something hurts the player.


def checkDamagingCollisionsToPro():
    if pro.invincibility <= 0:
        for projectile in enemyBullets:
            if eval(projectile.checksCollisionWhen) and projectile.delay <= 0 and \
                    projectile.hitbox.checkCollision(pro.hitbox):
                pro.hurt(projectile.damage)
                projectile.piercing -= 1
                exec(projectile.playerContactEffect)

                if projectile.piercing < 0:
                    projectile.linger = 0

                if projectile.impactAnimation is not None:
                    currentRoom.temporaryAnimations.append(temporaryAnimation(projectile.impactAnimation,
                                                                              projectile.x, projectile.y))

                return 1

        for foe in currentRoom.foes:
            if foe.spawnDelay <= 0 < foe.damage and foe.hitbox.checkCollision(pro.hitbox):
                pro.hurt(foe.damage)

                return 1

        for trap in currentRoom.damagingTraps:
            if trap.hitbox.checkCollision(pro.hitbox):
                pro.hurt(trap.damage)
                return 1


def checkDroppedItemCollisionsWithPro():
    for droppedItem in currentRoom.droppedItems:
        if droppedItem.hitbox.checkCollision(pro.hitbox):
            try:
                droppedItem.item.qty = pro.gainItem(droppedItem.item)

                if droppedItem.item.qty == 0:
                    currentRoom.droppedItems.remove(droppedItem)

            except IndexError:
                pass


def checkTeleporterCollisionsWithPro():
    if not currentRoom.foes:
        for member in currentRoom.teleporters:
            if pro.hitbox.checkCollision(member.hitbox):
                pro.room = member.destination[:]
                pro.x = member.destinationX
                pro.y = member.destinationY
                pro.move()
                clearBullets()
                time.sleep(1)
                drawGame()
                time.sleep(1)
                roomSwitchingProcedure()


def checkCollisionWithPro():
    """checkCollisionWithPro() should check if things are colliding with the player."""
    checkDamagingCollisionsToPro()
    checkDroppedItemCollisionsWithPro()
    checkTeleporterCollisionsWithPro()


def checkCollisionsToFoes():
    """checkCollisionsToFoes() should check if player projectiles are colliding with foes."""
    for projectile in pro.bullets:
        if eval(projectile.checksCollisionWhen):
            for foe in currentRoom.foes:
                if foe.spawnDelay <= 0 and foe.hp > 0:
                    if projectile.hitbox.checkCollision(foe.hitbox):
                        if foe.shieldedBy not in currentRoom.foes:
                            foe.hp -= projectile.damage

                        projectile.piercing -= 1

                        if projectile.piercing < 0:
                            projectile.linger = 0

                            if projectile.impactAnimation is not None:
                                currentRoom.temporaryAnimations.append(temporaryAnimation(projectile.impactAnimation,
                                                                                          projectile.x, projectile.y))

                        break


def checkCollisionsToEnvironmentObjects():
    for thing in currentRoom.environmentObjects:
        for projectile in pro.bullets + enemyBullets:
            if projectile.hitbox.checkCollision(thing.hitbox):
                projectile.piercing -= 1
                thing.hp -= projectile.damage

                if thing.hp <= 0 and thing in currentRoom.environmentObjects:
                    currentRoom.environmentObjects.remove(thing)

                    try:
                        currentRoom.droppedItems.append(thing.drops)

                    except AttributeError:
                        pass

                if projectile.piercing < 0:
                    projectile.linger = 0

                    if projectile.impactAnimation is not None:
                        currentRoom.temporaryAnimations.append(temporaryAnimation(projectile.impactAnimation,
                                                                                  projectile.x, projectile.y))


def checkCollisions():
    """checkCollisions() checks collision for every case where collision needs to be checked."""
    checkCollisionWithPro()
    checkCollisionsToFoes()
    checkCollisionsToEnvironmentObjects()


def removeFoes():
    """removeFoes() gets rid of foes that have no hp left and handles other procedures for when
    foes are gotten rid of."""

    for foe in currentRoom.foes:

        if foe.hp <= 0:
            while foe in currentRoom.foes:
                currentRoom.foes.remove(foe)

            while foe in pro.aggressiveFoes:
                pro.aggressiveFoes.remove(foe)

            if foe.deathAnimation is not None:
                currentRoom.temporaryAnimations.append(temporaryAnimation(foe.deathAnimation, foe.x, foe.y))

            if foe.spawnsOnDefeat is not None:

                for enemy in foe.spawnsOnDefeat:
                    enemy.spawnDelay = 1000
                    enemy.yBoundary = foe.yBoundary

                currentRoom.foes += foe.spawnsOnDefeat

            for thing in foe.loot:
                if percentChance(thing[1]):
                    currentRoom.droppedItems.append(droppedItem(foe.x, foe.y, thing[0].sprite, thing[0].item))

            if not currentRoom.foes:
                roomClearingProcedure()


def roomClearingProcedure():
    """roomClearingProcedure() should add more enemies to the player's room or heal the player as is wanted."""
    currentRoom.wave += 1

    if currentRoom.locks:
        try:
            currentRoom.foes = currentRoom.waves[currentRoom.wave].copy()

            for foe in currentRoom.foes:
                foe.spawnDelay = 250

        except IndexError:
            pro.hp = lesser(130, pro.hp + 40)
            pro.hpRect = pygame.Rect(0, 3, pro.hp * width / (10 * pro.maxHp), height / 90)
            currentRoom.foes = []

            if currentRoom.coordinate == [0, 4, 10]:
                pro.startingRoom = [0, 4, 10]
                rooms.rooms[(0, 4, 10)].foesUponRespawn = []

            if currentRoom.coordinate == [0, 5, 10]:
                pro.startingRoom = [0, 5, 10]
                pro.startingCoord = [width / 2, 3 * height / 4]
                rooms.rooms[(0, 1, 10)].damagingTraps = []
                currentRoom.damagingTraps = []

                for i in range(6):
                    rooms.rooms[(0, i, 10)].foesUponRespawn = []

            save()

    else:
        currentRoom.foesUponRespawn = []
        save()

    if currentRoom.isBossRoom and not currentRoom.foes:
        currentRoom.respawnsFoes = False


def removeBullets():
    """removeBullets() should get rid of projectiles as appropriate."""
    for projectile in enemyBullets:
        if projectile.linger <= 0:
            enemyBullets.remove(projectile)
            exec(projectile.endEffect)

    for projectile in pro.bullets:
        if projectile.linger <= 0:
            pro.bullets.remove(projectile)
            exec(projectile.endEffect)


def removeEnvironmentObjects():
    for obj in currentRoom.environmentObjects:
        if obj.hp <= 0:
            currentRoom.environmentObjects.remove(obj)


def handleScaryCooldownAndSpawningScary():
    global currentRoom

    if currentRoom.background == 'desertCaveLumisLake.bmp':
        pro.scaryCooldown -= 1

    if pro.scaryCooldown <= 0:
        currentRoom.foes.append(foe('scary', width / 2, height / 2, currentRoom.coordinate, spawnDelay=770))
        pro.scaryCooldown = 2


def roomSwitchingProcedure():
    #switchMusic()
    global currentRoom
    clearBullets()
    currentRoom = proRoom()
    pro.bullets = []
    pro.invincibility = 200
    handleScaryCooldownAndSpawningScary()

    for spot in rooms.rooms.values():
        if spot.difficulty == -1:
            try:
                spot.spawnFoesFromRoomSwitch()

            except AttributeError or IndexError:
                pass

        spot.spawnResourcesFromRoomSwitch()

    save()


# def switchMusic():
#     global song
#     depth = currentRoom.coordinate[2]
#     initialSong = song
#
#     if currentRoom.biome == 'ship':
#         song = 'shelter.mp3'
#
#     elif currentRoom.biome == 'desert':
#         if depth == -1:
#             song = 'fantasyInDMinorByMozart.mp3'
#
#         elif depth == -2:
#             song = 'PreludeNo8Book1.mp3'
#
#         elif depth == -3:
#             song = 'little_fugue.mp3'
#
#     if initialSong != song:
#         play(song)


def runGame():
    global currentRoom
    initialTime = datetime.datetime.now()
    initialRoom = proRoom()
    drawGame()

    if pro.actions():
        # TODO make this block's work be done in pro.py.

        for enemy in proRoom().foes:
            if enemy not in pro.aggressiveFoes:
                pro.aggressiveFoes.append(enemy)

                if enemy.locksRoomOnAggression:
                    proRoom().locks = True

    currentRoom = proRoom()
    foeActions()
    moveBullets()
    checkCollisions()
    removeBullets()
    removeFoes()
    passiveCritterActions()
    currentRoom.action()

    if initialRoom != currentRoom:
        roomSwitchingProcedure()

    return datetime.datetime.now() - initialTime


def respawn():
    global enemyBullets

    for room in rooms.rooms.values():
        if room.environmentObjectsUponRespawn is not None:
            room.environmentObjects = room.environmentObjectsUponRespawn.copy()

        if room.respawnsFoes:
            room.foes = [copy.deepcopy(enemy) for enemy in room.foesUponRespawn]
            room.wave = -1
            room.waves = []

            for i in room.wavesUponRespawn.copy():
                waveAdded = []

                for j in i:
                    waveAdded.append(copy.deepcopy(j))

                room.waves.append(waveAdded)

        for enemy in room.foes:
            enemy.hp = enemy.initialHp

        room.locks = room.usuallyLocks

    pro.room = pro.startingRoom.copy()
    pro.x = pro.startingCoord[0]
    pro.y = pro.startingCoord[1]
    pro.hp = pro.maxHp + 1
    pro.hurt(1)
    pro.hp += 1
    pro.aggressiveFoes = []
    enemyBullets = []
    pro.bullets = []


while True:
    while pro.hp > -float('0'):
        try:
            time.sleep(greater(0.0381 - runGame().seconds, 0))

        except KeyboardInterrupt:
            pro.hr = 0
            pro.vr = 0
            save()
            sys.exit(0)

    respawn()
