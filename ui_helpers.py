import pygame

# 🎨 UI Style Constants
INVENTORY_COLOR = (111, 78, 55)         # Panel BG
INVENTORY_BORDER = (77, 51, 38)         # Border
INVENTORY_SLOT_COLOR = (139, 101, 75)   # Slot background
INVENTORY_SLOT_BORDER = (60, 40, 30)    # Slot outline
TEXT_COLOR = (255, 255, 240)            # Text color

# 📏 Layout Constants
INVENTORY_COLUMNS = 6
INVENTORY_ROWS = 4
INVENTORY_SLOT_SIZE = 75
HOTBAR_SLOTS = 8
SLOT_SIZE = 60
ICON_SIZE = 40
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800


def draw_inventory(screen, inventory_slots, open_, ITEM_TYPES, dragged_item=None, dragged_index=None, dragged_from=None):
    if not open_:
        return

    INVENTORY_X = 100
    INVENTORY_Y = 100
    font = pygame.font.Font(None, 30)

    # Draw background and border
    pygame.draw.rect(
        screen,
        INVENTORY_BORDER,
        (INVENTORY_X - 5, INVENTORY_Y - 5,
         INVENTORY_COLUMNS * INVENTORY_SLOT_SIZE + 10,
         INVENTORY_ROWS * INVENTORY_SLOT_SIZE + 10)
    )
    pygame.draw.rect(
        screen,
        INVENTORY_COLOR,
        (INVENTORY_X, INVENTORY_Y,
         INVENTORY_COLUMNS * INVENTORY_SLOT_SIZE,
         INVENTORY_ROWS * INVENTORY_SLOT_SIZE)
    )

    # Draw inventory slots
    for i, slot in enumerate(inventory_slots):
        row = i // INVENTORY_COLUMNS
        col = i % INVENTORY_COLUMNS
        slot_x = INVENTORY_X + col * INVENTORY_SLOT_SIZE
        slot_y = INVENTORY_Y + row * INVENTORY_SLOT_SIZE

        # Slot box
        pygame.draw.rect(screen, INVENTORY_SLOT_COLOR, (slot_x, slot_y, INVENTORY_SLOT_SIZE, INVENTORY_SLOT_SIZE))
        pygame.draw.rect(screen, INVENTORY_SLOT_BORDER, (slot_x, slot_y, INVENTORY_SLOT_SIZE, INVENTORY_SLOT_SIZE), 3)

        # Skip drawing if this is the dragged item
        if dragged_from == "inventory" and dragged_index == i:
            continue

        if slot:
            item_type = slot["item"]
            count = slot["count"]

            # Draw icon
            icon_x = slot_x + 10
            icon_y = slot_y + 10
            if item_type == "Water":
                pygame.draw.rect(screen, (50, 143, 168), (icon_x, icon_y, 40, 40))
            else:
                screen.blit(ITEM_TYPES[item_type], (icon_x, icon_y))

            # Draw count
            if count > 1:
                count_text = font.render(str(count), True, TEXT_COLOR)
                text_rect = count_text.get_rect(bottomright=(slot_x + INVENTORY_SLOT_SIZE - 8, slot_y + INVENTORY_SLOT_SIZE - 8))
                screen.blit(count_text, text_rect)


def draw_hotbar(screen, hotbar_slots, ITEM_TYPES, selected_index=0, dragged_item=None, dragged_index=None, dragged_from=None):
    HOTBAR_X = SCREEN_WIDTH // 2 - (HOTBAR_SLOTS * SLOT_SIZE) // 2
    HOTBAR_Y = SCREEN_HEIGHT - 70
    font = pygame.font.Font(None, 28)

    # Hotbar panel
    pygame.draw.rect(screen, (0, 0, 0), (HOTBAR_X - 4, HOTBAR_Y - 4, HOTBAR_SLOTS * SLOT_SIZE + 8, SLOT_SIZE + 8))
    pygame.draw.rect(screen, INVENTORY_COLOR, (HOTBAR_X, HOTBAR_Y, HOTBAR_SLOTS * SLOT_SIZE, SLOT_SIZE))

    for i in range(HOTBAR_SLOTS):
        slot_x = HOTBAR_X + i * SLOT_SIZE

        # Draw slot border
        pygame.draw.rect(screen, (0, 0, 0), (slot_x, HOTBAR_Y, SLOT_SIZE, SLOT_SIZE), 4)

        # Highlight selected
        if i == selected_index:
            pygame.draw.rect(screen, (255, 255, 255), (slot_x + 2, HOTBAR_Y + 2, SLOT_SIZE - 4, SLOT_SIZE - 4), 2)

        if dragged_from == "hotbar" and dragged_index == i:
            continue

        slot = hotbar_slots[i]
        if slot:
            item_type = slot["item"]
            count = slot["count"]
            icon_x = slot_x + 10
            icon_y = HOTBAR_Y + 10

            # Draw icon
            if item_type == "Water":
                pygame.draw.rect(screen, (50, 143, 168), (icon_x, icon_y, ICON_SIZE - 10, ICON_SIZE - 10))
            else:
                icon = pygame.transform.scale(ITEM_TYPES[item_type], (ICON_SIZE - 10, ICON_SIZE - 10))
                screen.blit(icon, (icon_x, icon_y))

            # Draw count
            if count > 1:
                count_text = font.render(str(count), True, TEXT_COLOR)
                text_rect = count_text.get_rect(bottomright=(slot_x + SLOT_SIZE - 8, HOTBAR_Y + SLOT_SIZE - 8))
                screen.blit(count_text, text_rect)


def draw_dragged_item(screen, dragged_item, ITEM_TYPES):
    if dragged_item:
        mx, my = pygame.mouse.get_pos()
        item_type = dragged_item["item"]
        if item_type == "Water":
            pygame.draw.rect(screen, (50, 143, 168), (mx - 20, my - 20, 40, 40))
        else:
            icon = ITEM_TYPES[item_type]
            screen.blit(icon, (mx - 20, my - 20))


def draw_grid(screen, grid_surface, camera_x, camera_y):
    screen.blit(grid_surface, (-camera_x, -camera_y))
