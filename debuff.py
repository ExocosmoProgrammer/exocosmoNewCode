class debuff:
    def __init__(self, sprite, effect, duration, source=None, effectUponEnding='pass'):
        self.sprite = sprite
        self.effect = effect
        self.duration = duration

        # self.source can be used to track which projectile inflicted self.
        self.source = source

        # self.effectUponEnding will be executed if the thing that self affects dies or if self.duration <= 0.
        self.effectUponEnding = effectUponEnding
