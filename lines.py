from definitions import lesser, greater


class line:
    def __init__(self, slope, constant, boundaries, **extra):
        # For vertical lines, 'slope' is None, 'constant' is the x value of all the points on the line,
        # and 'boundaries' represents the y boundaries of the line. For other lines, 'slope' is the slope of the line,
        # 'constant' is what the line's y intercept would be if the line has a y-intercept or were extended enough
        # to have a y-intercept, and 'boundaries' represents the x boundaries of the line.
        self.slope = slope
        self.constant = constant
        self.boundaries = [lesser(boundaries[0], boundaries[1]),
                           greater(boundaries[0], boundaries[1])]

        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')

    def YAtX(self, x):
        """return self.slope * x + self.constant"""
        return self.slope * x + self.constant
