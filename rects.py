from definitions import rotate, lesser, greater, checkLineCollision
from lines import line
from variables import display
import pygame
# I will use the rect class for collision detection, so that collision can be checked with rotated rectangles.


class rect:
    def __init__(self, pyRect=None, angle=0, pointOfRotation=None, **extra):
        if pyRect != None:
            self.points = [[pyRect.left, pyRect.top], [pyRect.right, pyRect.top],
                           [pyRect.right, pyRect.bottom], [pyRect.left, pyRect.bottom]]
            self.center = [pyRect.centerx, pyRect.centery]
            self.angle = angle
            self.updatePoints()

            if angle != 0:
                if pointOfRotation is not None:
                    for i in range(4):
                        self.points[i] = rotate(self.points[i], eval(pointOfRotation), angle)
                else:
                    for i in range(4):
                        self.points[i] = rotate(self.points[i], self.center, angle)

        self.updatePoints()

        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')

    def updatePoints(self):
        self.left = min([point[0] for point in self.points])
        self.right = max([point[0] for point in self.points])
        self.bottom = max([point[1] for point in self.points])
        self.top = min([point[1] for point in self.points])
        self.center = [(self.left + self.right) / 2, (self.top + self.bottom) / 2]
        self.centerx = self.center[0]
        self.centery = self.center[1]
        self.width = self.right - self.left
        self.height = self.bottom - self.top

    def rotate(self, angle=None):
        self.angle += angle
        for i in range(4):
            self.points[i] = rotate(self.points[i], self.center, angle)

    def move(self, x, y):
        for point in self.points:
            point[0] += x
            point[1] += y

    def scale(self, x, y):
        angle = self.angle
        self.updatePoints()
        self.rotate(-self.angle)
        self.updatePoints()

        for point in self.points:
            if point[0] == self.left:
                point[0] = self.centerx - x / 2

            else:
                point[0] = self.centerx + x / 2

            if point[1] == self.top:
                point[1] = self.centery - y / 2

            else:
                point[1] = self.centery + y / 2

        self.rotate(angle)

    def getMajorInfo(self):
        self.left = min([point[0] for point in self.points])
        self.right = max([point[0] for point in self.points])
        self.bottom = max([point[1] for point in self.points])
        self.top = min([point[1] for point in self.points])
        self.width = self.right - self.left
        self.height = self.bottom - self.top

    def getEnds(self):
        self.left = min([point[0] for point in self.points])
        self.right = max([point[0] for point in self.points])
        self.bottom = max([point[1] for point in self.points])
        self.top = min([point[1] for point in self.points])

    def getLines(self):
        self.lines = []

        for i in range(-1, 3):
            try:
                slope = (self.points[i][1] - self.points[i + 1][1]) / (self.points[i][0] - self.points[i + 1][0])
                constant = self.points[i][1] - slope * self.points[i][0]
                boundaries = [self.points[i][0], self.points[i + 1][0]]

            except ZeroDivisionError:
                slope = None
                constant = self.points[i][0]
                boundaries = [self.points[i][1], self.points[i + 1][1]]

            self.lines.append(line(slope, constant, boundaries))

    def showCollision(self, rectangle):

        for i in self.points:
            display.fill((255, 255, 255), pygame.Rect(i[0] - 5, i[1] - 5, 10, 10))

        for i in rectangle.points:
            display.fill((100, 100, 100), pygame.Rect(i[0] - 5, i[1] - 5, 10, 10))

    def checkCollision(self, rectangle=None):
        self.updatePoints()
        rectangle.updatePoints()

        if self.points[0][0] == self.points[1][0] or self.points[0][1] == self.points[1][1]:
            selfDiagonal = 0

        else:
            selfDiagonal = 1

        if rectangle.points[0][0] == rectangle.points[1][0] or rectangle.points[0][1] == rectangle.points[1][1]:
            rectDiagonal = 0

        else:
            rectDiagonal = 1

        if self.top < rectangle.bottom and rectangle.top < self.bottom and self.left < rectangle.right and \
                rectangle.left < self.right:
            pass

        else:
            return 0

        if rectDiagonal == 0 and selfDiagonal == 0:
            return 1

        elif selfDiagonal == 0 and rectDiagonal == 1:
            rectangle.getLines()

            try:
                for point in self.points:
                    if lesser(rectangle.lines[0].YAtX(point[0]), rectangle.lines[2].YAtX(point[0])) <= point[1] <= \
                            greater(rectangle.lines[0].YAtX(point[0]), rectangle.lines[2].YAtX(point[0])) \
                            and lesser(rectangle.lines[1].YAtX(point[0]), rectangle.lines[3].YAtX(point[0])) <= \
                            point[1] <= greater(rectangle.lines[1].YAtX(point[0]), rectangle.lines[3].YAtX(point[0])):
                        return 1

            except TypeError:
                return 1

            self.getLines()

            for selfLine in self.lines:
                for rectLine in rectangle.lines:
                    if checkLineCollision(selfLine, rectLine):
                        return 1

        elif rectDiagonal == 0 and selfDiagonal == 1:
            self.getLines()

            try:
                for point in rectangle.points:
                    if lesser(self.lines[0].YAtX(point[0]), self.lines[2].YAtX(point[0])) <= point[1] <= \
                            greater(self.lines[0].YAtX(point[0]), self.lines[2].YAtX(point[0])) \
                            and lesser(self.lines[1].YAtX(point[0]), self.lines[3].YAtX(point[0])) <= point[1] <= \
                            greater(self.lines[1].YAtX(point[0]), self.lines[3].YAtX(point[0])):
                        self.showCollision(rectangle)
                        return 1
            except TypeError:
                return 1

            rectangle.getLines()

            for rectLine in rectangle.lines:
                for selfLine in self.lines:
                    if checkLineCollision(selfLine, rectLine):
                        self.showCollision(rectangle)
                        return 1
        else:
            self.getLines()
            rectangle.getLines()

            for point in rectangle.points:
                if lesser(self.lines[0].YAtX(point[0]), self.lines[2].YAtX(point[0])) <= point[1] <= \
                        greater(self.lines[0].YAtX(point[0]), self.lines[2].YAtX(point[0])) \
                        and lesser(self.lines[1].YAtX(point[0]), self.lines[3].YAtX(point[0])) <= point[1] <= \
                        greater(self.lines[1].YAtX(point[0]), self.lines[3].YAtX(point[0])):
                    return 1

            for point in self.points:
                if lesser(rectangle.lines[0].YAtX(point[0]), rectangle.lines[2].YAtX(point[0])) <= point[1] <= \
                        greater(rectangle.lines[0].YAtX(point[0]), rectangle.lines[2].YAtX(point[0])) \
                        and lesser(rectangle.lines[1].YAtX(point[0]), rectangle.lines[3].YAtX(point[0])) <= point[1] \
                        <= greater(rectangle.lines[1].YAtX(point[0]), rectangle.lines[3].YAtX(point[0])):
                    return 1

            for rectLine in rectangle.lines:
                for selfLine in self.lines:
                    if checkLineCollision(selfLine, rectLine):
                        return 1

        return 0
