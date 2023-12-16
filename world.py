import pygame

from room import room
from plainSprites import plainSprite
from variables import height, width, yBoundaryShip
from foe import foe
from droppedItem import droppedItem
from item import item
from damagingTrap import damagingTrap
from definitions import saveWithPickle, loadWithPickle
from teleporter import teleporter
from rects import rect

import random


class world:
    def __init__(self, **extra):
        self.desertCaveDepthTwoEntranceCoord = None
        self.rooms = {(0, 6, -1): room([0, 6, -1], 'desert', background='topDesertCaveEntranceBackground.bmp', locks=0)}
        self.unavailableCoords = [(0, 5, -1), (-1, 6, -1), (1, 6, -1)]
        self.potentialCoordinates = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0]]
        shipRooms = [room([0, 0, 10], 'ship'),

                     room([0, 1, 10], 'ship', droppedItems=[
                         droppedItem(width / 2, height / 2, 'pistolInInventory.png',
                                     item('nanotechRevolver', 'pistolInInventory.png',
                                          description='Fires a nanotech bullet'))
                     ], damagingTraps=[damagingTrap('fireTrap2.png', 26, width / 20
                                                    * (1 + 2 * i), height * (2 / 3 - i * 13 / 900)) for
                                       i in range(10)]),

                     room([0, -1, 10], 'ship', foes=[
                         foe('hellhound', width / 2, height / 2, [0, -1, 10],
                             dependentFoes=[foe('tougherShipMiniboss', width / 2, height / 4, [0, -1, 10])])],
                          damagingTraps=[damagingTrap('aFire.png', 26, width * i / 31,
                                                      height * 856 / 900) for i in range(32)] + [
                                            damagingTrap('aFire.png', 26, width * 31 / 1600,
                                                         (height - yBoundaryShip) * i / 14 + yBoundaryShip) for i in
                                            range(1, 14)
                                        ] + [damagingTrap('aFire.png', 26, width * 1569 / 1600,
                                                          (height - yBoundaryShip) * i / 14 + yBoundaryShip) for i in
                                             range(1, 14)]
                                        + [damagingTrap('aFire.png', 26, width * i / 31,
                                                        height * 44 / 900 + yBoundaryShip) for i in range(1, 13)
                                           ] + [
                                            damagingTrap('aFire.png', 26, width * i / 31,
                                                         height * 44 / 900 + yBoundaryShip) for i in range(19, 31)
                                        ]),

                     room([0, 2, 10], 'ship', foes=[
                         foe('brokenTurret', width / 2, height / 2, [0, 2, 10])]),

                     room([0, 3, 10], 'ship', foes=[
                         foe('flamingRobot', width / 2, height / 3, [0, 3, 10])
                     ], waves=[[
                         foe('brokenTurret', width / 3, height * 2 / 3, [0, 3, 10]),
                         foe('brokenTurret', width * 2 / 3, height * 2 / 3, [0, 3, 10])
                     ]]),

                     room([0, 4, 10], 'ship', foes=[
                         foe('robotBodyguard', width / 2, height / 2, [0, 4, 10])
                     ], waves=[[foe('robotBodyguard', width / 2, height / 2, [0, 4, 10]),
                                foe('flamingRobot', width / 2, height / 3, [0, 4, 10]),
                                foe('brokenTurret', width / 2, height / 4, [0, 4, 10])]]),

                     room([0, 5, 10], 'ship', foes=[
                         foe('robotBodyguard', width / 2, height / 2, [0, 5, 10]),
                         foe('brokenTurret', width / 2, height / 3, [0, 5, 10]),
                     ], damagingTraps=[damagingTrap('fireTrap2.png', 26, width / 20
                                                    * (1 + 2 * i), height * (5 / 8 - i * 13 / 900)) for
                                       i in range(10)],
                          waves=[[foe('flamingRobot', width / 4, height / 2, [0, 5, 10]),
                                  foe('flamingRobot', width * 3 / 4, height / 2, [0, 5, 10], ),
                                  foe('brokenTurret', width / 2, height / 4, [0, 5, 10]),
                                  foe('brokenTurret', width / 2, height * 3 / 4, [0, 5, 10], )],
                                 [foe('robotBodyguard', width / 10, height / 4, [0, 5, 10], ),
                                  foe('robotBodyguard', width / 10, height * .75, [0, 5, 10], ),
                                  foe('robotBodyguard', width * 9 / 10, height / 5, [0, 5, 10], ),
                                  foe('robotBodyguard', width * 9 / 10, height * .75, [0, 5, 10], ),
                                  ]], teleporters=[teleporter(width / 2, height / 3, 'mineshaftFromShip.bmp',
                                                              [0, 6, -1], destinationXandY=[width / 2,
                                                                                            height * 38 / 39])]),

                     room([0, 6, 10], 'ship', foes=[
                         foe('robotBodyguard', width / 2, height / 2, [0, 6, 10],
                             spawnsOnDefeat=[foe('robotBodyguard', width / 2, height / 2, [0, 4, 10],
                                                 spawnsOnDefeat=[
                                                     foe('brokenTurret', width / 2, height / 2, [0, 6, 10])]),
                                             foe('flamingRobot', width / 2, height / 3, [0, 4, 10],
                                                 spawnsOnDefeat=[
                                                     foe('robotBodyguard', width / 2, height / 2, [0, 6, 10])]),
                                             foe('brokenTurret', width / 2, height / 4, [0, 4, 10],
                                                 spawnsOnDefeat=[
                                                     foe('flamingRobot', width / 2, height / 2, [0, 6, 10])])]),
                         foe('flamingRobot', width / 2, height / 3, [0, 6, 10],
                             spawnsOnDefeat=[foe('robotBodyguard', width / 2, height / 2, [0, 4, 10],
                                                 spawnsOnDefeat=[
                                                     foe('brokenTurret', width / 2, height / 2, [0, 6, 10])]),
                                             foe('flamingRobot', width / 2, height / 3, [0, 4, 10],
                                                 spawnsOnDefeat=[
                                                     foe('robotBodyguard', width / 2, height / 2, [0, 6, 10])]),
                                             foe('brokenTurret', width / 2, height / 4, [0, 4, 10],
                                                 spawnsOnDefeat=[
                                                     foe('flamingRobot', width / 2, height / 2, [0, 6, 10])])]),
                         foe('brokenTurret', width / 2, height / 4, [0, 6, 10],
                             spawnsOnDefeat=[foe('robotBodyguard', width / 2, height / 2, [0, 4, 10],
                                                 spawnsOnDefeat=[
                                                     foe('brokenTurret', width / 2, height / 2, [0, 6, 10])]),
                                             foe('flamingRobot', width / 2, height / 3, [0, 4, 10],
                                                 spawnsOnDefeat=[
                                                     foe('robotBodyguard', width / 2, height / 2, [0, 6, 10])]),
                                             foe('brokenTurret', width / 2, height / 4, [0, 4, 10],
                                                 spawnsOnDefeat=[
                                                     foe('flamingRobot', width / 2, height / 2, [0, 6, 10])])])
                     ]), ]

        for place in shipRooms:
            self.rooms[tuple(place.coordinate)] = place

        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')

    def checkAdjacentEmptySpaces(self, coord):
        adjSpaces = [(coord[0], coord[1] + 1, coord[2]), (coord[0], coord[1] - 1, coord[2]),
                     (coord[0] + 1, coord[1], coord[2]), (coord[0] - 1, coord[1], coord[2])]

        return [space for space in adjSpaces if space not in self.rooms.keys() and space not in self.unavailableCoords]

    def addTopDesertCaveLayerSpecialRooms(self, biome):
        yCoords = [member.coordinate[1] for member in biome]
        choices = [member for member in biome if member.coordinate[1] == max(yCoords)]
        chosenRoom = random.choice(choices)
        newRoomCoord = (chosenRoom.coordinate[0], chosenRoom.coordinate[1] + 1, chosenRoom.coordinate[2])
        self.unavailableCoords += [(chosenRoom.coordinate[0], chosenRoom.coordinate[1] + 2, chosenRoom.coordinate[2]),
                                   (chosenRoom.coordinate[0] - 1, chosenRoom.coordinate[1] + 1,
                                    chosenRoom.coordinate[2]),
                                   (chosenRoom.coordinate[0] + 2, chosenRoom.coordinate[1] + 1,
                                    chosenRoom.coordinate[2])]
        ledgeDestinationCoord = (chosenRoom.coordinate[0], chosenRoom.coordinate[1] + 1, -2)
        teleporterHitbox = rect(pygame.Rect(0, 0, width, height * 763 / 1024))
        self.rooms[newRoomCoord] = room(newRoomCoord, 'desert', background='ledgeToDesertCaveDepthTwo.bmp',
                                        teleporters=[teleporter(0, 0, 'invisiblePixels.png',
                                                                list(ledgeDestinationCoord),
                                                                [width / 2, height * 38 / 39],
                                                                hitbox=teleporterHitbox)],
                                        yBoundaries=height * 357 / 512, difficulty=4,
                                        foes=[foe('desertCaveLargeFly', width * i / 7, height / 4, newRoomCoord) for
                                                                                            i in range(1, 7)])
        self.rooms[ledgeDestinationCoord] = room(ledgeDestinationCoord, 'desert', locks=0)
        self.desertCaveDepthTwoEntranceCoord = ledgeDestinationCoord

    def addMiddleDesertCaveLayerSpecialRooms(self, biome):
        yCoords = [member.coordinate[1] for member in biome]
        choices = [member for member in biome if member.coordinate[1] == max(yCoords)]
        chosenRoom = random.choice(choices)
        newRoomCoord = (chosenRoom.coordinate[0], chosenRoom.coordinate[1] + 1, chosenRoom.coordinate[2])
        self.unavailableCoords += [(chosenRoom.coordinate[0], chosenRoom.coordinate[1] + 2, chosenRoom.coordinate[2]),
                                   (chosenRoom.coordinate[0] - 1, chosenRoom.coordinate[1] + 1,
                                    chosenRoom.coordinate[2]),
                                   (chosenRoom.coordinate[0] + 2, chosenRoom.coordinate[1] + 1,
                                    chosenRoom.coordinate[2])]
        ledgeDestinationCoord = (chosenRoom.coordinate[0], chosenRoom.coordinate[1] + 1, -3)
        teleporterHitbox = rect(pygame.Rect(0, 0, width, height * 763 / 1024))
        self.rooms[newRoomCoord] = room(newRoomCoord, 'desert', background='ledgeToDesertCaveDepthTwo.bmp',
                                        teleporters=[teleporter(0, 0, 'invisiblePixels.png',
                                                                list(ledgeDestinationCoord),
                                                                [width / 2, height * 38 / 39],
                                                                hitbox=teleporterHitbox)])
        self.rooms[ledgeDestinationCoord] = room(ledgeDestinationCoord, 'desert', locks=0)
        self.desertCaveDepthThreeEntranceCoord = ledgeDestinationCoord

    def makeRooms(self, qty, biome, rootRoom, difficultyQtys):
        potentialCoords = self.checkAdjacentEmptySpaces(rootRoom)
        calmRooms = []

        for i in range(qty):
            newRoomCoord = random.choice(potentialCoords)
            potentialCoords.remove(newRoomCoord)
            self.rooms[newRoomCoord] = room(newRoomCoord, biome, locks=0)
            calmRooms.append(self.rooms[newRoomCoord])

            for coord in self.checkAdjacentEmptySpaces(newRoomCoord):
                if coord not in potentialCoords:
                    potentialCoords.append(coord)

        if biome == 'desert' and rootRoom[2] == -1:
            self.addTopDesertCaveLayerSpecialRooms(calmRooms)

        elif biome == 'desert' and rootRoom[2] == -2:
            self.addMiddleDesertCaveLayerSpecialRooms(calmRooms)

        for key in list(difficultyQtys.keys()):
            for i in range(difficultyQtys[key]):
                combatRoom = random.choice(calmRooms)
                combatRoom.addFoes(key)
                calmRooms.remove(combatRoom)

                if key == 5:
                    combatRoom.locks = 1

    def addDoors(self):
        coordinates = list(self.rooms.keys())

        for place in list(self.rooms.values()):
            if (place.coordinate[0] - 1, place.coordinate[1], place.coordinate[2]) in coordinates:
                place.doors.append(plainSprite('door.bmp', width * 31 / 3200,
                                               height / 2))

            if (place.coordinate[0] + 1, place.coordinate[1], place.coordinate[2]) in coordinates:
                place.doors.append(plainSprite('door.bmp', width * 3169 / 3200,
                                               height / 2))

            if (place.coordinate[0], place.coordinate[1] + 1, place.coordinate[2]) in coordinates:
                place.doors.append(plainSprite('door.bmp', width / 2,
                                               height / 45))

            if (place.coordinate[0], place.coordinate[1] - 1, place.coordinate[2]) in coordinates:
                place.doors.append(plainSprite('door.bmp', width / 2,
                                               height * 44 / 45))


rooms = world()
rooms.makeRooms(1, 'desert', (0, 6, -1), {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0})
rooms.makeRooms(5, 'desert', rooms.desertCaveDepthTwoEntranceCoord, {0: 0})
rooms.makeRooms(5, 'desert', rooms.desertCaveDepthThreeEntranceCoord, {0: 0})
rooms.addDoors()


def saveWorld(file):
    saveWithPickle(f'worldSave{file}.pickle', rooms)


def loadWorld(file):
    return loadWithPickle(f'worldSave{file}.pickle')
