import random
import pygame
from rocks import Rock
from cow import Cow
from water_tile import WaterTile
from camp import Camp

def spawn_lakes(num, size, lakes, PLAYER_SAFE_ZONE, MAP_WIDTH, MAP_HEIGHT, GRID_SIZE):
    for _ in range(num):
        base_x = random.randint(100, MAP_WIDTH - 100)
        base_y = random.randint(100, MAP_HEIGHT - 100)
        lake_tiles, collides = [], False
        for i in range(size):
            for j in range(size):
                dist = abs(size // 2 - i) + abs(size // 2 - j)
                if random.random() < 1 - dist * 0.2:
                    tx, ty = base_x + i * GRID_SIZE, base_y + j * GRID_SIZE
                    rect = pygame.Rect(tx, ty, GRID_SIZE, GRID_SIZE)
                    if PLAYER_SAFE_ZONE.colliderect(rect):
                        collides = True
                    lake_tiles.append(WaterTile(tx, ty))
        if not collides and lake_tiles:
            lakes.append(lake_tiles)

def spawn_rocks(n, rocks, occupied_tiles, PLAYER_SAFE_ZONE, MAP_WIDTH, MAP_HEIGHT, GRID_SIZE, rock_images):
    for _ in range(n):
        x, y = random.randint(0, MAP_WIDTH // GRID_SIZE) * GRID_SIZE, random.randint(0, MAP_HEIGHT // GRID_SIZE) * GRID_SIZE
        if (x, y) in occupied_tiles or PLAYER_SAFE_ZONE.collidepoint(x, y):
            continue
        rocks.append(Rock(x, y, random.choice(rock_images)))
        occupied_tiles.add((x, y))

def spawn_items(n, items, occupied_tiles, PLAYER_SAFE_ZONE, MAP_WIDTH, MAP_HEIGHT, GRID_SIZE):
    for _ in range(n):
        x = random.randint(50, MAP_WIDTH - 50)
        y = random.randint(50, MAP_HEIGHT - 50)
        x = (x // GRID_SIZE) * GRID_SIZE
        y = (y // GRID_SIZE) * GRID_SIZE
        if (x, y) in occupied_tiles or PLAYER_SAFE_ZONE.collidepoint(x, y):
            continue
        x += random.uniform(1, 30)
        y += random.uniform(1, 30)
        items.append({"type": "Wood", "x": x, "y": y})
        occupied_tiles.add((x, y))

def spawn_cows(n, cows, MAP_WIDTH, MAP_HEIGHT, cow_image):
    for _ in range(n):
        cows.append(Cow(random.randint(100, MAP_WIDTH - 100), random.randint(100, MAP_HEIGHT - 100), cow_image))

def spawn_camps(n, camps, PLAYER_SAFE_ZONE, MAP_WIDTH, MAP_HEIGHT, GRID_SIZE):
    tries = 0
    while len(camps) < n and tries < 500:
        x = random.randint(0, (MAP_WIDTH - GRID_SIZE * 2) // GRID_SIZE) * GRID_SIZE
        y = random.randint(0, (MAP_HEIGHT - GRID_SIZE * 2) // GRID_SIZE) * GRID_SIZE
        rect = pygame.Rect(x, y, GRID_SIZE * 2, GRID_SIZE * 2)
        if PLAYER_SAFE_ZONE.colliderect(rect):
            continue
        if any(c.rect.colliderect(rect.inflate(256, 256)) for c in camps):
            continue
        camps.append(Camp(x, y))
        tries += 1
