import pygame

class Player(pygame.sprite.DirtySprite):
    # sprite global variables
    total_sprite_counter = 4
    sprite_speed = 0.2
    current_sprite = 0

    def __init__(self, image_path, x, y, *groups):
        self._layer = 3
        super().__init__(*groups)
    # Load individual animation frames into a list
        self.sprites = self.load_images(image_path)
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
        try:
            self.direction = directions.index(str.lower(direction_name))
        except:
            print("Type Error: direction not value, game_graphics Player line 23")
            

    def get_size(self):
        return self.rect.width, self.rect.height

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
    player_size = (16, 16)
    def __init__(self, image_name, screen_center, player_size, *groups):
        self._layer = 0  # Lowest layer, draws behind all the other sprites
        super().__init__(*groups)
        self.image = pygame.image.load("res/bgd/"+image_name).convert_alpha()
        self.rect = self.image.get_rect(center = screen_center) # Sets the center of the image to the center given
        print(self.rect.x, self.rect.y)
        initial_coords = {"x": self.rect.x, "y": self.rect.y}
        self.x_bounds = (initial_coords["x"]-int(self.rect.width/2), initial_coords["x"]+self.rect.width/2)
        self.y_bounds = (initial_coords["y"]-int(self.rect.height/2), initial_coords["y"]+self.rect.height/2)
        if isinstance(player_size, (int, float)) and isinstance(player_size, bool): # check if player_size is singular num (square) or tuple
            self.player_size = (player_size, player_size)
        else:
            try:
                self.player_size = (player_size[0], player_size[1])
            except:
                print("Not valid player_size, game_graphics Background line 61")
        self.dirty = 1

    def update(self, dx, dy):
        # Move the background
        if dx != 0 or dy != 0:
            self.rect.x -= dx
            self.rect.y -= dy
            if self.rect.x-self.player_size[0] <= self.x_bounds[0]:
                self.rect.x = self.x_bounds[0]+self.player_size[0]
            if self.rect.x+self.player_size[0] >= self.x_bounds[1]:
                self.rect.x = self.x_bounds[1]-self.player_size[0]
            if self.rect.y-self.player_size[1] <= self.y_bounds[0]:
                self.rect.y = self.y_bounds[0]+self.player_size[1]
            if self.rect.y+self.player_size[1] >= self.y_bounds[1]:
                self.rect.y = self.y_bounds[1]-self.player_size[1]
            self.dirty = 1

    def get_size(self):
        return self.rect.width, self.rect.height
    
       