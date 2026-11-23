import random
import pygame

import frodo_wordle as logic

# ---------- colors ----------
BG = (18, 18, 19)
TILE_EMPTY = (58, 58, 60)
TILE_FILLED = (86, 87, 88)
TEXT = (255, 255, 255)
SUBTEXT = (170, 170, 175)
MAROON = (80, 0, 0)  # Aggie maroon
STATE_COLORS = {
    2: (83, 141, 78),    # green  - right spot
    1: (181, 159, 59),   # yellow - wrong spot
    0: (58, 58, 60),     # gray   - not in word
}
KEY_DEFAULT = (129, 131, 132)
KEY_ROWS = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]


class WordleScene:
    def __init__(self, surface, total_rounds=3, max_attempts=6, piece="D"):
        self.total_rounds = total_rounds
        self.max_attempts = max_attempts
        self.piece = piece

        self.w, self.h = surface.get_size()
        self.font_title = pygame.font.SysFont("arial", 30, bold=True)
        self.font_tile = pygame.font.SysFont("arial", 28, bold=True)
        self.font_key = pygame.font.SysFont("arial", 18, bold=True)
        self.font_msg = pygame.font.SysFont("arial", 20)
        self.font_big = pygame.font.SysFont("arial", 38, bold=True)

        # layout (sized to fit a 640x640 window)
        self.header_h = 56
        self.tile = max(30, min(60, (self.h - 330) // self.max_attempts - 8))
        self.gap = 8
        self.grid_top = self.header_h + 40
        self.key_w, self.key_h, self.key_gap = 40, 50, 6

        self.done = False   # popup dismissed, game finished
        self.won = False    # earned the word piece
        self.reset()

    # ---------- game state ----------
    def reset(self):
        bank = [w.upper() for w in logic.wordbank()]
        self.words = random.sample(bank, self.total_rounds)  # different word each round
        self.round = 0
        self.done = False
        self.won = False
        self.start_round()

    def start_round(self):
        self.answer = self.words[self.round]
        self.guesses = []       # submitted words
        self.results = []       # list of [0/1/2 x5] per submitted word
        self.current = ""       # word being typed
        self.key_state = {}     # letter -> best result so far this round
        self.state = "playing"  # playing | round_over | game_over
        self.toast = ""
        self.toast_until = 0
        self.shake_until = 0

    def show_toast(self, text, ms=1500):
        self.toast = text
        self.toast_until = pygame.time.get_ticks() + ms

    def submit(self):
        guess = self.current
        if len(guess) != 5:
            self.show_toast("The word must be FIVE letters")
            self.shake_until = pygame.time.get_ticks() + 350
            return
        if not logic.exist(guess):
            self.show_toast("Not a valid English word")
            self.shake_until = pygame.time.get_ticks() + 350
            return

        result = logic.correctLetter(self.answer, guess)
        self.guesses.append(guess)
        self.results.append(result)
        self.current = ""

        for ch, r in zip(guess, result):  # keep the best result per letter
            if r > self.key_state.get(ch, -1):
                self.key_state[ch] = r

        if result == [2, 2, 2, 2, 2]:
            self.state = "game_over"
            self.won = True
        elif len(self.guesses) == self.max_attempts:
            if self.round == self.total_rounds - 1:
                self.state = "game_over"
                self.won = False
            else:
                self.state = "round_over"

    # ---------- input ----------
    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        confirm = event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)

        if self.state == "round_over":
            if confirm:
                self.round += 1
                self.start_round()
            return
        if self.state == "game_over":
            if confirm:
                self.done = True
            return

        if event.key == pygame.K_BACKSPACE:
            self.current = self.current[:-1]
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.submit()
        else:
            ch = event.unicode.upper()
            if len(ch) == 1 and ch.isascii() and ch.isalpha() and len(self.current) < 5:
                self.current += ch

    # ---------- drawing ----------
    def draw(self, screen):
        screen.fill(BG)
        self._header(screen)
        self._grid(screen)
        self._keyboard(screen)
        self._toast(screen)
        if self.state == "round_over":
            self._overlay(
                screen,
                "You FAILED this round!",
                f"The word was {self.answer}. {self.total_rounds - self.round - 1} round(s) left.",
                "Press ENTER for a new word",
            )
        elif self.state == "game_over":
            if self.won:
                self._overlay(
                    screen,
                    "You found the word!",
                    f'You got a word piece... it\'s... "{self.piece}"!!',
                    "Press ENTER to continue",
                )
            else:
                self._overlay(
                    screen,
                    "You failed this game!",
                    "You are not a qualified Aggie. No word piece for you.",
                    "Press ENTER to continue",
                )

    def _text(self, screen, text, font, color, cx, cy):
        surf = font.render(text, True, color)
        screen.blit(surf, surf.get_rect(center=(cx, cy)))

    def _header(self, screen):
        pygame.draw.rect(screen, MAROON, (0, 0, self.w, self.header_h))
        self._text(screen, "AGGIE WORDLE", self.font_title, TEXT, self.w // 2, self.header_h // 2)
        self._text(
            screen,
            f"Round {self.round + 1}/{self.total_rounds}   |   "
            f"Attempt {min(len(self.guesses) + 1, self.max_attempts)}/{self.max_attempts}",
            self.font_msg, SUBTEXT, self.w // 2, self.header_h + 20,
        )

    def _grid(self, screen):
        t, g = self.tile, self.gap
        left = (self.w - (5 * t + 4 * g)) // 2
        now = pygame.time.get_ticks()

        for row in range(self.max_attempts):
            offset = 0
            if row == len(self.guesses) and now < self.shake_until:
                offset = 8 if (now // 40) % 2 else -8
            for col in range(5):
                rect = pygame.Rect(left + col * (t + g) + offset, self.grid_top + row * (t + g), t, t)
                letter = ""
                if row < len(self.guesses):
                    letter = self.guesses[row][col]
                    pygame.draw.rect(screen, STATE_COLORS[self.results[row][col]], rect, border_radius=4)
                elif row == len(self.guesses) and self.state == "playing" and col < len(self.current):
                    letter = self.current[col]
                    pygame.draw.rect(screen, TILE_FILLED, rect, width=2, border_radius=4)
                else:
                    pygame.draw.rect(screen, TILE_EMPTY, rect, width=2, border_radius=4)
                if letter:
                    self._text(screen, letter, self.font_tile, TEXT, rect.centerx, rect.centery)

    def _keyboard(self, screen):
        kw, kh, kg = self.key_w, self.key_h, self.key_gap
        top = self.grid_top + self.max_attempts * (self.tile + self.gap) + 14
        for r, row in enumerate(KEY_ROWS):
            left = (self.w - (len(row) * kw + (len(row) - 1) * kg)) // 2
            for i, ch in enumerate(row):
                rect = pygame.Rect(left + i * (kw + kg), top + r * (kh + kg), kw, kh)
                s = self.key_state.get(ch)
                pygame.draw.rect(screen, KEY_DEFAULT if s is None else STATE_COLORS[s], rect, border_radius=5)
                self._text(screen, ch, self.font_key, TEXT, rect.centerx, rect.centery)

    def _toast(self, screen):
        if self.toast and pygame.time.get_ticks() < self.toast_until:
            surf = self.font_msg.render(self.toast, True, (0, 0, 0))
            box = surf.get_rect(center=(self.w // 2, self.header_h + 20)).inflate(24, 12)
            pygame.draw.rect(screen, (240, 240, 240), box, border_radius=6)
            screen.blit(surf, surf.get_rect(center=box.center))

    def _overlay(self, screen, title, line, prompt):
        shade = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 200))
        screen.blit(shade, (0, 0))
        cy = self.h // 2
        self._text(screen, title, self.font_big, TEXT, self.w // 2, cy - 50)
        self._text(screen, line, self.font_msg, TEXT, self.w // 2, cy + 5)
        self._text(screen, prompt, self.font_msg, SUBTEXT, self.w // 2, cy + 50)


# =====================================================================
# Functions that main.py calls
# =====================================================================
def start_full_game():
    """Create a fresh game. Call after the 640x640 display has been set."""
    surface = pygame.display.get_surface()
    scene = WordleScene(surface)
    return {"scene": scene, "state": "playing"}


def draw_wordle(screen, event, game, first_draw=False):
    """
    Handle one event (skipped when first_draw is True or event is None),
    redraw the Wordle screen, flip the display, and return the game dict.
    Safe to call every frame with event=None so animations/messages update.
    """
    scene = game["scene"]
    if event is not None and not first_draw:
        scene.handle_event(event)

    scene.draw(screen)
    pygame.display.flip()

    if scene.done:
        game["state"] = "won" if scene.won else "lost"
    return game