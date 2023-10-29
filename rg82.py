import math
import time

import pygame
from definitions import draw, drawToFullScreen, lesser, checkMouseCollision, loadWithPickle, saveWithPickle, play
from pro import player
from variables import display, IMAGES, width, height, GAMESPEED
from button import button
from bullets import bullet
from world import rooms

pro = player()
enemyBullets = []
# play('music/little_fugue.mp3')


def proRoom():
    """proRoom() returns the room the player is in."""
    return rooms.rooms[tuple(pro.room)]


# Last I tried using saving and loading, the player loaded properly, but the world did not load right.


def save():
    """save() should save the game."""
    saveWithPickle(f'playerSave{file}.pickle', pro)
    saveWithPickle(f'worldSave{file}.pickle', rooms)


def load():
    """load() should load the player's saved data."""
    global pro, rooms
    rooms = loadWithPickle(f'worldSave{file}.pickle')
    pro = loadWithPickle(f'playerSave{file}.pickle')


def drawGame():
    """drawGame() draws every sprite and flips the display."""
    if not pro.mapShown:
        drawToFullScreen(proRoom().background)

        for door in rooms.rooms[tuple(pro.room)].doors:
            draw(door)

        for trap in proRoom().damagingTraps:
            draw(trap)

        for item in proRoom().droppedItems:
            draw(item)

        draw(pro)

        for enemy in proRoom().foes:
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

        for enemy in proRoom().foes:
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

    for enemy in proRoom().foes:
        enemy.actAsFoe(pro)
        enemyBullets += enemy.newBullets
        proRoom().foes += enemy.newFoes
        enemy.newFoes = []
        enemy.newBullets = []


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


def checkCollisionWithPro():
    """checkCollisionWithPro() should check if things are colliding with the player."""

    if pro.invincibility <= 0:
        for projectile in enemyBullets:
            if eval(projectile.checksCollisionWhen) and projectile.delay <= 0:
                if projectile.hitbox.checkCollision(pro.hitbox):
                    pro.hurt(projectile.damage)
                    projectile.piercing -= 1

                    if projectile.piercing < 0:
                        projectile.linger = 0

                    return 1

        for foe in proRoom().foes:
            if foe.spawnDelay <= 0:
                if foe.hitbox.checkCollision(pro.hitbox):
                    pro.hurt(foe.damage)
                    return 1

        for trap in proRoom().damagingTraps:
            if trap.hitbox.checkCollision(pro.hitbox):
                pro.hurt(trap.damage)
                return 1

    for droppedItem in proRoom().droppedItems:
        if droppedItem.hitbox.checkCollision(pro.hitbox):
            try:
                pro.gainItem(droppedItem.item)
                proRoom().droppedItems.remove(droppedItem)

            except IndexError:
                pass


def checkCollisionsToFoes():
    """checkCollisionsToFoes() should check if player projectiles are colliding with foes."""
    for projectile in pro.bullets:
        if eval(projectile.checksCollisionWhen):
            for foe in proRoom().foes:
                if foe.spawnDelay <= 0:
                    if projectile.hitbox.checkCollision(foe.hitbox):
                        if foe.shieldedBy not in proRoom().foes:
                            foe.hp -= projectile.damage

                        projectile.piercing -= 1

                        if projectile.piercing < 0:
                            projectile.linger = 0


def checkCollisions():
    """checkCollisions() checks collision for every case where collision needs to be checked."""
    checkCollisionWithPro()
    checkCollisionsToFoes()


def removeFoes():
    """removeFoes() gets rid of foes that have no hp left and handles other procedures for when
    foes are gotten rid of."""

    for foe in proRoom().foes:
        if foe.hp <= 0:
            proRoom().foes.remove(foe)

            if foe.spawnsOnDefeat is not None:

                for enemy in foe.spawnsOnDefeat:
                    enemy.spawnDelay = 1000
                    enemy.yBoundary = foe.yBoundary

                proRoom().foes += foe.spawnsOnDefeat

            if not proRoom().foes:
                roomClearingProcedure()


def roomClearingProcedure():
    """roomClearingProcedure() should add more enemies to the player's room or heal the player as is wanted."""
    proRoom().wave += 1

    try:
        proRoom().foes = proRoom().waves[proRoom().wave].copy()
        for foe in proRoom().foes:
            foe.spawnDelay = 1000

    except IndexError:
        pro.hp = lesser(130, pro.hp + 40)
        pro.hpRect = pygame.Rect(0, 3, pro.hp * width / (10 * pro.maxHp), height / 90)
        proRoom().foes = []
        save()


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


def runGame():
    """runGame() runs the game."""
    pro.actions()
    foeActions()
    moveBullets()
    checkCollisions()
    removeFoes()
    removeBullets()
    drawGame()


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


while pro.hp > -float('inf'):
    runGame()
    time.sleep(0.028)

while True:
    pygame.event.pump()
