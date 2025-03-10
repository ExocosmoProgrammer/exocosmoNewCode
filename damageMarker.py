from word import word
from variables import GAMESPEED, width

import math


class damageMarker:
    def __init__(self, damage, x, y):
        """Members of this class will be used to show the damage inflicted to enemies."""

        damageStr = str(int(damage))
        left = x - width * len(damageStr) / 640
        self.text = word(left, y, damageStr, 'fancyNumber', extraHorizontalSpacing=-width / 480)
        self.initialX = x
        self.initialY = y
        self.duration = 200

    def update(self):
        """Update self."""

        self.duration -= GAMESPEED
        self.text.move(0, 3 * math.cos(self.duration * math.pi / 300))
