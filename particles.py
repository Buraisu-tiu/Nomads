import pygame
import random

class Particle:
    def __init__(self, x, y, size, lifetime, color, spread_x):
        self.x = x + random.uniform(-spread_x, spread_x)  # Spread out on X-axis
        self.y = y
        self.size = size
        self.lifetime = lifetime  # How long the particle lasts
        self.color = color
        self.velocity_x = random.uniform(-0.3, 0.3)  # Slight side movement
        self.velocity_y = random.uniform(0.5, 1.2)  # Moves downward slightly

    def update(self):
        """Update particle movement and reduce lifetime."""
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.lifetime -= 1  # Slowly disappears

    def draw(self, screen, camera_x, camera_y):
        """Draw the particle relative to the camera position."""
        if self.lifetime > 0:
            pygame.draw.circle(screen, self.color, (int(self.x - camera_x), int(self.y - camera_y)), self.size)


class Footprint:
    def __init__(self, x, y, size, lifetime):
        self.x = x
        self.y = y
        self.size = size
        self.lifetime = lifetime  # How long the footprint lasts
        self.alpha = 255  # Opacity (fades out over time)

    def update(self):
        """Slowly fade out and disappear."""
        self.lifetime -= 1
        self.alpha = max(0, self.alpha - 3)  # Gradually fade

    def draw(self, screen, camera_x, camera_y):
        """Draw footprints with fading effect."""
        if self.lifetime > 0:
            footprint_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            footprint_surface.fill((100, 80, 60, self.alpha))  # Brownish color with alpha
            screen.blit(footprint_surface, (self.x - camera_x, self.y - camera_y))


class ParticleSystem:
    def __init__(self):
        self.particles = []  # List of active particles
        self.footprints = []  # List of footprints

    def add_particle(self, x, y, speed):
        """Create a new sand particle behind the player."""
        if random.random() < 0.3:  # Lower chance of spawning (30% chance per frame)
            size = random.randint(2, 3)  # Small particle size
            lifetime = random.randint(10, 18)  # How long it lasts
            color = (210, 180, 140)  # Sand color
            spread_x = 5  # Spread out left & right

            self.particles.append(Particle(x, y, size, lifetime, color, spread_x))

    def add_footprint(self, x, y):
        """Add a footprint at the player's position with lower chance."""
        if random.random() < 0.3:  # 30% chance per step (previously 60%)
            size = random.randint(6, 9)  # Footprint size
            lifetime = 60  # Lasts about 2 seconds (60 frames at 30 FPS)
            self.footprints.append(Footprint(x, y, size, lifetime))

    def update(self):
        """Update all particles and footprints."""
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update()

        self.footprints = [f for f in self.footprints if f.lifetime > 0]
        for footprint in self.footprints:
            footprint.update()

    def draw(self, screen, camera_x, camera_y):
        """Draw footprints first (so particles appear above them)."""
        for footprint in self.footprints:
            footprint.draw(screen, camera_x, camera_y)

        for particle in self.particles:
            particle.draw(screen, camera_x, camera_y)
