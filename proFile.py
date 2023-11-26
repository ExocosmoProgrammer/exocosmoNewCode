from pro import player
from definitions import loadWithPickle

pro = player()


def load(file):
    pro = loadWithPickle(f'playerSave{file}.pickle')
