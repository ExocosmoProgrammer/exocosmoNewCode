import math
import time
import datetime
import pygame

import proFile
import worldFile
from definitions import draw, drawToFullScreen, lesser, checkMouseCollision, loadWithPickle, saveWithPickle, play,\
    greater, sign
import random
from proFile import pro
from variables import display, IMAGES, width, height, GAMESPEED
from button import button
from bullets import bullet
from worldFile import rooms

enemyBullets = []
frameTime = 0
song = 'little_fugue.mp3'


def proRoom():
    """proRoom() returns the room the player is in."""
    return rooms.rooms[tuple(pro.room)]


currentRoom = proRoom()
# Last I tried using saving and loading, the player loaded properly, but the world did not load right.


def save():
    """save() should save the game."""
    saveWithPickle(f'playerSave{file}.pickle', pro)
    saveWithPickle(f'worldSave{file}.pickle', rooms)


def load():
    """load() should load the player's saved data."""
    global pro, rooms, agg
    newRooms = pro.loadRooms(file)

    if newRooms is not None:
        rooms = newRooms

    pro = loadWithPickle(f'playerSave{file}.pickle')
    worldFile.load(file)
    proFile.load(file)
    pro.aggressiveFoes = []


def drawGame():
    """drawGame() draws every sprite and flips the display."""
    if not pro.mapShown:
        drawToFullScreen(currentRoom.background)

        for door in currentRoom.doors:
            draw(door)

        for member in currentRoom.teleporters:
            draw(member)

        for trap in currentRoom.damagingTraps:
            draw(trap)

        for item in currentRoom.droppedItems:
            draw(item)

        draw(pro)

        for enemy in currentRoom.foes:
            if enemy.spawnDelay <= 0:
                if enemy.rotated:
                    draw(enemy, enemy.angle * -180 / math.pi)

                else:
                    draw(enemy)

            else:
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
        enemy.actAsFoe(pro)
        enemyBullets += enemy.newBullets
        currentRoom.foes += enemy.newFoes
        enemy.newFoes = []
        enemy.newBullets = []

    for enemy in pro.aggressiveFoes:
        if enemy.room[2] == pro.room[2] and enemy not in currentRoom.foes:
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
                enemy.chaseThroughRooms(pro, axis)
                rooms.rooms[tuple(enemy.room)].foes.append(enemy)


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

                if projectile.piercing < 0:
                    projectile.linger = 0

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
                pro.gainItem(droppedItem.item)
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
                if foe.spawnDelay <= 0:
                    if projectile.hitbox.checkCollision(foe.hitbox):
                        if foe.shieldedBy not in currentRoom.foes:
                            foe.hp -= projectile.damage

                        projectile.piercing -= 1

                        if projectile.piercing < 0:
                            projectile.linger = 0
                            break


def checkCollisions():
    """checkCollisions() checks collision for every case where collision needs to be checked."""
    checkCollisionWithPro()
    checkCollisionsToFoes()


def removeFoes():
    """removeFoes() gets rid of foes that have no hp left and handles other procedures for when
    foes are gotten rid of."""

    for foe in currentRoom.foes:
        if foe.hp <= 0:
            currentRoom.foes.remove(foe)

            try:
                pro.aggressiveFoes.remove(foe)

            except ValueError:
                pass

            if foe.spawnsOnDefeat is not None:

                for enemy in foe.spawnsOnDefeat:
                    enemy.spawnDelay = 1000
                    enemy.yBoundary = foe.yBoundary

                currentRoom.foes += foe.spawnsOnDefeat

            if not currentRoom.foes:
                roomClearingProcedure()


def roomClearingProcedure():
    """roomClearingProcedure() should add more enemies to the player's room or heal the player as is wanted."""
    currentRoom.wave += 1

    try:
        currentRoom.foes = currentRoom.waves[currentRoom.wave].copy()
        for foe in currentRoom.foes:
            foe.spawnDelay = 1000

    except IndexError:
        if currentRoom.locks:
            pro.hp = lesser(130, pro.hp + 40)
            pro.hpRect = pygame.Rect(0, 3, pro.hp * width / (10 * pro.maxHp), height / 90)
            currentRoom.foes = []
            save()
            currentRoom.locks = 0

            if currentRoom.coordinate == [0, 5, 1]:
                pro.startingRoom = [0, 5, 1]
                pro.startingCoord = [width / 2, 3 * height / 4]
                rooms.rooms[(0, 1, 10)].damagingTraps = []
                currentRoom.damagingTraps = []


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


def roomSwitchingProcedure():
    switchMusic()
    global currentRoom
    clearBullets()
    currentRoom = proRoom()

    for enemy in currentRoom.foes:
        if enemy not in pro.aggressiveFoes:
            pro.aggressiveFoes.append(enemy)

    for spot in rooms.rooms.values():
        if spot.difficulty == -1:
            try:
                spot.spawnFoesFromRoomSwitch()

            except AttributeError or IndexError:
                pass

    save()


def switchMusic():
    global song
    depth = currentRoom.coordinate[2]
    print(depth, currentRoom.biome)
    initialSong = song

    if currentRoom.biome == 'ship':
        song = 'shelter.mp3'

    elif currentRoom.biome == 'desert':
        if depth == -1:
            song = 'fantasyInDMinorByMozart.mp3'

        elif depth == -2:
            song = 'PreludeNo8Book1.mp3'

        elif depth == -3:
            song = 'little_fugue.mp3'

    if initialSong != song:
        play(song)


def runGame():
    global currentRoom
    initialTime = datetime.datetime.now()
    initialRoom = proRoom()
    pro.actions()
    currentRoom = proRoom()
    foeActions()
    moveBullets()
    checkCollisions()
    removeBullets()
    drawGame()
    removeFoes()
    proRoom().action()

    if initialRoom != currentRoom:
        roomSwitchingProcedure()

    return datetime.datetime.now() - initialTime


startButton = button('startButton.png', width / 2, height / 2)
exitButton = button('exitButton.png', width / 2, height * 2 / 3)
save1Button = button('save1Button.png', width / 2, height / 2)
save2Button = button('save2Button.png', width / 2, height * 5 / 8)
save3Button = button('save3Button.png', width / 2, height * 3 / 4)
backButton = button('backButton.png', width / 2, height * 7 / 8)
menu = 'title'
file = None

while file is None:
    drawToFullScreen('titleScreenBackground.png')

    if menu == 'title':
        draw(startButton)
        draw(exitButton)

        if pygame.event.get(pygame.MOUSEBUTTONDOWN, pump=False):

            if checkMouseCollision(startButton.hitbox):
                menu = 'saveSelection'

            elif checkMouseCollision(exitButton.hitbox):
                assert False

    elif menu == 'saveSelection':
        for i in range(1, 4):
            exec(f'draw(save{i}Button)')

        if pygame.event.get(pygame.MOUSEBUTTONDOWN, pump=False):
            for i in range(1, 4):
                exec(f"if checkMouseCollision(save{i}Button.hitbox): file = {i}")

    pygame.event.pump()
    pygame.display.flip()

load()

while pro.hp > -float(0):
    time.sleep(greater(0.0336 - runGame().seconds, 0))

while True:
    pygame.event.pump()
