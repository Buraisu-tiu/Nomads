import json
import os
import random
SAVE_FILE = "savegame.json"

def save_game(player, inventory_slots, hotbar_slots, rocks, items, campfires, lakes, camps, cows):
    def slot_data(slots):
        return [{"item": slot["item"], "count": slot["count"]} if slot else None for slot in slots]

    data = {
        "player": {"x": player.x, "y": player.y},
        "inventory_slots": slot_data(inventory_slots),
        "hotbar_slots": slot_data(hotbar_slots),
        "rocks": [{"x": r.x, "y": r.y, "mined": r.mined} for r in rocks],
        "items": [{"x": i["x"], "y": i["y"], "type": i["type"]} for i in items],
        "campfires": [{"x": cf.x, "y": cf.y} for cf in campfires],
        "lakes": [
            [{"x": tile.x, "y": tile.y} for tile in lake] for lake in lakes
        ],
        "camps": [{"x": c.x, "y": c.y} for c in camps],
        "cows": [{"x": cow.x, "y": cow.y} for cow in cows]
    }

    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_game(rock_images, cow_image):
    if not os.path.exists(SAVE_FILE):
        return None

    with open(SAVE_FILE, "r") as f:
        data = json.load(f)

    from rocks import Rock
    from campfire import Campfire
    from water_tile import WaterTile
    from camp import Camp
    from cow import Cow

    def rebuild_slots(slot_list):
        return [slot if slot else None for slot in slot_list]

    return {
        "player": data["player"],
        "inventory_slots": rebuild_slots(data["inventory_slots"]),
        "hotbar_slots": rebuild_slots(data["hotbar_slots"]),
        "rocks": [Rock(r["x"], r["y"], random.choice(rock_images), mined=r["mined"]) for r in data["rocks"]],
        "items": data["items"],
        "campfires": [Campfire(cf["x"], cf["y"]) for cf in data["campfires"]],
        "lakes": [
            [WaterTile(tile["x"], tile["y"]) for tile in lake] for lake in data.get("lakes", [])
        ],
        "camps": [Camp(c["x"], c["y"]) for c in data.get("camps", [])],
        "cows": [Cow(cow["x"], cow["y"], cow_image) for cow in data.get("cows", [])]
    }
