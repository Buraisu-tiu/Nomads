from save_load import save_game, load_game

def initialize_game_state(rock_images, cow_image, MAP_WIDTH, MAP_HEIGHT, GRID_SIZE, PLAYER_SAFE_ZONE):
    saved = load_game(rock_images, cow_image)
    if saved:
        return saved
    else:
        return {
            "player": {"x": MAP_WIDTH // 2, "y": MAP_HEIGHT // 2},
            "inventory_slots": [None] * 24,
            "hotbar_slots": [None] * 8,
            "rocks": [],
            "items": [],
            "campfires": [],
            "lakes": [],
            "camps": [],
            "cows": [],
            "time_of_day": 0,
            "hunger": 100,
            "thirst": 100,
        }

def inventory_to_dict(slots):
    d = {}
    for slot in slots:
        if slot:
            item = slot["item"]
            d[item] = d.get(item, 0) + slot["count"]
    return d

def dict_to_inventory(data, slots):
    for i in range(len(slots)):
        slots[i] = None
    i = 0
    for item, count in data.items():
        if i < len(slots):
            slots[i] = {"item": item, "count": count}
            i += 1
