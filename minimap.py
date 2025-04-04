import pygame

class MiniMap:
    def __init__(self, map_width, map_height, screen_width, screen_height):
        self.map_width = map_width
        self.map_height = map_height
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.small_size = (200, 200)  # Increased size for small minimap
        self.large_size = (600, 600)  # Increased size for large minimap
        self.surface = pygame.Surface(self.small_size, pygame.SRCALPHA)
        self.width, self.height = self.small_size  # Set initial width and height from small_size
        self.opacity = 200
        self.fullscreen = False

        self.border_color = (80, 60, 40)
        self.bg_color = (20, 20, 20, 180)
        self.camp_color = (255, 220, 100)
        self.player_color = (255, 80, 80)
        self.rock_color = (130, 130, 130)
        self.water_color = (50, 140, 255)
        self.cow_color = (200, 255, 200)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        new_size = self.large_size if self.fullscreen else self.small_size
        self.surface = pygame.Surface(new_size, pygame.SRCALPHA)
        self.width, self.height = new_size  # Update width and height when toggling fullscreen

    def draw(self, screen, player_x, player_y, camps, rocks, water_tiles, cows):
        # Clear minimap
        self.surface.fill((30, 30, 30))  # Dark background

        # Draw camps as yellow squares
        for camp in camps:
            cx = int((camp.x / self.map_width) * self.width)
            cy = int((camp.y / self.map_height) * self.height)
            pygame.draw.rect(self.surface, (255, 230, 100), (cx, cy, 4, 4))  # Yellow for camps

        # Draw water as blue squares
        for lake in water_tiles:
            for tile in lake:
                lx = int((tile.x / self.map_width) * self.width)
                ly = int((tile.y / self.map_height) * self.height)
                pygame.draw.rect(self.surface, (50, 120, 255), (lx, ly, 2, 2))  # Blue for lakes

        # Draw rocks as gray squares
        for rock in rocks:
            rx = int((rock.x / self.map_width) * self.width)
            ry = int((rock.y / self.map_height) * self.height)
            pygame.draw.rect(self.surface, (100, 100, 100), (rx, ry, 2, 2))  # Gray for rocks

        # Draw cows as green dots
        for cow in cows:
            cow_x = int((cow.x / self.map_width) * self.width)
            cow_y = int((cow.y / self.map_height) * self.height)
            pygame.draw.circle(self.surface, (0, 255, 0), (cow_x, cow_y), 2)  # Green for cows

        # Draw player as a red dot
        mini_x = int((player_x / self.map_width) * self.width)
        mini_y = int((player_y / self.map_height) * self.height)
        pygame.draw.circle(self.surface, (255, 0, 0), (mini_x, mini_y), 5)

        # Blit to screen
        screen.blit(self.surface, (self.screen_width - self.width - 20, 20))  # Adjusted position
