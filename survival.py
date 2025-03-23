import pygame

class Survival:
    def __init__(self):
        self.hunger = 100
        self.thirst = 100

        # Balanced default drain rates
        self.hunger_decrease = 0.005   # Idle drain (very slow)
        self.thirst_decrease = 0.0075  # Idle drain (very slow)

        self.font = pygame.font.Font(None, 28)

    def update(self, player_state, near_fire=False):
        if near_fire:
            hunger_rate = 0.0002
            thirst_rate = 0.0003
        else:
            hunger_rate = 0.0005
            thirst_rate = 0.00094

        if player_state["sprinting"]:
            self.hunger -= hunger_rate * 2
            self.thirst -= thirst_rate * 2
        elif player_state["moving"]:
            self.hunger -= hunger_rate
            self.thirst -= thirst_rate
        elif player_state["crouching"]:
            self.hunger -= hunger_rate * 0.5
            self.thirst -= thirst_rate * 0.5

        self.hunger = max(0, self.hunger)
        self.thirst = max(0, self.thirst)

    def eat(self, inventory):
        if "Meat" in inventory and inventory["Meat"] > 0:
            inventory["Meat"] -= 1
            if inventory["Meat"] == 0:
                del inventory["Meat"]
            self.hunger = min(100, self.hunger + 20)
            return True
        return False

    def drink(self, inventory):
        if "Water" in inventory and inventory["Water"] > 0:
            inventory["Water"] -= 1
            if inventory["Water"] == 0:
                del inventory["Water"]
            self.thirst = min(100, self.thirst + 30)
            return True
        return False

    def draw(self, screen):
        bar_x = 20
        bar_y = 20
        bar_width = 200
        bar_height = 22
        spacing = 12

        font = pygame.font.Font("freesansbold.ttf", 18)

        def draw_bar(label, value, y_offset, color):
            outer_rect = pygame.Rect(bar_x - 4, bar_y + y_offset - 4, bar_width + 8, bar_height + 8)
            bg_rect = pygame.Rect(bar_x, bar_y + y_offset, bar_width, bar_height)
            fill_width = int((value / 100) * bar_width)
            fill_rect = pygame.Rect(bar_x, bar_y + y_offset, fill_width, bar_height)

            pygame.draw.rect(screen, (20, 20, 20), outer_rect, border_radius=6)
            pygame.draw.rect(screen, (40, 40, 40), bg_rect, border_radius=4)
            pygame.draw.rect(screen, color, fill_rect, border_radius=4)

            label_surface = font.render(f"{label}: {int(value)}", True, (240, 240, 240))
            screen.blit(label_surface, (bar_x + bar_width + 16, bar_y + y_offset + 2))

        draw_bar("Hunger", self.hunger, 0, (200, 50, 50))
        draw_bar("Thirst", self.thirst, bar_height + spacing, (50, 120, 255))
