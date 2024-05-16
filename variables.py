import pygame
import os

# I use the dictionary, 'IMAGES', to store sprites so that I don't have to use pygame.image.load function for
# each new sprite that gets created.

IMAGES = {}
display = pygame.display.set_mode((1440, 900))
pygame.display.toggle_fullscreen()
width = display.get_width()
height = display.get_height()
fullscreenRect = pygame.Rect(0, 0, width, height)
diagonal = (width ** 2 + height ** 2) ** (1 / 2)
GAMESPEED = 6
MOVESPEED = 1
# I resize the images according to the display size. Images are saved to the IMAGES dictionary so that they only
# have to be loaded with pygame once.

for i in os.listdir('images'):
    if i not in ['font', 'backgrounds', 'lasers']:
        try:
            IMAGES[i] = pygame.image.load(f'images/{i}')
            IMAGES[i] = pygame.transform.scale(IMAGES[i], (IMAGES[i].get_width() * width / 1600,
                                               IMAGES[i].get_height() * height / 900))

        except pygame.error:
            pass

for i in os.listdir('images/font'):
    IMAGES[i] = pygame.image.load(f'images/font/{i}')

backgroundsList = ['earlyMorningOvergroundDesertBackground.bmp', 'shelterBackgroundBMP.bmp',
                   'altShelterBackgroundBMP.bmp']
BACKGROUNDS = {}
LASERS = {}

for i in os.listdir('images/backgrounds'):
    try:
        BACKGROUNDS[i] = pygame.transform.scale(pygame.image.load(f'images/backgrounds/{i}'), (width, height))

    except pygame.error:
        pass


laserSprites = [f'watchdogLaser{i + 1}.png' for i in range(4)] + \
               [f'desertCaveFlyMinibossLaserProjectile{i}.png' for i in range(1, 4)]

for laser in laserSprites:
    IMAGES[laser] = pygame.transform.scale(IMAGES[laser], (diagonal, IMAGES[laser].get_height() * height / 900))

yBoundaryShip = 85 * height / 900
environmentObjectsPerBiome = {('desert', -1): [['desertCaveSmallAmethyst', 5], ['desertCaveLargeAmethyst', 2]]}
randomDamagingTrapsPerBiome = {('desert', -1): ['damagingTrap("desertCaveTentacle1.png", 30, coord[0], coord[1], '
                                                'animation=[f"desertCaveTentacle{i}.png" for i in range(1, 5) for j '
                                                'in range(30)])']}
plainSpritesPerBiome = {('desert', -1): ['desertCaveLumisFern.png',
                                         'desertCaveFloweryFern.png', 'desertCaveVine.png', 'desertCaveOrb.png'],
                        ('desertCaveForest', -1): ['desertCaveLumisFern.png']}
notRespawningEnvironmentObjectsPerBiome = {('desert', -1): ['desertCaveLumisTree'],
                                           ('desertCaveForest', -1): ['desertCaveLumisTree']}
recipes = {tuple(sorted(['moth dust'] * 5 + ['lumis'] * 50)):
               ('item("lumisFlamethrower", "basicSpreadInInventory.png", "The lumis flamethrower fires a shot.", '
                'stackSize=1)')}
