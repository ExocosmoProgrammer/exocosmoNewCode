import random
from plainSprites import plainSprite
from droppedItem import droppedItem
from variables import display
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
            self.yBoundaries = [74 * display.get_height() / 900, display.get_height()]

        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')