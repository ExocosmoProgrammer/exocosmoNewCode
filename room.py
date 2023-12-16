import random
from plainSprites import plainSprite
from droppedItem import droppedItem
from variables import width, height, GAMESPEED
from foe import foe
from definitions import skip


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
        self.locks = 0
        self.wave = -1
        self.leftXBoundary = 0
        self.rightXBoundary = width
        self.difficulty = -1
        roomActions = {('desert', -3): self.actAsDesertCaveDepthThreeRoom}
        self.environmentObjects = []
        self.temporaryAnimations = []

        try:
            self.action = roomActions[(self.biome, self.coordinate[2])]

        except KeyError:
            self.action = skip

        if biome == 'desert' and coordinate[2] == 0:
            self.background = 'earlyMorningOvergroundDesertBackground.bmp'

        elif coordinate == [0, 6, -1]:
            self.yBoundaries = height * 7 / 10
            self.leftXBoundary = width * 37 / 128
            self.rightXBoundary = width * 749 / 1024

        elif biome == 'desert' and coordinate[2] == -1:
            self.background = 'topDesertCaveBackground.bmp'
            self.yBoundaries = 0
            self.standardRoomMaxDifficulty = random.choice([3, 3, 3, 4, 4, 4, 5, 5, 6, 7])
            self.foeDifficulties = {'desertCaveJellyfish': (1, 33), 'desertCaveLargeFly': (1, 33),
                                    'desertCaveSpider': (5, 10)}

        elif biome == 'desert' and coordinate[2] == -2:
            self.background = 'temporaryDesertCave.bmp'
            self.yBoundaries = 0
            self.standardRoomMaxDifficulty = random.randint(7, 8)
            self.foeDifficulties = {'desertCaveSummoner': (4, 25)}

        elif biome == 'desert' and coordinate[2] == -3:
            self.background = 'temporaryBottomDesertCave.bmp'
            self.yBoundaries = 0
            self.standardRoomMaxDifficulty = 20
            self.foeDifficulties = {'antlionLarva': (1, 50), 'desertCaveSummoner': (4, 25)}
            self.spawnCooldown = 100

        elif biome == 'ship':
            self.yBoundaries = 84 * height / 900
            self.difficulty = -2

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

        if self.biome == 'desert' and self.coordinate[2] == -1:
            self.foes = [foe('desertCaveJellyfish', random.randint(int(self.leftXBoundary), int(self.rightXBoundary)),
                             random.randint(int(self.yBoundaries), height),
                             self.coordinate) for i in range(5)]

            if difficulty >= 1:
                self.foes += [foe('desertCaveLargeFly', random.randint(int(width / 16), int(width * 15 / 16)),
                                  random.randint(int(height / 16), int(height * 5 / 16)), self.coordinate) for
                              i in range(difficulty - 1)]

            if difficulty >= 4:
                self.foes += [foe('desertCaveSpider',
                                  random.randint(int(self.leftXBoundary), int(self.rightXBoundary)),
                                  random.randint(int(self.yBoundaries), height),
                                  self.coordinate)]

        for enemy in self.foes:
            enemy.yBoundary = self.yBoundaries

    def spawnFoesFromRoomSwitch(self):
        """if random.randint(1, 6) == 1:
            currentCumulativeDifficulty = 0

            for enemy in self.foes:
                try:
                    currentCumulativeDifficulty += self.foeDifficulties[enemy.type]

                except KeyError:
                    pass

            potentialSpawn = [name for name in self.foeDifficulties.keys() if self.foeDifficulties[name] <=
                              self.standardRoomMaxDifficulty - currentCumulativeDifficulty]

            try:
                spawned = random.choice(potentialSpawn)
                self.foes.append(foe(spawned, random.randint(int(width / 16), int(width * 15 / 16)),
                                      random.randint(int(height / 16), int(height * 15 / 16)),
                                      self.coordinate))

            except IndexError:
                pass"""
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

    def actAsDesertCaveDepthThreeRoom(self):
        self.spawnCooldown -= GAMESPEED

        if self.spawnCooldown <= 0:
            self.foes.append(foe('antlionLarva', random.randint(int(width / 16), int(width * 15 / 16)),
                                 random.randint(int(height / 16), int(height * 15 / 16)), self.coordinate))
            self.spawnCooldown = 100

