# Example file showing a circle moving on screen
import pygame
import game_graphics

# pygame setup
pygame.init()
screen = pygame.display.set_mode((640, 480))
background = pygame.Surface(screen.get_size())
background.fill('white')
screen.blit(background, (0, 0))
pygame.display.flip()

clock = pygame.time.Clock()
running = True
dt = 0

sprites = pygame.sprite.LayeredDirty()
player = game_graphics.Player("res/red_player/", screen.get_width()/2, screen.get_height()/2, sprites)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        dx, dy = 0, 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.set_direction(1)
            dy -= 300 * dt       
        if keys[pygame.K_s]:
            player.set_direction(0)
            dy += 300 * dt
        if keys[pygame.K_a]:
            player.set_direction(2)
            dx -= 300 * dt
        if keys[pygame.K_d]:
            player.set_direction(3)
            dx += 300 * dt
    # fill the screen with a color to wipe away anything from last frame
    # screen.fill("white")

    # pygame.draw.circle(screen, "red", player_pos, 40)
    # pygame.draw(Button(screen, 200, 200))
    
    sprites.update(dx, dy)
    # sprites.draw(screen)
    dirty_rects = sprites.draw(screen, background)
    pygame.display.update(dirty_rects)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()