import random
from plainSprites import plainSprite
from droppedItem import droppedItem
from variables import width, height
from foe import foe


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
        self.locks = 1
        self.wave = -1

        if biome == 'desert' and coordinate[2] == 0:
            self.background = 'earlyMorningOvergroundDesertBackground.bmp'

        elif biome == 'ship':
            self.yBoundaries = 84 * height / 900

        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')

        if self.biome == 'ship':
            self.background = 'shipBackgroundWithDoor.bmp'

            for foe in self.foes:
                foe.yBoundary = (165 - foe.place.height) * height / 900

            for wave in self.waves:
                for foe in wave:
                    foe.yBoundary = (165 - foe.place.height) * height / 900
