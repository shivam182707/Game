import pygame
import random
import os
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Setup Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sky Strike: Fighter Jet Ace")
clock = pygame.time.Clock()

# Asset Paths
ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')

def load_image(name, size=None):
    path = os.path.join(ASSET_DIR, name)
    try:
        image = pygame.image.load(path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except Exception as e:
        print(f"Warning: Could not load image {name}: {e}")
        # Return a placeholder surface
        surf = pygame.Surface(size or (50, 50), pygame.SRCALPHA)
        pygame.draw.rect(surf, RED if 'enemy' in name else BLUE, surf.get_rect(), border_radius=10)
        return surf

# Load Assets
PLAYER_SIZE = (60, 60)
ENEMY_SIZE = (50, 50)
BULLET_SIZE = (5, 15)

player_img = load_image('player.png', PLAYER_SIZE)
enemy_img = load_image('enemy.png', ENEMY_SIZE)
background_img = load_image('background.png', (WIDTH, HEIGHT))

# Background scrolling variables
bg_y1 = 0
bg_y2 = -HEIGHT
scroll_speed = 2

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20
        self.speed = 7
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
        
        if keys[pygame.K_SPACE]:
            self.shoot()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(3, 8)
        self.speedx = random.randrange(-1, 2)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 25:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(3, 8)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface(BULLET_SIZE)
        self.image.fill((255, 255, 0)) # Yellow bullets
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

# Groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

for i in range(8):
    e = Enemy()
    all_sprites.add(e)
    enemies.add(e)

score = 0
font = pygame.font.SysFont("Arial", 24, bold=True)

def draw_text(surf, text, size, x, y):
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

# Main Loop
running = True
game_over = False

while running:
    # 1. Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_r:
                # Reset game
                game_over = False
                all_sprites.empty()
                enemies.empty()
                bullets.empty()
                player = Player()
                all_sprites.add(player)
                for i in range(8):
                    e = Enemy()
                    all_sprites.add(e)
                    enemies.add(e)
                score = 0

    if not game_over:
        # 2. Update
        all_sprites.update()

        # Collisions - Bullet hits Enemy
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            score += 10
            e = Enemy()
            all_sprites.add(e)
            enemies.add(e)

        # Collisions - Enemy hits Player
        hits = pygame.sprite.spritecollide(player, enemies, False)
        if hits:
            game_over = True

        # Background scrolling
        bg_y1 += scroll_speed
        bg_y2 += scroll_speed
        if bg_y1 >= HEIGHT: bg_y1 = -HEIGHT
        if bg_y2 >= HEIGHT: bg_y2 = -HEIGHT

    # 3. Draw
    screen.fill(BLACK)
    
    # Draw Background
    screen.blit(background_img, (0, bg_y1))
    screen.blit(background_img, (0, bg_y2))

    all_sprites.draw(screen)
    draw_text(screen, f"SCORE: {score}", 30, WIDTH // 2, 10)

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        draw_text(screen, "GAME OVER", 64, WIDTH // 2, HEIGHT // 3)
        draw_text(screen, f"Final Score: {score}", 32, WIDTH // 2, HEIGHT // 2)
        draw_text(screen, "Press 'R' to Restart", 24, WIDTH // 2, HEIGHT * 2 // 3)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
