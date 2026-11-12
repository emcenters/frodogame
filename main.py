# Example file showing a circle moving on screen
import pygame
class Button(pygame.sprite.Sprite):
    x_pos = 0
    y_pos = 0
    def __init__(self, image_path, x, y):
       pygame.sprite.Sprite.__init__(self)
       self.image = pygame.image.load(image_path).convert_alpha()
       self.rect = self.image.get_rect(center = (x, y))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect.y -= 300 * dt       
        if keys[pygame.K_s]:
            self.rect.y += 300 * dt
        if keys[pygame.K_a]:
            self.rect.x -= 300 * dt
        if keys[pygame.K_d]:
            self.rect.x += 300 * dt
       
# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

button = Button("res/button4.png", screen.get_width() / 2, screen.get_height() / 2)
sprites = pygame.sprite.Group()
sprites.add(button)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    # pygame.draw.circle(screen, "red", player_pos, 40)
    # pygame.draw(Button(screen, 200, 200))

    sprites.update()
    sprites.draw(screen)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000
    print(pygame.time.get_ticks()//1000)

pygame.quit()