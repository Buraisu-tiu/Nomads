import pygame
import time

class Campfire:
    def __init__(self, x, y, duration=90000):  # Burns for 90 sec (ms)
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 48, 48)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        self.image = self.make_flame_image()

    def make_flame_image(self):
        surface = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.circle(surface, (255, 140, 50), (24, 24), 20)
        pygame.draw.circle(surface, (255, 180, 100), (24, 24), 12)
        return surface

    def is_burning(self):
        return pygame.time.get_ticks() - self.start_time < self.duration

    def draw(self, screen, camera_x, camera_y):
        if self.is_burning():
            flicker = pygame.Surface((48, 48), pygame.SRCALPHA)
            flicker.fill((255, 100, 50, 40 + (pygame.time.get_ticks() % 60)))
            screen.blit(self.image, (self.x - camera_x, self.y - camera_y))
            screen.blit(flicker, (self.x - camera_x, self.y - camera_y))
