import pygame

GRID_SIZE = 64

class WaterTile:
    def __init__(self, x, y):
        self.x = (x // GRID_SIZE) * GRID_SIZE  # Align to grid
        self.y = (y // GRID_SIZE) * GRID_SIZE  # Align to grid
        self.size = GRID_SIZE  # or whatever your lake tile size is
        self.rect = pygame.Rect(self.x, self.y, GRID_SIZE, GRID_SIZE)  # Size matches grid
        self.harvested = False

    def draw(self, screen, camera_x, camera_y):
        if not self.harvested:
            pygame.draw.rect(screen, (50, 143, 168), (self.x - camera_x, self.y - camera_y, self.size, self.size))

    def harvest(self):
        self.harvested = True
