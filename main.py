import pygame
import game_graphics

# pygame setup
pygame.init()
screen = pygame.display.set_mode((640, 480))
set_bgd = pygame.Surface(screen.get_size())
set_bgd.fill('white')
screen.blit(set_bgd, (0, 0))
pygame.display.flip()

clock = pygame.time.Clock()
running = True
dt = 0

sprites = pygame.sprite.LayeredDirty()
sprites.clear(screen, set_bgd)
player = game_graphics.Player("res/red_player/", screen.get_width()/2, screen.get_height()/2, sprites)
print(player.get_size())
background = game_graphics.Background("bgd.png", screen.get_rect().center, player.get_size(), sprites)
# game loop that runs until the player hits to close window
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        dx, dy = 0, 0
        # listening to keys pressed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            player.set_direction("up")
            dy -= 300 * dt       
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            player.set_direction("down")
            dy += 300 * dt
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player.set_direction("left")
            dx -= 300 * dt
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player.set_direction("right")
            dx += 300 * dt
    sprites.update(dx, dy)
    dirty_rects = sprites.draw(screen)
    pygame.display.update(dirty_rects)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame
    dt = clock.tick(60) / 1000

pygame.quit()