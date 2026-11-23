import pygame
import game_graphics
import frodo_maze
import frodo_wordle
import wordle_graphics
import yell_leaders_simon
import textbox


MAIN_SCREEN = 0
WORDLE_SCREEN = 1
MAZE_SCREEN = 2
BUS_SCREEN = 3
SIMON_SAYS_SCREEN = 4
END_SCREEN = 5

current_screen = 0

WINDOW_SIZE = (1080, 640)
SCREEN_FLAGS = pygame.SCALED

at_maze = False
at_wordle = True
at_simon = False
at_bus = False

gen_font = pygame.font.SysFont("arial", 200, bold=True)

# pygame setup
pygame.init()

screen = pygame.display.set_mode(WINDOW_SIZE, SCREEN_FLAGS)
set_bgd = pygame.Surface(screen.get_size())
set_bgd.fill('black')
screen.blit(set_bgd, (0, 0))
pygame.display.flip()

clock = pygame.time.Clock()
running = True
dt = 0
distance_factor = 400
sprites = pygame.sprite.LayeredDirty()
sprites.clear(screen, set_bgd)
player = game_graphics.Player("res/sprite_sheet/", True, screen.get_width()/2, screen.get_height()/2, 2, sprites)
background = game_graphics.Background("bgd.png", screen.get_rect().center, player.get_size(), 0, sprites)
fullscreen = False

# For the maze
maze_turns = frodo_maze.directions()



# game loop that runs until the player hits to close window
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                pygame.display.toggle_fullscreen()
                    
            elif event.key == pygame.K_ESCAPE:
                if fullscreen:
                    pygame.display.toggle_fullscreen()
                fullscreen = False
            if current_screen == MAIN_SCREEN:
                if event.key == pygame.K_e and type(at_wordle) == bool and at_wordle:
                    current_screen = WORDLE_SCREEN
                    screen = pygame.display.set_mode((640, 640), SCREEN_FLAGS)
                    if fullscreen:
                        pygame.display.toggle_fullscreen()
                    wordle_bgd = pygame.Surface(screen.get_size())
                    screen.blit(wordle_bgd, (0, 0))
                    game = wordle_graphics.start_full_game()
                    wordle_graphics.draw_wordle(screen, event, game, True)
                    pygame.display.flip()
            elif current_screen == MAZE_SCREEN:
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    frodo_maze.check_guess("L")
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    frodo_maze.check_guess("R")
            elif current_screen == WORDLE_SCREEN:
                game = wordle_graphics.draw_wordle(screen, event, game, False)
                if game["state"] == "won":
                    print("WON")
                    current_screen = MAIN_SCREEN
                    screen = pygame.display.set_mode(WINDOW_SIZE, SCREEN_FLAGS)
                    sprites.clear(screen, set_bgd)
                    for sprite in sprites:
                        sprite.dirty = 1
                    got_letter = textbox.Textbox(player.get_coords()[0]+player.get_size()[0]//2, player.get_coords()[1]-10, 400, 200, gen_font)
                    sprites.add(got_letter)
                    pygame.display.flip()

    if current_screen == MAIN_SCREEN:
        dx, dy = 0, 0
        # listening to keys pressed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            player.set_direction("up")
            dy -= distance_factor * dt       
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            player.set_direction("down")
            dy += distance_factor * dt
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player.set_direction("left")
            dx -= distance_factor * dt
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player.set_direction("right")
            dx += distance_factor * dt
        sprites.update(dx, dy)
        dirty_rects = sprites.draw(screen)
        pygame.display.update(dirty_rects)
        pygame.display.flip()
    elif current_screen == MAZE_SCREEN:
        pass
    # flip() the display to put your work on screen
    

    # limits FPS to 60
    # dt is delta time in seconds since last frame
    dt = clock.tick(60) / 1000

pygame.quit()