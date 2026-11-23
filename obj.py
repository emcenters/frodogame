import pygame
class Object(pygame.sprite.DirtySprite):
    def __init__(self, want_collision, x, y, *groups):
        super().__init__(*groups)
        self.is_solid = want_collision
        self.x = x
        self.y = y
        print(self.x, self.y)

    def update(self):
        pass


