import pygame
import time
import random

glow_radius = random.randint(280, 320)
alpha = random.randint(130, 180)

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
        # Fire sprite or box
        pygame.draw.rect(screen, (200, 90, 40), (self.x - camera_x, self.y - camera_y, 64, 64))

        # 🔦 Light glow (this is where we increase the glow!)
        glow_radius = 180  # Increase this number to make the light spread farther!
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 140, 50, alpha), (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surface, (self.x - glow_radius - camera_x + 32, self.y - glow_radius - camera_y + 32))