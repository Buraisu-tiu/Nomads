import pygame
import random
import os

class Rock:
    def __init__(self, x, y, image, **kwargs):
        self.x = x
        self.y = y
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mining_timer = 0
        self.mined = kwargs.get("mined", False)


    def draw(self, screen, camera_x, camera_y):
        if not self.mined:
            screen.blit(self.image, (self.x - camera_x, self.y - camera_y))

    def update(self, dt, is_holding, player_rect, has_pickaxe):
        if self.mined:
            return

        if self.rect.colliderect(player_rect) and is_holding and has_pickaxe:
            self.mining_timer += dt
            if self.mining_timer >= 2000:  # 2 seconds to mine
                self.mined = True
                print("Rock mined!")
        else:
            self.mining_timer = 0

    def blocks_movement(self, player_rect):
        return self.rect.colliderect(player_rect)
