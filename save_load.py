import json
import os
import random
from rocks import Rock
from cow import Cow
from water_tile import WaterTile
from camp import Camp
from campfire import Campfire

SAVE_FILE = "savegame.json"

def save_game(player, inventory_slots, hotbar_slots, rocks, items, campfires, lakes, camps, cows, time_of_day, hunger, thirst):
    data = {
        "player": {
            "x": player.x,
            "y": player.y
        },
        "inventory_slots": inventory_slots,
        "hotbar_slots": hotbar_slots,
        "rocks": [{"x": r.x, "y": r.y, "mined": r.mined} for r in rocks],
        "items": items,
        "campfires": [{"x": cf.x, "y": cf.y} for cf in campfires],
        "lakes": [[{"x": tile.x, "y": tile.y} for tile in lake] for lake in lakes],
        "camps": [{"x": camp.x, "y": camp.y} for camp in camps],
        "cows": [{"x": cow.x, "y": cow.y} for cow in cows],
        "time_of_day": time_of_day,
        "hunger": hunger,
        "thirst": thirst
    }

    with open("savegame.json", "w") as f:
        json.dump(data, f, indent=4)


def load_game(rock_images, cow_image):
    if not os.path.exists(SAVE_FILE):
        return None

    with open(SAVE_FILE, "r") as f:
        data = json.load(f)

    # Reconstruct rocks
    rocks = [Rock(r["x"], r["y"], random.choice(rock_images), mined=r.get("mined", False)) for r in data.get("rocks", [])]

    # Reconstruct cows
    cows = [Cow(c["x"], c["y"], cow_image) for c in data.get("cows", [])]

    # Reconstruct campfires
    campfires = [Campfire(cf["x"], cf["y"]) for cf in data.get("campfires", [])]

    # Reconstruct lakes (2D list of WaterTile objects)
    lakes = []
    for lake_data in data.get("lakes", []):
        lake = [WaterTile(tile["x"], tile["y"]) for tile in lake_data]
        lakes.append(lake)

    # Reconstruct camps
    camps = [Camp(c["x"], c["y"]) for c in data.get("camps", [])]

    return {
        "player": data["player"],
        "inventory_slots": data["inventory_slots"],
        "hotbar_slots": data["hotbar_slots"],
        "rocks": rocks,
        "items": data["items"],
        "campfires": campfires,
        "lakes": lakes,
        "camps": camps,
        "cows": cows,
        "time_of_day": data.get("time_of_day", 0),
        "hunger": data.get("hunger", 100),
        "thirst": data.get("thirst", 100)
    }