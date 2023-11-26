import pygame
import os

# I use the dictionary, 'IMAGES', to store sprites so that I don't have to use pygame.image.load function for
# each new sprite that gets created.

IMAGES = {}
display = pygame.display.set_mode((1600, 900))
width = display.get_width()
height = display.get_height()
diagonal = (width ** 2 + height ** 2) ** (1 / 2)
GAMESPEED = 6
MOVESPEED = 1
# I resize the images according to the display size.

for i in os.listdir('images'):
    if i != 'font' and i != 'backgrounds' and i != 'lasers':
        IMAGES[i] = pygame.image.load(f'images/{i}')
        IMAGES[i] = pygame.transform.scale(IMAGES[i], (IMAGES[i].get_width() * width / 1600,
                                           IMAGES[i].get_height() * height / 900))

for i in os.listdir('images/font'):
    IMAGES[i] = pygame.image.load(f'images/font/{i}')

backgroundsList = ['earlyMorningOvergroundDesertBackground.bmp', 'shelterBackgroundBMP.bmp',
                   'altShelterBackgroundBMP.bmp']
BACKGROUNDS = {}
LASERS = {}

for i in os.listdir('images/backgrounds'):
    BACKGROUNDS[i] = pygame.transform.scale(pygame.image.load(f'images/backgrounds/{i}'), (width, height))


laserSprites = [f'watchdogLaser{i + 1}.png' for i in range(4)]

for laser in laserSprites:
    IMAGES[laser] = pygame.transform.scale(IMAGES[laser], (diagonal, IMAGES[laser].get_height() * height / 900))

yBoundaryShip = 85 * height / 900
