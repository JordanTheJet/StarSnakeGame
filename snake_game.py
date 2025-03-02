import pygame
import random
import colorsys
import time
import math
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 600
GRID_SIZE = 30  # Increased grid size for better star visibility
GRID_COUNT = WINDOW_SIZE // GRID_SIZE
RESPAWN_TIME = 3  # seconds

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

class Star:
    def __init__(self):
        self.reset_position()
        self.hue = 0
        self.is_respawning = False
        self.respawn_start = 0
        self.rotation = 0

    def reset_position(self):
        self.positions = [(GRID_COUNT // 2, GRID_COUNT // 2)]
        self.direction = (1, 0)
        self.add_segment = False

    def move(self):
        if self.is_respawning:
            return

        current = self.positions[0]
        x, y = self.direction
        new_position = (current[0] + x, current[1] + y)

        if self.add_segment:
            self.positions.insert(0, new_position)
            self.add_segment = False
        else:
            self.positions.pop()
            self.positions.insert(0, new_position)
        
        self.hue = (self.hue + 0.02) % 1.0
        self.rotation = (self.rotation + 5) % 360

    def get_rainbow_colors(self):
        colors = []
        for i in range(len(self.positions)):
            hue = (self.hue + i * 0.1) % 1.0
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            color = tuple(int(x * 255) for x in rgb)
            colors.append(color)
        return colors

    def grow(self):
        self.add_segment = True

    def start_respawn(self):
        self.is_respawning = True
        self.respawn_start = time.time()

    def check_respawn(self):
        if self.is_respawning and time.time() - self.respawn_start >= RESPAWN_TIME:
            self.is_respawning = False
            self.reset_position()
            return True
        return False

def draw_star(surface, color, pos, size):
    x, y = pos
    points = []
    for i in range(5):
        # Outer points of the star
        angle = math.pi * 2 * i / 5 - math.pi / 2
        points.append((
            x + size * math.cos(angle),
            y + size * math.sin(angle)
        ))
        # Inner points of the star
        angle += math.pi / 5
        points.append((
            x + size * 0.4 * math.cos(angle),
            y + size * 0.4 * math.sin(angle)
        ))
    pygame.draw.polygon(surface, color, points)

def main():
    clock = pygame.time.Clock()
    star = Star()
    food = (random.randint(0, GRID_COUNT-1), random.randint(0, GRID_COUNT-1))
    score = 0
    lives = 2
    game_over = False

    # Create the window
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption('Star Trail Game')

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            elif event.type == KEYDOWN:
                if game_over:
                    if event.key == K_SPACE:
                        star = Star()
                        food = (random.randint(0, GRID_COUNT-1), random.randint(0, GRID_COUNT-1))
                        score = 0
                        lives = 2
                        game_over = False
                        continue
                elif not star.is_respawning:
                    if event.key == K_UP and star.direction != (0, 1):
                        star.direction = (0, -1)
                    elif event.key == K_DOWN and star.direction != (0, -1):
                        star.direction = (0, 1)
                    elif event.key == K_LEFT and star.direction != (1, 0):
                        star.direction = (-1, 0)
                    elif event.key == K_RIGHT and star.direction != (-1, 0):
                        star.direction = (1, 0)

        if not game_over and not star.is_respawning:
            star.move()
            head = star.positions[0]

            # Check for collisions with walls
            if (head[0] < 0 or head[0] >= GRID_COUNT or 
                head[1] < 0 or head[1] >= GRID_COUNT):
                lives -= 1
                if lives > 0:
                    star.start_respawn()
                else:
                    game_over = True

            # Check for collisions with self
            elif head in star.positions[1:]:
                game_over = True

            # Check for food collision
            elif head == food:
                star.grow()
                score += 1
                food = (random.randint(0, GRID_COUNT-1), random.randint(0, GRID_COUNT-1))
                while food in star.positions:
                    food = (random.randint(0, GRID_COUNT-1), random.randint(0, GRID_COUNT-1))

        # Check if respawn timer is complete
        if star.check_respawn():
            food = (random.randint(0, GRID_COUNT-1), random.randint(0, GRID_COUNT-1))

        # Draw everything
        screen.fill(BLACK)
        
        # Draw star trail with rainbow colors
        rainbow_colors = star.get_rainbow_colors()
        for i, (position, color) in enumerate(zip(star.positions, rainbow_colors)):
            center_x = position[0] * GRID_SIZE + GRID_SIZE // 2
            center_y = position[1] * GRID_SIZE + GRID_SIZE // 2
            size = GRID_SIZE // 2 if i == 0 else GRID_SIZE // 3  # Bigger star for head
            draw_star(screen, color, (center_x, center_y), size)
        
        # Draw food as a star
        food_x = food[0] * GRID_SIZE + GRID_SIZE // 2
        food_y = food[1] * GRID_SIZE + GRID_SIZE // 2
        draw_star(screen, RED, (food_x, food_y), GRID_SIZE // 2)

        # Draw score and lives
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}  Lives: {lives}', True, WHITE)
        screen.blit(score_text, (10, 10))

        if star.is_respawning:
            time_left = RESPAWN_TIME - (time.time() - star.respawn_start)
            respawn_text = font.render(f'Respawning in: {time_left:.1f}', True, WHITE)
            text_rect = respawn_text.get_rect(center=(WINDOW_SIZE/2, WINDOW_SIZE/2))
            screen.blit(respawn_text, text_rect)
        elif game_over:
            game_over_text = font.render('Game Over! Press SPACE to restart', True, WHITE)
            text_rect = game_over_text.get_rect(center=(WINDOW_SIZE/2, WINDOW_SIZE/2))
            screen.blit(game_over_text, text_rect)

        pygame.display.flip()
        clock.tick(20)

if __name__ == '__main__':
    main()
