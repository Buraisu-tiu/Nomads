# main.py

import pygame
import random
import os

# --- Imports ---
from minimap import MiniMap
from survival import Survival
from particles import ParticleSystem
from player import Player
from day_night import DayNightCycle
from crafting import CraftingSystem
from rocks import Rock
from cow import Cow
from water_tile import WaterTile
from ui_helpers import draw_inventory, draw_hotbar, draw_dragged_item, draw_grid
from camp import Camp
from campfire import Campfire
from save_load import save_game, load_game

pygame.init()

# --- Display & World ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
MAP_WIDTH, MAP_HEIGHT = 4000, 3000
GRID_SIZE = 64
ITEM_SIZE = 30

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Nomads")



dragged_item = None
dragged_index = None
dragged_from = None  # "inventory" or "hotbar"

# --- Colors ---
DESERT_COLOR = (199, 168, 107)
GRID_COLOR = (0, 0, 0, 25)

# --- Inventory UI Constants (✅ Fixed!) ---
INVENTORY_COLUMNS = 6
INVENTORY_ROWS = 4
INVENTORY_SLOT_SIZE = 75
HOTBAR_SLOTS = 8
selected_hotbar_index = 0


# --- Game State ---
INVENTORY_COLUMNS = 6
INVENTORY_ROWS = 4
HOTBAR_SLOTS = 8

# 24 inventory slots (6 x 4)
inventory_slots = [None] * (INVENTORY_COLUMNS * INVENTORY_ROWS)

# 8 hotbar slots
hotbar_slots = [None] * HOTBAR_SLOTS

inventory_open = False
last_water_pickup_time = 0
WATER_PICKUP_COOLDOWN = 1000  # ms
camera_shake_intensity = 0
camera_shake_duration = 0
chest_e_pressed_last = False
campfires = []
camps = []

