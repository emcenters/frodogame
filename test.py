import random
import pygame

pygame.init()

# Screen & layout
WIDTH, HEIGHT = 640, 780
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aggie Wordle")

ROWS, COLS = 6, 5
TILE_SIZE = 58
GAP = 8
GRID_WIDTH = COLS * TILE_SIZE + (COLS - 1) * GAP
START_X = (WIDTH - GRID_WIDTH) // 2
START_Y = 125

# Colors
BG_COLOR = (18, 18, 19)
TILE_EMPTY = (18, 18, 19)
TILE_BORDER = (58, 58, 60)
TILE_ACTIVE = (129, 131, 132)
KEY_UNUSED = (129, 131, 132)
GREEN = (83, 141, 78)       # code 2: right letter, right spot
YELLOW = (181, 159, 59)     # code 1: right letter, wrong spot
GRAY = (58, 58, 60)         # code 0: not in word
WHITE = (255, 255, 255)
AGGIE_MAROON = (155, 45, 62)
TEXT_MUTED = (185, 185, 190)

STATUS_TO_COLOR = {
    -1: KEY_UNUSED,
    0: GRAY,
    1: YELLOW,
    2: GREEN,
}

# Fonts
font_title = pygame.font.SysFont("arial", 30, bold=True)
font_sub = pygame.font.SysFont("arial", 16)
font_tile = pygame.font.SysFont("arial", 30, bold=True)
font_msg = pygame.font.SysFont("arial", 18, bold=True)
font_key = pygame.font.SysFont("arial", 16, bold=True)

KEYBOARD_ROWS = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
    ["Z", "X", "C", "V", "B", "N", "M"],
]

INTRO_TEXT = "Welcome to Aggie Wordle! Tests if you are a qualified Aggie."
RULES_TEXT = "Up to 3 rounds · 6 tries per round · Win within 3 rounds for anagram piece \"D\"."


# --- Team Logic ---

def wordbank(filename="wordle_words.txt"):
    """Return a list of possible 5-letter TAMU-related words."""
    try:
        with open(filename, encoding="utf-8") as file:
            word_bank = []
            for line in file:
                cleaned = line.strip().lstrip("\ufeff").upper()
                if cleaned:
                    word_bank.append(cleaned)
            return word_bank
    except FileNotFoundError:
        return ["AGGY", "HOWDY", "BONFIRE", "REVEILLE", "CORPS"][:0] + ["HOWDY", "AGGIE", "REVEL", "KYLE", "CHIRP"]


def exist(s, filename="words.txt"):
    """Check if input s is an existing 5-letter English word."""
    s = s.upper()
    try:
        with open(filename, encoding="utf-8") as file:
            existing = {line.strip().lstrip("\ufeff").upper() for line in file if line.strip()}
        return s in existing
    except FileNotFoundError:
        # Fallback if words.txt isn't present locally during testing
        return len(s) == 5 and s.isalpha()


def correctLetter(correct, guess):
    """
    Return list of 5 ints:
      2 = right letter, right index
      1 = right letter, wrong index
      0 = not in word
    """
    correct = correct.upper()
    guess = guess.upper()
    result = [0, 0, 0, 0, 0]
    occurrence = {}
    matched = {}

    for i in range(5):
        occurrence[correct[i]] = occurrence.get(correct[i], 0) + 1

        if guess[i] == correct[i]:
            result[i] = 2
            matched[guess[i]] = matched.get(guess[i], 0) + 1
        elif guess[i] in correct:
            result[i] = 1

    for letter, count in matched.items():
        occurrence[letter] -= count

    for i in range(5):
        if result[i] == 1:
            if occurrence.get(guess[i], 0) > 0:
                occurrence[guess[i]] -= 1
            else:
                result[i] = 0

    return result


def create_letter_tracker():
    alphabet = "QWERTYUIOPASDFGHJKLZXCVBNM"
    return {ch: -1 for ch in alphabet}


def letter_used(guess, result, tracker=None):
    """Update and return the letter status map (-1 unused, 0 gray, 1 yellow, 2 green)."""
    letters = tracker if tracker is not None else create_letter_tracker()
    for i in range(5):
        ch = guess[i].upper()
        new_state = result[i]
        prev_state = letters.get(ch, -1)
        # Keep the strongest clue seen so far (2 > 1 > 0 > -1)
        if new_state > prev_state:
            letters[ch] = new_state
    return letters


# --- Game State Helpers ---

def new_round(bank):
    word = random.choice(bank)
    bank.remove(word)
    board = [["" for _ in range(COLS)] for _ in range(ROWS)]
    colors = [[TILE_EMPTY for _ in range(COLS)] for _ in range(ROWS)]
    return word, board, colors, 0, 0, create_letter_tracker()


def start_full_game():
    bank = wordbank()
    if not bank:
        return None
    round_num = 1
    word_this_round, board, tile_colors, attempt, col, tracker = new_round(bank)
    return {
        "bank": bank,
        "round": round_num,
        "max_rounds": min(3, len(bank) + 1),
        "word": word_this_round,
        "board": board,
        "tile_colors": tile_colors,
        "attempt": attempt,
        "col": col,
        "tracker": tracker,
        "message": "",
        "state": "playing",  # "playing", "round_lost", "won", "game_lost"
    }


game = start_full_game()
if game is None:
    pygame.quit()
    raise SystemExit  # Note: remove even this if you want zero imports of sys anywhere; `return` inside a main() function works cleanly without sys.

