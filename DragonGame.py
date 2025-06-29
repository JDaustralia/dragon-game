import pygame
import random

# Constants
WIDTH, HEIGHT = 600, 700  # 600 for game, 100 for status
PLAY_HEIGHT = 600         # New constant to separate play area
GRID_SIZE = 20
FPS = 30

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

# Colors
RED = (200, 30, 60)
BLUE = (30, 30, 200)
BG = (30, 30, 30)


def opening_screen():
    pygame.init()


    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font = pygame.font.SysFont(None, 23)
    title_font = pygame.font.SysFont(None, 25)

    background = pygame.image.load("background5.png").convert() # This is an AI prepared image
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA).convert_alpha()
    overlay.fill((255, 255, 255, 200))  # 80 = semi-transparent white

    # In your draw loop:
    screen.blit(background, (0, 0))
    screen.blit(overlay, (0, 0))


    # Slider values
    lookahead = 2
    enemy_seek = 0.5
    wall_avoidance = 0.5
    directional_stability = 0.5

    # Slider positions
    slider_x = 100
    sliders = [
        {"label": "      Lookahead", "min": 1, "max": 4, "step": 1, "value": lookahead},
        {"label": "      Enemy Seek", "min": 0.0, "max": 1.0, "step": 0.01, "value": enemy_seek},
        {"label": "      Wall Avoidance", "min": 0.0, "max": 1.0, "step": 0.01, "value": wall_avoidance},
        {"label": "      Directional Stability", "min": 0.0, "max": 1.0, "step": 0.01, "value": directional_stability}
    ]

    selected = 0
    running = True
    while running:
        screen.blit(background, (0, 0))

        # Intro text
        intro_lines = [
            "                                       Welcome to the Dragon Challenge!",
            "                             Your goal is to design a Blue Dragon that can defeat",
            "                                 the Champion Red Dragon three times in a row.",
            "                               Ties are allowed, but one loss ends the challenge.",
            "",
            "                              Grow your Blue Dragon using the DNA attributes below",

            "                              Use UP/DOWN to select a trait, LEFT/RIGHT to adjust.",
            ""
        ]
        intro_start_y = 10  # Move intro text closer to the top
        for i, line in enumerate(intro_lines):
            text = font.render(line, True, (0, 0, 0))
            screen.blit(text, (20, intro_start_y + i * 24))

        # Draw sliders
        slider_start_y = 370  # Move sliders further down
        slider_spacing = 28  # Single-line spacing
        slider_x = 160  # Move sliders to the left/right
        last_slider_y = slider_start_y + len(sliders) * slider_spacing


        for i, s in enumerate(sliders):
            label = f"{s['label']}: {round(s['value'], 2)}"
            color = BLUE if i == selected else (0, 0, 0)
            text = title_font.render(label, True, color)
            screen.blit(text, (slider_x, slider_start_y + i * slider_spacing))

        outro_lines = [
            "       Press ENTER to",
            "  begin the challenge!"
        ]

        for i, line in enumerate(outro_lines):
            text = font.render(line, True, (0, 0, 0))
            screen.blit(text, (200, last_slider_y + 20 + i * 24))  # 24px line spacing

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(sliders)
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(sliders)
                elif event.key == pygame.K_LEFT:
                    sliders[selected]["value"] = max(
                        sliders[selected]["min"],
                        sliders[selected]["value"] - sliders[selected]["step"]
                    )
                elif event.key == pygame.K_RIGHT:
                    sliders[selected]["value"] = min(
                        sliders[selected]["max"],
                        sliders[selected]["value"] + sliders[selected]["step"]
                    )
                elif event.key == pygame.K_RETURN:
                    running = False


    #pygame.quit()
    return DragonDNA(
        lookahead_depth=int(sliders[0]["value"]),
        enemy_seek=sliders[1]["value"],
        wall_avoidance=sliders[2]["value"],
        directional_stability=sliders[3]["value"]
    )

class DragonDNA:
    def __init__(self, lookahead_depth=None, enemy_seek=None, wall_avoidance=None, directional_stability=None):
        self.lookahead_depth = lookahead_depth if lookahead_depth is not None else random.randint(1, 4)
        self.enemy_seek = enemy_seek if enemy_seek is not None else random.uniform(0, 1)
        self.wall_avoidance = wall_avoidance if wall_avoidance is not None else random.uniform(0, 1)
        self.directional_stability = directional_stability if directional_stability is not None else random.uniform(0, 1)
        self.turn_agility = max(1, 5 - self.lookahead_depth)

    def __repr__(self):
        return f"DNA(LA={self.lookahead_depth}, ES={self.enemy_seek:.2f}, WA={self.wall_avoidance:.2f}, DS={self.directional_stability:.2f})"


