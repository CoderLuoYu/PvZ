import pygame
import Constants
from image_loader import Image


class Menu:
    def __init__(self):
        self.image = Image()
        self.menu = self.image.load_image("主菜单", Constants.MENU)
        self.start_button = self.image.load_image("开始按钮", Constants.START_BUTTON)
        self.start_button_pressed = self.image.load_image("按下后的开始按钮", Constants.START_BUTTON_PRESSED)
        self.level_choose = self.image.load_image("选关界面", Constants.LEVEL_CHOOSE)
        self.level_card = self.image.load_image("选项卡", Constants.LEVEL_CARD)
        self.start_time = 0
        self.framerate = 100
        self.frame_index = 0
        self.level = "menu"

    def start_game(self, window, animation):
        """开始游戏"""
        if self.level == "choose_level" and self.frame_index != 24:
            current_time = pygame.time.get_ticks()
            if current_time - self.start_time > self.framerate * (self.frame_index + 1):
                self.frame_index += 1
            window.blit(animation[self.frame_index], (200, 220))

    def draw(self, window):
        """绘制"""
        if self.level == "menu":
            window.blit(self.menu, (0, 0))
            window.blit(self.start_button, (470, 60))
        elif self.level == "choose_level" and self.frame_index != 24:
            window.blit(self.menu, (0, 0))
            if self.frame_index % 2 == 0:
                window.blit(self.start_button, (470, 60))
            else:
                window.blit(self.start_button_pressed, (470, 73))
        elif self.level == "choose_level" and self.frame_index == 24:
            window.blit(self.level_choose, (0, 0))
            window.blit(self.level_card, (50, 100))
            font = pygame.font.Font(f"{Constants.FONT}", 36, )
            text = font.render("选择关卡", True, (0, 0, 0))
            window.blit(text, (375, 30))

    def is_start_game(self, pos):
        """判断是否开始游戏"""
        x, y = pos
        if self.level == "menu" and 470 <= x <= 801 and 60 <= y <= 220:
            pygame.mixer.music.load(Constants.CLICK_BUTTON)
            pygame.mixer.music.play()
            # pygame.mixer.music.load(Constant.EVIL_LAUGH)
            # pygame.mixer.music.play()
            self.level = "choose_level"
            self.start_time = pygame.time.get_ticks()