import pygame
import os

# I use the dictionary, 'IMAGES', to store sprites so that I don't have to use pygame.image.load function for
# each new sprite that gets created.

IMAGES = {}
FILE = 1
display = pygame.display.set_mode((1600, 900))
GAMESPEED = 1 / 1.2
MOVESPEED = display.get_width() * display.get_height() / 1440000
# I resize the images according to the display size.

for i in os.listdir('images'):
    if i != 'font' and i != 'backgrounds':
        IMAGES[i] = pygame.image.load(f'images/{i}')
        IMAGES[i] = pygame.transform.scale(IMAGES[i], (IMAGES[i].get_width() * display.get_width() / 1600,
                                           IMAGES[i].get_height() * display.get_height() / 900))

for i in os.listdir('images/font'):
    IMAGES[i] = pygame.image.load(f'images/font/{i}')

backgroundsList = ['earlyMorningOvergroundDesertBackground.bmp', 'shelterBackgroundBMP.bmp',
                   'altShelterBackgroundBMP.bmp']
BACKGROUNDS = {}

for i in os.listdir('images/backgrounds'):
    BACKGROUNDS[i] = pygame.transform.scale(pygame.image.load(f'images/backgrounds/{i}'),
                                            (display.get_width(), display.get_height()))

yBoundary = 74 * display.get_height() / 900