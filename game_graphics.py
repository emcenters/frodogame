import pygame

class Player(pygame.sprite.DirtySprite):
    x_pos = 0
    y_pos = 0
    def __init__(self, image_path, x, y, *groups):
        super().__init__(*groups)
    # Load individual animation frames into a list
        self.sprites = self.load_images(image_path)
        self.current_sprite = 0
        self._layer = 3
        self.direction = 0
        self.image = self.sprites[self.direction][self.current_sprite]
        self.rect = self.image.get_rect(center=(x, y))

    def load_images(self, image_path="res/"):
        sprites = {0: [], 1: [], 2: [], 3: []}
        counter, directions = 0, ["down", "up", "left", "right"]
        for i in range(12):
            if i%3 == 0 and i != 0:
                counter += 1
            sprites[counter].append(pygame.transform.scale_by(pygame.image.load(image_path+directions[counter]+str(i%3)+".png").convert_alpha(), 3))
        return sprites
    def set_direction(self, direction_name):
        directions = ["down", "up", "left", "right"]
        if not str.lower(direction_name) in directions:
            print("Type Error: direction not value, game_graphics line 23")
        else:
            self.direction = directions.index(str.lower(direction_name))

    def update(self, dx, dy):
        if dx != 0 or dy != 0:
            self.dirty = 1
            self.rect.x += dx
            self.rect.y += dy
        self.current_sprite += 0.2
        if self.current_sprite >= 3:
            self.dirty = 1
            self.current_sprite = 0
        self.image = self.sprites[self.direction][int(self.current_sprite)]

class Background(pygame.sprite.DirtySprite):
    def __init__(self, image_name, *groups):
        super().__init__(*groups)
        self._layer = 0  # Lowest layer so it draws behind everything
        self.image = pygame.image.load("res/bgd/"+image_name)
        self.rect = self.image.get_rect()

    def update(self, dx, dy):
        # Move the background
        self.rect.x -= dx
        self.rect.y -= dy
        
        # Loop seamlessly when halfway across
        if self.rect.x <= -800:
            self.rect.x = 0
            
        # Flag as dirty so LayeredDirty redraws it
        self.dirty = 1
    
       