class Dragon:
    def __init__(self, color, start_pos, direction, dna, length=6):
        self.color = color
        self.direction = direction
        self.dna = dna
        self.body = [start_pos]
        for i in range(1, length):
            x, y = start_pos
            dx, dy = (-direction[0], -direction[1])
            self.body.append((x + i * dx * GRID_SIZE, y + i * dy * GRID_SIZE))
        self.alive = True
        self.frames_since_turn = 0

    def move(self):
        if not self.alive:
            return

        self.random_turn()

        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx * GRID_SIZE, head_y + dy * GRID_SIZE)

        if not self.in_bounds(new_head):
            self.avoid_wall()
            dx, dy = self.direction
            new_head = (head_x + dx * GRID_SIZE, head_y + dy * GRID_SIZE)

        self.body = [new_head] + self.body[:-1]

        if not self.in_bounds(new_head):
            self.alive = False

    def random_turn(self):
        if random.random() < 0.1:
            valid_dirs = self.valid_directions()
            if valid_dirs:
                self.direction = random.choice(valid_dirs)

    def avoid_wall(self):
        valid_dirs = self.valid_directions()
        if valid_dirs:
            self.direction = random.choice(valid_dirs)

    def valid_directions(self):
        head_x, head_y = self.body[0]
        opposite = (-self.direction[0], -self.direction[1])
        options = []
        for d in DIRECTIONS:
            if d == opposite:
                continue
            new_x = head_x + d[0] * GRID_SIZE
            new_y = head_y + d[1] * GRID_SIZE
            if 0 <= new_x < WIDTH and 0 <= new_y < PLAY_HEIGHT:  # Use PLAY_HEIGHT here
                options.append(d)
        return options

    def in_bounds(self, pos):
        x, y = pos
        return 0 <= x < WIDTH and 0 <= y < PLAY_HEIGHT  # Only allow movement in play area

    def draw(self, screen):
        for i, segment in enumerate(self.body):
            color = (255, 200, 90) if i == 0 else self.color
            pygame.draw.rect(screen, color, (*segment, GRID_SIZE, GRID_SIZE))

    def head(self):
        return self.body[0]

    def sides(self):
        return self.body[1:]

def wait_for_continue(screen):
    font = pygame.font.SysFont(None, 28)
    msg = font.render("Press any key to continue...", True, (200, 30, 30))
    rect = msg.get_rect(topright=(WIDTH - 10, PLAY_HEIGHT + 10))
    screen.blit(msg, rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                waiting = False


def check_collision(dragon1, dragon2):
    head1 = dragon1.head()
    head2 = dragon2.head()
    sides1 = dragon1.sides()
    sides2 = dragon2.sides()

    if head1 == head2:
        dragon1.alive = dragon2.alive = False
    else:
        hit1 = head1 in sides2
        hit2 = head2 in sides1

        if hit1 and hit2:
            dragon1.alive = dragon2.alive = False
        elif hit1:
            dragon2.alive = False
        elif hit2:
            dragon1.alive = False


def draw_status(screen, match_num, wins, result_text, dna_red, dna_blue):
    pygame.draw.rect(screen, (255, 255, 255), (0, PLAY_HEIGHT, WIDTH, HEIGHT - PLAY_HEIGHT))  # White panel

    font = pygame.font.SysFont(None, 24)
    lines = [
        (f"Match {match_num} | Blue Wins: {wins}/3", BLUE),
        (f"Last Result: {result_text}", (0, 0, 0)),
        (f"", (0, 0, 0)),
        #(f"Red DNA: LA={dna_red.lookahead_depth}, ES={dna_red.enemy_seek:.2f}, WA={dna_red.wall_avoidance:.2f}, DS={dna_red.directional_stability:.2f}", (0, 0, 0)),
        (f"Blue DNA: LA={dna_blue.lookahead_depth}, ES={dna_blue.enemy_seek:.2f}, WA={dna_blue.wall_avoidance:.2f}, DS={dna_blue.directional_stability:.2f}", (0, 0, 0))
    ]
    for i, (line, color) in enumerate(lines):
        text = font.render(line, True, color)
        screen.blit(text, (10, PLAY_HEIGHT + 10 + i * 20))


def play_match(dna_red, dna_blue, match_num, wins):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    d1 = Dragon(RED, (100, 100), RIGHT, dna_red)
    d2 = Dragon(BLUE, (400, 400), LEFT, dna_blue)

    result = None
    result_text = "You're in with a chance"
    running = True
    while running:
        screen.fill(BG)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if d1.alive and d2.alive:
            d1.move()
            d2.move()
            check_collision(d1, d2)
        else:
            if not d1.alive and not d2.alive:
                result_text = "It's a Tie!"
                result = "tie"
            elif not d1.alive:
                result_text = "Blue Wins!"
                result = "blue"
            elif not d2.alive:
                result_text = "Red Wins!"
                result = "red"
            running = False

        d1.draw(screen)
        d2.draw(screen)
        draw_status(screen, match_num, wins, result_text, dna_red, dna_blue)
        pygame.display.flip()
        clock.tick(FPS)


    # Final frame is already drawn — now wait for key press
    wait_for_continue(screen)

    pygame.quit()
    return result


def play_end_screen(message):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill(BG)
    font = pygame.font.SysFont(None, 60)
    msg = font.render(message, True, (255, 255, 0))
    rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(msg, rect)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                waiting = False
    pygame.quit()


def run_challenge(dna_red, dna_blue):
    wins = 0
    round_num = 1
    while wins < 3:
        result = play_match(dna_red, dna_blue, round_num, wins)
        if result == "blue":
            wins += 1
        elif result == "red":
            return {
                "winner": "Red",
                "message": "Blue lost. Challenge failed. Try again?",
                "rounds_played": round_num
            }
        round_num += 1

    return {
        "winner": "Blue",
        "message": "Blue is the new champion!",
        "rounds_played": round_num - 1
    }

def run_game():
    # Hardcoded Red Champion
    dna_red = DragonDNA(
        lookahead_depth=1,
        enemy_seek=0.38778546510067036,
        wall_avoidance=0.43758348977319944,
        directional_stability=0.43375173021459623
    )

    # Player designs Blue Dragon
    dna_blue = opening_screen()

    run_challenge(dna_red, dna_blue)

if __name__ == "__main__":
    run_game()

