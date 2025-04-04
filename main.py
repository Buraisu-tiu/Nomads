import pygame
import random
import os

# --- Imports ---
from minimap import MiniMap
from survival import Survival
from particles import ParticleSystem
from player import Player
from day_night import DayNightCycle
from crafting import CraftingSystem, add_to_inventory
from rocks import Rock
from cow import Cow
from water_tile import WaterTile
from camp import Camp
from campfire import Campfire
from save_load import save_game, load_game
from world_generation import spawn_lakes, spawn_rocks, spawn_items, spawn_cows, spawn_camps
from game_state import initialize_game_state
from event_handling import handle_events
from drawing import draw_game
from ui_helpers import draw_inventory, draw_hotbar, draw_dragged_item, draw_grid

pygame.init()

# --- Display and World Settings ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 900
MAP_WIDTH, MAP_HEIGHT = 4000, 3000
GRID_SIZE = 64
ITEM_SIZE = 30
ICON_SIZE = 40

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Nomads")

# --- Colors ---
DESERT_COLOR = (199, 168, 107)
GRID_COLOR = (0, 0, 0, 25)

# --- UI Constants ---
INVENTORY_COLUMNS = 6
INVENTORY_ROWS = 4
INVENTORY_SLOT_SIZE = 75
HOTBAR_SLOTS = 8
selected_hotbar_index = 0

# --- Inventory State ---
inventory_slots = [None] * (INVENTORY_COLUMNS * INVENTORY_ROWS)
hotbar_slots = [None] * HOTBAR_SLOTS
dragged_item = None
dragged_index = None
dragged_from = None

# --- Game State ---
inventory_open = False
last_water_pickup_time = 0
WATER_PICKUP_COOLDOWN = 1000
camera_shake_intensity = 0
camera_shake_duration = 0
chest_e_pressed_last = False
campfires = []
camps = []

