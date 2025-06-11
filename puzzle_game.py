import pygame
import sys
import random
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
PUZZLE_ROWS = 3
PUZZLE_COLS = 3
TILE_SIZE = WINDOW_WIDTH // PUZZLE_COLS
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

# Create the window
DISPLAY_SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Puzzle Game')
CLOCK = pygame.time.Clock()

class PuzzleGame:
    def __init__(self):
        self.board = []
        self.solved_board = []
        for i in range(PUZZLE_ROWS * PUZZLE_COLS):
            self.solved_board.append(i)
        
        # Create a solvable puzzle
        self.board = self.solved_board.copy()
        self.shuffle()
        
        # Load and split the image
        self.load_image("puzzle_image.png")  # You'll need to provide an image file
        
        self.blank_pos = self.board.index(PUZZLE_ROWS * PUZZLE_COLS - 1)
        self.game_solved = False
    
    def load_image(self, image_path):
        try:
            self.original_image = pygame.image.load(image_path)
            self.original_image = pygame.transform.scale(self.original_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
            self.tiles = []
            
            for row in range(PUZZLE_ROWS):
                for col in range(PUZZLE_COLS):
                    rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    tile_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
                    tile_surface.blit(self.original_image, (0, 0), rect)
                    self.tiles.append(tile_surface)
                    
            # Make the last tile blank
            self.tiles[-1].fill(WHITE)
        except pygame.error:
            # If image loading fails, create colored tiles instead
            self.tiles = []
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), 
                      (255, 255, 0), (255, 0, 255), (0, 255, 255),
                      (128, 0, 0), (0, 128, 0), (0, 0, 128)]
            
            for i in range(PUZZLE_ROWS * PUZZLE_COLS):
                tile_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
                if i < len(colors):
                    tile_surface.fill(colors[i])
                else:
                    tile_surface.fill(WHITE)
                
                # Add number to the tile
                if i < PUZZLE_ROWS * PUZZLE_COLS - 1:
                    font = pygame.font.Font(None, 36)
                    text = font.render(str(i + 1), True, BLACK)
                    text_rect = text.get_rect(center=(TILE_SIZE // 2, TILE_SIZE // 2))
                    tile_surface.blit(text, text_rect)
                
                self.tiles.append(tile_surface)
    
    def shuffle(self):
        # Fisher-Yates shuffle algorithm
        for i in range(len(self.board) - 2, -1, -1):
            j = random.randint(0, i)
            self.board[i], self.board[j] = self.board[j], self.board[i]
        
        # Ensure the puzzle is solvable
        if not self.is_solvable():
            # Swap the first two tiles to make it solvable
            self.board[0], self.board[1] = self.board[1], self.board[0]
    
    def is_solvable(self):
        # Count inversions
        inversions = 0
        for i in range(len(self.board)):
            if self.board[i] == PUZZLE_ROWS * PUZZLE_COLS - 1:  # Skip the blank tile
                blank_row = i // PUZZLE_COLS
                continue
            for j in range(i + 1, len(self.board)):
                if self.board[j] == PUZZLE_ROWS * PUZZLE_COLS - 1:  # Skip the blank tile
                    continue
                if self.board[i] > self.board[j]:
                    inversions += 1
        
        # For odd-sized puzzles, solvable if inversions is even
        if PUZZLE_ROWS % 2 == 1:
            return inversions % 2 == 0
        # For even-sized puzzles, solvable if blank on even row from bottom + odd inversions,
        # or blank on odd row from bottom + even inversions
        else:
            blank_row_from_bottom = PUZZLE_ROWS - blank_row
            return (blank_row_from_bottom % 2 == 0 and inversions % 2 == 1) or \
                   (blank_row_from_bottom % 2 == 1 and inversions % 2 == 0)
    
    def draw(self):
        DISPLAY_SURFACE.fill(WHITE)
        
        for row in range(PUZZLE_ROWS):
            for col in range(PUZZLE_COLS):
                index = row * PUZZLE_COLS + col
                tile_value = self.board[index]
                
                # Draw the tile
                DISPLAY_SURFACE.blit(self.tiles[tile_value], (col * TILE_SIZE, row * TILE_SIZE))
                
                # Draw grid lines
                pygame.draw.rect(DISPLAY_SURFACE, BLACK, 
                                (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)
        
        if self.game_solved:
            font = pygame.font.Font(None, 48)
            text = font.render("Puzzle Solved!", True, (0, 128, 0))
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 180))
            DISPLAY_SURFACE.blit(overlay, (0, 0))
            DISPLAY_SURFACE.blit(text, text_rect)
    
    def handle_click(self, mouse_pos):
        if self.game_solved:
            return
            
        col = mouse_pos[0] // TILE_SIZE
        row = mouse_pos[1] // TILE_SIZE
        
        clicked_index = row * PUZZLE_COLS + col
        blank_index = self.board.index(PUZZLE_ROWS * PUZZLE_COLS - 1)
        
        # Check if the clicked tile is adjacent to the blank tile
        blank_row, blank_col = blank_index // PUZZLE_COLS, blank_index % PUZZLE_COLS
        clicked_row, clicked_col = clicked_index // PUZZLE_COLS, clicked_index % PUZZLE_COLS
        
        if (abs(blank_row - clicked_row) == 1 and blank_col == clicked_col) or \
           (abs(blank_col - clicked_col) == 1 and blank_row == clicked_row):
            # Swap the tiles
            self.board[blank_index], self.board[clicked_index] = self.board[clicked_index], self.board[blank_index]
            
            # Check if the puzzle is solved
            if self.board == self.solved_board:
                self.game_solved = True
    
    def reset(self):
        self.board = self.solved_board.copy()
        self.shuffle()
        self.game_solved = False

def main():
    game = PuzzleGame()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                game.handle_click(event.pos)
            elif event.type == KEYUP:
                if event.key == K_r:  # Reset the game
                    game.reset()
        
        game.draw()
        pygame.display.update()
        CLOCK.tick(FPS)

if __name__ == '__main__':
    main()
