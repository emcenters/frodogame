import pygame

import yell_leaders_simon as logic

CHOICES = ["Gig 'em Aggies", "Farmer's Fight", "BTHO", "Ol' Army Fight"]

# ---------- colors ----------
BG = (18, 18, 19)
MAROON = (80, 0, 0)
TEXT = (255, 255, 255)
SUBTEXT = (170, 170, 175)
GOOD = (83, 141, 78)
BAD = (190, 60, 60)
# (dim color, lit color) for each button
BUTTON_COLORS = [
    ((110, 25, 25), (240, 70, 70)),     # red
    ((25, 60, 110), (70, 140, 245)),    # blue
    ((30, 95, 45), (80, 210, 100)),     # green
    ((115, 95, 20), (250, 215, 60)),    # yellow
]

LEAD_MS = 700    # pause before the sequence starts
SLOT_MS = 1000   # time per yell in the sequence
LIT_MS = 750     # how long each yell stays lit
PRESS_MS = 250   # flash when the player presses a button
FEEDBACK_MS = 900


class SimonScene:
    def __init__(self, surface, total_attempts=3, length=4, piece="A"):
        self.total_attempts = total_attempts
        self.length = length
        self.piece = piece

        self.w, self.h = surface.get_size()
        self._fonts = {}

        # layout
        self.header_h = 56
        pad = 16
        top = 170
        bw = (self.w - 3 * pad) // 2
        bh = (self.h - top - 2 * pad) // 2
        self.buttons = []
        for i in range(4):
            col, row = i % 2, i // 2
            self.buttons.append(pygame.Rect(pad + col * (bw + pad), top + row * (bh + pad), bw, bh))

        self.done = False
        self.won = False
        self.reset()

    # ---------- helpers ----------
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
        self.attempt = 1
        self.done = False
        self.won = False
        self.start_attempt()
        self.phase = "intro"

    def start_attempt(self):
        self.sequence = logic.randomizer(CHOICES, self.length)
        self.k = 1                 # how many yells are shown this round
        self.guess = []            # indexes (0-3) the player has picked
        self.press_idx = None
        self.press_until = 0
        self.feedback = ""
        self.feedback_color = TEXT
        self.feedback_until = 0
        self.begin_showing()

    def begin_showing(self):
        self.phase = "showing"
        self.phase_start = self.now()
        self.guess = []

    def lit_index(self):
        """Which button is lit right now (or None)."""
        now = self.now()
        if self.phase == "showing":
            t = now - self.phase_start - LEAD_MS
            if t >= 0:
                slot = t // SLOT_MS
                if slot < self.k and t % SLOT_MS < LIT_MS:
                    return CHOICES.index(self.sequence[slot])
        if self.press_idx is not None and now < self.press_until:
            return self.press_idx
        return None

    def tick(self):
        """Time-based phase changes. Called from draw()."""
        now = self.now()
        if self.phase == "showing":
            if now - self.phase_start >= LEAD_MS + self.k * SLOT_MS:
                self.phase = "input"
                self.guess = []
        elif self.phase == "feedback":
            if now >= self.feedback_until:
                self.k += 1
                self.begin_showing()

    def pick(self, idx):
        if self.phase != "input":
            return
        self.guess.append(idx)
        self.press_idx = idx
        self.press_until = self.now() + PRESS_MS

        if len(self.guess) < self.k:
            return

        guess_strs = [CHOICES[i] for i in self.guess]
        correct = logic.is_guess_correct(guess_strs, self.sequence[:self.k])
        if correct:
            if self.k == self.length:
                self.phase = "game_over"
                self.won = True
            else:
                self.phase = "feedback"
                self.feedback = "Correct!"
                self.feedback_color = GOOD
                self.feedback_until = self.now() + FEEDBACK_MS
        else:
            if self.attempt >= self.total_attempts:
                self.phase = "game_over"
                self.won = False
            else:
                self.phase = "retry"

    # ---------- input ----------
    def handle_event(self, event):
        confirm = False
        if event.type == pygame.KEYDOWN:
            confirm = event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            confirm = True
        else:
            return

        if self.phase == "intro":
            if confirm:
                self.begin_showing()
            return
        if self.phase == "retry":
            if confirm:
                self.attempt += 1
                self.start_attempt()
            return
        if self.phase == "game_over":
            if confirm:
                self.done = True
            return

        if self.phase != "input":
            return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                self.pick(event.key - pygame.K_1)
            elif event.key in (pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4):
                self.pick(event.key - pygame.K_KP1)
            elif event.key == pygame.K_BACKSPACE and self.guess:
                self.guess.pop()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i, rect in enumerate(self.buttons):
                if rect.collidepoint(event.pos):
                    self.pick(i)
                    break

    # ---------- drawing ----------
    def draw(self, screen):
        self.tick()
        screen.fill(BG)
        self._header(screen)
        self._status(screen)
        self._slots(screen)
        self._buttons(screen)

        if self.phase == "intro":
            self._intro(screen)
        elif self.phase == "retry":
            left = self.total_attempts - self.attempt
            self._overlay(
                screen,
                "Incorrect!",
                [f"That was attempt number {self.attempt}.", f"{left} attempt(s) left. You get a new sequence."],
                "Press ENTER to try again",
            )
        elif self.phase == "game_over":
            if self.won:
                self._overlay(
                    screen,
                    "Congratulations, you win!",
                    [f'The letter you receive is "{self.piece}".'],
                    "Press ENTER to continue",
                )
            else:
                self._overlay(
                    screen,
                    "Out of attempts!",
                    ["Unfortunately you ran out of attempts", "for this mini-game."],
                    "Press ENTER to continue",
                )

    def _text(self, screen, text, font, color, cx, cy):
        surf = font.render(text, True, color)
        screen.blit(surf, surf.get_rect(center=(cx, cy)))

    def _header(self, screen):
        pygame.draw.rect(screen, MAROON, (0, 0, self.w, self.header_h))
        self._text(screen, "FOLLOW THE YELL LEADERS", self.font(28, True), TEXT, self.w // 2, self.header_h // 2)
        self._text(
            screen,
            f"Attempt {min(self.attempt, self.total_attempts)}/{self.total_attempts}   |   "
            f"Yell {self.k}/{self.length}",
            self.font(20), SUBTEXT, self.w // 2, self.header_h + 22,
        )

    def _status(self, screen):
        if self.phase == "showing":
            msg, color = "Watch the yells...", TEXT
        elif self.phase == "input":
            msg, color = f"Your turn! Repeat {self.k} yell(s) in order.", TEXT
        elif self.phase == "feedback":
            msg, color = self.feedback, self.feedback_color
        else:
            msg, color = "", TEXT
        if msg:
            self._text(screen, msg, self.font(22, True), color, self.w // 2, self.header_h + 58)

    def _slots(self, screen):
        """Row of small boxes showing the player's picks so far."""
        n = self.k
        size, gap = 26, 8
        total = n * size + (n - 1) * gap
        left = (self.w - total) // 2
        y = self.header_h + 84
        for i in range(n):
            rect = pygame.Rect(left + i * (size + gap), y, size, size)
            if self.phase == "input" and i < len(self.guess):
                pygame.draw.rect(screen, BUTTON_COLORS[self.guess[i]][1], rect, border_radius=5)
                self._text(screen, str(self.guess[i] + 1), self.font(16, True), (0, 0, 0), rect.centerx, rect.centery)
            else:
                pygame.draw.rect(screen, (70, 70, 72), rect, width=2, border_radius=5)

    def _fit_label(self, text, max_w):
        for size in (32, 28, 24, 20, 16):
            f = self.font(size, True)
            if f.size(text)[0] <= max_w:
                return f
        return self.font(14, True)

    def _buttons(self, screen):
        lit = self.lit_index()
        for i, rect in enumerate(self.buttons):
            dim, bright = BUTTON_COLORS[i]
            pygame.draw.rect(screen, bright if lit == i else dim, rect, border_radius=14)
            if lit == i:
                pygame.draw.rect(screen, TEXT, rect, width=4, border_radius=14)
            label = CHOICES[i]
            self._text(screen, label, self._fit_label(label, rect.w - 24), TEXT, rect.centerx, rect.centery)
            self._text(screen, str(i + 1), self.font(18, True), SUBTEXT, rect.left + 20, rect.top + 20)

    def _shade(self, screen, alpha=210):
        shade = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        shade.fill((0, 0, 0, alpha))
        screen.blit(shade, (0, 0))

    def _intro(self, screen):
        self._shade(screen, 225)
        cy = self.h // 2
        self._text(screen, 'Follow the Yell Leaders', self.font(36, True), TEXT, self.w // 2, cy - 130)
        lines = [
            "Watch the yells light up, then repeat them in order.",
            "Each round adds one more yell, up to 4.",
            "Click the buttons (or press 1-4). Backspace undoes.",
            f"You have {self.total_attempts} attempts.",
        ]
        for i, line in enumerate(lines):
            self._text(screen, line, self.font(20), TEXT, self.w // 2, cy - 60 + i * 32)
        self._text(screen, "Click or press ENTER to start", self.font(20), SUBTEXT, self.w // 2, cy + 110)

    def _overlay(self, screen, title, lines, prompt):
        self._shade(screen)
        cy = self.h // 2
        self._text(screen, title, self.font(36, True), TEXT, self.w // 2, cy - 60)
        for i, line in enumerate(lines):
            self._text(screen, line, self.font(20), TEXT, self.w // 2, cy - 5 + i * 28)
        self._text(screen, prompt, self.font(20), SUBTEXT, self.w // 2, cy + 20 + len(lines) * 28 + 15)


# =====================================================================
# Functions that main.py calls
# =====================================================================
def start_full_game():
    """Create a fresh game. Call after the display for the Simon screen is set."""
    surface = pygame.display.get_surface()
    return {"scene": SimonScene(surface), "state": "playing", "letter": None}


def draw_simon(screen, event, game, first_draw=False):
    """
    Handle one event (skipped when first_draw is True or event is None),
    redraw, flip the display, and return the game dict.
    Call this EVERY frame (event=None when nothing happened) so the
    yell sequence can animate.
    """
    scene = game["scene"]
    if event is not None and not first_draw:
        scene.handle_event(event)

    scene.draw(screen)
    pygame.display.flip()

    if scene.done:
        game["state"] = "won" if scene.won else "lost"
        game["letter"] = scene.piece if scene.won else None
    return game