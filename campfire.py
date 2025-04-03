import pygame
import time
import random


DESERT_COLOR = (199, 168, 107)


class Campfire:
    def __init__(self, x, y, duration=90000):  # Burns for 90 sec (ms)
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 48, 48)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        self.image = self.make_flame_image()
        self.glow_radius = random.randint(280, 320)  # Initial dynamic glow radius
        self.alpha = 180  # Initial alpha for light intensity
        self.last_flicker_time = pygame.time.get_ticks()  # Timer for flicker updates
        self.flicker_interval = 500  # Flicker every 500ms (adjust for slower flicker)

    def make_flame_image(self):
        surface = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.circle(surface, (255, 140, 50), (24, 24), 20)
        pygame.draw.circle(surface, (255, 180, 100), (24, 24), 12)
        return surface

    def is_burning(self):
        return pygame.time.get_ticks() - self.start_time < self.duration

    def update_light_effect(self):
        """Update the glow radius and alpha to create a slower flickering effect and gradual fade-out."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_flicker_time >= self.flicker_interval:
            self.last_flicker_time = current_time  # Reset the timer

            elapsed_time = current_time - self.start_time
            remaining_time_ratio = max(0, 1 - elapsed_time / self.duration)  # Ratio of remaining burn time (0 to 1)

            # Gradually reduce alpha and glow radius as the fire burns out
            self.alpha = int(180 * remaining_time_ratio)  # Fade out light intensity
            self.glow_radius = int(random.randint(280, 320) * remaining_time_ratio)  # Shrink glow radius

            # Slow down flickering by reducing randomness
            self.glow_radius += random.randint(-10, 10)

    def draw(self, screen, camera_x, camera_y):
        # Fire sprite or box
        pygame.draw.rect(screen, (200, 90, 40), (self.x - camera_x, self.y - camera_y, 64, 64))

        # 🔦 Dynamic light glow with correct brightness (brightest at center, fades outward)
        self.update_light_effect()  # Update glow radius and alpha
        glow_surface = pygame.Surface((self.glow_radius * 2, self.glow_radius * 2), pygame.SRCALPHA)

        for radius in range(self.glow_radius, 0, -1):
            fade_alpha = int(self.alpha * (1 - (radius / self.glow_radius)))  # Brightest at center, fades outward
            blended_color = (
                int(DESERT_COLOR[0] * 0.8 + 255 * 0.2),  # Blend with orange
                int(DESERT_COLOR[1] * 0.8 + 140 * 0.2),
                int(DESERT_COLOR[2] * 0.8 + 50 * 0.2),
                fade_alpha
            )
            pygame.draw.circle(glow_surface, blended_color, (self.glow_radius, self.glow_radius), radius)

        screen.blit(glow_surface, (self.x - self.glow_radius - camera_x + 32, self.y - self.glow_radius - camera_y + 32))