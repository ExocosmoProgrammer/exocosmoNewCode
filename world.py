import copy

import pygame

from room import room
from plainSprites import plainSprite
from variables import height, width, yBoundaryShip
from foe import foe
from droppedItem import droppedItem
from item import item
from damagingTrap import damagingTrap
from teleporter import teleporter
from rects import rect

import random


class world:
    def __init__(self, **extra):
        self.desertCaveDepthTwoEntranceCoord = None
        self.rooms = {(0, 6, -1): room([0, 6, -1], 'desert',
                                       background='topDesertCaveEntranceBackground.bmp', locks=False, foes=[], isSafe=1,
                                       difficulty=-2)}
        self.unavailableCoords = [(0, 5, -1), (-1, 6, -1), (1, 6, -1)]
        shipRooms = [room([0, 0, 10], 'ship'),

                     room([0, 1, 10], 'ship', droppedItems=[
                         droppedItem(width / 2, height / 2, 'pistolInInventory.png',
                                     item('nanotechRevolver', 'pistolInInventory.png',
                                          description='Fires a nanotech bullet', stackSize=1))
                     ], damagingTraps=[damagingTrap('fireTrap2.png', 26, width / 20
                                                    * (1 + 2 * i), height * (2 / 3 - i * 13 / 900)) for
                                       i in range(10)]),

                     room([0, -1, 10], 'ship', foes=[
                         foe('hellhound', width / 2, height / 2, [0, -1, 10],
                             dependentFoes=[foe('tougherShipMiniboss', width / 2, height / 4,
                                                [0, -1, 10])])],
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
                                        ], isBossRoom=True),

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
                                  ]], teleporters=[teleporter(width / 2, height / 3, 'doorToDesertCaves1.png',
                                                              [0, 6, -1], destinationXandY=[width / 2,
                                                                                            height * 38 / 39],
                                                              animationWhenApproached=[f'doorToDesertCaves{i}.png' for \
                                                                                       i in [2, 3] for j in \
                                                                                       range(90)])]),

                     room([0, 6, 10], 'ship', foes=[
                         foe('robotBodyguard', width / 2, height / 2, [0, 6, 10],
                             spawnsOnDefeat=[foe('robotBodyguard', width / 2, height / 2, [0, 4, 10],
                                                 spawnsOnDefeat=[
                                                     foe('brokenTurret', width / 2, height / 2,
                                                         [0, 6, 10])]),
                                             foe('flamingRobot', width / 2, height / 3, [0, 4, 10],
                                                 spawnsOnDefeat=[
                                                     foe('robotBodyguard', width / 2, height / 2,
                                                         [0, 6, 10])]),
                                             foe('brokenTurret', width / 2, height / 4, [0, 4, 10],
                                                 spawnsOnDefeat=[
                                                     foe('flamingRobot', width / 2, height / 2,
                                                         [0, 6, 10])])]),
                         foe('flamingRobot', width / 2, height / 3, [0, 6, 10],
                             spawnsOnDefeat=[foe('robotBodyguard', width / 2, height / 2, [0, 4, 10],
                                                 spawnsOnDefeat=[
                                                     foe('brokenTurret', width / 2, height / 2,
                                                         [0, 6, 10])]),
                                             foe('flamingRobot', width / 2, height / 3, [0, 4, 10],
                                                 spawnsOnDefeat=[
                                                     foe('robotBodyguard', width / 2, height / 2,
                                                         [0, 6, 10])]),
                                             foe('brokenTurret', width / 2, height / 4, [0, 4, 10],
                                                 spawnsOnDefeat=[
                                                     foe('flamingRobot', width / 2, height / 2,
                                                         [0, 6, 10])])]),
                         foe('brokenTurret', width / 2, height / 4, [0, 6, 10],
                             spawnsOnDefeat=[foe('robotBodyguard', width / 2, height / 2, [0, 4, 10],
                                                 spawnsOnDefeat=[
                                                     foe('brokenTurret', width / 2, height / 2,
                                                         [0, 6, 10])]),
                                             foe('flamingRobot', width / 2, height / 3, [0, 4, 10],
                                                 spawnsOnDefeat=[
                                                     foe('robotBodyguard', width / 2, height / 2,
                                                         [0, 6, 10])]),
                                             foe('brokenTurret', width / 2, height / 4, [0, 4, 10],
                                                 spawnsOnDefeat=[
                                                     foe('flamingRobot', width / 2, height / 2,
                                                         [0, 6, 10])])])
                     ]), ]

        for place in shipRooms:
            self.rooms[tuple(place.coordinate)] = place

        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')

    def checkAdjacentEmptySpaces(self, coord):
        adjSpaces = [(coord[0], coord[1] + 1, coord[2]), (coord[0], coord[1] - 1, coord[2]),
                     (coord[0] + 1, coord[1], coord[2]), (coord[0] - 1, coord[1], coord[2])]

        return [space for space in adjSpaces if space not in self.rooms.keys() and space not in self.unavailableCoords]

    def connectsToBiome(self, coord, biome):
        for i in [[coord[0], coord[1] + 1], [coord[0], coord[1] - 1],
                     [coord[0] + 1, coord[1]], [coord[0] - 1, coord[1]]]:
            if i in [j.coordinate[:2] for j in biome]:
                return 1

        return 0

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
                                        foes=[foe('desertCaveLargeFly', width * i / 7, height / 4,
                                                  newRoomCoord) for i in range(1, 7)])
        biome.append(self.rooms[newRoomCoord])
        self.rooms[ledgeDestinationCoord] = room(ledgeDestinationCoord, 'desert', locks=False)
        self.desertCaveDepthTwoEntranceCoord = ledgeDestinationCoord
        roomWithMiniboss = random.choice([place for place in biome if place.difficulty == -1])
        roomWithMiniboss.foes = [foe('desertCaveFlyMiniboss', width / 2,
                                                                    height / 2, roomWithMiniboss.coordinate)]
        roomWithMiniboss.getFoesUponRespawn()
        roomWithMiniboss.usesFoesUponRespawn = True
        roomWithMiniboss.difficulty = 0
        roomWithMiniboss.respawnsFoes = True
        roomWithMiniboss.isBossRoom = True
        random.shuffle(biome)

        for i in [i for i in biome if i.difficulty <= -1]:
            if self.areThereEnoughRoomsConnectedToTheInitialRoom(i, 25):
                initialForestRoom = i.coordinate
                break

        self.rooms[tuple(initialForestRoom)] = room(initialForestRoom, 'desertCaveForest')
        biome += self.makeRooms(25, 'desertCaveForest', initialForestRoom, {})
        lumisLakeCoordinates = self.whereCanSquareOfRoomsFitInEmptyArea(13, biome)
        topLumisLakeYCoord = max([i[1] for i in lumisLakeCoordinates])
        bottomLumisLakeYCoord = min([i[1] for i in lumisLakeCoordinates])
        rightLumisLakeXCoord = max([i[0] for i in lumisLakeCoordinates])
        leftLumisLakeXCoord = min([i[0] for i in lumisLakeCoordinates])

        for coord in lumisLakeCoordinates:
            self.rooms[coord] = room(coord, 'desertCaveLumisLake')

            if coord[1] == topLumisLakeYCoord:
                self.rooms[coord].background = 'topmostLumisLake.bmp'
                self.rooms[coord].bottomYBoundary = height * 0.45
                self.rooms[coord].oxygenLoss = 0

            elif coord[1] == bottomLumisLakeYCoord:
                self.rooms[coord].background = 'bottommostLumisLake.bmp'
                self.rooms[coord].yBoundaries = height * 0.55
                self.rooms[coord].oxygenLoss = 0

            elif coord[0] == rightLumisLakeXCoord:
                self.rooms[coord].background = 'rightmostLumisLake.bmp'
                self.rooms[coord].leftXBoundary = width  * 0.33
                self.rooms[coord].oxygenLoss = 0

            elif coord[0] == leftLumisLakeXCoord:
                self.rooms[coord].background = 'leftmostLumisLake.bmp'
                self.rooms[coord].rightXBoundary = width * 0.66
                self.rooms[coord].oxygenLoss = 0

            else:
                surfaceCoord = tuple(list(coord[:2]) + [9])
                self.rooms[surfaceCoord] = room(surfaceCoord, 'desertCaveLumisLake')
                self.rooms[surfaceCoord].roomThatCanBeManuallyTeleportedTo = self.rooms[coord]
                self.rooms[coord].roomThatCanBeManuallyTeleportedTo = self.rooms[surfaceCoord]
                self.rooms[coord].assignEnvironmentObjectsFromListOfLayouts()
                self.rooms[coord].environmentObjectsUponRespawn = self.rooms[coord].environmentObjects.copy()

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
        self.rooms[ledgeDestinationCoord] = room(ledgeDestinationCoord, 'desert', locks=False)
        self.desertCaveDepthThreeEntranceCoord = ledgeDestinationCoord

    def areThereEnoughRoomsConnectedToTheInitialRoom(self, initialRoom, qty):
        experimentalWorld = copy.deepcopy(self)
        roomsAdded = 0
        potentialCoords = experimentalWorld.checkAdjacentEmptySpaces(initialRoom.coordinate)

        while True:
            if roomsAdded >= qty:
                return 1

            if not potentialCoords:
                return 0

            roomAdded = random.choice(potentialCoords)
            experimentalWorld.rooms[roomAdded] = room(roomAdded, 'ship')
            potentialCoords.remove(roomAdded)
            potentialCoords += experimentalWorld.checkAdjacentEmptySpaces(roomAdded)
            roomsAdded += 1

    def whereCanSquareOfRoomsFitInEmptyArea(self, length, biome):
        minXSide = min([i.coordinate[0] for i in biome]) - length
        maxXSide = max([i.coordinate[0] for i in biome]) + length
        minYSide = min([i.coordinate[1] for i in biome]) - length
        maxYSide = max([i.coordinate[1] for i in biome]) + length
        depth = biome[0].coordinate[2]
        leftRangeLen  = maxXSide + 1 - length - minXSide
        bottomRangeLen = maxYSide + 1 - length - minYSide
        roomCoordsAtBottomLeftSquare = [[minXSide + i, minYSide + j] for i in range(length) for j in range(length)]

        for i in range(leftRangeLen):
            for j in range(bottomRangeLen):
                coords = [(i + k[0], j + k[1], depth) for k in roomCoordsAtBottomLeftSquare.copy()]

                if not [coord for coord in coords if coord in list(self.rooms.keys()) + self.unavailableCoords] and \
                        [coord for coord in coords if self.connectsToBiome(coord, biome)]:
                    return coords

    def makeRooms(self, qty, biome, rootRoom, difficultyQtys):
        potentialCoords = self.checkAdjacentEmptySpaces(rootRoom)
        calmRooms = []

        for i in range(qty):
            newRoomCoord = random.choice(potentialCoords)
            potentialCoords.remove(newRoomCoord)
            self.rooms[newRoomCoord] = room(newRoomCoord, biome, locks=False)
            calmRooms.append(self.rooms[newRoomCoord])

            for coord in self.checkAdjacentEmptySpaces(newRoomCoord):
                if coord not in potentialCoords:
                    potentialCoords.append(coord)

        biomeRooms = calmRooms.copy()

        for key in list(difficultyQtys.keys()):
            for i in range(difficultyQtys[key]):
                if key > -1:
                    combatRoom = random.choice(calmRooms)
                    combatRoom.addFoes(key)
                    calmRooms.remove(combatRoom)

                    if key == 5:
                        combatRoom.locks = True

                else:
                    roomChanged = random.choice(calmRooms)
                    calmRooms.remove(roomChanged)
                    roomChanged.difficulty = key

        if biome == 'desert' and rootRoom[2] == -1:
            self.addTopDesertCaveLayerSpecialRooms(biomeRooms)

        elif biome == 'desert' and rootRoom[2] == -2:
            self.addMiddleDesertCaveLayerSpecialRooms(biomeRooms)

        return biomeRooms

    def addDoors(self):
        coordinates = list(self.rooms.keys())

        for place in [i for i in self.rooms.values() if not i.disconnected]:
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
