# 🌵 Nomads – A Dune-Inspired Survival Game

**Nomads** is a survival sandbox game built with **Python** and **Pygame**.

Set in a massive, sun-scorched desert, you'll gather resources, craft tools, build camps, and fight to survive the heat, the hunger, and the harsh world around you.

---

## 🎮 Features

- 🏜️ Massive desert world (4000x3000 tiles)
- 🌞 Dynamic day-night cycle with lighting
- 🔥 Build camps and place campfires
- 💧 Survival system with hunger and thirst
- 🪓 Gather wood, mine rocks, and hunt cows
- 🧱 Craft items like planks, pickaxes, and swords
- 🎒 Slot-based inventory and hotbar with drag-and-drop
- 📦 Lootable camp chests with storage
- 🗺️ Minimap with fullscreen toggle
- 💾 Full save/load system for your world state

---

## 📦 Requirements

- Python 3.10 or higher
- [pygame-ce](https://pypi.org/project/pygame-ce/)

To install the required library, run:

```bash
pip install pygame-ce
```

---

## 🚀 How to Run the Game

1. Clone or download the project files
2. Open a terminal in the project folder
3. Run the game with:

```bash
python main.py
```

---

## 🕹️ Controls

| Key       | Action                           |
|-----------|----------------------------------|
| ↑ ↓ → ←   | Move around                      |
| E         | Open/close inventory or chest    |
| C         | Toggle crafting menu             |
| F         | Interact (pickup, drink water)   |
| R         | Use equipped tool (mine, attack) |
| 1–8       | Select hotbar slot               |
| H / J     | Eat / Drink                      |
| M         | Toggle minimap                   |
| O         | Save game                        |
| ESC       | Close inventory/camp UI          |

---

## 🧠 Developer Notes

- Inventory is slot-based and supports item stacking
- Crafting removes required resources and adds crafted items
- Camp chests can be looted with stacking and overflow handling
- The game saves the entire world, including:
  - Player position
  - Rocks and mining state
  - Items and dropped loot
  - Lakes, cows, camps, and campfires

This project is great for learning how to build:
- Tile-based open-world systems
- Slot-based inventories and UIs
- Event-based interactions (looting, crafting, etc.)
- Procedural generation and world saving
- Basic entity AI and camera tracking

---

## 🔮 Planned Features

- Cooking system and temperature survival
- Enemies with combat AI
- More advanced crafting and building
- Environmental hazards (storms, heatwaves)
- Multiplayer support (maybe!)

---

## 🙌 Credits & Inspiration

Inspired by survival games like **Don't Starve**, **Stardew Valley**, and **Dune**.  
Developed using [pygame-ce](https://github.com/pygame-community/pygame-ce).  
All pixel art is either custom-made or open-source placeholders.

---

## 🧊 Stay cool, survive the dunes, and thrive like a true Nomad.

---
