from world import world
from definitions import saveWithPickle, loadWithPickle

rooms = world()
rooms.makeRooms(1, 'desert', (0, 6, -1), {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0})
rooms.makeRooms(5, 'desert', rooms.desertCaveDepthTwoEntranceCoord, {0: 0})
rooms.makeRooms(5, 'desert', rooms.desertCaveDepthThreeEntranceCoord, {0: 0})
rooms.addDoors()


def load(file):
    rooms = loadWithPickle(f'worldSave{file}.pickle')
