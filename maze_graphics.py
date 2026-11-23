import pygame

import frodo_maze as logic

LETTER_BG_PATH = "res/bgd/maze_bgd.png"   # <- your image for the "got the letter" screen
LETTER_BG_DIM = 110                          # 0-255, darkens the image so the text stays readable

# ---------- colors ----------
BG = (18, 18, 19)
PATH = (176, 152, 108)
PATH_EDGE = (96, 80, 52)
MAROON = (80, 0, 0)
TEXT = (255, 255, 255)
SUBTEXT = (190, 190, 190)
GOOD = (90, 200, 110)
BAD = (230, 80, 80)
BUTTON = (110, 25, 25)
BUTTON_HOVER = (160, 45, 45)
BUTTON_OFF = (60, 40, 40)

WALK_MS = 1500          # suspense time between picking a direction and seeing if it was right
CORRECT_PAUSE_MS = 600
DEADEND_MS = 600


class MazeScene:
    def __init__(self, surface, piece="Q"):
        self.piece = piece
        self.w, self.h = surface.get_size()
        self._fonts = {}

        # geometry of the fork on screen
        cx = self.w // 2
        self.base = (cx, int(self.h * 0.70))
        self.fork = (cx, int(self.h * 0.56))
        dx, end_y = int(self.w * 0.17), int(self.h * 0.38)
        self.ends = {"L": (cx - dx, end_y), "R": (cx + dx, end_y)}
        self.header_h = 56

        # buttons
        bw, bh = 180, 52
        by = self.h - bh - 20
        self.buttons = {
            "L": pygame.Rect(cx - bw - 10, by, bw, bh),
            "R": pygame.Rect(cx + 10, by, bw, bh),
        }

        self.done = False
        self.won = False
        self.letter_bg = self._load_letter_bg()
        self.reset()

    # ---------- helpers ----------
    def _load_letter_bg(self):
        """AI-assisted: Load the letter-screen image, scaled to cover the window. None if missing."""
        try:
            img = pygame.image.load(LETTER_BG_PATH).convert()
        except (pygame.error, FileNotFoundError):
            return None
        iw, ih = img.get_size()
        scale = max(self.w / iw, self.h / ih)
        scaled = pygame.transform.smoothscale(img, (int(iw * scale) + 1, int(ih * scale) + 1))
        surf = pygame.Surface((self.w, self.h))
        surf.blit(scaled, ((self.w - scaled.get_width()) // 2, (self.h - scaled.get_height()) // 2))
        return surf

    def font(self, size, bold=False):
        key = (size, bold)
        if key not in self._fonts:
            self._fonts[key] = pygame.font.SysFont("arial", size, bold=bold)
        return self._fonts[key]

    @staticmethod
    def now():
        return pygame.time.get_ticks()

    # ---------- game state ----------
    def reset(self):
        '''Team-written: resets the logic of the game. Prepares it for a new game'''
        self.key = logic.directions()   # e.g. ["L", "R", "R", "L"]
        self.step = 0                   # how many forks Frodo has passed
        self.restarts = 0
        self.choice = None
        self.correct = False
        self.phase = "intro"            # intro | choose | walking | correct_pause | deadend | game_over
        self.phase_start = 0
        self.done = False
        self.won = False

    def set_phase(self, phase):
        self.phase = phase
        self.phase_start = self.now()

    def guess(self, direction):
        if self.phase != "choose":
            return
        self.choice = direction
        self.correct = (direction == self.key[self.step])
        self.set_phase("walking")

    def tick(self):
        elapsed = self.now() - self.phase_start
        if self.phase == "walking" and elapsed >= WALK_MS:
            self.set_phase("correct_pause" if self.correct else "deadend")
        elif self.phase == "correct_pause" and elapsed >= CORRECT_PAUSE_MS:
            self.step += 1
            self.choice = None
            if self.step >= len(self.key):
                self.won = True
                self.set_phase("game_over")
            else:
                self.set_phase("choose")
        elif self.phase == "deadend" and elapsed >= DEADEND_MS:
            self.step = 0               # start over
            self.restarts += 1
            self.choice = None
            self.set_phase("choose")

    # ---------- input ----------
    def handle_event(self, event):
        confirm = False
        if event.type == pygame.KEYDOWN:
            confirm = event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
        # elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        #     confirm = True
        else:
            return

        if self.phase == "intro":
            if confirm or event.type == pygame.KEYDOWN:
                self.set_phase("choose")
            return
        if self.phase == "game_over":
            if confirm:
                self.done = True
            return
        if self.phase != "choose":
            return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_a, pygame.K_LEFT):
                self.guess("L")
            elif event.key in (pygame.K_d, pygame.K_RIGHT):
                self.guess("R")
        # elif event.type == pygame.MOUSEBUTTONDOWN:
        #     for d, rect in self.buttons.items():
        #         if rect.collidepoint(event.pos):
        #             self.guess(d)
        #             break

    # ---------- drawing ----------
    def draw(self, screen):
        self.tick()
        screen.fill(BG)
        self._header(screen)
        self._progress(screen)
        self._maze(screen)
        self._status(screen)
        self._buttons(screen)

        if self.phase == "intro":
            self._intro(screen)
        elif self.phase == "game_over":
            self._overlay(
                screen,
                "Frodo made it!",
                ["Frodo has made it to Professor Spears' office!", f'Frodo gets a new letter, "{self.piece}".'],
                "Press ENTER to continue",
                use_image=True,
            )

    def _text(self, screen, text, font, color, cx, cy):
        surf = font.render(text, True, color)
        screen.blit(surf, surf.get_rect(center=(cx, cy)))

    def _header(self, screen):
        pygame.draw.rect(screen, MAROON, (0, 0, self.w, self.header_h))
        self._text(screen, "FRODO'S MAZE", self.font(30, True), TEXT, self.w // 2, self.header_h // 2)

    def _progress(self, screen):
        """4 dots for the 4 forks, then the office."""
        total = len(self.key)
        done_count = self.step + (1 if self.phase == "correct_pause" else 0)
        y = self.header_h + 34
        spacing = 56
        start_x = self.w // 2 - (total * spacing) // 2
        pygame.draw.line(screen, PATH_EDGE, (start_x, y), (start_x + total * spacing, y), 4)
        for i in range(total):
            x = start_x + i * spacing
            if i < done_count:
                pygame.draw.circle(screen, GOOD, (x, y), 12)
            else:
                pygame.draw.circle(screen, (60, 80, 66), (x, y), 12)
                if i == done_count and self.phase != "game_over":
                    pygame.draw.circle(screen, TEXT, (x, y), 12, 3)
        # office icon
        ox = start_x + total * spacing
        pygame.draw.rect(screen, (150, 110, 90), (ox - 12, y - 8, 24, 20))
        pygame.draw.polygon(screen, MAROON, [(ox - 16, y - 8), (ox + 16, y - 8), (ox, y - 22)])
        self._text(screen, "Prof. Spears' office", self.font(14), SUBTEXT, ox, y + 28)

    def _thick(self, screen, p1, p2, width, color):
        pygame.draw.line(screen, color, p1, p2, width)
        pygame.draw.circle(screen, color, p1, width // 2)
        pygame.draw.circle(screen, color, p2, width // 2)

    def _maze(self, screen):
        segments = [(self.base, self.fork), (self.fork, self.ends["L"]), (self.fork, self.ends["R"])]
        for p1, p2 in segments:       # border first
            self._thick(screen, p1, p2, 46, PATH_EDGE)
        for p1, p2 in segments:       # then the path
            self._thick(screen, p1, p2, 36, PATH)

        # highlight the branch the player picked while waiting for the result
        if self.choice and self.phase == "walking":
            self._thick(screen, self.fork, self.ends[self.choice], 36, (232, 208, 140))

        # branch labels
        for d, label in (("L", "LEFT"), ("R", "RIGHT")):
            ex, ey = self.ends[d]
            self._text(screen, label, self.font(18, True), TEXT, ex, ey - 34)

        # outcome marks at the end of the chosen branch
        if self.choice and self.phase in ("correct_pause", "deadend"):
            ex, ey = self.ends[self.choice]
            if self.correct:
                pygame.draw.circle(screen, GOOD, (ex, ey), 20)
                pygame.draw.lines(screen, TEXT, False, [(ex - 9, ey), (ex - 2, ey + 8), (ex + 11, ey - 8)], 5)
            else:
                wall = pygame.Rect(0, 0, 70, 16)
                wall.center = (ex, ey - 18)
                pygame.draw.rect(screen, (110, 110, 115), wall, border_radius=3)
                pygame.draw.circle(screen, BAD, (ex, ey + 6), 18)
                pygame.draw.line(screen, TEXT, (ex - 9, ey - 3), (ex + 9, ey + 15), 4)
                pygame.draw.line(screen, TEXT, (ex + 9, ey - 3), (ex - 9, ey + 15), 4)


    def _status(self, screen):
        if self.phase == "choose":
            msg, color = "Which way should Frodo go?", TEXT
        elif self.phase == "walking":
            dots = "." * (1 + ((self.now() - self.phase_start) // 400) % 3)
            side = "LEFT" if self.choice == "L" else "RIGHT"
            msg, color = f"You chose {side}{dots}", TEXT
        elif self.phase == "correct_pause":
            msg, color = "Correct!", GOOD
        elif self.phase == "deadend":
            msg, color = "Sorry, wrong way! Start over.", BAD
        else:
            return
        self._text(screen, msg, self.font(24, True), color, self.w // 2, self.header_h + 88)
        if self.restarts and self.phase != "game_over":
            self._text(screen, f"Restarts: {self.restarts}", self.font(16), SUBTEXT, self.w - 70, self.header_h + 20)

    def _buttons(self, screen):
        enabled = self.phase == "choose"
        mouse = pygame.mouse.get_pos()
        for d, label in (("L", "LEFT  (A)"), ("R", "RIGHT  (D)")):
            rect = self.buttons[d]
            if not enabled:
                color = BUTTON_OFF
            elif rect.collidepoint(mouse):
                color = BUTTON_HOVER
            else:
                color = BUTTON
            pygame.draw.rect(screen, color, rect, border_radius=10)
            self._text(screen, label, self.font(22, True), TEXT if enabled else SUBTEXT, rect.centerx, rect.centery)

    def _shade(self, screen, alpha=215):
        shade = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        shade.fill((0, 0, 0, alpha))
        screen.blit(shade, (0, 0))

    def _intro(self, screen):
        self._shade(screen, 225)
        cy = self.h // 2
        self._text(screen, "Frodo is lost in the maze!", self.font(34, True), TEXT, self.w // 2, cy - 110)
        lines = [
            "Help him reach Professor Spears' office.",
            f"Choose LEFT or RIGHT at each of the {len(self.key)} forks.",
            "A wrong turn sends Frodo back to the start,",
            "but the correct path stays the same - remember it!",
            "Use A / D, the arrow keys, or click the buttons.",
        ]
        for i, line in enumerate(lines):
            self._text(screen, line, self.font(20), TEXT, self.w // 2, cy - 50 + i * 30)
        self._text(screen, "Click or press ENTER to start", self.font(20), SUBTEXT, self.w // 2, cy + 130)

    def _overlay(self, screen, title, lines, prompt, use_image=False):
        if use_image and self.letter_bg is not None:
            screen.blit(self.letter_bg, (0, 0))
            self._shade(screen, LETTER_BG_DIM)
        else:
            self._shade(screen)
        cy = self.h // 2
        self._text(screen, title, self.font(38, True), TEXT, self.w // 2, cy - 60)
        for i, line in enumerate(lines):
            self._text(screen, line, self.font(20), TEXT, self.w // 2, cy - 5 + i * 28)
        self._text(screen, prompt, self.font(20), SUBTEXT, self.w // 2, cy + 20 + len(lines) * 28 + 15)


# =====================================================================
# Functions that main.py calls
# =====================================================================
def start_full_game():
    """Create a fresh maze game. Call after the display for the maze screen is set."""
    surface = pygame.display.get_surface()
    return {"scene": MazeScene(surface), "state": "playing", "letter": None}


def draw_maze(screen, event, game, first_draw=False):
    """
    Handle one event (skipped when first_draw is True or event is None),
    redraw, flip the display, and return the game dict.
    Call this EVERY frame (event=None when nothing happened) so Frodo can walk.
    """
    scene = game["scene"]
    if event is not None and not first_draw:
        scene.handle_event(event)

    scene.draw(screen)
    pygame.display.flip()

    if scene.done:
        game["state"] = "won"
        game["letter"] = scene.piece
    return game