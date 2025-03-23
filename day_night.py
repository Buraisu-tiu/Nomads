import pygame

class DayNightCycle:
    def __init__(self, day_length=30000, night_length=15000):
        """Initialize the day-night cycle with different day and night speeds."""
        self.start_time = pygame.time.get_ticks()  # Start time in milliseconds
        self.day_length = day_length * 1000  # Convert day duration to milliseconds
        self.night_length = night_length * 1000  # Convert night duration to milliseconds
        self.full_cycle = self.day_length + self.night_length  # Total cycle length
        self.night_opacity = 180  # How dark night gets (0-255)

    def get_time_of_day(self):
        """Returns a value between 0 (morning) and 1 (midnight)."""
        current_time = (pygame.time.get_ticks() - self.start_time) % self.full_cycle
        if current_time < self.day_length:
            return (current_time / self.day_length) * 0.5  # Daytime (0 to 0.5)
        else:
            return 0.5 + ((current_time - self.day_length) / self.night_length) * 0.5  # Nighttime (0.5 to 1)

    def draw(self, screen):
        """Draws a transparent overlay to simulate day-night lighting."""
        time_of_day = self.get_time_of_day()
        darkness = 0

        # **Sunset (Evening) Transition**
        if 0.25 < time_of_day < 0.5:  
            darkness = int(((time_of_day - 0.25) / 0.25) * self.night_opacity)  
        
        # **Midnight (Full Night)**
        elif 0.5 <= time_of_day < 0.75:
            darkness = self.night_opacity
        
        # **Sunrise (Morning) Transition**
        elif 0.75 <= time_of_day < 1:
            darkness = int(((1 - time_of_day) / 0.25) * self.night_opacity)

        # **Apply Darkness Overlay**
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, darkness))  
        screen.blit(overlay, (0, 0))

        # Draw the clock GUI
        self.draw_clock(screen, time_of_day)

    def draw_clock(self, screen, time_of_day):
        """Draws a simple clock UI showing sun & moon movement."""
        clock_x, clock_y = 550, 20  # Centered at the top
        clock_width, clock_height = 300, 30  # Clock bar size

        # **Draw Background**
        pygame.draw.rect(screen, (50, 50, 50), (clock_x, clock_y, clock_width, clock_height))  
        pygame.draw.rect(screen, (0, 0, 0), (clock_x - 2, clock_y - 2, clock_width + 4, clock_height + 4), 2)  # Black Border

        # **Determine Sun & Moon Position**
        sun_x = int(clock_x + (time_of_day * clock_width))  # Move sun based on time
        moon_x = int(clock_x + ((time_of_day + 0.5) % 1 * clock_width))  # Moon moves opposite to sun

        # **Draw Sun (Orange Square)**
        pygame.draw.rect(screen, (255, 165, 0), (sun_x, clock_y + 5, 20, 20))  # Sun position

        # **Draw Moon (Gray Square)**
        pygame.draw.rect(screen, (180, 180, 180), (moon_x, clock_y + 5, 20, 20))  # Moon position
