import random
import copy
import pygame

from plainSprites import plainSprite
from droppedItem import droppedItem
from variables import (width, height, GAMESPEED, environmentObjectsPerBiome, IMAGES, plainSpritesPerBiome,
                       randomDamagingTrapsPerBiome, notRespawningEnvironmentObjectsPerBiome, playerHeight)
from foe import foe
from definitions import skip, percentChance, greater, lesser, getYBoundary, getYBoundaryFromPlace
from environmentObject import environmentObject
from rects import rect
from damagingTrap import damagingTrap
from passiveCritter import passiveCritter


class room:
    def __init__(self, coordinate, biome, **extra):
        self.foes = []
        self.coordinate = list(coordinate)
        self.biome = biome
        self.doors = []
        self.mapMarker = f'mapImage{random.randint(1, 6)}.png'
        self.enemyBullets = []
        self.droppedItems = []
        self.damagingTraps = []
        self.waves = []
        self.teleporters = []
        self.locks = True
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
        self.cleared = 1
        self.addsResources = 1
        self.cells = []
        self.passiveCritters = []

        if biome == 'desert':
            if coordinate[2] == 0:
                self.background = 'earlyMorningOvergroundDesertBackground.bmp'
                self.standardRoomMaxDifficulty = 0
                self.maxResources = 0

            elif coordinate[2] == -1:
                self.background = 'desertCaveTopLayerNew.bmp'
                self.yBoundaries = height * 125 / 900
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
                self.yBoundaries = height * 543 / 900
                self.leftXBoundary = width * 37 / 128
                self.rightXBoundary = width * 749 / 1024
                self.difficulty = -2
                self.standardRoomMaxDifficulty = 0
                self.maxResources = 0
                self.environmentObjects = []
                self.plainSprites = []
                self.damagingTraps = []
                self.addsResources = 0

        elif biome == 'ship':
            self.yBoundaries = 84 * height / 900
            self.difficulty = 0
            self.standardRoomMaxDifficulty = 0
            self.maxResources = 0

        elif biome == 'desertCaveForest':
            self.difficulty = -2
            self.standardRoomMaxDifficulty = 0
            self.maxResources = 0
            self.background = 'desertCaveForest.bmp'
            self.yBoundaries = height * 23 / 164
            self.environmentObjects = []
            self.plainSprites = []
            self.damagingTraps = []
            self.getCells()
            self.addsResources = 0

            for i in range(70):
                try:
                    treeSprite = random.choice([f'desertCaveLumisTree{i}' for i in ['', 'B', 'C', 'D', 'E', 'F',
                                                                                        'G', 'H']])
                    pyRect = IMAGES[f'{treeSprite}.png'].get_rect()
                    rectangle = environmentObject(treeSprite, 0, 0).hitbox
                    coord = self.getLocationInCell(pyRect, hitbox=rectangle)
                    self.environmentObjects.append(environmentObject(treeSprite, coord[0], coord[1]))

                except (IndexError, KeyError):
                    pass

            for i in range(70):
                try:
                    coord = self.getLocationInCell(IMAGES['desertCaveLumisFern.png'].get_rect())
                    self.plainSprites.append(plainSprite('desertCaveLumisFern.png', coord[0], coord[1]))

                except (KeyError, IndexError):
                    pass

            for i in range(random.randint(0, 5)):
                critter = random.choice(['desertCaveSlug', 'desertCaveButterfly', 'desertCaveAmphipod',
                                         'desertCaveCritterWithThreeLegs'])
                critterRect = passiveCritter(critter, 0, 0, self).hitbox
                self.passiveCritters.append(passiveCritter(critter,
                                                           random.randint(int(critterRect.width / 2),
                                                                          int(width - critterRect.width / 2)),
                                                           random.randint(int(critterRect.height / 2),
                                                                          int(height - critterRect.height / 2)), self))

        self.getCells()

        try:
            self.action = roomActions[(self.biome, self.coordinate[2])]

        except KeyError:
            self.action = skip

        if self.addsResources:
            try:
                for i in range(random.choice([0, 0, 0, 0, 0, 1, 1, 1, 2])):
                    availablePlainSprites = plainSpritesPerBiome[(self.biome, self.coordinate[2])]
                    spriteUsed = random.choice(availablePlainSprites)
                    coord = self.getLocationInCell(IMAGES[spriteUsed].get_rect())
                    self.plainSprites.append(plainSprite(spriteUsed, coord[0], coord[1]))

            except KeyError:
                pass

            try:
                for i in range(random.choice([0, 0, 0, 0, 0, 1, 1, 1, 2])):
                    availableObjects = notRespawningEnvironmentObjectsPerBiome[(self.biome, self.coordinate[2])]
                    spriteUsed = random.choice(availableObjects)
                    coord = self.getLocationInCell(IMAGES[environmentObject(spriteUsed, 0, 0).sprite].get_rect())
                    self.environmentObjects.append(environmentObject(spriteUsed, coord[0], coord[1]))

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

        if not hasattr(self, 'maxResources'):
            self.maxResources = random.choice([0, 0, 0, 0, 1, 1, 1, 2])
            
        try:
            self.availableResources = environmentObjectsPerBiome[(self.biome, self.coordinate[2])]
            
        except KeyError:
            self.availableResources = None

        self.foesUponRespawn = [copy.copy(enemy) for enemy in self.foes]

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

        self.wavesUponRespawn = []

        for i in self.waves.copy():
            waveAdded = []

            for j in i:
                waveAdded.append(copy.deepcopy(j))

            self.wavesUponRespawn.append(waveAdded)

        self.foesUponRespawn = [copy.deepcopy(enemy) for enemy in self.foes]

    def addFoes(self, difficulty):
        self.difficulty = difficulty
        self.cleared = 0

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

    def getCells(self):
        for i in range(20):
            for j in range(20):
                self.cells.append([width * i / 20, width * (i + 1) / 20, height * j / 20,
                                   height * (j + 1) / 20])

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

    def getUnavailableCells(self, place, hitbox):
        unavailableCells = []
        yBoundary = getYBoundaryFromPlace(place, self.yBoundaries, hitbox)

        for cell in self.cells:
            area = pygame.Rect(cell[0], cell[2], width / 11, height / 11)

            for thing in self.environmentObjects + self.plainSprites:
                if (abs(thing.place.centerx - (area.left + width / 22)) <= (width / 11 + thing.place.width) / 2) and \
                        (abs(thing.place.centery - (area.top + height / 22)) <= (height / 11 + thing.place.height) / 2):
                    unavailableCells.append(cell)
                    break

            if cell[2] <= yBoundary:
                if cell[3] > yBoundary:
                    cell[2] = yBoundary

                else:
                    unavailableCells.append(cell)

        return unavailableCells

    def getLocationInCell(self, pyRect, hitbox=None):
        if hitbox is None:
            hitbox = rect(pyRect)

        unavailableCells = self.getUnavailableCells(pyRect, hitbox)
        yBoundary = getYBoundaryFromPlace(pyRect, self.yBoundaries, hitbox)
        cellUsed = random.choice([i for i in self.cells if i not in unavailableCells])
        minX = int(pyRect.width / 2 + cellUsed[0])
        maxX = int(cellUsed[1] - pyRect.width / 2)
        minY = int(cellUsed[2] + pyRect.height / 2)
        maxY = int(cellUsed[3] - pyRect.height / 2)

        try:
            xCoord = random.randint(minX, maxX)

        except ValueError:
            xCoord = lesser(greater(cellUsed[0] + width / 40, hitbox.width / 2),
                            width - hitbox.width / 2)


        try:
            yCoord = random.randint(minY, maxY)

        except ValueError:
            yCoord = lesser(greater(cellUsed[2] + height / 40, yBoundary + pyRect.height / 2),
                            height - hitbox.height / 2)

        area = pygame.Rect(xCoord - pyRect.width / 2, yCoord - pyRect.height / 2, pyRect.width, pyRect.height)

        for i in self.environmentObjects:
            otherRect = i.place

            if abs(area.centerx - otherRect.centerx) <= (area.width + otherRect.width) / 2 and \
                    abs(area.centery - otherRect.centery) <= (area.height + otherRect.height) / 2:
                # A KeyError will prevent the object that this function is called for from spawning.
                raise KeyError

        for i in self.plainSprites:
            otherRect = i.place

            if abs(area.centerx - otherRect.centerx) <= (area.width + otherRect.width) / 2 and \
                    abs(area.centery - otherRect.centery) <= (area.height + otherRect.height) / 2:
                # A KeyError will prevent the object that this function is called for from spawning.
                raise KeyError

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

        except (IndexError, KeyError):
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
