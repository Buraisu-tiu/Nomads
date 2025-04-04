import pygame
from ui_helpers import draw_grid, draw_inventory, draw_hotbar  # Import draw_inventory and draw_hotbar

def draw_game(
    screen, player, camera_x, camera_y, lakes, rocks, cows, items, camps, campfires,
    inventory_open, inventory_slots, hotbar_slots, dragged_item, dragged_index,
    dragged_from, survival, minimap, crafting_system, day_night_cycle, particle_system,
    ITEM_TYPES, grid_surface  # Add grid_surface as a parameter
):
    for lake in lakes:
        for tile in lake:
            tile.draw(screen, camera_x, camera_y)

    for rock in rocks:
        rock.draw(screen, camera_x, camera_y)

    for cow in cows:
        cow.draw(screen, camera_x, camera_y)

    for item in items:
        ix, iy = item["x"] - camera_x, item["y"] - camera_y
        if item["type"] == "Water":
            pygame.draw.rect(screen, (50, 143, 168), (ix, iy, 30, 30))
        else:
            screen.blit(ITEM_TYPES[item["type"]], (ix, iy))  # Use ITEM_TYPES to draw items

    for camp in camps:
        camp.draw(screen, camera_x, camera_y)

    player.draw(screen, camera_x, camera_y, debug=True)
    day_night_cycle.draw(screen)

    for fire in campfires:
        if fire.is_burning():
            fire.draw(screen, camera_x, camera_y)

    survival.draw(screen)
    minimap.draw(screen, player.x, player.y, camps=camps, rocks=rocks, water_tiles=lakes, cows=cows)
    crafting_system.draw(screen, inventory_slots)
    particle_system.update()
    particle_system.draw(screen, camera_x, camera_y)

    # Draw grid
    draw_grid(screen, grid_surface, camera_x, camera_y)  # Use imported draw_grid

    # Draw inventory
    draw_inventory(screen, inventory_slots, inventory_open, ITEM_TYPES, dragged_item=dragged_item, dragged_index=dragged_index, dragged_from=dragged_from)

    # Draw hotbar
    draw_hotbar(screen, hotbar_slots, ITEM_TYPES, selected_index=0, dragged_item=dragged_item, dragged_index=dragged_index, dragged_from=dragged_from)
