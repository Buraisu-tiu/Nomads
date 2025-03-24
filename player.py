import pygame

class Player:
    def __init__(self, x, y, scale=2.5):
        """Initialize the player with position, animations, scaling, and movement settings."""
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.base_speed = 3 # Default movement speed
        self.speed = self.base_speed
        self.direction = "right"  # Default direction
        self.frame_index = 0  # Animation frame index
        self.base_animation_speed = 0.1  # Default animation speed
        self.animation_speed = self.base_animation_speed
        self.timer = 0  # Timer for animation updates
        self.scale = scale  # Scale factor for sprites
        self.is_crouching = False  # Track if crouching
        self.last_direction = "down"  # default

        # Load animations
        self.idle_sprites = self.load_sprite_sheet("character/idle.png", num_frames=5)
        self.run_sprites = self.load_sprite_sheet("character/run.png", num_frames=8)

        # Set default animation
        self.current_sprites = self.idle_sprites
        self.sprite_width, self.sprite_height = self.current_sprites[0].get_size()

        # Create a rect for collision & centering
        hitbox_offset_x = 4
        hitbox_offset_y = 2
        hitbox_width = self.sprite_width * 0.1
        hitbox_height = self.sprite_height * 0.6

        self.rect = pygame.Rect(
            self.x + hitbox_offset_x,
            self.y + hitbox_offset_y,
            hitbox_width,
            hitbox_height
        )

        # Store the offset to apply later during movement
        self.hitbox_offset = (hitbox_offset_x, hitbox_offset_y)

    def load_sprite_sheet(self, path, num_frames):
        """Load sprite sheet, extract vertically stacked frames, and scale them up."""
        sheet = pygame.image.load(path).convert_alpha()
        frame_width = sheet.get_width()
        frame_height = sheet.get_height() // num_frames  # Divide height by frame count

        frames = []
        for i in range(num_frames):
            frame = sheet.subsurface((0, i * frame_height, frame_width, frame_height))
            frame = pygame.transform.scale(frame, (int(frame_width * self.scale), int(frame_height * self.scale)))  # Scale up
            frames.append(frame)

        return frames

    def update(self, keys, map_width, map_height):
        """Update player movement, animations, and keep within boundaries."""
        previous_sprites = self.current_sprites  # Store previous animation state

        # Reset velocity & animation speed
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = self.base_speed
        self.animation_speed = self.base_animation_speed
        self.is_crouching = False

        # Sprinting & Crouching
        if keys[pygame.K_LSHIFT]:  # Sprint (Faster movement & animation)
            self.speed = 5
            self.animation_speed = 0.2  # Faster animations when sprinting
        elif keys[pygame.K_LCTRL]:  # Crouch (Slower movement & animation)
            self.speed = 2
            self.animation_speed = 0.05  # Slower animations when crouching
            self.is_crouching = True

        # Arrow Key Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -self.speed
            self.direction = "left"
            self.last_direction = "left"
            self.current_sprites = self.run_sprites
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = self.speed
            self.direction = "right"
            self.last_direction = "right"
            self.current_sprites = self.run_sprites

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.velocity_y = -self.speed
            self.last_direction = "up"
            self.current_sprites = self.run_sprites
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.velocity_y = self.speed
            self.last_direction = "down"
            self.current_sprites = self.run_sprites

        # If not moving, switch to idle animation
        if self.velocity_x == 0 and self.velocity_y == 0:
            self.current_sprites = self.idle_sprites

        # 🔥 Fix: Reset frame index when switching animations
        if self.current_sprites != previous_sprites:
            self.frame_index = 0  

        # Apply movement
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Keep player inside map boundaries
        self.x = max(0, min(self.x, map_width - self.rect.width))
        self.y = max(0, min(self.y, map_height - self.rect.height))

        # Update collision rect position
        self.rect.topleft = (self.x + self.hitbox_offset[0], self.y + self.hitbox_offset[1])


        # Update animation frame
        self.update_animation()

    def update_animation(self):
        """Update the player's animation frame safely."""
        self.timer += self.animation_speed
        if self.timer >= 1:
            self.timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.current_sprites)

    def draw(self, screen, camera_x, camera_y, debug=False):
        """Draw the player at the correct position relative to the camera."""
        sprite = self.current_sprites[int(self.frame_index)]  # Get current frame safely

        # Flip sprite when facing left
        if self.direction == "left":
            sprite = pygame.transform.flip(sprite, True, False)

        # Apply squash effect when crouching
        crouch_offset_y = 0  # Track how much to move down when crouching
        if self.is_crouching:
            sprite = pygame.transform.scale(sprite, (sprite.get_width(), int(sprite.get_height() * 0.75)))  # Shorter sprite
            crouch_offset_y = 10  # Move player down slightly

        # **Fixed centering issue**
        # Base offset to push sprite lower
        sprite_offset_y = -22

        # Directional horizontal offset
        if self.direction == "left":
            sprite_offset_x = 13  # shift more to the left
        else:
            sprite_offset_x = 0  # no offset when facing right

        # Apply centered positioning + offsets
        offset_x = -sprite.get_width() // 1.3 + self.rect.width // 2 + sprite_offset_x
        offset_y = -sprite.get_height() // 4 + self.rect.height // 2 + crouch_offset_y + sprite_offset_y
        # Adjust up/down, move down when crouching
        # Draw shadow
        shadow_width = self.rect.width
        shadow_height = 12
        shadow_x = self.rect.x - camera_x + offset_x + sprite.get_width() // 1.9 - shadow_width // 1.9
        shadow_y = self.rect.y - camera_y + offset_y + sprite.get_height() - 25

        shadow = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 80), shadow.get_rect())
        screen.blit(shadow, (shadow_x, shadow_y))
        screen.blit(sprite, (self.rect.x - camera_x + offset_x, self.rect.y - camera_y + offset_y))

        # Debug: Draw collision box
        if debug:
            pygame.draw.rect(screen, (255, 0, 0), (self.rect.x - camera_x, self.rect.y - camera_y, self.rect.width, self.rect.height), 2)

    def get_current_frame(self):
        """Returns the current animation frame safely."""
        return self.current_sprites[int(self.frame_index)] if self.current_sprites else None
    
    def get_state(self):
        return {
            "sprinting": self.speed >= 6,
            "crouching": self.is_crouching,
            "moving": abs(self.velocity_x) > 0 or abs(self.velocity_y) > 0
        }