# --- Safe Zone ---
PLAYER_SAFE_ZONE = pygame.Rect(MAP_WIDTH // 2 - 64, MAP_HEIGHT // 2 - 64, 128, 128)

# --- Assets ---
def load_icon(name):
    return pygame.transform.scale(pygame.image.load(name), (ICON_SIZE, ICON_SIZE))

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

items, rocks, cows, lakes = [], [], [], []
occupied_tiles = set()

# --- Grid ---
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

# Initialize game state
game_state = initialize_game_state(rock_images, cow_image, MAP_WIDTH, MAP_HEIGHT, GRID_SIZE, PLAYER_SAFE_ZONE)
player.x, player.y = game_state["player"]["x"], game_state["player"]["y"]
inventory_slots = game_state["inventory_slots"]
hotbar_slots = game_state["hotbar_slots"]
rocks = game_state["rocks"]
items = game_state["items"]
campfires = game_state["campfires"]
lakes = game_state["lakes"]
camps = game_state["camps"]
cows = game_state["cows"]

# Ensure time of day, hunger, and thirst are initialized
day_night_cycle.time_of_day = game_state.get("time_of_day", 0)
survival.hunger = game_state.get("hunger", 100)
survival.thirst = game_state.get("thirst", 100)

# World generation
spawn_lakes(5, 4, lakes, PLAYER_SAFE_ZONE, MAP_WIDTH, MAP_HEIGHT, GRID_SIZE)
spawn_rocks(30, rocks, occupied_tiles, PLAYER_SAFE_ZONE, MAP_WIDTH, MAP_HEIGHT, GRID_SIZE, rock_images)
spawn_items(550, items, occupied_tiles, PLAYER_SAFE_ZONE, MAP_WIDTH, MAP_HEIGHT, GRID_SIZE)
spawn_cows(10, cows, MAP_WIDTH, MAP_HEIGHT, cow_image)
spawn_camps(6, camps, PLAYER_SAFE_ZONE, MAP_WIDTH, MAP_HEIGHT, GRID_SIZE)

# --- Game Loop ---
clock = pygame.time.Clock()
running = True
water_pickup_timer = 0  # Timer for water pickup progress

while running:
    dt = clock.tick(60)
    screen.fill(DESERT_COLOR)
    keys = pygame.key.get_pressed()  # Update keys every frame

    # --- Camera Logic ---
    camera_x = player.rect.centerx - SCREEN_WIDTH // 2
    camera_y = player.rect.centery - SCREEN_HEIGHT // 2

    # Clamp camera to map boundaries
    camera_x = max(0, min(camera_x, MAP_WIDTH - SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, MAP_HEIGHT - SCREEN_HEIGHT))

    # --- Event Handling ---
    for event in pygame.event.get():
        running, inventory_open = handle_events(
            event, keys, inventory_open, crafting_system, minimap, survival,
            inventory_slots, hotbar_slots, player, camps, rocks, items, campfires,
            lakes, cows, day_night_cycle
        )

    # Update player movement
    player.update(keys, MAP_WIDTH, MAP_HEIGHT, rocks, lakes)

    # Update survival stats
    survival.update(player.get_state())

    # Check for item pickups
    for item in items[:]:
        item_rect = pygame.Rect(item["x"], item["y"], ITEM_SIZE, ITEM_SIZE)
        if player.rect.colliderect(item_rect):
            add_to_inventory(inventory_slots, item["type"], hotbar=hotbar_slots)
            items.remove(item)

    # Check for water pickup
    offsets = {"up": (0, -GRID_SIZE), "down": (0, GRID_SIZE), "left": (-GRID_SIZE, 0), "right": (GRID_SIZE, 0)}
    cursor_rect = pygame.Rect(
        (player.rect.centerx + offsets[player.last_direction][0]) // GRID_SIZE * GRID_SIZE,
        (player.rect.centery + offsets[player.last_direction][1]) // GRID_SIZE * GRID_SIZE,
        GRID_SIZE, GRID_SIZE
    )
    is_cursor_over_water = any(
        tile.rect.colliderect(cursor_rect) for lake in lakes for tile in lake
    )

    if keys[pygame.K_f] and is_cursor_over_water:
        water_pickup_timer += dt
        if water_pickup_timer >= 2000:  # 2 seconds to pick up water
            add_to_inventory(inventory_slots, "Water", hotbar=hotbar_slots)
            water_pickup_timer = 0
    else:
        water_pickup_timer = 0

    # --- Drawing ---
    draw_game(
        screen, player, camera_x, camera_y, lakes, rocks, cows, items, camps, campfires,
        inventory_open, inventory_slots, hotbar_slots, dragged_item, dragged_index,
        dragged_from, survival, minimap, crafting_system, day_night_cycle, particle_system,
        ITEM_TYPES, grid_surface
    )

    # Draw cursor in front of the player
    dx, dy = offsets.get(player.last_direction, (0, 0))
    cursor_x = (player.rect.centerx + dx) // GRID_SIZE * GRID_SIZE
    cursor_y = (player.rect.centery + dy) // GRID_SIZE * GRID_SIZE
    pygame.draw.rect(screen, (255, 255, 255), (cursor_x - camera_x, cursor_y - camera_y, GRID_SIZE, GRID_SIZE), 2)

    # Draw water pickup progress bar
    if is_cursor_over_water and water_pickup_timer > 0:
        bar_width = 100
        bar_height = 10
        bar_x = cursor_x - camera_x + GRID_SIZE // 2 - bar_width // 2
        bar_y = cursor_y - camera_y - 20
        progress = min(water_pickup_timer / 2000, 1)  # Progress ratio (0 to 1)

        pygame.draw.rect(screen, (0, 0, 0), (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))  # Border
        pygame.draw.rect(screen, (50, 143, 168), (bar_x, bar_y, int(bar_width * progress), bar_height))  # Fill

    pygame.display.update()

pygame.quit()