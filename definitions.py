import math
import pickle
import random
import pygame
import pydub
import time

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


def draw(sprite, rotation=0, scaling=None, offset=(0, 0), flippedHorizontally=False, flippedVertically=False):
    """draw(x, y, (a, b)) draws x's sprite, scaled to have dimensions a X b and rotated y degrees, to the display."""

    scaledSprite = IMAGES[sprite.sprite] if scaling is None else \
        pygame.transform.scale(IMAGES[sprite.sprite], scaling)
    properSprite = pygame.transform.flip(scaledSprite, flippedHorizontally, flippedVertically)

    blitWithOffset(pygame.transform.rotate(properSprite, rotation), sprite.place, offset)


def blitWithOffset(sprite, place, offset):
    """Draw sprite to place shifted by offset."""
    offsetPlace = place.copy()
    offsetPlace.x += offset[0]
    offsetPlace.y += offset[1]
    display.blit(sprite, offsetPlace)


def fillWithOffset(color, place, offset):
    """Fill place shifted by offset with color."""
    offsetPlace = place.copy()
    offsetPlace.x += offset[0]
    offsetPlace.y += offset[1]
    display.fill(color, offsetPlace)


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
    """getPartiallyRandomPath(x, y, z, a) returns a list of the horizontal and vertical movement of a projectile that
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


def checkMouseCollision(unrotatedRectangle):
    """checkMouseCollision(x) returns 1 if the mouse is over rect x. Otherwise, checkMouseCollision(x) returns 0."""
    unrotatedRectangle.getMajorInfo()

    if unrotatedRectangle.left < pygame.mouse.get_pos()[0] < unrotatedRectangle.right \
            and unrotatedRectangle.top < pygame.mouse.get_pos()[1] < unrotatedRectangle.bottom:
        return 1

    return 0


def drawToFullScreen(sprite, offset=(0, 0)):
    """drawToFullScreen(x) prints image x from the BACKGROUNDS folder to the full screen."""
    blitWithOffset(BACKGROUNDS[sprite], fullscreenRect, offset)


def signOrRandom(x):
    """signOrRandom(x) returns sign(x) if x is not 0. Otherwise, signOrRandom(x) returns a random number from
       [-1, 1]."""
    return sign(x) if x != 0 else random.choice([-1, 1])


def sec(x):
    return 1 / math.cos(x)


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


def camelCaseToNormalText(text: str, capitalizeStart=True, titleCase=True):
    """Converts text from camel case to normal text."""

    # finalText will be returned.
    finalText = text[0].upper() if capitalizeStart or titleCase else text[0]

    # Add to the finalText.
    for i in range(1, len(text)):
        # If the next character is capital, then a space is added to separate words. The next
        # character may be made lowercase.
        if text[i].isupper():
            finalText += ' '
            finalText += text[i] if titleCase else text[i].lower()

        # Otherwise, just add the next character.
        else:
            finalText += text[i]

    # Return the desired text.
    return finalText


def normalTextToCamelCase(text):
    """Converts normal text to text in camel case."""

    # finalText will be returned.
    finalText = text[0].lower()

    # capitalizeNext determines whether the next character should be capital.
    capitalizeNext = False

    # Add to finalText.
    for i in range(1, len(text)):
        # If text[i] is a space, then the next character should be capitalized.
        if text[i] == ' ':
            capitalizeNext = True

        # Otherwise, add text[i] in the desired case to finalText and set capitalizeNext to False.
        else:
            finalText += text[i].upper() if capitalizeNext else text[i].lower()
            capitalizeNext = False

    # Return the result.
    return finalText


def getEvents(eventTypes: dict):
    """Returns events of specified types and removes them from the event queue while keeping other events. eventTypes
    should be a dictionary where the keys are accepted event types and the values are lists of accepted keys when
    applicable."""

    # returnedEvents will be returned.
    returnedEvents = []

    # Add events to returnedEvents and remove accepted events from the event queue.
    for event in pygame.event.get():
        # If event's type is accepted and the key is accepted if applicable, then add event to returnedEvents.
        if event.type in eventTypes.keys() and (not hasattr(event, 'key') or event.key in eventTypes[event.type]):
            returnedEvents.append(event)

        # Otherwise, put the event back in the event queue.
        else:
            pygame.event.post(event)

    # Return returnedEvents.
    return returnedEvents


def temporarilyPlay(music):
    pygame.mixer.music.load(f'music/{music}')
    pygame.mixer.music.play(-1)


def playSoundEffect(effect, volume=0.3):
    """Play effect."""

    soundEffect = pygame.mixer.Sound(f'sounds/{effect}')
    soundEffect.set_volume(volume)
    soundEffect.play()


def angleToMouse(obj):
    """Returns the angle from object obj with attributes x and y to the mouse."""

    return getRadians(pygame.mouse.get_pos()[0] - obj.x, pygame.mouse.get_pos()[1] - obj.y)


def degToMouse(obj):
    """Returns the degrees from object obj with attributes x and y to the mouse."""

    return getDegrees(pygame.mouse.get_pos()[0] - obj.x, pygame.mouse.get_pos()[1] - obj.y)


def playAnimation(animation, pause=0.2, fillBeforeFrames=None):
    """Plays the animation, pausing for pause seconds after each frame. Fills the screen with color fillBeforeFrames
    if it is not None."""

    for i in animation:
        if fillBeforeFrames is not None:
            display.fill(fillBeforeFrames)

        display.blit(IMAGES[i], fullscreenRect)
        pygame.display.flip()
        time.sleep(pause)
