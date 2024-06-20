from rects import rect
from variables import IMAGES
from item import item
from droppedItem import droppedItem

import random
import pygame


class environmentObject:
    def __init__(self, name, x, y):
        self.checksCollision = True

        match name:
            case 'desertCaveSmallAmethyst':
                self.sprite = 'Amethyst.png'
                self.hp = 5
                self.drops = droppedItem(x, y, 'amethystInInventory.png',
                                         item('amethyst', 'amethystInInventory.png',
                                              qty=random.randint(1, 2)))
    
            case 'desertCaveLargeAmethyst':
                self.sprite = 'amethyst2.png'
                self.hp = 15
                self.drops = droppedItem(x, y, 'amethystInInventory.png',
                                         item('amethyst', 'amethystInInventory.png',
                                              qty=random.randint(3, 4)))
    
            case 'desertCaveFuelPit':
                self.sprite = 'desertCaveFuelPit.png'
                self.hp = float('inf')
                self.checksCollision = False
                self.drops = item('fossilFuel', 'fossilFuelInInventory.png', qty=1, x=x, y=y)
    
            case 'desertCaveLargeFlower':
                self.sprite = 'desertCaveLargeFlower.png'
                self.hp = 15
                self.drops = droppedItem(x, y, 'desertCaveLittleFlower.png',
                                         item('lumis flower', 'desertCaveLittleFlower.png',
                                              qty=random.randint(5, 10)))
    
            case 'desertCaveLumisTree':
                self.sprite = 'desertCaveLumisTree.png'
                self.hp = float('inf')
                self.place = IMAGES[self.sprite].get_rect(center=(x, y))
                self.hitbox = rect(pygame.Rect(self.place.left + self.place.width / 3,
                                               self.place.top + self.place.height * 4 / 5, self.place.width / 3,
                                               self.place.height / 5))
    
            case 'desertCaveLumisTreeB':
                self.sprite = 'desertCaveLumisTreeB.png'
                self.hp = float('inf')
                self.place = IMAGES[self.sprite].get_rect(center=(x, y))
                self.hitbox = rect(pygame.Rect(self.place.left + self.place.width * 57 / 150,
                                               self.place.top + self.place.height * 147 / 190,
                                               self.place.width * 22 / 75, self.place.height * 43 / 190))
    
            case 'desertCaveLumisTreeC':
                self.sprite = 'desertCaveLumisTreeC.png'
                self.hp = float('inf')
                self.place = IMAGES[self.sprite].get_rect(center=(x, y))
                self.hitbox = rect(pygame.Rect(self.place.left + self.place.width * 20 / 73,
                                               self.place.top + self.place.height * 67 / 79,
                                               self.place.width * 41 / 146, self.place.height * 12 / 79))
    
            case 'desertCaveLumisTreeD':
                self.sprite = 'desertCaveLumisTreeD.png'
                self.hp = float('inf')
                self.place = IMAGES[self.sprite].get_rect(center=(x, y))
                self.hitbox = rect(pygame.Rect(self.place.left + self.place.width * 47 / 133,
                                               self.place.top + self.place.height * 9 / 11,
                                               self.place.width * 41 / 133, self.place.height * 2 / 11))
    
            case 'desertCaveLumisTreeE':
                self.sprite = 'desertCaveLumisTreeE.png'
                self.hp = float('inf')
                self.place = IMAGES[self.sprite].get_rect(center=(x, y))
                self.hitbox = rect(pygame.Rect(self.place.left + self.place.width * 15 / 43,
                                               self.place.top + self.place.height * 109 / 132,
                                               self.place.width * 16 / 43, self.place.height * 23 / 132))
    
            case 'desertCaveLumisTreeF':
                self.sprite = 'desertCaveLumisTreeF.png'
                self.hp = float('inf')
                self.place = IMAGES[self.sprite].get_rect(center=(x, y))
                self.hitbox = rect(pygame.Rect(self.place.left + self.place.width * 15 / 43, self.place.top + self.place.height * 109 / 132,
                                               self.place.width * 16 / 43, self.place.height * 23 / 132))
    
            case 'desertCaveLumisTreeG':
                self.sprite = 'desertCaveLumisTreeG.png'
                self.hp = float('inf')
                self.place = IMAGES[self.sprite].get_rect(center=(x, y))
                self.hitbox = rect(pygame.Rect(self.place.left + self.place.width * 25 / 62,
                                               self.place.top + self.place.height * 82 / 101,
                                               self.place.width * 17 / 62, self.place.height * 19 / 101))
    
            case 'desertCaveLumisTreeH':
                self.sprite = 'desertCaveLumisTreeH.png'
                self.hp = float('inf')
                self.place = IMAGES[self.sprite].get_rect(center=(x, y))
                self.hitbox = rect(pygame.Rect(self.place.left, self.place.height * 31 / 66 + self.place.top,
                                               self.place.width, self.place.height * 35 / 66))

        if not hasattr(self, 'place'):
            self.place = IMAGES[self.sprite].get_rect(center=(x, y))

        if not hasattr(self, 'hitbox'):
            self.hitbox = rect(self.place)

        if not hasattr(self, 'drops'):
            self.drops = droppedItem(x, y, 'invisiblePixels.png', item('empty',
                                                                       'invisiblePixels.png', stackSize=1))
