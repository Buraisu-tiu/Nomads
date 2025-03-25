import pygame


def inventory_to_dict(inventory_slots, hotbar_slots=None):
    data = {}
    for slot in (inventory_slots + (hotbar_slots or [])):
        if slot:
            item = slot["item"]
            data[item] = data.get(item, 0) + slot["count"]
    return data

def consolidate_duplicates(inventory_slots, hotbar_slots):
    """Merge duplicate item stacks without reordering or teleporting between inventory/hotbar."""

    all_slots = inventory_slots + hotbar_slots
    seen = {}

    for i, slot in enumerate(all_slots):
        if not slot:
            continue

        item = slot["item"]

        # If this item type has already been seen, merge into the first slot
        if item in seen:
            target_index = seen[item]
            target_slot = all_slots[target_index]
            target_slot["count"] += slot["count"]

            # Clear the current duplicate slot (but don't delete it)
            all_slots[i] = None
        else:
            seen[item] = i  # Mark this as the "main" stack for this item

    # Reassign back to original lists (since we merged them earlier)
    for i in range(len(inventory_slots)):
        inventory_slots[i] = all_slots[i]

    for i in range(len(hotbar_slots)):
        hotbar_slots[i] = all_slots[i + len(inventory_slots)]
    

def add_to_inventory(inventory_slots, item_name, amount=1, hotbar=None):
    """Adds item to inventory or hotbar, stacking if possible, and consolidates after."""
    # Step 1: Stack into existing hotbar slots
    if hotbar:
        for slot in hotbar:
            if slot and slot["item"] == item_name:
                slot["count"] += amount
                break
        else:
            # Step 2: Stack into existing inventory slots
            for slot in inventory_slots:
                if slot and slot["item"] == item_name:
                    slot["count"] += amount
                    break
            else:
                # Step 3: Add to empty hotbar slot
                for i in range(len(hotbar)):
                    if hotbar[i] is None:
                        hotbar[i] = {"item": item_name, "count": amount}
                        break
                else:
                    # Step 4: Add to empty inventory slot
                    for i in range(len(inventory_slots)):
                        if inventory_slots[i] is None:
                            inventory_slots[i] = {"item": item_name, "count": amount}
                            break
                    else:
                        print("Inventory and hotbar full! Could not add", item_name)
                        return
    else:
        # No hotbar given, just do inventory
        for slot in inventory_slots:
            if slot and slot["item"] == item_name:
                slot["count"] += amount
                break
        else:
            for i in range(len(inventory_slots)):
                if inventory_slots[i] is None:
                    inventory_slots[i] = {"item": item_name, "count": amount}
                    break
            else:
                print("Inventory full! Could not add", item_name)
                return

    # ✅ Final Step: Consolidate inventory and hotbar after adding
    if hotbar:
        consolidate_duplicates(inventory_slots, hotbar)

class CraftingSystem:
    def __init__(self):
        self.recipes = {
            "Plank": {"Wood": 2},
            "Wooden Pickaxe": {"Wood": 3, "Plank": 2},
            "Stone Sword": {"Stone": 2, "Plank": 1},
            "Campfire": {"Stone": 4, "Wood": 3},
        }
        self.buttons = []  # Holds crafting button rects
        self.is_open = False
        self.panel_x = 100
        self.panel_y = 100
        self.panel_width = 300
        self.panel_height = 400

    def toggle(self):
        self.is_open = not self.is_open

    def is_over_button(self, mouse_pos, button_index):
        """Check if the mouse is over a specific crafting button."""
        if 0 <= button_index < len(self.buttons):
            return self.buttons[button_index].collidepoint(mouse_pos)
        return False

    def can_craft(self, item_name, inventory_slots, hotbar_slots):
        inventory = inventory_to_dict(inventory_slots, hotbar_slots)
        if item_name not in self.recipes:
            return False
        for material, amount in self.recipes[item_name].items():
            if inventory.get(material, 0) < amount:
                return False
        return True


    def craft_item(self, item_name, inventory_slots, hotbar_slots):
        """
        Craft an item by consuming materials from both inventory and hotbar.
        """
        if not self.can_craft(item_name, inventory_slots, hotbar_slots):
            print(f"Cannot craft {item_name}. Insufficient materials.")
            return False

        # Combine inventory and hotbar into one list for material deduction
        combined_slots = inventory_slots + hotbar_slots

        for material, amount in self.recipes[item_name].items():
            for slot in combined_slots:
                if slot and slot["item"] == material:
                    if slot["count"] >= amount:
                        slot["count"] -= amount
                        if slot["count"] == 0:
                            slot.clear()
                        break
                    else:
                        amount -= slot["count"]
                        slot.clear()

        return item_name



    def handle_mouse_click(self, mouse_pos, inventory_slots, hotbar_slots):
        """
        Handle mouse click for crafting.
        """
        for i, item_name in enumerate(self.recipes.keys()):
            if self.is_over_button(mouse_pos, i):
                if self.can_craft(item_name, inventory_slots, hotbar_slots):
                    crafted_item = self.craft_item(item_name, inventory_slots, hotbar_slots)
                    if crafted_item:
                        print(f"Crafted {crafted_item}!")
                        # Add the crafted item to inventory or hotbar
                        add_to_inventory(inventory_slots, crafted_item, amount=1, hotbar=hotbar_slots)
                else:
                    print(f"Not enough materials to craft {item_name}")


    def draw(self, screen, inventory):
        """Draw the crafting UI."""
        if not self.is_open:
            return

        # Draw crafting panel
        pygame.draw.rect(screen, (50, 50, 50), (self.panel_x, self.panel_y, self.panel_width, self.panel_height))
        pygame.draw.rect(screen, (200, 200, 200), (self.panel_x, self.panel_y, self.panel_width, self.panel_height), 3)

        font = pygame.font.Font(None, 24)
        self.buttons = []
        y_offset = self.panel_y + 50

        for item_name, recipe in self.recipes.items():
            # Draw crafting button background
            button_rect = pygame.Rect(self.panel_x + 20, y_offset, self.panel_width - 40, 40)
            pygame.draw.rect(screen, (80, 80, 80), button_rect)
            pygame.draw.rect(screen, (120, 120, 120), button_rect, 2)
            self.buttons.append(button_rect)

            # Draw item name and recipe
            text = f"{item_name} - {', '.join([f'{v}x {k}' for k, v in recipe.items()])}"
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (self.panel_x + 30, y_offset + 10))

            # Update y_offset for next button
            y_offset += 50