clock = pygame.time.Clock()
running = True

while running:
    clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif game["state"] in ("won", "game_lost"):
                if event.key in (pygame.K_RETURN, pygame.K_r):
                    game = start_full_game()

            elif game["state"] == "round_lost":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if game["round"] < game["max_rounds"] and game["bank"]:
                        game["round"] += 1
                        (
                            game["word"],
                            game["board"],
                            game["tile_colors"],
                            game["attempt"],
                            game["col"],
                            game["tracker"],
                        ) = new_round(game["bank"])
                        game["message"] = f"Round {game['round']} started! New word chosen."
                        game["state"] = "playing"
                    else:
                        game["state"] = "game_lost"
                        game["message"] = "You failed this game! No word piece earned. Press R to retry."

            elif game["state"] == "playing":
                row = game["attempt"]

                if event.key == pygame.K_BACKSPACE:
                    if game["col"] > 0:
                        game["col"] -= 1
                        game["board"][row][game["col"]] = ""
                        game["message"] = ""

                elif event.key == pygame.K_RETURN:
                    if game["col"] < COLS:
                        game["message"] = "Invalid input: the word must be FIVE letters."
                    else:
                        guess = "".join(game["board"][row])
                        if not exist(guess):
                            game["message"] = "Invalid input: must be a valid English word."
                        else:
                            codes = correctLetter(game["word"], guess)
                            for c_idx, code in enumerate(codes):
                                game["tile_colors"][row][c_idx] = STATUS_TO_COLOR[code]

                            game["tracker"] = letter_used(guess, codes, game["tracker"])

                            if codes == [2, 2, 2, 2, 2]:
                                game["state"] = "won"
                                game["message"] = 'Congrats! You got your word piece: "D"! Press R to replay.'
                            else:
                                game["attempt"] += 1
                                game["col"] = 0
                                if game["attempt"] >= ROWS:
                                    if game["round"] < game["max_rounds"] and game["bank"]:
                                        game["state"] = "round_lost"
                                        rem = game["max_rounds"] - game["round"]
                                        game["message"] = f"Word was {game['word']}. {rem} round(s) left — press Enter."
                                    else:
                                        game["state"] = "game_lost"
                                        game["message"] = f"Word was {game['word']}. You failed this game! Press R."
                                else:
                                    game["message"] = ""

                else:
                    ch = event.unicode.upper()
                    if len(ch) == 1 and "A" <= ch <= "Z" and game["col"] < COLS:
                        game["board"][row][game["col"]] = ch
                        game["col"] += 1
                        game["message"] = ""

    # --- Draw ---
    screen.fill(BG_COLOR)

    title_surf = font_title.render(f"AGGIE WORDLE  ·  Round {game['round']}/{game['max_rounds']}", True, WHITE)
    screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 34)))

    intro_surf = font_sub.render(INTRO_TEXT, True, AGGIE_MAROON)
    screen.blit(intro_surf, intro_surf.get_rect(center=(WIDTH // 2, 66)))

    rules_surf = font_sub.render(RULES_TEXT, True, TEXT_MUTED)
    screen.blit(rules_surf, rules_surf.get_rect(center=(WIDTH // 2, 90)))

    # 6x5 Guess Grid
    for r in range(ROWS):
        for c in range(COLS):
            x = START_X + c * (TILE_SIZE + GAP)
            y = START_Y + r * (TILE_SIZE + GAP)
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

            fill = game["tile_colors"][r][c]
            pygame.draw.rect(screen, fill, rect, border_radius=4)

            if fill == TILE_EMPTY:
                border = TILE_ACTIVE if game["board"][r][c] else TILE_BORDER
                pygame.draw.rect(screen, border, rect, width=2, border_radius=4)

            letter = game["board"][r][c]
            if letter:
                surf = font_tile.render(letter, True, WHITE)
                screen.blit(surf, surf.get_rect(center=rect.center))

    # Status / Feedback Message
    if game["message"]:
        msg_surf = font_msg.render(game["message"], True, WHITE)
        screen.blit(msg_surf, msg_surf.get_rect(center=(WIDTH // 2, 532)))

    # Letter Tracker Keyboard Display
    key_w, key_h, key_gap = 42, 46, 6
    kb_start_y = 568
    for r_idx, row_keys in enumerate(KEYBOARD_ROWS):
        row_w = len(row_keys) * key_w + (len(row_keys) - 1) * key_gap
        start_x = (WIDTH - row_w) // 2
        y = kb_start_y + r_idx * (key_h + key_gap)
        for c_idx, k in enumerate(row_keys):
            x = start_x + c_idx * (key_w + key_gap)
            k_rect = pygame.Rect(x, y, key_w, key_h)
            state_code = game["tracker"].get(k, -1)
            k_color = STATUS_TO_COLOR[state_code]
            pygame.draw.rect(screen, k_color, k_rect, border_radius=4)
            k_surf = font_key.render(k, True, WHITE)
            screen.blit(k_surf, k_surf.get_rect(center=k_rect.center))

    footer_surf = font_sub.render("Type A-Z · Backspace to delete · Enter to guess · R to restart · Esc to quit", True, TEXT_MUTED)
    screen.blit(footer_surf, footer_surf.get_rect(center=(WIDTH // 2, 746)))

    pygame.display.flip()

pygame.quit()