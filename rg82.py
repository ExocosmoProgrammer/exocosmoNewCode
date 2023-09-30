import math

import pygame
from definitions import draw, drawToFullScreen, lesser
from pro import player
from world import rooms
from variables import display, IMAGES

file = 1
pro = player()
enemyBullets = []


def proRoom():
    return rooms.rooms[tuple(pro.room)]


def drawGame():
    """The drawEverything function draws every sprite and flips the display."""
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
                display.blit(IMAGES['activeLionPit.png'], enemy.place)

        for bullet in pro.bullets:
            draw(bullet, bullet.rotation)

        for bullet in enemyBullets:
            draw(bullet, bullet.rotation)

        if pro.inventoryShown:
            pro.showInventory()

        pro.showInfo()

    else:
        pro.showMap()

    pygame.display.flip()


def foeActions():
    global enemyBullets

    for enemy in proRoom().foes:
        enemy.actAsFoe(pro)
        enemyBullets += enemy.newBullets
        enemy.newBullets = []



def moveBullets():
    for bullet in pro.bullets:
        bullet.move()

    for bullet in enemyBullets:
        bullet.move()


def checkCollisions():
    for bullet in pro.bullets:
        for foe in proRoom().foes:
            if foe.spawnDelay <= 0:
                if bullet.hitbox.checkCollision(foe.hitbox):
                    foe.hp -= bullet.damage
                    bullet.linger = 0

    if pro.invincibility <= 0:
        for bullet in enemyBullets:
            if bullet.hitbox.checkCollision(pro.hitbox):
                pro.hurt(bullet.damage)
                bullet.linger = 0
                break

        for foe in proRoom().foes:
            if foe.spawnDelay <= 0:
                if foe.hitbox.checkCollision(pro.hitbox):
                    pro.hurt(foe.damage)
                    break

        for trap in proRoom().damagingTraps:
            if trap.hitbox.checkCollision(pro.hitbox):
                pro.hurt(trap.damage)
                break

    for droppedItem in proRoom().droppedItems:
        if droppedItem.hitbox.checkCollision(pro.hitbox):
            try:
                pro.gainItem(droppedItem.item)
                proRoom().droppedItems.remove(droppedItem)

            except IndexError:
                pass


def removeFoes():
    for foe in proRoom().foes:
        if foe.hp <= 0:
            proRoom().foes.remove(foe)

            if not proRoom().foes:
                roomClearingProcedure()


def roomClearingProcedure():
    proRoom().wave += 1

    try:
        proRoom().foes = proRoom().waves[proRoom().wave].copy()

    except IndexError:
        pro.hp = lesser(130, pro.hp + 40)
        pro.hpRect = pygame.Rect(0, 3, pro.hp * display.get_width() / (10 * pro.maxHp), display.get_height() / 90)


def removeBullets():
    for bullet in enemyBullets:
        if bullet.linger <= 0:
            enemyBullets.remove(bullet)

    for bullet in pro.bullets:
        if bullet.linger <= 0:
            pro.bullets.remove(bullet)


def runGame():
    drawGame()
    pro.actions()
    foeActions()
    moveBullets()
    checkCollisions()
    removeFoes()
    removeBullets()


while pro.hp > 0:
    runGame()

while True:
    pygame.event.pump()
