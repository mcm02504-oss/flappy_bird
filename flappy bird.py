
 
import pygame
import random
import sys

pygame.init()

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 432, 768
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird – Challenge Mode")

CLOCK = pygame.time.Clock()
FONT_BIG = pygame.font.SysFont("Arial", 42, bold=True)
FONT = pygame.font.SysFont("Arial", 28, bold=True)

GRAVITY = 0.45
FLAP = -8
PIPE_GAP = 160
PIPE_SPEED = 4
GROUND_Y = 650
WIN_SCORE = 50

# Colors
SKY = (120, 200, 255)
PIPE_GREEN = (95, 181, 67)
PIPE_DARK = (70, 150, 50)
GROUND = (222, 216, 149)
GROUND_DARK = (200, 190, 120)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CITY = (60, 70, 90)
WINDOW = (255, 230, 120)
ENEMY_RED = (200, 50, 50)

# ---------------- TEXTURES ----------------
def make_bird(frame):
    surf = pygame.Surface((34, 24), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (255, 220, 0), (2, 2, 28, 20))
    pygame.draw.ellipse(surf, WHITE, (6, 8, 14, 10))
    pygame.draw.ellipse(surf, BLACK, (2, 2, 28, 20), 1)
    pygame.draw.circle(surf, BLACK, (22, 10), 3)
    pygame.draw.circle(surf, WHITE, (23, 9), 1)
    pygame.draw.polygon(surf, (255, 140, 0), [(26,12),(34,14),(26,16)])
    wing_y = [14, 12, 10][frame]
    pygame.draw.ellipse(surf, (255, 200, 0), (8, wing_y, 10, 6))
    return surf

def make_pipe(h, flip=False):
    surf = pygame.Surface((80, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, PIPE_GREEN, (0, 0, 80, h))
    pygame.draw.rect(surf, PIPE_DARK, (0, 0, 10, h))
    pygame.draw.rect(surf, PIPE_DARK, (70, 0, 10, h))
    pygame.draw.rect(surf, PIPE_GREEN, (-5, h-20, 90, 20))
    if flip:
        surf = pygame.transform.flip(surf, False, True)
    return surf

def generate_city():
    surf = pygame.Surface((WIDTH * 2, HEIGHT), pygame.SRCALPHA)
    x = 0
    while x < surf.get_width():
        w = random.randint(40, 70)
        h = random.randint(120, 260)
        y = GROUND_Y - h
        pygame.draw.rect(surf, CITY, (x, y, w, h))
        for wy in range(y + 10, y + h - 10, 20):
            for wx in range(x + 8, x + w - 8, 16):
                if random.random() > 0.6:
                    pygame.draw.rect(surf, WINDOW, (wx, wy, 8, 10))
        x += w + 6
    return surf

# ---------------- CLASSES ----------------
class Bird:
    def __init__(self):
        self.x = 80
        self.y = HEIGHT // 2
        self.vel = 0
        self.frame = 0

    def update(self):
        self.vel += GRAVITY
        self.y += self.vel
        self.frame = (self.frame + 1) % 3

    def flap(self):
        self.vel = FLAP

    def draw(self):
        SCREEN.blit(make_bird(self.frame), (self.x, self.y))

    def rect(self):
        return pygame.Rect(self.x, self.y, 30, 22)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.top_h = random.randint(120, 350)
        self.bottom_y = self.top_h + PIPE_GAP
        self.passed = False
        self.top = make_pipe(self.top_h, True)
        self.bottom = make_pipe(HEIGHT - self.bottom_y)

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self):
        SCREEN.blit(self.top, (self.x, 0))
        SCREEN.blit(self.bottom, (self.x, self.bottom_y))

    def collide(self, bird):
        return bird.rect().colliderect((self.x,0,80,self.top_h)) or \
               bird.rect().colliderect((self.x,self.bottom_y,80,HEIGHT))

class Enemy:
    def __init__(self):
        self.x = WIDTH + random.randint(100, 300)
        self.y = random.randint(150, GROUND_Y - 120)
        self.speed = PIPE_SPEED + 1
        self.dir = random.choice([-1, 1])

    def update(self):
        self.x -= self.speed
        self.y += self.dir * 2
        if self.y < 120 or self.y > GROUND_Y - 80:
            self.dir *= -1

    def draw(self):
        pygame.draw.rect(SCREEN, ENEMY_RED, (self.x, self.y, 30, 30))

    def rect(self):
        return pygame.Rect(self.x, self.y, 30, 30)

# ---------------- GAME ----------------
def draw_text(text, y, big=False):
    font = FONT_BIG if big else FONT
    t = font.render(text, True, WHITE)
    SCREEN.blit(t, (WIDTH//2 - t.get_width()//2, y))

def main():
    bird = Bird()
    pipes = [Pipe(WIDTH + 100)]
    enemies = []
    score = 0
    high_score = 0
    active = False
    win = False

    enemy_timer = 0  # cooldown timer

    city = generate_city()
    city_x = 0
    ground_x = 0

    while True:
        CLOCK.tick(60)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                if not active:
                    bird = Bird()
                    pipes = [Pipe(WIDTH + 100)]
                    enemies = []
                    score = 0
                    win = False
                    enemy_timer = 0
                    active = True
                elif active and not win:
                    bird.flap()

        SCREEN.fill(SKY)

        # City
        city_x -= PIPE_SPEED * 0.3
        if city_x <= -WIDTH:
            city_x = 0
        SCREEN.blit(city, (city_x, 0))
        SCREEN.blit(city, (city_x + WIDTH, 0))

        if active and not win:
            bird.update()
            enemy_timer += 1

            if pipes[-1].x < WIDTH - 200:
                pipes.append(Pipe(WIDTH))

            # ENEMIES: sometimes, before score 50
            if score < WIN_SCORE and enemy_timer > 180 and random.random() < 0.4:
                enemies.append(Enemy())
                enemy_timer = 0

            for p in pipes:
                p.update()
                if p.collide(bird):
                    active = False
                if p.x + 80 < bird.x and not p.passed:
                    p.passed = True
                    score += 1
                    high_score = max(high_score, score)
                    if score >= WIN_SCORE:
                        win = True
                        active = False

            for en in enemies:
                en.update()
                if en.rect().colliderect(bird.rect()):
                    active = False

            enemies = [e for e in enemies if e.x > -50]
            pipes = [p for p in pipes if p.x > -100]

            if bird.y > GROUND_Y or bird.y < 0:
                active = False

        for p in pipes:
            p.draw()
        for en in enemies:
            en.draw()

        bird.draw()

        ground_x = (ground_x - PIPE_SPEED) % WIDTH
        pygame.draw.rect(SCREEN, GROUND, (ground_x, GROUND_Y, WIDTH, HEIGHT))
        pygame.draw.rect(SCREEN, GROUND, (ground_x - WIDTH, GROUND_Y, WIDTH, HEIGHT))
        pygame.draw.rect(SCREEN, GROUND_DARK, (0, GROUND_Y, WIDTH, 10))

        draw_text(f"Score: {score}", 20)
        draw_text(f"High Score: {high_score}", 55)

        if not active:
            if win:
                draw_text("YOU WIN", 300, True)
                draw_text("Tap to Restart", 360)
            else:
                draw_text("Reach Score 50 And Win", 310, False)
                draw_text("Tap to Start", 360)

        pygame.display.update()

main()
