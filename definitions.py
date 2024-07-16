import math
import pickle
import random
import pygame

from pygame import mixer
from variables import display, IMAGES, BACKGROUNDS, width, height, fullscreenRect, playerHeight, getProperPath


def sqrt(x):
    """sqrt(x) returns the square root of x."""
    return x ** (1 / 2)


def sign(x):
    """sign(x) will return 1 if x is positive, 0 if x is zero, and -1 if x is negative."""
    return 0 if x == 0 else x / abs(x)


def getRadians(x, y):
    """getRadians(x, y) returns the angle, in radians, from -π to π, made by the x-axis right of the origin and
        a line from the origin to point(x, y)."""
    return 0 if x == y == 0 else -math.acos(x / sqrt(x ** 2 + y ** 2)) * sign(y)


def getDegrees(x, y):
    """getDegrees(x, y) returns the angle, in degrees, from -180 to 180, made by the x-axis right of the origin and a
    line from the origin to point(x, y)."""
    return getRadians(x, y) * 180 / math.pi


def pointDistance(p1, p2):
    """pointDistance(p1, p2) returns the distance from point p1 to point p2."""
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def rotate(point, center, angle):
    """rotate(x, y, z) returns the coordinates of point x rotated z radians around point y."""
    dis = pointDistance(point, center)
    newAngle = getRadians(point[0] - center[0], point[1] - center[1]) - angle
    return [center[0] + dis * math.cos(newAngle), center[1] + dis * math.sin(newAngle)]


def strIndex(string, character):
    """strIndex(x, y) returns the index of the first usage of character y in string x."""
    for i in string:
        if i == character:
            return i


def lesser(a, b):
    """lesser(a, b) returns the lesser value of a and b."""
    return a if a < b else b


def greater(a, b):
    """greater(a, b) returns the greater value of a and b."""
    return a if a > b else b


def checkLineCollision(a, b):
    """checkLineCollision(a, b) returns 1 if line object a and line object b collide within their ranges
        and domains, else checkLineCollision(a, b) returns 0."""

    # A line with slope None represents a vertical line.
    if a.slope is not None and b.slope is None:
        # Find where a and b would intersect if they were extended infinitely.
        intersectPoint = (b.constant, a.constant + a.slope * b.constant)

        # If the point of intersection is within the boundaries of both lines, return 1.
        if a.boundaries[0] <= intersectPoint[0] <= a.boundaries[1] and b.boundaries[0] <= intersectPoint[1] \
                <= b.boundaries[1]:
            return 1

    elif a.slope is None and b.slope is not None:
        # Find where a and b would intersect if they were extended infinitely.
        intersectPoint = (a.constant, b.constant + b.slope * a.constant)

        # If the point of intersection is within the boundaries of both lines, return 1.
        if b.boundaries[0] <= intersectPoint[0] <= b.boundaries[1] and a.boundaries[0] <= intersectPoint[1] <= \
                a.boundaries[1]:
            return 1

    elif a.slope is not None and b.slope is not None:
        try:
            # Find where a and b would intersect if they were extended infinitely.
            intersectPoint = (b.constant - a.constant) / (a.slope - b.slope)

            # If the point of intersection is within the boundaries of both lines, return 1.
            if b.boundaries[0] <= intersectPoint <= b.boundaries[1] and a.boundaries[0] <= intersectPoint <= \
                    a.boundaries[1]:
                return 1

        # The next except block will execute iff a and b have the same slope.
        except ZeroDivisionError:
            # If a and b are segments of the same infinite line and their boundaries overlap, return 1.
            if a.constant == b.constant and a.boundaries[1] >= b.boundaries[0] and b.boundaries[1] >= \
                    a.boundaries[0]:
                return 1

    # If both lines are vertical, are segments of the same line, and have overlapping boundaries, return 1.
    elif a.boundaries[1] >= b.boundaries[0] and b.boundaries[1] >= a.boundaries[0] and a.constant == b.constant:
        return 1

    # If a and b do not collide, return 0.
    return 0


def checkConditionListItems(items, condition):
    """checkConditionalListItems(x, y) returns 1 if condition y is true for any item in list x, else
        checkConditionalListItems(x, y) returns 0."""
    for item in items:
        if eval(condition):
            return 1

    return 0


def draw(sprite, rotation=0, scaling=None):
    """draw(x, y, (a, b)) draws x's sprite, scaled to have dimensions a X b and rotated y degrees, to the display."""

    if scaling is None:
        scaledSprite = IMAGES[sprite.sprite]

    else:
        scaledSprite = pygame.transform.scale(IMAGES[sprite.sprite], scaling)

    display.blit(pygame.transform.rotate(scaledSprite, rotation), sprite.place)


