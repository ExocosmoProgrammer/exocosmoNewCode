from room import room
from plainSprites import plainSprite
from variables import display
from foe import foe
from droppedItem import droppedItem
from item import item
from damagingTrap import damagingTrap

import random


class world:
    def __init__(self, **extra):
        self.rooms = {(0, 0, 0): room([0, 0, 0], 'desert')}
        self.potentialCoordinates = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0]]
        shipRooms = [room([0, 0, 10], 'ship', background='shipBackgroundWithDoor.bmp'),

                     room([0, 1, 10], 'ship', background='shipBackgroundWithDoor.bmp', droppedItems=[
                         droppedItem(display.get_width() / 2, display.get_height() / 2, 'pistolInInventory.png',
                                     item('nanotechRevolver', 'pistolInInventory.png'))
                     ], damagingTraps=[damagingTrap('fireTrap2.png', 26, display.get_width() / 20
                                                    * (1 + 2 * i), display.get_height() * (2 / 3 - i * 13 / 900)) for
                                       i in range(10)]),

                     room([0, 2, 10], 'ship', background='shipBackgroundWithDoor.bmp', foes=[
                         foe('brokenTurret', display.get_width() / 2, display.get_height() / 2, [0, 2, 10])]),

                     room([0, 3, 10], 'ship', background='shipBackgroundWithDoor.bmp', foes=[
                         foe('flamingRobot', display.get_width() / 2, display.get_height() / 6, [0, 2, 10])
                     ], waves=[[
                         foe('brokenTurret', display.get_width() / 3, display.get_height() * 2 / 3, [0, 3, 10], 1),
                         foe('brokenTurret', display.get_width() * 2 / 3, display.get_height() * 2 / 3, [0, 3, 10], 1)
                     ]]),

                     room([0, 4, 10], 'ship', background='shipBackgroundWithDoor.bmp', foes=[
                         foe('robotBodyguard', display.get_width() / 2, display.get_height() / 2, [0, 4, 10])
                     ], waves=[[foe('robotBodyguard', display.get_width() / 2, display.get_height() / 2, [0, 4, 10]),
                                foe('flamingRobot', display.get_width() / 2, display.get_height() / 3, [0, 4, 10]),
                                foe('brokenTurret', display.get_width() / 2, display.get_height() / 4, [0, 4, 10], 1)]]),

                     room([0, 5, 10], 'ship', background='shipBackgroundWithDoor.bmp', foes=[
                         foe('robotBodyguard', display.get_width() / 2, display.get_height() / 2, [0, 4, 10]),
                         foe('brokenTurret', display.get_width() / 2, display.get_height() / 3, [0, 4, 10]),
                     ], damagingTraps=[damagingTrap('fireTrap2.png', 26, display.get_width() / 20
                                                    * (1 + 2 * i), display.get_height() * (3 / 4 - i * 13 / 900)) for
                                       i in range(10)],
                          waves=[[foe('flamingRobot', display.get_width() / 4, display.get_height() / 2, [0, 4, 10], 1),
                                  foe('flamingRobot', display.get_width() * 3 / 4, display.get_height() / 2, [0, 4, 10],
                                      1),
                                  foe('brokenTurret', display.get_width() / 2, display.get_height() / 4, [0, 4, 10], 1),
                                  foe('brokenTurret', display.get_width() / 2, display.get_height() * 3 / 4, [0, 4, 10],
                                      1)],
                                 [foe('robotBodyguard', display.get_width() / 10, display.get_height() / 4, [0, 4, 10],
                                      1),
                                  foe('robotBodyguard', display.get_width() / 10, display.get_height() * .75, [0, 4, 10],
                                      1),
                                  foe('robotBodyguard', display.get_width() * 9 / 10, display.get_height() / 5, [0, 4, 10],
                                      1),
                                  foe('robotBodyguard', display.get_width() * 9 / 10, display.get_height() * .75, [0, 4, 10],
                                      1),
                                  ]])]

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
                place.doors.append(plainSprite('door.bmp', display.get_width() * 31 / 3200,
                                               display.get_height() / 2))

            if (place.coordinate[0] + 1, place.coordinate[1], place.coordinate[2]) in coordinates:
                place.doors.append(plainSprite('door.bmp', display.get_width() * 3169 / 3200,
                                               display.get_height() / 2))

            if (place.coordinate[0], place.coordinate[1] + 1, place.coordinate[2]) in coordinates:
                place.doors.append(plainSprite('door.bmp', display.get_width() / 2,
                                               display.get_height() / 45))

            if (place.coordinate[0], place.coordinate[1] - 1, place.coordinate[2]) in coordinates:
                place.doors.append(plainSprite('door.bmp', display.get_width() / 2,
                                               display.get_height() * 44 / 45))


rooms = world()
# rooms.makeRooms(16, 'desert')
rooms.addDoors()
