import pygame
from image_loader import ImageLoader
import Constants


class Sun(pygame.sprite.Sprite):
    def __init__(self, x, y, end_y):
        super().__init__()
        self.image = ImageLoader()
        self.animation = self.image.load_animation("阳光", f"{Constants.SUN}", 29)
        self.rect = self.animation[0].get_rect()
        self.rect.x = x
        self.rect.y = y
        self.end_y = end_y
        self.landed_time = 0
        self.current_frame_index = -1
        self.delete_flag = False

    def draw(self, window):
        sun_animation = self.animation[self.current_frame_index]
        window.blit(sun_animation, (self.rect.x, self.rect.y))
        if Constants.SUN_COLLISION_BOX:
            pygame.draw.rect(window, (0, 0, 0), self.rect, 2)

    def update(self):
        """移动"""
        # 切换帧
        self.current_frame_index = (self.current_frame_index + 1) % 29
        # 如果阳光还未到达底部
        if self.rect.y < self.end_y:
            # 纵坐标增加
            self.rect.y += 1
        elif self.rect.y == self.end_y:
            self.landed_time = pygame.time.get_ticks()
            self.rect.y += 1

    def delete(self):
        """清除经过一段时间后未收集的阳光"""
        if self.landed_time:
            current_time = pygame.time.get_ticks()
            if current_time - self.landed_time > Constants.SUN_EXIST_TIME:
                self.delete_flag = True


class LawnMower(pygame.sprite.Sprite):
    """小推车"""
    def __init__(self, x, y, row):
        super().__init__()
        self.x, self.y = x, y
        self.image_loader = ImageLoader()
        self.image = self.image_loader.load_animation("小推车", f"{Constants.LAWNMOWER}", 17)
        self.row = row
        self.rect = self.image[0].get_rect()
        self.rect.x = x
        self.rect.y = y
        self.state = "await"
        self.current_frame_index = 0

    def draw(self, window):
        """绘制"""
        if self.state == "await":
            frame = self.image[0]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.LAWNMOWER_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x, self.y, width, height), 2)
            window.blit(self.image[0], (self.x, self.y))
        if self.state == "trigger":
            if Constants.LAWNMOWER_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), self.rect, 2)
            window.blit(self.image[self.current_frame_index], (self.x, self.y))
            self.rect = self.get_rect()

    def update(self, current_time):
        """更新"""
        if self.state == "trigger":
            self.x += 5
            self.current_frame_index = (self.current_frame_index + 1) % 17
            if self.x >= 900:
                self.kill()

    def get_rect(self):
        """获取碰撞箱"""
        frame = self.image[self.current_frame_index]
        width = frame.get_width()
        height = frame.get_height()
        rect = pygame.Rect(self.x, self.y, width, height)
        return rect
