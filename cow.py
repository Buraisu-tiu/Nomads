import pygame
import random

class Cow:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.rect = pygame.Rect(x, y, image.get_width(), image.get_height())

        self.health = 3
        self.speed = 1.3
        self.run_speed = 5.0
        self.facing_right = True

        self.invincibility_frames = 0
        self.moving_timer = 0
        self.moving_direction = [0, 0]
        self.run_direction = [0, 0]

    def wander(self, blocked_rects=[]):
        dx, dy = 0, 0  # Make sure dx and dy always exist

        if self.invincibility_frames > 0:
            self.invincibility_frames -= 1
            dx = self.run_direction[0] * self.run_speed
            dy = self.run_direction[1] * self.run_speed
        else:
            if self.moving_timer <= 0:
                self.moving_direction = [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
                self.moving_timer = random.randint(30, 90)
            else:
                self.moving_timer -= 1

            dx = self.moving_direction[0] * self.speed
            dy = self.moving_direction[1] * self.speed

        self.x += dx
        self.y += dy

        # Facing direction
        if dx != 0:
            self.facing_right = dx < 0

        # Clamp to map
        self.x = max(0, min(self.x, 4000 - self.image.get_width()))
        self.y = max(0, min(self.y, 3000 - self.image.get_height()))
        self.rect.topleft = (self.x, self.y)

        # Collision with environment
        for rect in blocked_rects:
            if self.rect.colliderect(rect):
                self.x -= dx
                self.y -= dy
                self.rect.topleft = (self.x, self.y)
                break

    def take_damage(self, player_pos):
        if self.invincibility_frames > 0:
            return False

        self.health -= 1
        self.invincibility_frames = 15  # ~0.5 sec

        # Run away direction
        dx = self.x - player_pos[0]
        dy = self.y - player_pos[1]
        dist = (dx**2 + dy**2) ** 0.5 or 1
        self.run_direction = [dx / dist, dy / dist]

        return self.health <= 0

    def draw(self, screen, camera_x, camera_y):
        sprite = self.image
        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)

        screen.blit(sprite, (self.x - camera_x, self.y - camera_y))

        # Health bar
        if self.health < 3:
            bar_w, bar_h = 40, 6
            ratio = self.health / 3
            bar_x = self.x + self.image.get_width() // 2 - bar_w // 2 - camera_x
            bar_y = self.y - 12 - camera_y

            pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, int(bar_w * ratio), bar_h))
