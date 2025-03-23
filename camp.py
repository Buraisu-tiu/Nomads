import pygame
import random

GRID_SIZE = 64

class Camp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = GRID_SIZE * 2
        self.height = GRID_SIZE * 2
        self.rect = pygame.Rect(x, y, self.width, self.height)

        self.chest_rect = pygame.Rect(x + GRID_SIZE // 2, y + GRID_SIZE, GRID_SIZE, GRID_SIZE)
        self.is_open = False
        self.selected_index = 0
        self.cursor_timer = 0

        # Now using slot-style chest inventory
        self.inventory = self.generate_loot()

    def generate_loot(self):
        # Generate list of slot dictionaries like: {"item": "Stone", "count": 1}
        return [{"item": random.choice(["Plank", "Water", "Meat", "Stone", "Leather"]), "count": random.randint(1, 3)} 
                for _ in range(random.randint(2, 6))]

    def draw(self, screen, camera_x, camera_y):
        # Camp base
        pygame.draw.rect(screen, (160, 130, 100), (self.x - camera_x, self.y - camera_y, self.width, self.height))

        # Tent
        pygame.draw.polygon(screen, (180, 80, 60), [
            (self.x - camera_x + 10, self.y - camera_y + 52),
            (self.x - camera_x + 32, self.y - camera_y + 10),
            (self.x - camera_x + 54, self.y - camera_y + 52)
        ])

        # Crate
        pygame.draw.rect(screen, (139, 90, 30), (self.x + GRID_SIZE - camera_x + 4, self.y - camera_y + 4, GRID_SIZE - 8, GRID_SIZE - 8))

        # Chest
        chest_color = (184, 134, 11) if not self.is_open else (110, 90, 60)
        pygame.draw.rect(screen, chest_color, (self.chest_rect.x - camera_x, self.chest_rect.y - camera_y, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, (0, 0, 0), (self.chest_rect.x - camera_x, self.chest_rect.y - camera_y, GRID_SIZE, GRID_SIZE), 2)

    def open_if_hovered(self, cursor_rect, pressed_e):
        if self.chest_rect.colliderect(cursor_rect) and pressed_e:
            self.is_open = True
            return True
        return False

    def handle_input(self, keys, pressed_e, player_inventory):
        if not self.is_open or not self.inventory:
            return

        self.cursor_timer += 1
        if self.cursor_timer > 5:
            if keys[pygame.K_RIGHT]:
                self.selected_index = (self.selected_index + 1) % len(self.inventory)
                self.cursor_timer = 0
            elif keys[pygame.K_LEFT]:
                self.selected_index = (self.selected_index - 1) % len(self.inventory)
                self.cursor_timer = 0

        if pressed_e:
            if 0 <= self.selected_index < len(self.inventory):
                chest_item = self.inventory[self.selected_index]
                item_name = chest_item["item"]

                # Try to stack with same item
                for slot in player_inventory:
                    if slot and slot["item"] == item_name:
                        slot["count"] += 1
                        chest_item["count"] -= 1
                        break
                else:
                    # Try to place in an empty slot
                    for i in range(len(player_inventory)):
                        if player_inventory[i] is None:
                            player_inventory[i] = {"item": item_name, "count": 1}
                            chest_item["count"] -= 1
                            break
                    else:
                        print("Inventory full!")

                # Remove chest item if depleted
                if chest_item["count"] <= 0:
                    self.inventory.pop(self.selected_index)
                    if self.selected_index >= len(self.inventory):
                        self.selected_index = max(0, len(self.inventory) - 1)

    def draw_chest_ui(self, screen, ITEM_TYPES):
        if not self.is_open:
            return

        panel_width = 360
        panel_height = 110
        panel_x = screen.get_width() - panel_width - 30
        panel_y = 110

        pygame.draw.rect(screen, (35, 25, 15), (panel_x, panel_y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(screen, (90, 70, 50), (panel_x, panel_y, panel_width, panel_height), 3, border_radius=10)

        font = pygame.font.Font(None, 30)

        for i, slot in enumerate(self.inventory):
            item_x = panel_x + 20 + i * 60
            item_y = panel_y + 25

            item_name = slot["item"]
            count = slot["count"]

            # Icon
            if item_name == "Water":
                pygame.draw.rect(screen, (50, 143, 168), (item_x, item_y, 40, 40))
            else:
                screen.blit(ITEM_TYPES[item_name], (item_x, item_y))

            # Count
            if count > 1:
                count_text = font.render(str(count), True, (255, 255, 255))
                screen.blit(count_text, (item_x + 24, item_y + 24))

            # Highlight selected
            if i == self.selected_index:
                pygame.draw.rect(screen, (255, 255, 255), (item_x - 4, item_y - 4, 48, 48), 2)

        # Title
        title = font.render("Chest", True, (255, 255, 255))
        screen.blit(title, (panel_x + 10, panel_y - 28))
