import random

import pygame

from plainSprites import plainSprite
from droppedItem import droppedItem
from variables import (width, height, GAMESPEED, environmentObjectsPerBiome, IMAGES, plainSpritesPerBiome,
                       randomDamagingTrapsPerBiome)
from foe import foe
from definitions import skip, percentChance, greater
from environmentObject import environmentObject
from rects import rect
from damagingTrap import damagingTrap


class room:
    def __init__(self, coordinate, biome, **extra):
        self.foes = []
        self.coordinate = coordinate
        self.biome = biome
        self.doors = []
        self.mapMarker = f'mapImage{random.randint(1, 6)}.png'
        self.enemyBullets = []
        self.droppedItems = []
        self.damagingTraps = []
        self.waves = []
        self.teleporters = []
        self.locks = 1
        self.wave = -1
        self.leftXBoundary = 0
        self.rightXBoundary = width
        # If self.difficulty is -1, enemies can spawn here randomly.
        self.difficulty = -1
        roomActions = {('desert', -3): self.actAsDesertCaveDepthThreeRoom}
        self.environmentObjects = []
        self.temporaryAnimations = []
        self.isSafe = 0
        self.cells = []
        self.plainSprites = []
        self.yBoundaries = 0

        for i in range(9):
            for j in range(9):
                self.cells.append([width * (i + 1) / 11, width * (i + 2) / 11, height * (j + 1) / 11,
                                   height * (j + 2) / 11])

        try:
            self.action = roomActions[(self.biome, self.coordinate[2])]

        except KeyError:
            self.action = skip

        try:
            for i in range(random.choice([0, 0, 0, 1, 1, 2])):
                availablePlainSprites = plainSpritesPerBiome[(self.biome, self.coordinate[2])]
                spriteUsed = random.choice(availablePlainSprites)
                coord = self.getLocationInCell(IMAGES[spriteUsed].get_rect())
                self.plainSprites.append(plainSprite(spriteUsed, coord[0], coord[1]))

        except KeyError:
            pass

        try:
            for i in range(random.choice([0, 0, 0, 1, 1, 2])):
                availableTraps = randomDamagingTrapsPerBiome[(self.biome, self.coordinate[2])]
                trapUsed = random.choice(availableTraps)
                coord = (0, 0)
                coord = self.getLocationInCell(IMAGES[eval(trapUsed).sprite].get_rect())
                self.damagingTraps.append(eval(trapUsed))

        except KeyError:
            pass

        if biome == 'desert':
            if coordinate[2] == 0:
                self.background = 'earlyMorningOvergroundDesertBackground.bmp'
                self.standardRoomMaxDifficulty = 0
                self.maxResources = 0

            elif coordinate[2] == -1:
                self.background = 'topDesertCaveBackground.bmp'
                self.yBoundaries = 0
                self.standardRoomMaxDifficulty = random.choice([1, 2, 3, 3, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6])
                self.foeDifficulties = {'desertCaveJellyfish': (1, 33), 'desertCaveLargeFly': (1, 33),
                                        'desertCaveSpider': (5, 50), 'desertCaveMoth': (3, 50)}

            elif coordinate[2] == -2:
                self.background = 'temporaryDesertCave.bmp'
                self.yBoundaries = 0
                self.standardRoomMaxDifficulty = random.randint(7, 8)
                self.foeDifficulties = {'desertCaveSummoner': (4, 25)}

            elif coordinate[2] == -3:
                self.background = 'temporaryBottomDesertCave.bmp'
                self.yBoundaries = 0
                self.standardRoomMaxDifficulty = 20
                self.foeDifficulties = {'antlionLarva': (1, 50), 'desertCaveSummoner': (4, 25)}
                self.spawnCooldown = 100

            elif coordinate == [0, 6, -1]:
                self.yBoundaries = height * 7 / 10
                self.leftXBoundary = width * 37 / 128
                self.rightXBoundary = width * 749 / 1024
                self.difficulty = -2
                self.standardRoomMaxDifficulty = 0
                self.maxResources = 0
                self.environmentObjects = self.plainSprites = self.damagingTraps = []

        elif biome == 'ship':
            self.yBoundaries = 84 * height / 900
            self.difficulty = -2
            self.standardRoomMaxDifficulty = 0
            self.maxResources = 0

        if not hasattr(self, 'maxResources'):
            self.maxResources = self.standardRoomMaxDifficulty + random.randint(0, 2)
            
        try:
            self.availableResources = environmentObjectsPerBiome[(self.biome, self.coordinate[2])]
            
        except KeyError:
            self.availableResources = None

        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')

        if self.biome == 'ship':
            self.background = 'shipBackgroundWithDoor.bmp'

            for foe in self.foes:
                foe.yBoundary = (165 - foe.place.height) * height / 900

            for wave in self.waves:
                for foe in wave:
                    foe.yBoundary = (165 - foe.place.height) * height / 900

        for enemy in self.foes:
            enemy.yBoundary = self.yBoundaries

    def addFoes(self, difficulty):
        self.difficulty = difficulty

        if difficulty == 5:
            self.mapMarker = 'difficultyFiveMapImage.png'

        if difficulty > -1:
            if self.biome == 'desert' and self.coordinate[2] == -1:
                self.foes = [foe('desertCaveJellyfish',
                                 random.randint(int(self.leftXBoundary), int(self.rightXBoundary)),
                                 random.randint(int(self.yBoundaries), height),
                                 self.coordinate) for i in range(5)]

                if difficulty >= 1:
                    self.foes += [foe('desertCaveLargeFly', random.randint(int(width / 4), int(width / 2)),
                                      random.randint(int(height / 4), int(height / 2)), self.coordinate) for
                                  i in range(difficulty)] + \
                                 [foe('desertCaveLargeFly', random.randint(int(width / 2), int(width * 3 / 4)),
                                      random.randint(int(height / 4), int(height / 2)), self.coordinate) for
                                  i in range(difficulty)]

                if difficulty >= 3:
                    self.foes += [foe('desertCaveMoth', random.randint(int(width / 4), int(width / 2)),
                                      random.randint(int(height / 2), int(height * 3 / 4)), self.coordinate) for
                                  i in range(difficulty - 2)] + \
                                 [foe('desertCaveMoth', random.randint(int(width / 2), int(width * 3 / 4)),
                                      random.randint(int(height / 2), int(height * 3 / 4)), self.coordinate) for
                                  i in range(difficulty - 2)]

                if difficulty >= 4:
                    self.foes += [foe('desertCaveSpider',
                                      random.randint(int(self.leftXBoundary), int(self.rightXBoundary)),
                                      random.randint(int(self.yBoundaries), height),
                                      self.coordinate)]

        for enemy in self.foes:
            enemy.yBoundary = self.yBoundaries

    def spawnFoesFromRoomSwitch(self):
        currentCumulativeDifficulty = 0

        for enemy in self.foes:
            try:
                currentCumulativeDifficulty += self.foeDifficulties[enemy.type][0]

            except KeyError:
                pass

        for enemy in self.foeDifficulties.keys():
            if random.randint(1, 100) <= self.foeDifficulties[enemy][1] and self.foeDifficulties[enemy][0] <= \
                    self.standardRoomMaxDifficulty - currentCumulativeDifficulty:
                self.foes.append(foe(enemy, random.randint(int(width / 16), int(width * 15 / 16)),
                                     random.randint(int(height / 16), int(height * 15 / 16)),
                                     self.coordinate))

        for enemy in self.foes:
            enemy.yBoundary = self.yBoundaries

    def getUnavailableCells(self):
        unavailableCells = []

        for cell in self.cells:
            area = rect(pygame.Rect(cell[0], cell[2], width / 11, height / 11))

            for thing in self.environmentObjects + self.plainSprites:
                if thing.hitbox.checkCollision(area):
                    unavailableCells.append(cell)
                    break

            if cell[2] < self.yBoundaries:
                unavailableCells.append(cell)

        return unavailableCells

    def getLocationInCell(self, pyRect):
        unavailableCells = self.getUnavailableCells()
        cellUsed = random.choice([i for i in self.cells if i not in unavailableCells])
        minX = int(pyRect.width / 2 + cellUsed[0])
        maxX = int(cellUsed[1] - pyRect.width / 2)
        minY = int(cellUsed[2] + pyRect.height / 2)
        maxY = int(cellUsed[3] - pyRect.height / 2)

        try:
            xCoord = random.randint(minX, maxX)

        except ValueError:
            xCoord = cellUsed[0] + width / 22

        try:
            yCoord = random.randint(minY, maxY)

        except ValueError:
            yCoord = cellUsed[2] + height / 22

        return [xCoord, yCoord]
            
    def spawnResourcesFromRoomSwitch(self):
        try:
            if self.availableResources is not None:
                currentResources = len(self.environmentObjects)

                for resource in self.availableResources:
                    if percentChance(resource[1]) and currentResources < self.maxResources:
                        coord = self.getLocationInCell(IMAGES[environmentObject(resource[0], 0,
                                                                                0).sprite].get_rect())
                        self.environmentObjects.append(environmentObject(resource[0], coord[0], coord[1]))
                        currentResources += 1

        except IndexError:
            pass

    def actAsDesertCaveDepthThreeRoom(self):
        self.spawnCooldown -= GAMESPEED

        if self.spawnCooldown <= 0:
            self.foes.append(foe('antlionLarva', random.randint(int(width / 16), int(width * 15 / 16)),
                                 random.randint(int(height / 16), int(height * 15 / 16)), self.coordinate))
            self.spawnCooldown = 100

    def getUpdate(self):
        comparison = room(self.coordinate, self.biome)
        stats = vars(comparison)

        for key in stats.keys():
            if not hasattr(self, key):
                self.__setattr__(key, stats[key])
