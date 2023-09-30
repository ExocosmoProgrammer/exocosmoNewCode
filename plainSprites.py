from variables import IMAGES


class plainSprite:
    def __init__(self, sprite, centerx, centery):
        self.sprite = sprite
        self.place = IMAGES[sprite].get_rect(center=(centerx, centery))