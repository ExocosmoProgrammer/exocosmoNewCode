from room import room
from plainSprites import plainSprite
from variables import height, width, yBoundaryShip
from foe import foe
from droppedItem import droppedItem
from item import item
from damagingTrap import damagingTrap
from definitions import saveWithPickle, loadWithPickle

import random


class world:
    def __init__(self, **extra):
        self.rooms = {(0, 0, 0): room([0, 0, 0], 'desert')}
        self.potentialCoordinates = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0]]
        shipRooms = [room([0, 0, 10], 'ship', background='shipBackgroundWithDoor.bmp'),

                     room([0, 1, 10], 'ship', droppedItems=[
                         droppedItem(width / 2, height / 2, 'pistolInInventory.png',
                                     item('nanotechRevolver', 'pistolInInventory.png'))
                     ], damagingTraps=[damagingTrap('fireTrap2.png', 26, width / 20
                                                    * (1 + 2 * i), height * (2 / 3 - i * 13 / 900)) for
                                       i in range(10)]),

                     room([0, -1, 10], 'ship', foes=[
                         foe('hellhound', width / 2, height / 2, [0, 2, 10]),
                         foe('tougherShipMiniboss', width / 2, height / 4, [0, 2, 10])],
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
                         foe('flamingRobot', width / 2, height / 3, [0, 2, 10])
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
                         foe('robotBodyguard', width / 2, height / 2, [0, 4, 10]),
                         foe('brokenTurret', width / 2, height / 3, [0, 4, 10]),
                     ], damagingTraps=[damagingTrap('fireTrap2.png', 26, width / 20
                                                    * (1 + 2 * i), height * (5 / 8 - i * 13 / 900)) for
                                       i in range(10)],
                          waves=[[foe('flamingRobot', width / 4, height / 2, [0, 4, 10]),
                                  foe('flamingRobot', width * 3 / 4, height / 2, [0, 4, 10], ),
                                  foe('brokenTurret', width / 2, height / 4, [0, 4, 10]),
                                  foe('brokenTurret', width / 2, height * 3 / 4, [0, 4, 10], )],
                                 [foe('robotBodyguard', width / 10, height / 4, [0, 4, 10], ),
                                  foe('robotBodyguard', width / 10, height * .75, [0, 4, 10], ),
                                  foe('robotBodyguard', width * 9 / 10, height / 5, [0, 4, 10], ),
                                  foe('robotBodyguard', width * 9 / 10, height * .75, [0, 4, 10], ),
                                  ]]),

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

    def makeRooms(self, qty, biome):
        for i in range(qty):
            coordinate = self.potentialCoordinates[random.randint(0, len(self.potentialCoordinates) - 1)]
            self.potentialCoordinates.remove(coordinate)
            self.rooms[tuple(coordinate)] = room(coordinate, biome)

            for position in [[coordinate[0], coordinate[1] + 1, 0],
                             [coordinate[0], coordinate[1] - 1, 0],
                             [coordinate[0] + 1, coordinate[1], 0],
                             [coordinate[0] + 1, coordinate[1], 0]]:
                if tuple(position) not in list(self.rooms.keys()) and position not in self.potentialCoordinates:
                    self.potentialCoordinates.append(position)

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
# rooms.makeRooms(16, 'desert')
rooms.addDoors()


def saveWorld(file):
    saveWithPickle(f'worldSave{file}.pickle', rooms)


def loadWorld(file):
    return loadWithPickle(f'worldSave{file}.pickle')
