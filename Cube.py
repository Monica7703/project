import pygame
import sys
import os

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 0.5
JUMP_STRENGTH = -12
PLAYER_SPEED = 5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LAVA_COLOR = (207, 16, 32)
PLATFORM_COLOR = (46, 139, 87)
GOAL_COLOR = (255, 215, 0)
WALL_COLOR = (100, 100, 100)  # Gray color for walls

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cube Hop")
clock = pygame.time.Clock()

# Load fonts
font = pygame.font.SysFont('Bison', 64)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Simple cube player
        self.image = pygame.Surface((30, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = SCREEN_HEIGHT - 150
        self.velocity_y = 0
        self.on_ground = False
        self.facing_right = True

    def update(self, platforms, walls):
        # Apply gravity
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        # Check for platform collisions
        self.on_ground = False
        for platform in platforms:
            if self.velocity_y > 0 and self.rect.colliderect(platform.rect):
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                self.on_ground = True

        # Check for wall collisions (vertical)
        for wall in walls:
            # Check if hitting wall from left side
            if self.rect.right > wall.rect.left and self.rect.left < wall.rect.left and self.rect.bottom > wall.rect.top and self.rect.top < wall.rect.bottom:
                self.rect.right = wall.rect.left
            
            # Check if hitting wall from right side
            elif self.rect.left < wall.rect.right and self.rect.right > wall.rect.right and self.rect.bottom > wall.rect.top and self.rect.top < wall.rect.bottom:
                self.rect.left = wall.rect.right

        # Prevent falling through bottom
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity_y = 0
            self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.velocity_y = JUMP_STRENGTH

    def move_left(self):
        self.rect.x -= PLAYER_SPEED
        if self.rect.left < 0:
            self.rect.left = 0
        self.facing_right = False

    def move_right(self):
        self.rect.x += PLAYER_SPEED
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        self.facing_right = True

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(PLATFORM_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(LAVA_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(WALL_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GOAL_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def create_level():
    """Create all game objects for the level"""
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    lava_pits = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    
    # Create player
    player = Player()
    all_sprites.add(player)
    
    # Create ground platform
    ground = Platform(0, SCREEN_HEIGHT - 70, SCREEN_WIDTH, 80)
    platforms.add(ground)
    all_sprites.add(ground)
    
    # Add some platforms
    platforms_list = [
        (500, SCREEN_HEIGHT - 250, 50, 20),
        (200, SCREEN_HEIGHT - 300, 50, 20),
        (200, SCREEN_HEIGHT - 480, 50, 20),
        (300, SCREEN_HEIGHT - 180, 50, 20),
    ]
    
    for x, y, w, h in platforms_list:
        platform = Platform(x, y, w, h)
        platforms.add(platform)
        all_sprites.add(platform)
    
    # Add lava pits
    lava_list = [
        (250, SCREEN_HEIGHT - 80, 600, 100),
    ]
    
    for x, y, w, h in lava_list:
        lava = Lava(x, y, w, h)
        lava_pits.add(lava)
        all_sprites.add(lava)
    
    # Add walls (obstacles in front of goal)
    wall_list = [
        (650, SCREEN_HEIGHT - 500, 20, 419),  # Left wall
        (730, SCREEN_HEIGHT - 500, 20, 419),   # Right wall
    ]
    
    for x, y, w, h in wall_list:
        wall = Wall(x, y, w, h)
        walls.add(wall)
        all_sprites.add(wall)
    
    # Add goal (behind the walls)
    goal = Goal(675, SCREEN_HEIGHT - 120, 50, 30)
    all_sprites.add(goal)
    
    return player, all_sprites, platforms, lava_pits, walls, goal

def draw_text(text, color, x, y):
    """Helper function to draw text on screen"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def main():
    player, all_sprites, platforms, lava_pits, walls, goal = create_level()
    
    game_over = False
    victory = False
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over and not victory:
                    player.jump()
                if event.key == pygame.K_r and (game_over or victory):
                    # Reset game
                    player, all_sprites, platforms, lava_pits, walls, goal = create_level()
                    game_over = False
                    victory = False
        
        if not game_over and not victory:
            # Get keys pressed
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.move_left()
            elif keys[pygame.K_RIGHT]:
                player.move_right()
            
            # Update
            player.update(platforms, walls)
            
            # Check for lava collision
            if pygame.sprite.spritecollide(player, lava_pits, False):
                game_over = True
            
            # Check for goal collision
            if pygame.sprite.collide_rect(player, goal):
                victory = True
        
        # Draw
        screen.fill(BLACK)
        all_sprites.draw(screen)
        
        # Draw UI messages
        if game_over:
            draw_text("GAME OVER - Press R to restart", RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        if victory:
            draw_text("VICTORY! - Press R to play again", GOAL_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()