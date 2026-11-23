import pygame
import game_graphics
import frodo_maze
import wordle_graphics
import simon_graphics
import maze_graphics
    

MAIN_SCREEN = 0
WORDLE_SCREEN = 1
MAZE_SCREEN = 2
BUS_SCREEN = 3
SIMON_SAYS_SCREEN = 4
END_SCREEN = 5

current_screen = 0

WINDOW_SIZE = (1080, 640)
SCREEN_FLAGS = pygame.SCALED

at_maze = [True, False]
at_wordle = [False, False]
at_simon = [False, False]
at_bus = [False, False]

def reset_to_main_screen(screen):
    '''Team-written: resets the screen to the main game area.'''
    global current_screen, main_sprites
    current_screen = MAIN_SCREEN
    screen = pygame.display.set_mode(WINDOW_SIZE, SCREEN_FLAGS)
    main_sprites.clear(screen, black_bgd)
    for sprite in main_sprites:
        sprite.dirty = 1
    return [False, True]
# pygame setup
pygame.init()

screen = pygame.display.set_mode(WINDOW_SIZE, SCREEN_FLAGS)
black_bgd = pygame.Surface(screen.get_size())
black_bgd.fill('black')
screen.blit(black_bgd, (0, 0))
pygame.display.flip()

clock = pygame.time.Clock()
running = True
dt = 0
distance_factor = 400
main_sprites = pygame.sprite.LayeredDirty()
main_sprites.clear(screen, black_bgd)
player = game_graphics.Player("res/sprite_sheet/", True, screen.get_width()/2, screen.get_height()/2, 2, main_sprites)
main_bgd = game_graphics.Background("bgd.png", screen.get_rect().center, player.get_size(), 0, main_sprites)
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
                if event.key == pygame.K_e and at_wordle[0] and not at_wordle[1]:
                    current_screen = WORDLE_SCREEN
                    screen = pygame.display.set_mode((640, 640), SCREEN_FLAGS)
                    if fullscreen:
                        pygame.display.toggle_fullscreen()
                    wordle_bgd = pygame.Surface(screen.get_size())
                    screen.blit(wordle_bgd, (0, 0))
                    game = wordle_graphics.start_full_game()
                    wordle_graphics.draw_wordle(screen, event, game, True)
                    pygame.display.flip()
                elif event.key == pygame.K_e and at_simon[0] and not at_wordle[1]:
                    current_screen = SIMON_SAYS_SCREEN
                    screen = pygame.display.set_mode((640, 640), SCREEN_FLAGS)
                    simon_game = simon_graphics.start_full_game()
                    simon_graphics.draw_simon(screen, event, simon_game, True)
                elif event.key == pygame.K_e and at_maze[0] and not at_maze[1]:
                    current_screen = MAZE_SCREEN
                    screen = pygame.display.set_mode((640, 640), SCREEN_FLAGS)
                    maze_game = maze_graphics.start_full_game()
                    maze_graphics.draw_maze(screen, event, maze_game, True)
            elif current_screen == MAZE_SCREEN:
                maze_game = maze_graphics.draw_maze(screen, event, maze_game, False)
                if maze_game["state"] == "won":
                    at_maze = reset_to_main_screen(screen)
                elif maze_game["state"] == "lost":
                    current_screen = END_SCREEN
                    screen = pygame.display.set_mode(WINDOW_SIZE, SCREEN_FLAGS)
            elif current_screen == WORDLE_SCREEN:
                game = wordle_graphics.draw_wordle(screen, event, game, False)
                if game["state"] == "won":
                    at_wordle = reset_to_main_screen(screen)
                elif game["state"] == "lost":
                    current_screen = END_SCREEN
                    screen = pygame.display.set_mode(WINDOW_SIZE, SCREEN_FLAGS)
                pygame.display.flip()
            elif current_screen == SIMON_SAYS_SCREEN: 
                simon_game = simon_graphics.draw_simon(screen, event, simon_game, False)
                if simon_game["state"] == "won":
                    at_simon = reset_to_main_screen(screen)
                elif simon_game["state"] == "lost":
                    current_screen = END_SCREEN
                    screen = pygame.display.set_mode(WINDOW_SIZE, SCREEN_FLAGS)

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
        main_sprites.update(dx, dy)
        dirty_rects = main_sprites.draw(screen)
        pygame.display.update(dirty_rects)
        pygame.display.flip()

    elif current_screen == MAZE_SCREEN:
        maze_game = maze_graphics.draw_maze(screen, None, maze_game, False)
    elif current_screen == SIMON_SAYS_SCREEN:
        simon_game = simon_graphics.draw_simon(screen, None, simon_game, False)
        if simon_game["state"] in ("won", "lost"):
            current_screen = MAIN_SCREEN
            screen = pygame.display.set_mode(WINDOW_SIZE, SCREEN_FLAGS)
            main_sprites.clear(screen, main_bgd)
            for sprite in main_sprites:
                sprite.dirty = 1

    # dt is delta time in seconds since last frame
    dt = clock.tick(60) / 1000

pygame.quit()