def getDirection(x, y):
    """getDirection(x, y) returns a letter from ['w', 'a', 's', 'd'] depending on x and y."""

    if abs(x) > abs(y):
        return 'd' if x > 0 else 'a'

    else:
        return 's' if y > 0 else 'w'


def getPath(speed, a, b):
    """getPath(x, y, z) returns a list of the horizontal and vertical movement of a projectile that is starting
        with a center at point y and headed towards point z while moving x units per frame."""

    xdis = b[0] - a[0]
    ydis = b[1] - a[1]

    try:
        xpath = speed * sign(xdis) / sqrt(1 + (ydis / xdis) ** 2)

    except ZeroDivisionError:
        xpath = 0

    try:
        ypath = speed * sign(ydis) / sqrt(1 + (xdis / ydis) ** 2)

    except ZeroDivisionError:
        ypath = 0

    return [xpath, ypath]


def getPartiallyRandomPath(speed, a, b, angleVariationDegreeInt):
    """getPath(x, y, z, a) returns a list of the horizontal and vertical movement of a projectile that
       is starting with a center at point y and headed at a random angle that is withing a degrees of the
       angle that is from point y to point z while moving at x units per frame."""

    initialAngle = getDegrees(b[0] - a[0], a[1] - b[1])
    newAngle = (initialAngle + random.randint(-int(angleVariationDegreeInt * 100),
                                              int(angleVariationDegreeInt * 100)) / 100) * math.pi / 180
    return [math.cos(newAngle) * speed, math.sin(newAngle) * speed]


def saveWithPickle(file: str, object):
    """saveWithPickle(x, y) saves object y to file x. saveWithPickle(x) starts by making a file with name x if
       no file with name x can be accessed."""

    # Modify file as needed to access the correct file.
    file = getProperPath(file)

    # Attempt to save object to file.
    try:
        with open(file, 'wb') as saveFile:
            pickle.dump(object, saveFile)

    # If no file with name file is found, create one.
    except FileNotFoundError:
        with open(file, 'xb') as saveFile:
            pickle.dump(object, saveFile)


def loadWithPickle(file: str):
    """loadWithPickle(x) returns the object that file x contains."""

    with open(getProperPath(file), 'rb') as fileLoaded:
        return pickle.load(fileLoaded)


# def play(song):
#     mixer.init()
#     mixer.music.load(f'music/{song}')
#     mixer.music.set_volume(0)
#     mixer.music.play(-1)


def checkMouseCollision(unrotatedRectangle):
    """checkMouseCollision(x) returns 1 if the mouse is over rect x. Otherwise, checkMouseCollision(x) returns 0."""
    unrotatedRectangle.getMajorInfo()

    if unrotatedRectangle.left < pygame.mouse.get_pos()[0] < unrotatedRectangle.right \
            and unrotatedRectangle.top < pygame.mouse.get_pos()[1] < unrotatedRectangle.bottom:
        return 1

    return 0


def drawToFullScreen(sprite: str):
    """drawToFullScreen(x) prints image x from the BACKGROUNDS folder to the full screen."""
    display.blit(BACKGROUNDS[sprite], fullscreenRect)


def signOrRandom(x):
    """signOrRandom(x) returns sign(x) if x is not 0. Otherwise, signOrRandom(x) returns a random number from
       [-1, 1]."""
    return sign(x) if x != 0 else random.choice([-1, 1])


def skip(*args):
    """Calling the skip function does nothing regardless of what arguments are used. Skip may be used when a function
    must be called but does not need to do anything."""
    pass


def plusOrMinus(x):
    """plusOrMinus(x) randomly returns either x or -x."""
    return x if random.randint(0, 1) else -x


def percentChance(x):
    """percentChance(X) has an x% chance to return true and will otherwise return false."""
    return True if random.randint(1, 100) <= x else False


def getYBoundary(obj, playerYBoundary):
    """getYBoundary(x, y) returns the top y boundary that object x should have in a room where the player has
    top y boundary y."""
    return playerYBoundary + playerHeight - obj.place.height + obj.hitbox.height


def getYBoundaryFromPlace(place, playerYBoundary, hitbox):
    """getYBoundaryFromPlace(x, y, z) returns the top y boundary that an object with place x and hitbox z should have
    in a room where the player has top y boundary y."""
    return playerYBoundary + playerHeight - place.height + hitbox.height
