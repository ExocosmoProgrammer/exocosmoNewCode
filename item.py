import pygame

from variables import IMAGES, display, width, height, GAMESPEED
from rects import rect
from textBox import textBox


class item:
    def __init__(self, name, sprite, description=None, qty=1, stackSize = 99, animation=None, **extra):
        self.sprite = sprite
        self.name = name
        self.place = IMAGES[self.sprite].get_rect(center=(-width, -height))
        self.hitbox = rect(pygame.Rect( -width, -height, width / 15, height * 3 / 80))

        # self.dragged determines whether self should follow the mouse.
        self.dragged = False
        self.qty = qty

        # self.stackSize determines how many items of self's type can fit i one box in the player's inventory.
        self.stackSize = stackSize

        # For weapons that allow the player to attack, self.cooldown may be used to determine how long the player must
        # wait after performing an attack with self until doing so again.
        self.cooldown = 0

        # self.standardCooldown is a cooldown for using self's standard attack if possible.
        self.standardCooldown = 0

        # self.altCooldown is a cooldown for using self's alternate attack if possible.
        self.altCooldown = 0
        self.animation = [self.sprite] if animation is None else animation.copy()
        self.animationFrame = 0

        # self's description has a template that is used when another description is not specified for self.
        self.description = f'{name.title()} is a material.' if description is None else description

        # self.textBox will be drawn when the player's inventory is shown and the mouse collides with self.
        self.textBox = textBox(self.description, 'newLetter', 'textBox.png', self.hitbox.centerx,
                               self.hitbox.centery, width / 4)

        # You should already understand the purpose and functionality of the following loop.
        for stat in list(extra.keys()):
            exec(f'self.{stat} = extra[stat]')

    def progressAnimation(self):
        """Progress self's animation."""
        self.animationFrame += GAMESPEED

        if self.animationFrame >= len(self.animation):
            self.animationFrame = 0

        self.sprite = self.animation[int(self.animationFrame)]

    def updateHitbox(self):
        """Update self's hitbox and text box."""

        # Update the hitbox.
        self.hitbox = rect(pygame.Rect(self.place.centerx - width / 30, self.place.centery - height * 3 / 160,
                                       width / 15, height * 3 / 80))
        self.hitbox.updatePoints()

        # Update the text box.
        self.textBox = textBox(self.description, 'newLetter', 'textBox.png', self.hitbox.centerx,
                               self.hitbox.centery, width / 4)
