from world import world
from definitions import saveWithPickle, loadWithPickle

rooms = world()
rooms.makeRooms(100, 'desert', (0, 6, -1), {-2: 50, 0: 3, 1: 3, 2: 3, 3: 3, 4: 2, 5: 2})
rooms.makeRooms(75, 'desert', rooms.desertCaveDepthTwoEntranceCoord, {0: 0})
rooms.makeRooms(75, 'desert', rooms.desertCaveDepthThreeEntranceCoord, {0: 0})
rooms.addDoors()


def load(file):
    rooms = loadWithPickle(f'worldSave{file}.pickle')


def reset():
    global rooms

    rooms = world()
    rooms.makeRooms(100, 'desert', (0, 6, -1),
                    {-2: 70, 0: 3, 1: 3, 2: 3, 3: 3, 4: 2, 5: 2})
    rooms.makeRooms(75, 'desert', rooms.desertCaveDepthTwoEntranceCoord, {0: 0})
    rooms.makeRooms(75, 'desert', rooms.desertCaveDepthThreeEntranceCoord, {0: 0})
    rooms.addDoors()
    return rooms
