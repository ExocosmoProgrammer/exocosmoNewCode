from definitions import lesser, greater


class line:
    def __init__(self, slope, constant, boundaries, **extra):
        self.slope = slope
        self.constant = constant
        self.boundaries = [lesser(boundaries[0], boundaries[1]),
                           greater(boundaries[0], boundaries[1])]

        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')

    def YAtX(self, x):
        """return self.slope * x + self.constant"""
        return self.slope * x + self.constant
