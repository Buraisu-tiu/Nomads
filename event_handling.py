import pygame
from save_load import save_game
from crafting import inventory_to_dict  # Import inventory_to_dict

def handle_events(
    event, keys, inventory_open, crafting_system, minimap, survival, inventory_slots,
    hotbar_slots, player, camps, rocks, items, campfires, lakes, cows, day_night_cycle
):
    if event.type == pygame.QUIT:
        return False, inventory_open

    elif event.type == pygame.KEYDOWN:
        if pygame.K_1 <= event.key <= pygame.K_8:
            selected_hotbar_index = event.key - pygame.K_1
        elif event.key == pygame.K_e and not any(c.is_open for c in camps):
            inventory_open = not inventory_open  # Toggle inventory
        elif event.key == pygame.K_c:
            crafting_system.toggle()
        elif event.key == pygame.K_m:
            minimap.toggle_fullscreen()
        elif event.key == pygame.K_h:
            survival.eat(inventory_to_dict(inventory_slots))  # Use imported inventory_to_dict
        elif event.key == pygame.K_j:
            survival.drink(inventory_to_dict(inventory_slots))  # Use imported inventory_to_dict
        elif event.key == pygame.K_o:
            save_game(
                player,
                inventory_slots,
                hotbar_slots,
                rocks,
                items,
                campfires,
                lakes,
                camps,
                cows,
                day_night_cycle.time_of_day,
                survival.hunger,
                survival.thirst,
            )
            print("Game saved.")
        elif event.key == pygame.K_ESCAPE:
            inventory_open = False
            for c in camps:
                c.is_open = False

    return True, inventory_open
