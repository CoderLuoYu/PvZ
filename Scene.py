import Constants
import pygame.image
from image_loader import ImageLoader


class Scene:
    def __init__(self):
        # self.scene_image = pygame.images.load(Constants.DAYTIME).convert_alpha()
        # self.card_slot = pygame.images.load(Constants.CARD_SLOT).convert_alpha()
        self.image = ImageLoader()
        self.scene_image = self.image.load_image("白天", Constants.DAYTIME)
        self.card_slot = self.image.load_image("卡槽", Constants.CARD_SLOT)
        self.x = 0
        self.pause_time = 0
        self.state = "right"

    def update_state(self):
        """更新状态"""
        if self.state == "right" and self.x == 498:
            self.x = 500
        elif self.state == "right" and self.x == 500:
            self.state = "choose_botany"
        elif self.state == "choose_botany" and self.x == 150:
            self.state = "end"

    def update_rect(self):
        """更新矩形区域"""
        if self.state == "right" and self.x < 500:
            self.x += 3
        elif self.state == "choose_botany":
            self.x -= 2

    def draw(self, window):
        """绘制"""
        if self.state == "right" or self.state == "lift":
            window.blit(self.scene_image, (0, 0), (self.x, 0, Constants.GAME_WINDOW_WIDTH, Constants.GAME_WINDOW_HEIGHT))
        elif self.state == "choose_botany":
            window.blit(self.scene_image, (0, 0), (self.x, 0, Constants.GAME_WINDOW_WIDTH, Constants.GAME_WINDOW_HEIGHT))
            window.blit(self.card_slot, (0, 0))
