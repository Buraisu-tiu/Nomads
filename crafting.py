import pygame

# 🎨 Colors
PANEL_BG_COLOR = (111, 78, 55)        # Soft chocolate brown
PANEL_BORDER_COLOR = (77, 51, 38)     # Darker border
ITEM_BG = (139, 101, 75)              # Button base
ITEM_HOVER = (160, 120, 90)           # On hover
TEXT_COLOR = (255, 255, 240)          # Cream text
TEXT_SUB_COLOR = (210, 190, 170)      # Recipe text

class CraftingSystem:
    def __init__(self):
        self.crafting_open = False
        self.selected_item = None
        self.opacity = 0  # For fade-in
        self.max_opacity = 200

        # 📦 Crafting Recipes
        self.recipes = {
            "Plank": {"Wood": 2},
            "Wooden Pickaxe": {"Plank": 5},
            "Stone Sword": {"Plank": 2, "Stone": 3},
            "Campfire": {"Wood": 4, "Stone": 3},
        }

        # 📐 UI Layout
        self.panel_width = 280
        self.panel_height = 350
        self.slot_height = 60
        self.padding = 12
        self.right_offset = 50  # Distance from right edge
        self.craft_buttons = []

    def toggle(self):
        """Open/close the menu and reset fade."""
        if not self.crafting_open:
            self.opacity = 0
        self.crafting_open = not self.crafting_open
        
    def can_craft(self, output_name, inventory_dict):
        recipe = self.get_recipe(output_name)
        if not recipe:
            return False

        for material, amt in recipe["ingredients"].items():
            if inventory_dict.get(material, 0) < amt:
                return False
        return True


    def craft_item(self, recipe, inventory_slots):
        # 🧹 Remove ingredients
        for material, amt in recipe["ingredients"].items():
            remaining = amt
            for slot in inventory_slots:
                if slot and slot["item"] == material:
                    if slot["count"] > remaining:
                        slot["count"] -= remaining
                        remaining = 0
                        break
                    else:
                        remaining -= slot["count"]
                        slot["count"] = 0  # used up

            # Cleanup empty slots
            for i in range(len(inventory_slots)):
                if inventory_slots[i] and inventory_slots[i]["count"] == 0:
                    inventory_slots[i] = None

        # ➕ Add crafted item to inventory
        crafted_item = recipe["output"]
        self.add_to_inventory(inventory_slots, crafted_item)
        print(f"Crafted {crafted_item}!")


    def handle_mouse_click(self, mouse_pos, inventory_slots):
        inventory_dict = {}
        for slot in inventory_slots:
            if slot:
                item = slot["item"]
                count = slot["count"]
                inventory_dict[item] = inventory_dict.get(item, 0) + count

        for i, recipe in enumerate(self.recipes):
            if self.is_over_button(mouse_pos, i):
                if self.can_craft(recipe["output"], inventory_dict):
                    self.craft(recipe, inventory_slots)

    def draw(self, screen, inventory):
        if not self.crafting_open:
            return

        # 🧼 Fade-in
        if self.opacity < self.max_opacity:
            self.opacity += 10

        # ✨ Transparent overlay
        alpha_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        alpha_surface.set_alpha(self.opacity)

        # 📦 Panel position (anchored to right)
        panel_x = screen.get_width() - self.panel_width - self.right_offset
        panel_y = 100

        pygame.draw.rect(alpha_surface, PANEL_BORDER_COLOR, (panel_x - 4, panel_y - 4, self.panel_width + 8, self.panel_height + 8))
        pygame.draw.rect(alpha_surface, PANEL_BG_COLOR, (panel_x, panel_y, self.panel_width, self.panel_height))

        # 📜 Draw items
        font = pygame.font.Font(None, 28)
        self.craft_buttons = []

        for i, item in enumerate(self.recipes):
            item_y = panel_y + self.padding + i * (self.slot_height + self.padding)
            item_rect = pygame.Rect(panel_x + self.padding, item_y, self.panel_width - 2 * self.padding, self.slot_height)

            # Hover styling
            if item_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(alpha_surface, ITEM_HOVER, item_rect)
            else:
                pygame.draw.rect(alpha_surface, ITEM_BG, item_rect)

            pygame.draw.rect(alpha_surface, PANEL_BORDER_COLOR, item_rect, 2)

            # Name
            name_text = font.render(item, True, TEXT_COLOR)
            alpha_surface.blit(name_text, (item_rect.x + 10, item_rect.y + 8))

            # Recipe
            recipe_str = ", ".join([f"{mat}x{amt}" for mat, amt in self.recipes[item].items()])
            recipe_text = font.render(recipe_str, True, TEXT_SUB_COLOR)
            alpha_surface.blit(recipe_text, (item_rect.x + 10, item_rect.y + 32))

            self.craft_buttons.append((item_rect, item))

        # ✨ Render the entire thing
        screen.blit(alpha_surface, (0, 0))
