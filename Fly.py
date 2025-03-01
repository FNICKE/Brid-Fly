import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Game settings
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (0, 0, 255)
PIPE_WIDTH = 60
PIPE_HEIGHT = 500
BIRD_WIDTH = 20
BIRD_HEIGHT = 20
GAP_SIZE = 150
GRAVITY = 0.05  # Slower fall speed
JUMP_STRENGTH = -2  # Smaller jump strength
PIPE_VELOCITY = 5  # Slower pipe speed
BIRD_VELOCITY = 2
FPS = 40  # Lowered FPS for slower game speed
MAX_JUMPS = 1000  # Maximum jumps before recharge

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Initialize the game screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Load assets
bird_image = pygame.Surface((BIRD_WIDTH, BIRD_HEIGHT))
bird_image.fill((255, 255, 0))  # Bird in yellow
bird_rect = bird_image.get_rect()
bird_rect.center = (100, SCREEN_HEIGHT // 2)

# Fonts
font = pygame.font.SysFont("Arial", 30)

# Game clock
clock = pygame.time.Clock()

# Pipe class
class Pipe:
    def __init__(self, x_position):
        self.x = x_position
        self.height = random.randint(100, SCREEN_HEIGHT - GAP_SIZE)
        self.top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.height)
        self.bottom_rect = pygame.Rect(self.x, self.height + GAP_SIZE, PIPE_WIDTH, SCREEN_HEIGHT - self.height - GAP_SIZE)

    def move(self):
        self.x -= PIPE_VELOCITY
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.top_rect)
        pygame.draw.rect(screen, GREEN, self.bottom_rect)

    def off_screen(self):
        return self.x < -PIPE_WIDTH

# Bird class
class Bird:
    def __init__(self):
        self.rect = bird_rect
        self.velocity = BIRD_VELOCITY
        self.is_jumping = False
        self.jumps_left = MAX_JUMPS  # Track the number of jumps left
        self.is_descending = False  # Flag to track if the bird is descending faster

    def jump(self):
        """Make the bird jump if there are jumps left"""
        if self.jumps_left > 0:
            self.velocity = JUMP_STRENGTH
            self.is_jumping = True
            self.jumps_left -= 1  # Decrease the jumps left

    def descend(self):
        """Move the bird down quickly when the down arrow is pressed"""
        self.velocity = 5  # Increase descent speed

    def stop_descend(self):
        """Stop descending fast when the down arrow is released"""
        if not self.is_jumping:
            self.velocity = GRAVITY  # Restore normal gravity effect

    def move(self):
        """Apply gravity and move the bird's position"""
        if not self.is_descending:
            self.velocity += GRAVITY
        
        self.rect.y += self.velocity

        # Reset jump count when the bird hits the ground
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity = 0
            self.jumps_left = MAX_JUMPS  # Reset jumps when the bird lands

    def draw(self, screen):
        """Draw the bird on the screen"""
        screen.blit(bird_image, self.rect)

    def reset(self):
        """Reset bird's position and state"""
        self.rect.center = (100, SCREEN_HEIGHT // 2)
        self.velocity = BIRD_VELOCITY
        self.is_jumping = False
        self.jumps_left = MAX_JUMPS  # Reset jumps when the game is reset

# Game class
class Game:
    def __init__(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_over = False

    def spawn_pipe(self):
        """Spawn a new pipe"""
        if len(self.pipes) == 0 or self.pipes[-1].x < SCREEN_WIDTH - 300:
            # Modify seed based on score to change random pipe patterns
            random.seed(self.score)  # Increase randomness with score
            new_pipe = Pipe(SCREEN_WIDTH)
            self.pipes.append(new_pipe)

    def check_collisions(self):
        """Check for collisions with pipes or screen edges"""
        if self.bird.rect.top <= 0 or self.bird.rect.bottom >= SCREEN_HEIGHT:
            self.game_over = True
        for pipe in self.pipes:
            if self.bird.rect.colliderect(pipe.top_rect) or self.bird.rect.colliderect(pipe.bottom_rect):
                self.game_over = True

    def update(self):
        """Update game logic"""
        if self.game_over:
            return

        self.bird.move()
        self.spawn_pipe()

        # Move pipes and remove off-screen pipes
        for pipe in self.pipes[:]:
            pipe.move()
            if pipe.off_screen():
                self.pipes.remove(pipe)
                self.score += 1  # Increment score when pipe moves off screen

        self.check_collisions()

    def draw(self):
        """Draw the game elements on the screen"""
        screen.fill(BACKGROUND_COLOR)
        
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(screen)
        
        # Draw bird
        self.bird.draw(screen)

        # Draw score
        score_text = font.render(f"Score: {self.score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        # Display jumps left
        jump_text = font.render(f"Jumps Left: {self.bird.jumps_left}", True, BLACK)
        screen.blit(jump_text, (SCREEN_WIDTH - 150, 10))

        if self.game_over:
            game_over_text = font.render("Game Over!", True, BLACK)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 30))
            retry_text = font.render("Press SPACE to Retry", True, BLACK)
            screen.blit(retry_text, (SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 + 10))

    def reset(self):
        """Reset the game state"""
        self.bird.reset()
        self.pipes.clear()
        self.score = 0
        self.game_over = False

# Main game loop
def main():
    game = Game()
    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:  # Up arrow key for jumping
                    game.bird.jump()
                if event.key == pygame.K_DOWN:  # Down arrow key for descending faster
                    game.bird.descend()
                if event.key == pygame.K_SPACE and game.game_over:  # Restart on SPACE key press
                    game.reset()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:  # Stop descending when key is released
                    game.bird.stop_descend()

        # Update game logic
        game.update()

        # Draw everything
        game.draw()

        # Update the display
        pygame.display.update()

if __name__ == "__main__":
    main()