PLAYER_SAFE_ZONE = pygame.Rect(MAP_WIDTH // 2 - 64, MAP_HEIGHT // 2 - 64, 128, 128)

# --- Assets ---
ICON_SIZE = 40
def load_icon(name): return pygame.transform.scale(pygame.image.load(name), (ICON_SIZE, ICON_SIZE))

ITEM_TYPES = {
    "Meat": load_icon("meat.png"),
    "Leather": load_icon("leather.png"),
    "Wood": load_icon("wood.png"),
    "Water": None,
    "Plank": pygame.Surface((ICON_SIZE, ICON_SIZE)),
    "Wooden Pickaxe": load_icon("wooden_pickaxe.png"),
    "Stone": pygame.Surface((ICON_SIZE, ICON_SIZE)),
    "Stone Sword": load_icon("sword.png"),
    "Campfire": pygame.Surface((ICON_SIZE, ICON_SIZE))
}

ITEM_TYPES["Plank"].fill((139, 69, 19))
ITEM_TYPES["Stone"].fill((100, 100, 100))
ITEM_TYPES["Campfire"].fill((200, 90, 40))

rock_images = [pygame.transform.scale(pygame.image.load(os.path.join("gray_rock", f"rock{i}.png")), (48, 48)) for i in range(1, 6)]
cow_image = pygame.transform.scale(pygame.image.load("cow.png").convert_alpha(), (64, 64))

# --- Systems ---
player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
minimap = MiniMap(MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
survival = Survival()
particle_system = ParticleSystem()
crafting_system = CraftingSystem()
day_night_cycle = DayNightCycle(30, 15)

# --- World Entities ---
items, rocks, cows, lakes = [], [], [], []
occupied_tiles = set()

# --- Grid Surface ---
def create_grid_surface():
    surf = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)
    dash, space = 10, 6
    for x in range(0, MAP_WIDTH, GRID_SIZE):
        for y in range(0, MAP_HEIGHT, dash + space):
            pygame.draw.line(surf, GRID_COLOR, (x, y), (x, y + dash), 1)
    for y in range(0, MAP_HEIGHT, GRID_SIZE):
        for x in range(0, MAP_WIDTH, dash + space):
            pygame.draw.line(surf, GRID_COLOR, (x, y), (x + dash, y), 1)
    return surf

grid_surface = create_grid_surface()


def inventory_to_dict(inventory_slots):
    """
    Convert slot-based inventory to a dictionary for compatibility.
    Example: [{"item": "Wood", "count": 3}, None, {"item": "Stone", "count": 2}] 
    → {"Wood": 3, "Stone": 2}
    """
    inventory_dict = {}
    for slot in inventory_slots:
        if slot:
            item = slot["item"]
            count = slot["count"]
            inventory_dict[item] = inventory_dict.get(item, 0) + count
    return inventory_dict

def dict_to_inventory(inventory_dict, inventory_slots):
    """
    Update inventory_slots from a dictionary.
    Example: {"Wood": 3, "Stone": 2} 
    Updates: [{"item": "Wood", "count": 3}, {"item": "Stone", "count": 2}, None, ...]
    """
    # Clear all slots
    for i in range(len(inventory_slots)):
        inventory_slots[i] = None

    # Fill slots from the dictionary
    index = 0
    for item, count in inventory_dict.items():
        if index < len(inventory_slots):
            inventory_slots[index] = {"item": item, "count": count}
            index += 1

# ... rest of the code stays the same ...

def add_to_inventory(self, inventory_slots, item_name, amount=1):
    # Try stacking
    for slot in inventory_slots:
        if slot and slot["item"] == item_name:
            slot["count"] += amount
            return

    # Try empty slot
    for i in range(len(inventory_slots)):
        if inventory_slots[i] is None:
            inventory_slots[i] = {"item": item_name, "count": amount}
            return

    print("Inventory full! Couldn't add", item_name)


# --- World Gen ---
def spawn_lakes(num=5, size=4):
    for _ in range(num):
        base_x = random.randint(100, MAP_WIDTH - 100)
        base_y = random.randint(100, MAP_HEIGHT - 100)
        lake_tiles, collides = [], False
        for i in range(size):
            for j in range(size):
                dist = abs(size//2 - i) + abs(size//2 - j)
                if random.random() < 1 - dist * 0.2:
                    tx, ty = base_x + i * GRID_SIZE, base_y + j * GRID_SIZE
                    rect = pygame.Rect(tx, ty, GRID_SIZE, GRID_SIZE)
                    if PLAYER_SAFE_ZONE.colliderect(rect): collides = True
                    lake_tiles.append(WaterTile(tx, ty))
        if not collides and lake_tiles:
            lakes.append(lake_tiles)

def spawn_rocks(n=30):
    for _ in range(n):
        x, y = random.randint(0, MAP_WIDTH // GRID_SIZE) * GRID_SIZE, random.randint(0, MAP_HEIGHT // GRID_SIZE) * GRID_SIZE
        if (x, y) in occupied_tiles or PLAYER_SAFE_ZONE.collidepoint(x, y): continue
        rocks.append(Rock(x, y, random.choice(rock_images)))
        occupied_tiles.add((x, y))

def spawn_items(n=550):
    for _ in range(n):
        x = random.randint(50, MAP_WIDTH - 50)
        y = random.randint(50, MAP_HEIGHT - 50)
        x = (x // GRID_SIZE) * GRID_SIZE
        y = (y // GRID_SIZE) * GRID_SIZE
        if (x, y) in occupied_tiles or PLAYER_SAFE_ZONE.collidepoint(x, y): continue
        x += random.uniform(1, 30)
        y += random.uniform(1, 30)
        items.append({"type": "Wood", "x": x, "y": y})
        occupied_tiles.add((x, y))

def spawn_cows(n=10):
    for _ in range(n):
        cows.append(Cow(random.randint(100, MAP_WIDTH - 100), random.randint(100, MAP_HEIGHT - 100), cow_image))

def spawn_camps(n=6):
    tries = 0
    while len(camps) < n and tries < 500:
        x = random.randint(0, (MAP_WIDTH - GRID_SIZE*2) // GRID_SIZE) * GRID_SIZE
        y = random.randint(0, (MAP_HEIGHT - GRID_SIZE*2) // GRID_SIZE) * GRID_SIZE
        rect = pygame.Rect(x, y, GRID_SIZE * 2, GRID_SIZE * 2)
        if PLAYER_SAFE_ZONE.colliderect(rect): continue
        if any(c.rect.colliderect(rect.inflate(256, 256)) for c in camps): continue
        camps.append(Camp(x, y))
        tries += 1

# --- Load Game ---
saved = load_game(rock_images, cow_image)
if saved:
    player.x, player.y = saved["player"]["x"], saved["player"]["y"]
    player.rect.topleft = (player.x, player.y)
    inventory_slots = saved["inventory_slots"]
    hotbar_slots = saved["hotbar_slots"]
    rocks = saved["rocks"]
    items = saved["items"]
    campfires = saved["campfires"]
    lakes = saved["lakes"]
    camps = saved["camps"]
    cows = saved["cows"]
else:
    spawn_lakes()
    spawn_rocks()
    spawn_items()
    spawn_cows()
    spawn_camps()

# --- Game Loop ---
clock = pygame.time.Clock()
running = True
while running:
    dt = clock.tick(60)
    screen.fill(DESERT_COLOR)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        elif event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_8:
                selected_hotbar_index = event.key - pygame.K_1
            elif event.key == pygame.K_e and not any(c.is_open for c in camps):
                inventory_open = not inventory_open
            elif event.key == pygame.K_c:
                crafting_system.toggle()
            elif event.key == pygame.K_m:
                minimap.toggle_fullscreen()
            elif event.key == pygame.K_h:
                survival.eat(inventory_to_dict(inventory_slots))
            elif event.key == pygame.K_j:
                survival.drink(inventory_to_dict(inventory_slots))
            elif event.key == pygame.K_o:
                save_game(player, inventory_slots, hotbar_slots, rocks, items, campfires, lakes, camps, cows)
                print("saved game")
            elif event.key == pygame.K_ESCAPE:
                inventory_open = False
                for c in camps: c.is_open = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            crafting_system.handle_mouse_click(pygame.mouse.get_pos(), inventory_slots)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()

            if inventory_open:
                # Inventory slots
                for i, slot in enumerate(inventory_slots):
                    row = i // INVENTORY_COLUMNS
                    col = i % INVENTORY_COLUMNS
                    slot_x = 100 + col * INVENTORY_SLOT_SIZE
                    slot_y = 100 + row * INVENTORY_SLOT_SIZE
                    slot_rect = pygame.Rect(slot_x, slot_y, INVENTORY_SLOT_SIZE, INVENTORY_SLOT_SIZE)

                    if slot_rect.collidepoint(mx, my) and slot:
                        dragged_item = slot
                        dragged_index = i
                        dragged_from = "inventory"
                        inventory_slots[i] = None  # Remove temporarily
                        break

            # Hotbar slots
            hotbar_x = SCREEN_WIDTH // 2 - (HOTBAR_SLOTS * INVENTORY_SLOT_SIZE) // 2
            hotbar_y = SCREEN_HEIGHT - 70
            for i, slot in enumerate(hotbar_slots):
                slot_rect = pygame.Rect(hotbar_x + i * INVENTORY_SLOT_SIZE, hotbar_y, INVENTORY_SLOT_SIZE, INVENTORY_SLOT_SIZE)

                if slot_rect.collidepoint(mx, my) and slot:
                    dragged_item = slot
                    dragged_index = i
                    dragged_from = "hotbar"
                    hotbar_slots[i] = None
                    break
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if dragged_item:
                mx, my = pygame.mouse.get_pos()
                dropped = False

                # Drop into inventory
                for i in range(len(inventory_slots)):
                    row = i // INVENTORY_COLUMNS
                    col = i % INVENTORY_COLUMNS
                    slot_x = 100 + col * INVENTORY_SLOT_SIZE
                    slot_y = 100 + row * INVENTORY_SLOT_SIZE
                    slot_rect = pygame.Rect(slot_x, slot_y, INVENTORY_SLOT_SIZE, INVENTORY_SLOT_SIZE)

                    if slot_rect.collidepoint(mx, my):
                        if dragged_from == "inventory":
                            # Swap
                            inventory_slots[dragged_index], inventory_slots[i] = inventory_slots[i], dragged_item
                        elif dragged_from == "hotbar":
                            hotbar_slots[dragged_index], inventory_slots[i] = inventory_slots[i], dragged_item
                        dropped = True
                        break

                # Drop into hotbar
                if not dropped:
                    hotbar_x = SCREEN_WIDTH // 2 - (HOTBAR_SLOTS * INVENTORY_SLOT_SIZE) // 2
                    hotbar_y = SCREEN_HEIGHT - 70
                    for i in range(HOTBAR_SLOTS):
                        slot_rect = pygame.Rect(hotbar_x + i * INVENTORY_SLOT_SIZE, hotbar_y, INVENTORY_SLOT_SIZE, INVENTORY_SLOT_SIZE)

                        if slot_rect.collidepoint(mx, my):
                            if dragged_from == "inventory":
                                inventory_slots[dragged_index] = None
                                hotbar_slots[i] = dragged_item
                            elif dragged_from == "hotbar":
                                hotbar_slots[dragged_index], hotbar_slots[i] = hotbar_slots[i], dragged_item
                            dropped = True
                            break

                # If dropped nowhere, return to original slot
                if not dropped:
                    if dragged_from == "inventory":
                        inventory_slots[dragged_index] = dragged_item
                    elif dragged_from == "hotbar":
                        hotbar_slots[dragged_index] = dragged_item

                # Reset drag state
                dragged_item = None
                dragged_index = None
                dragged_from = None


    # --- Update Player ---
    old_x, old_y = player.x, player.y
    player.update(keys, MAP_WIDTH, MAP_HEIGHT)
    player_rect = pygame.Rect(player.x, player.y, player.rect.width, player.rect.height)

    # --- Collision ---
    for lake in lakes:
        for tile in lake:
            if player_rect.colliderect(tile.rect):
                player.x, player.y = old_x, old_y
                player.rect.topleft = (player.x, player.y)
    for rock in rocks:
        if not rock.mined and rock.blocks_movement(player_rect):
            player.x, player.y = old_x, old_y
            player.rect.topleft = (player.x, player.y)

    # --- Camera ---
    camera_x = max(0, min(player.x - SCREEN_WIDTH // 2, MAP_WIDTH - SCREEN_WIDTH))
    camera_y = max(0, min(player.y - SCREEN_HEIGHT // 2, MAP_HEIGHT - SCREEN_HEIGHT))

    if camera_shake_duration > 0:
        camera_x += random.randint(-int(camera_shake_intensity), int(camera_shake_intensity))
        camera_y += random.randint(-int(camera_shake_intensity), int(camera_shake_intensity))
        camera_shake_duration -= 1
        camera_shake_intensity *= 0.8

    # --- Cursor ---
    offsets = {"up": (0, -GRID_SIZE), "down": (0, GRID_SIZE), "left": (-GRID_SIZE, 0), "right": (GRID_SIZE, 0)}
    dx, dy = offsets.get(player.last_direction, (0, 0))
    cx = (player.x + player.rect.width // 2 + dx) // GRID_SIZE * GRID_SIZE
    cy = (player.y + player.rect.height // 2 + dy) // GRID_SIZE * GRID_SIZE
    cursor_rect = pygame.Rect(cx, cy, GRID_SIZE, GRID_SIZE)

    # --- Interactions ---
    if keys[pygame.K_f] and pygame.time.get_ticks() - last_water_pickup_time > WATER_PICKUP_COOLDOWN:
        for lake in lakes:
            for tile in lake:
                if cursor_rect.colliderect(tile.rect):
                    add_to_inventory("Water")
                    last_water_pickup_time = pygame.time.get_ticks()
                    break

    # Pickup items
    for item in items[:]:
        rect = pygame.Rect(item["x"], item["y"], ITEM_SIZE, ITEM_SIZE)
        if player.rect.colliderect(rect) or (keys[pygame.K_f] and cursor_rect.colliderect(rect)):
            add_to_inventory(item["type"])
            items.remove(item)

    # Rock mining
    selected_slot = hotbar_slots[selected_hotbar_index]
    tool = selected_slot["item"] if selected_slot else None
    if tool == "Wooden Pickaxe" and keys[pygame.K_r]:
        for rock in rocks:
            if rock.mined: continue
            rect = pygame.Rect(rock.x, rock.y, rock.image.get_width(), rock.image.get_height())
            if cursor_rect.colliderect(rect):
                if not hasattr(rock, "mining_start_time"):
                    rock.mining_start_time = pygame.time.get_ticks()
                    camera_shake_duration = 520
                    camera_shake_intensity = 4
                elif pygame.time.get_ticks() - rock.mining_start_time >= 2000:
                    rock.mined = True
                    add_to_inventory("Stone")
                    del rock.mining_start_time
    else:
        for rock in rocks:
            if hasattr(rock, "mining_start_time"):
                del rock.mining_start_time

    # Chest logic
    chest_pressed = keys[pygame.K_e] and not chest_e_pressed_last
    chest_e_pressed_last = keys[pygame.K_e]
    for camp in camps:
        if camp.open_if_hovered(cursor_rect, chest_pressed):
            inventory_open = True
        if camp.is_open:
            camp.handle_input(keys, chest_pressed, inventory_slots)




    # Combat
    if tool == "Stone Sword" and keys[pygame.K_r]:
        for cow in cows[:]:
            if cursor_rect.colliderect(pygame.Rect(cow.x, cow.y, cow.image.get_width(), cow.image.get_height())):
                if cow.take_damage((player.x, player.y)):
                    cows.remove(cow)
                    add_to_inventory("Meat")
                    add_to_inventory("Leather")

    # --- Draw World ---
    for lake in lakes:
        for tile in lake: tile.draw(screen, camera_x, camera_y)

    for rock in rocks:
        rock.draw(screen, camera_x, camera_y)
        if hasattr(rock, "mining_start_time"):
            elapsed = pygame.time.get_ticks() - rock.mining_start_time
            progress = min(elapsed / 2000, 1)
            bar_x = rock.x + rock.image.get_width() // 2 - 20 - camera_x
            bar_y = rock.y - 20 - camera_y
            pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, 40, 8))
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, int(40 * progress), 8))

    for cow in cows:
        cow.wander([r.rect for r in rocks if not r.mined] + [t.rect for lake in lakes for t in lake])
        cow.draw(screen, camera_x, camera_y)

    for item in items:
        ix, iy = item["x"] - camera_x, item["y"] - camera_y
        if item["type"] == "Water":
            pygame.draw.rect(screen, (50, 143, 168), (ix, iy, ITEM_SIZE, ITEM_SIZE))
        else:
            screen.blit(ITEM_TYPES[item["type"]], (ix, iy))

    for camp in camps:
        camp.draw(screen, camera_x, camera_y)
        camp.draw_chest_ui(screen, ITEM_TYPES)

    for fire in campfires:
        if fire.is_burning():
            fire.draw(screen, camera_x, camera_y)

    player.draw(screen, camera_x - 78, camera_y)
    draw_grid(screen, grid_surface, camera_x, camera_y)
    pygame.draw.rect(screen, (255, 255, 255), (cx - camera_x, cy - camera_y, GRID_SIZE, GRID_SIZE), 3)

    draw_inventory(screen, inventory_slots, inventory_open, ITEM_TYPES, dragged_item, dragged_index, dragged_from)
    draw_hotbar(screen, hotbar_slots, ITEM_TYPES, selected_hotbar_index, dragged_item, dragged_index, dragged_from)
    draw_dragged_item(screen, dragged_item, ITEM_TYPES)


    
    if dragged_item:
        mx, my = pygame.mouse.get_pos()
        from main import ITEM_TYPES
        icon = ITEM_TYPES[dragged_item["item"]]
        screen.blit(icon, (mx - 20, my - 20))

    survival.update(player.get_state())
    survival.draw(screen)
    minimap.draw(screen, player.x, player.y, camps=camps, rocks=rocks, water_tiles=lakes, cows=cows)
    crafting_system.draw(screen, inventory_slots)
    day_night_cycle.draw(screen)
    particle_system.update()
    particle_system.draw(screen, camera_x, camera_y)

    pygame.display.update()

pygame.quit()
