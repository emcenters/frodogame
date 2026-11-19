import pygame

class Player(pygame.sprite.DirtySprite):
    # sprite global variables
    total_sprite_counter = 4
    sprite_speed = 0.2
    current_sprite = 0

    def __init__(self, image_path, x, y, *groups):
        super().__init__(*groups)
    # Load individual animation frames into a list
        self.sprites = self.load_images(image_path)
        self._layer = 3
        self.direction = 0
        self.image = self.sprites[self.direction][self.current_sprite]
        self.rect = self.image.get_rect(center=(x, y))

    def load_images(self, image_path="res/"):
        sprites = {0: [], 1: [], 2: [], 3: []}
        counter, directions = 0, ["down", "up", "left", "right"]
        for i in range(16):
            if i%self.total_sprite_counter == 0 and i != 0:
                counter += 1
            sprites[counter].append(pygame.transform.scale_by(pygame.image.load(image_path+directions[counter]+str(i%4)+".png").convert_alpha(), 3))
        return sprites
    def set_direction(self, direction_name):
        directions = ["down", "up", "left", "right"]
        if not str.lower(direction_name) in directions:
            print("Type Error: direction not value, game_graphics line 23")
        else:
            self.direction = directions.index(str.lower(direction_name))

    def update(self, dx, dy):
        if dx != 0 or dy != 0:
            # self.dirty = 1
            # self.rect.x += dx
            # self.rect.y += dy
            self.current_sprite += self.sprite_speed
        elif self.current_sprite != 0:
            self.current_sprite += 1
        if self.current_sprite >= self.total_sprite_counter:
            self.dirty = 1
            self.current_sprite = 0
        self.image = self.sprites[self.direction][int(self.current_sprite)]

class Background(pygame.sprite.DirtySprite):
    def __init__(self, image_name, screen_center, *groups):
        super().__init__(*groups)
        self._layer = 0  # Lowest layer so it draws behind everything
        self.image = pygame.image.load("res/bgd/"+image_name).convert_alpha()
        self.rect = self.image.get_rect(center = screen_center)
        print(self.rect.x, self.rect.y)
        self.dirty = 1

    def update(self, dx, dy):
        # Move the background
        if dx != 0 or dy != 0:
            self.rect.x -= dx
            self.rect.y -= dy
            self.dirty = 1
            if self.rect.x-48 <= -1600:
                self.rect.x = -1600+48
                self.dirty = 1
            if self.rect.x+48 >= 320:
                self.rect.x = 320-48
                self.dirty = 1
            if self.rect.y-48 <= -840:
                self.rect.y = -840+48
                self.dirty = 1
            if self.rect.y+48 >= 240:
                self.rect.y = 240-48
                self.dirty = 1

    def get_size(self):
        return self.rect.width, self.rect.height
    
       