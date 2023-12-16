from world import world
from definitions import saveWithPickle, loadWithPickle

rooms = world()
rooms.makeRooms(100, 'desert', (0, 6, -1), {0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2})
rooms.makeRooms(75, 'desert', rooms.desertCaveDepthTwoEntranceCoord, {0: 0})
rooms.makeRooms(75, 'desert', rooms.desertCaveDepthThreeEntranceCoord, {0: 0})
rooms.addDoors()


def load(file):
    rooms = loadWithPickle(f'worldSave{file}.pickle')


def reset():
    global rooms

    rooms = world()
    rooms.makeRooms(100, 'desert', (0, 6, -1), {0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2})
    rooms.makeRooms(75, 'desert', rooms.desertCaveDepthTwoEntranceCoord, {0: 0})
    rooms.makeRooms(75, 'desert', rooms.desertCaveDepthThreeEntranceCoord, {0: 0})
    rooms.addDoors()

    return rooms
