import math

import numpy as np
import pygame
import Constants
from image_loader import ImageLoader


class AttackBotany(pygame.sprite.Sprite):
    def __init__(self, index, name, ability, sun_number, x, y, life, attack_power, attack_interval, attack_range, speed,
                 bullet_count):
        super().__init__()
        # 编号
        self.index = index
        # 名称
        self.name = name
        # 能力
        self.ability = ability
        # 坐标
        self.x, self.y = x, y
        # 种植消耗阳光
        self.sun_number = sun_number
        # 生命值
        self.life = life
        # 攻击力
        self.attack_power = attack_power
        # 攻击频率
        self.attack_interval = attack_interval
        # 攻击范围
        self.attack_range = attack_range
        # 子弹速度
        self.speed = speed
        # 子弹数量
        self.bullet_count = bullet_count
        # 状态
        self.state = "await"
        # 行号
        self.row, self.column = 0, 0

        self.image_loader = ImageLoader()
        """所有植物适用"""
        # 待机动画路径
        self.await_animation_path = None
        # 待机动画
        self.await_animation = []
        # 待机动画帧数
        self.await_frame_count = 0
        # 待机动画帧率
        self.await_frame_rate = 0
        # 待机动画帧索引
        self.await_frame_index = 0
        # 上一次更新帧的时间
        self.last_update_frame_time = None
        """攻击类植物"""
        # 攻击动画路径
        self.attack_animation_path = None
        # 攻击动画
        self.attack_animation = []
        # 攻击动画帧数
        self.attack_frame_count = 0
        # 攻击动画帧率
        self.attack_frame_rate = 0
        # 攻击动画帧索引
        self.attack_frame_index = 0
        # 上一次攻击时间
        self.last_attack_time = None

        # 子弹动画路径
        self.bullet_animation_path = None
        # 子弹动画
        self.bullet_animation = []
        # 子弹动画帧数
        self.bullet_frame_count = 0
        # 子弹动画帧率
        self.bullet_frame_rate = 0
        # 子弹动画帧索引
        self.bullet_frame_index = 0
        """一次性植物"""
        # 爆炸动画路径
        self.explode_animation_path = None
        # 爆炸动画
        self.explode_animation = []
        # 爆炸动画帧数
        self.explode_frame_count = 0
        # 爆炸动画帧率
        self.explode_frame_rate = 0
        # 爆炸时间
        self.explode_time = None
        # 预先计算的帧位置
        self.await_frame_positions = []
        self.attack_frame_positions = []
        # 冷却相关
        self.cooldown_start_time = None
        self.cooldown_duration = 0
        self.cooldown_percentage = 0.0
        self.rect = pygame.Rect(0, 0, 0, 0)

    def draw(self, window):
        """绘制"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 20, self.y - height, width, height), 2)
            window.blit(frame, (self.x - 20, self.y - height))
        elif self.state == "attack":
            frame = self.attack_animation[self.attack_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 20, self.y - height, width, height), 2)
            window.blit(frame, (self.x - 20, self.y - height))

    def update(self, current_time):
        """更新帧"""
        if self.state == "await":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >=\
                    self.await_frame_rate:
                self.await_frame_index = (self.await_frame_index + 1) % self.await_frame_count
                self.last_update_frame_time = current_time
        elif self.state == "attack":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >=\
                    self.attack_frame_rate:
                self.attack_frame_index = (self.attack_frame_index + 1) % self.attack_frame_count
                self.last_update_frame_time = current_time

    def load_animations(self):
        """加载动画"""
        if self.await_animation_path:
            self.await_animation = self.image_loader.load_animation(f"{self.name}待机", self.await_animation_path,
                                                                    self.await_frame_count)
            self.await_frame_positions = self.image_loader.get_location(f"{self.name}待机", self.await_animation_path,
                                                                        self.await_frame_count)
        if self.attack_animation_path:
            self.attack_animation = self.image_loader.load_animation(f"{self.name}攻击", self.attack_animation_path,
                                                                     self.attack_frame_count)
            self.attack_frame_positions = self.image_loader.get_location(f"{self.name}攻击", self.attack_animation_path,
                                                                         self.attack_frame_count)
        if self.bullet_animation_path:
            self.bullet_animation = self.image_loader.load_animation(f"{self.name}子弹", self.bullet_animation_path,
                                                                     self.bullet_frame_count)

    def get_rect(self):
        """获取碰撞箱"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            x, y, width, height = self.await_frame_positions[self.await_frame_index]
        elif self.state == "attack":
            frame = self.attack_animation[self.attack_frame_index]
            x, y, width, height = self.attack_frame_positions[self.attack_frame_index]
        else:
            return pygame.Rect(0, 0, 0, 0)
        rect = frame.get_rect(topleft=(self.x - x, self.y - y))
        return rect

    def start_cooldown(self):
        """植物卡片进入冷却"""
        self.cooldown_start_time = pygame.time.get_ticks()

    def attack(self, current_time):
        """攻击"""
        if self.state == "attack" and self.attack_frame_index == 13:
            if self.last_attack_time is None or current_time - self.last_attack_time > self.attack_interval:
                self.last_attack_time = current_time
                width = self.attack_animation[self.attack_frame_index].get_width()
                height = self.attack_animation[self.attack_frame_index].get_height()
                bullets = []
                for i in range(self.bullet_count):
                    if self.name == "双重射手" or self.name == "机枪射手":
                        bullet = Bullet(self.x + width + i * 30 - 30, self.y - height, self.row, self.speed,
                                        self.attack_power, self.name, self.bullet_animation_path,
                                        self.bullet_frame_count, self.bullet_frame_rate, i)
                    else:
                        bullet = Bullet(self.x + width - 30, self.y - height, self.row, self.speed, self.attack_power,
                                        self.name, self.bullet_animation_path, self.bullet_frame_count,
                                        self.bullet_frame_rate, i)
                    bullets.append(bullet)
                return bullets
            else:
                return None
        else:
            return None


class ProduceBotany(pygame.sprite.Sprite):
    """生产类植物"""
    def __init__(self, index, name, ability, sun_number, x, y, life, summon_count):
        super().__init__()
        # 编号
        self.index = index
        # 名称
        self.name = name
        # 能力
        self.ability = ability
        # 坐标
        self.x, self.y = x, y
        # 种植消耗阳光
        self.sun_number = sun_number
        # 生命值
        self.life = life
        # 状态
        self.state = "await"
        # 行号
        self.row, self.column = 0, 0

        self.image_loader = ImageLoader()
        # 待机动画路径
        self.await_animation_path = None
        # 待机动画
        self.await_animation = []
        # 待机动画帧数
        self.await_frame_count = 0
        # 待机动画帧率
        self.await_frame_rate = 0
        # 待机动画帧索引
        self.await_frame_index = 0
        # 上一次更新帧的时间
        self.last_update_frame_time = None
        # 召唤物动画路径
        self.summon_animation_path = None
        # 召唤物动画
        self.summon_animation = []
        # 召唤物动画帧数
        self.summon_frame_count = 0
        # 召唤物动画帧率
        self.produce_frame_rate = 3000
        # 召唤物动画帧索引
        self.summon_frame_index = 0
        # 召唤物数量
        self.summon_count = summon_count
        # 上一次生产时间
        self.last_produce_time = None
        # 预先计算的帧位置
        self.await_frame_positions = []
        # 冷却相关
        self.cooldown_start_time = None
        self.cooldown_duration = 0
        self.cooldown_percentage = 0.0
        self.rect = self.get_rect()

    def draw(self, window):
        """绘制"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 20, self.y - height, width, height), 2)
            window.blit(frame, (self.x - 20, self.y - height))

    def update(self, current_time):
        """更新帧"""
        if self.state == "await":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >=\
                    self.await_frame_rate:
                self.await_frame_index = (self.await_frame_index + 1) % self.await_frame_count
                self.last_update_frame_time = current_time

    def load_animations(self):
        """加载动画"""
        if self.await_animation_path:
            self.await_animation = self.image_loader.load_animation(f"{self.name}待机", self.await_animation_path,
                                                                    self.await_frame_count)
            self.await_frame_positions = self.image_loader.get_location(f"{self.name}待机", self.await_animation_path,
                                                                        self.await_frame_count)
        if self.summon_animation_path:
            self.summon_animation = self.image_loader.load_animation(f"{self.name}召唤物", self.summon_animation_path,
                                                                     self.summon_frame_count)

    def produce(self, current_time):
        """生产"""
        if self.last_produce_time:
            if current_time - self.last_produce_time >= self.produce_frame_rate:
                summon = Summon(self.x, self.y, self.name, self.summon_animation_path, self.summon_frame_count)
                self.last_produce_time = current_time
                return summon
            else:
                return None
        else:
            self.last_produce_time = current_time
            return None

    def get_rect(self):
        """获取碰撞箱"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            x, y, width, height = self.await_frame_positions[self.await_frame_index]
        else:
            return pygame.Rect(0, 0, 0, 0)
        rect = frame.get_rect(topleft=(self.x - x, self.y - y))
        return rect


class ProtectBotany(pygame.sprite.Sprite):
    """防御类植物"""
    def __init__(self, index, name, ability, sun_number, x, y, life):
        super().__init__()
        # 编号
        self.index = index
        # 名称
        self.name = name
        # 能力
        self.ability = ability
        # 种植消耗阳光
        self.sun_number = sun_number
        # 坐标
        self.x, self.y = x, y
        # 生命值
        self.life = life
        # 状态
        self.state = "await"
        # 行号
        self.row, self.column = 0, 0

        self.image_loader = ImageLoader()
        # 待机动画路径
        self.await_animation_path = None
        # 待机动画
        self.await_animation = []
        # 待机动画帧数
        self.await_frame_count = 0
        # 待机动画帧率
        self.await_frame_rate = 0
        # 待机动画帧索引
        self.await_frame_index = 0
        # 上一次更新帧的时间
        self.last_update_frame_time = None
        # 保护动画路径
        self.protect_animation_path = None
        # 保护动画
        self.protect_animation = []
        # 保护动画帧数
        self.protect_frame_count = 0
        # 保护动画帧率
        self.protect_frame_rate = 0
        # 保护动画帧索引
        self.protect_frame_index = 0
        # 预先计算的帧位置
        self.await_frame_positions = []
        # 冷却相关
        self.cooldown_start_time = None
        self.cooldown_duration = 0
        self.cooldown_percentage = 0.0
        self.rect = pygame.Rect(0, 0, 0, 0)

    def draw(self, window):
        """绘制"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 20, self.y - height, width, height), 2)
            window.blit(frame, (self.x - 20, self.y - height))
        elif self.state == "protect":
            frame = self.protect_animation[self.protect_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 20, self.y - height, width, height), 2)
            window.blit(frame, (self.x - 20, self.y - height))

    def load_animations(self):
        """加载动画"""
        if self.await_animation_path:
            self.await_animation = self.image_loader.load_animation(f"{self.name}待机", self.await_animation_path,
                                                                    self.await_frame_count)
            self.await_frame_positions = self.image_loader.get_location(f"{self.name}待机", self.await_animation_path,
                                                                        self.await_frame_count)

    def update(self, current_time):
        """更新帧"""
        if self.state == "await":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >= \
                    self.await_frame_rate:
                self.await_frame_index = (self.await_frame_index + 1) % self.await_frame_count
                self.last_update_frame_time = current_time

    def get_rect(self):
        """获取碰撞箱"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            x, y, width, height = self.await_frame_positions[self.await_frame_index]
        elif self.state == "protect":
            frame = self.protect_animation[self.protect_frame_index]
            x, y, = frame.get_size()
        else:
            return pygame.Rect(0, 0, 0, 0)
        rect = frame.get_rect(topleft=(self.x - x, self.y - y))
        return rect


class AshBotany(pygame.sprite.Sprite):
    """灰烬类植物"""
    def __init__(self, index, name, ability, sun_number, x, y, life, attack_power, attack_range, effect_count):
        super().__init__()
        # 编号
        self.index = index
        # 名称
        self.name = name
        # 能力
        self.ability = ability
        # 种植消耗阳光
        self.sun_number = sun_number
        # 坐标
        self.x, self.y = x, y
        # 生命值
        self.life = life
        # 攻击力
        self.attack_power = attack_power
        # 攻击范围
        self.attack_range = attack_range
        # 效果计数
        self.effect_count = effect_count
        # 状态
        self.state = "await"
        # 行号
        self.row, self.column = 0, 0

        self.image_loader = ImageLoader()
        # 待机动画路径
        self.await_animation_path = None
        # 待机动画
        self.await_animation = []
        # 待机动画帧数
        self.await_frame_count = 0
        # 待机动画帧率
        self.await_frame_rate = 0
        # 待机动画帧索引
        self.await_frame_index = 0
        # 上一次更新帧的时间
        self.last_update_frame_time = None
        # 攻击动画路径
        self.explore_animation_path = None
        # 爆炸动画
        self.explore_animation = []
        # 爆炸动画帧数
        self.explore_frame_count = 0
        # 爆炸动画帧率
        self.explore_frame_rate = 0
        # 爆炸动画帧索引
        self.explore_frame_index = 0
        # 效果动画路径
        self.effect_animation_path = None
        # 效果动画
        self.effect_animation = []
        # 效果动画帧数
        self.effect_frame_count = 0
        # 效果动画帧率
        self.effect_frame_rate = 0
        # 效果动画帧索引
        self.effect_frame_index = 0
        # 预先计算的帧位置
        self.await_frame_positions = []
        self.attack_frame_positions = []
        # 触发时间
        self.trigger_time = None
        # 冷却相关
        self.cooldown_start_time = None
        self.cooldown_duration = 0
        self.cooldown_percentage = 0.0

    def draw(self, window):
        """绘制"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 20, self.y - height, width, height), 2)
            window.blit(frame, (self.x - 20, self.y - height))
        elif self.state == "explore":
            frame = self.explore_animation[self.explore_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 20, self.y - height, width, height), 2)
            window.blit(frame, (self.x - 20, self.y - height))

    def update(self, current_time):
        """更新帧"""
        if self.state == "await":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >= \
                    self.await_frame_rate:
                if self.await_frame_index != self.await_frame_count - 1:
                    self.await_frame_index = (self.await_frame_index + 1) % self.await_frame_count
                    self.last_update_frame_time = current_time
                else:
                    self.state = "explore"
        elif self.state == "explore":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >= \
                    self.explore_frame_rate:
                if self.explore_frame_index != self.explore_frame_count - 1:
                    self.explore_frame_index = (self.explore_frame_index + 1) % self.explore_frame_count
                    self.last_update_frame_time = current_time
                else:
                    self.kill()

    def get_rect(self):
        """获取碰撞箱"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            x, y, width, height = self.await_frame_positions[self.await_frame_index]
        else:
            return pygame.Rect(0, 0, 0, 0)
        rect = frame.get_rect(topleft=(self.x - x, self.y - y))
        return rect

    def load_animations(self):
        """加载动画"""
        if self.await_animation_path:
            self.await_animation = self.image_loader.load_animation(f"{self.name}待机", self.await_animation_path,
                                                                    self.await_frame_count)
            self.await_frame_positions = self.image_loader.get_location(f"{self.name}待机", self.await_animation_path,
                                                                        self.await_frame_count)
        if self.explore_animation_path:
            self.explore_animation = self.image_loader.load_animation(f"{self.name}攻击", self.explore_animation_path,
                                                                      self.explore_frame_count)
            self.attack_frame_positions = self.image_loader.get_location(f"{self.name}攻击", self.explore_animation_path,
                                                                         self.explore_frame_count)


class FunctionalBotany(pygame.sprite.Sprite):
    """功能类植物"""
    def __init__(self, index, name, ability, sun_number, x, y, life):
        super().__init__()
        # 编号
        self.index = index
        # 名称
        self.name = name
        # 能力
        self.ability = ability
        # 种植消耗阳光
        self.sun_number = sun_number
        # 坐标
        self.x, self.y = x, y
        # 生命值
        self.life = life
        # 状态
        self.state = "await"
        # 行号
        self.row, self.column = 0, 0

        self.image_loader = ImageLoader()
        # 待机动画路径
        self.await_animation_path = None
        # 待机动画
        self.await_animation = []
        # 待机动画帧数
        self.await_frame_count = 0
        # 待机动画帧率
        self.await_frame_rate = 0
        # 待机动画帧索引
        self.await_frame_index = 0

        self.crumble_animation_path = None
        # 上一次更新帧的时间
        self.last_update_frame_time = None

    def draw(self, window):
        """绘制"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 20, self.y - height, width, height), 2)
            window.blit(frame, (self.x - 20, self.y - height))

    def load_animations(self):
        """加载动画"""
        if self.await_animation_path:
            self.await_animation = self.image_loader.load_animation(f"{self.name}待机", self.await_animation_path,
                                                                    self.await_frame_count)

    def update(self, current_time):
        """更新帧"""
        if self.state == "await":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >= \
                    self.await_frame_rate:
                self.await_frame_index = (self.await_frame_index + 1) % self.await_frame_count
                self.last_update_frame_time = current_time

    def get_rect(self):
        """获取碰撞箱"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            x, y, = frame.get_size()
        else:
            return pygame.Rect(0, 0, 0, 0)
        rect = frame.get_rect(topleft=(self.x - x, self.y - y))
        return rect


class Peashooter(AttackBotany):
    """豌豆射手"""
    def __init__(self, x, y):
        super().__init__(index=0, name="豌豆射手", ability=["attack"], sun_number=100, x=x, y=y, life=300,
                         attack_power=20, attack_interval=1400, attack_range="前方一行", speed=2.5, bullet_count=1)
        self.await_frame_count = 25
        self.attack_frame_count = 25
        self.await_frame_rate = 100
        self.attack_frame_rate = 100
        self.bullet_frame_count = 1
        self.bullet_frame_rate = 100
        self.await_animation_path = f"{Constants.PEASHOOTER}await"
        self.attack_animation_path = f"{Constants.PEASHOOTER}attack"
        self.bullet_animation_path = f"{Constants.PEASHOOTER}bullet"
        self.cooldown_duration = 7500
        self.load_animations()
        self.rect = self.get_rect()


class Sunflower(ProduceBotany):
    """向日葵"""
    def __init__(self, x, y):
        super().__init__(index=1, name="向日葵", ability=["produce"], sun_number=50, x=x, y=y, life=300, summon_count=1)
        self.await_frame_count = 25
        self.summon_frame_count = 29
        self.await_frame_rate = 100
        self.produce_frame_rate = 24000
        self.await_animation_path = f"{Constants.SUNFLOWER}await"
        self.summon_animation_path = f"{Constants.SUNFLOWER}summon"
        self.cooldown_duration = 7500
        self.load_animations()
        self.rect = self.get_rect()


class CherryBomb(AshBotany):
    """樱桃炸弹"""
    def __init__(self, x, y):
        super().__init__(index=2, name="樱桃炸弹", ability=["ash"], sun_number=150, x=x, y=y, life=300,
                         attack_power=1800, attack_range="半径1.5格", effect_count=1)
        self.await_frame_count = 25
        self.explode_frame_count = 25
        self.await_frame_rate = 100
        self.explode_frame_rate = 100
        self.await_animation_path = f"{Constants.CHERRYBOMB}await"
        self.explode_animation_path = f"{Constants.CHERRYBOMB}explode"
        self.effect_animation_path = f"{Constants.CHERRYBOMB}effect"


class Wallnut(ProtectBotany):
    """坚果"""
    def __init__(self, x, y):
        super().__init__(index=3, name="坚果", ability=["protect"], sun_number=50, x=x, y=y, life=4000)
        self.await_frame_count = 17
        self.await_frame_rate = 100
        self.await_animation_path = f"{Constants.WALLNUT}await"
        self.cooldown_duration = 30000
        self.load_animations()
        self.rect = self.get_rect()

    def draw(self, window):
        """绘制"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 20, self.y - height, width, height), 2)
            window.blit(frame, (self.x - 20, self.y - height))

    def get_rect(self):
        """获取矩形"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            height = frame.get_height()
        else:
            return pygame.Rect(0, 0, 0, 0)
        rect = frame.get_rect(topleft=(self.x - 20, self.y - height))
        return rect


class PotatoMine(AshBotany):
    """土豆地雷"""
    def __init__(self, x, y):
        super().__init__(index=4, name="土豆地雷", ability=["ash"], sun_number=25, x=x, y=y, life=300,
                         attack_power=1800, attack_range="所在格", effect_count=1)
        self.state = "rise"
        self.rise_animation = []
        self.rise_frame_count = 19
        self.rise_frame_rate = 100
        self.rise_frame_index = 0
        self.plant_time = None
        self.rise_time = 15000
        self.await_frame_count = 11
        self.await_frame_rate = 100
        self.effect_frame_count = 1
        self.effect_frame_rate = 100
        self.explore_center = (self.x + 30, self.y - 35)
        self.radius = 42
        self.rise_animation_path = f"{Constants.POTATO_MINE}rise"
        self.await_animation_path = f"{Constants.POTATO_MINE}await"
        self.effect_animation_path = f"{Constants.POTATO_MINE}effect"
        self.cooldown_duration = 7500
        self.load_animations()
        self.rect = self.get_rect()

    def update(self, current_time):
        if self.state == "rise":
            if self.plant_time is not None:
                if current_time - self.plant_time >= self.rise_time:
                    if self.last_update_frame_time is None or current_time - self.last_update_frame_time >= \
                            self.rise_frame_rate:
                        self.rise_frame_index += 1
                        self.last_update_frame_time = current_time
                        if self.rise_frame_index == self.rise_frame_count - 1:
                            self.state = "await"
            else:
                self.plant_time = current_time
        elif self.state == "await":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >= \
                    self.await_frame_rate:
                self.await_frame_index = (self.await_frame_index + 1) % self.await_frame_count
                self.last_update_frame_time = current_time

    def draw(self, window):
        if self.state == "rise":
            frame = self.rise_animation[self.rise_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 10, self.y - height - 20, width, height), 2)
            window.blit(frame, (self.x - 10, self.y - height - 20))
        elif self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 10, self.y - height - 20, width, height), 2)
            window.blit(frame, (self.x - 10, self.y - height - 20))

    def load_animations(self):
        if self.rise_animation_path:
            self.rise_animation = self.image_loader.load_animation("土豆地雷破土", self.rise_animation_path,
                                                                   self.rise_frame_count)
        if self.await_animation_path:
            self.await_animation = self.image_loader.load_animation("土豆雷待机", self.await_animation_path,
                                                                    self.await_frame_count)

    def get_rect(self):
        if self.state == "rise":
            frame = self.rise_animation[self.rise_frame_index]
            width, height = frame.get_size()
            return pygame.Rect(self.x - 10, self.y - height - 20, width, height)
        elif self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            width, height = frame.get_size()
            return pygame.Rect(self.x - 10, self.y - height - 20, width, height)

    def explore(self):
        if self.state == "explore":
            effects = []
            for i in range(self.effect_count):
                effect = Effect(self.x - 40, self.y - 90, self.name, self.attack_power, self.effect_animation_path,
                                self.effect_frame_count, self.effect_frame_rate, self.explore_center, self.radius)
                effects.append(effect)
            self.kill()
            return effects


class SnowPea(AttackBotany):
    """寒冰射手"""
    def __init__(self, x, y):
        super().__init__(index=5, name="寒冰射手", ability=["attack"], sun_number=175, x=x, y=y, life=300,
                         attack_power=20, attack_interval=1400, attack_range="前方一行", speed=2.5, bullet_count=1)
        self.await_frame_count = 25
        self.attack_frame_count = 25
        self.await_frame_rate = 100
        self.attack_frame_rate = 100
        self.bullet_frame_count = 1
        self.bullet_frame_rate = 100
        self.await_animation_path = f"{Constants.SNOW_PEA}await"
        self.attack_animation_path = f"{Constants.SNOW_PEA}attack"
        self.bullet_animation_path = f"{Constants.SNOW_PEA}bullet"
        self.cooldown_duration = 7500
        self.load_animations()
        self.rect = self.get_rect()


class Chomper(AttackBotany):
    """大嘴花"""
    def __init__(self, x, y):
        super().__init__(index=6, name="大嘴花", ability=["attack"], sun_number=150, x=x, y=y, life=300,
                         attack_power=1800, attack_interval=1400, attack_range="前方1.5格", speed=None, bullet_count=None)
        self.await_frame_count = 25
        self.attack_frame_count = 25
        self.await_frame_rate = 100
        self.attack_frame_rate = 100
        self.await_animation_path = f"{Constants.CHOMPER}await"
        self.attack_animation_path = f"{Constants.CHOMPER}attack"
        self.chew_animation = []
        self.chew_animation_path = f"{Constants.CHOMPER}chew"
        self.chew_frame_count = 16
        self.chew_frame_rate = 100
        self.chew_frame_index = 0
        self.chew_start_time = None
        self.chew_time = 42000
        self.swallow_animation = []
        self.swallow_animation_path = f"{Constants.CHOMPER}swallow"
        self.swallow_frame_count = 28
        self.swallow_frame_rate = 100
        self.swallow_frame_index = 0
        self.cooldown_duration = 7500
        self.load_animations()
        self.rect = self.get_rect()

    def draw(self, window):
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 20, self.y - height, width, height), 2)
            window.blit(frame, (self.x - 20, self.y - height))
        elif self.state == "attack":
            frame = self.attack_animation[self.attack_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 20, self.y - height, width, height), 2)
            window.blit(frame, (self.x - 20, self.y - height))
        elif self.state == "chew":
            frame = self.chew_animation[self.chew_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 20, self.y - height, width, height), 2)
            window.blit(frame, (self.x - 20, self.y - height))
        elif self.state == "swallow":
            frame = self.swallow_animation[self.swallow_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 20, self.y - height, width, height), 2)
            window.blit(frame, (self.x - 20, self.y - height))
            if self.swallow_frame_index == self.swallow_frame_count - 1:
                self.state = "await"
                self.swallow_frame_index = 0
        self.rect = self.get_rect()

    def update(self, current_time):
        if self.state == "await":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >=\
                    self.await_frame_rate:
                self.await_frame_index = (self.await_frame_index + 1) % self.await_frame_count
                self.last_update_frame_time = current_time
        elif self.state == "attack":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >=\
                    self.attack_frame_rate:
                self.attack_frame_index = (self.attack_frame_index + 1) % self.attack_frame_count
                self.last_update_frame_time = current_time
        elif self.state == "chew":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >=\
                    self.chew_frame_rate:
                self.chew_frame_index = (self.chew_frame_index + 1) % self.chew_frame_count
                self.last_update_frame_time = current_time
                if self.chew_start_time is None:
                    self.chew_start_time = current_time
                if current_time - self.chew_start_time >= self.chew_time:
                    self.state = "swallow"
                    self.chew_start_time = None
        elif self.state == "swallow":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >=\
                    self.swallow_frame_rate:
                self.swallow_frame_index = (self.swallow_frame_index + 1) % self.swallow_frame_count
                self.last_update_frame_time = current_time

    def attack(self, current_time):
        if self.state == "attack" and self.attack_frame_index == self.attack_frame_count - 1:
            self.state = "chew"

    def load_animations(self):
        """加载动画"""
        if self.await_animation_path:
            self.await_animation = self.image_loader.load_animation(f"{self.name}待机", self.await_animation_path,
                                                                    self.await_frame_count)
        if self.attack_animation_path:
            self.attack_animation = self.image_loader.load_animation(f"{self.name}攻击", self.attack_animation_path,
                                                                     self.attack_frame_count)
        if self.chew_animation_path:
            self.chew_animation = self.image_loader.load_animation(f"{self.name}咀嚼", self.chew_animation_path,
                                                                   self.chew_frame_count)
        if self.swallow_animation_path:
            self.swallow_animation = self.image_loader.load_animation(f"{self.name}吞咽", self.swallow_animation_path,
                                                                      self.swallow_frame_count)

    def get_rect(self):
        """获取碰撞箱"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            height = frame.get_height()
            rect = frame.get_rect(topleft=(self.x - 20, self.y - height))
        elif self.state == "attack":
            frame = self.attack_animation[self.attack_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            rect = pygame.Rect(self.x - 20, self.y - height, width + 20, height)
        elif self.state == "chew":
            frame = self.chew_animation[self.chew_frame_index]
            height = frame.get_height()
            rect = frame.get_rect(topleft=(self.x - 20, self.y - height))
        elif self.state == "swallow":
            frame = self.swallow_animation[self.swallow_frame_index]
            height = frame.get_height()
            rect = frame.get_rect(topleft=(self.x - 20, self.y - height))
        else:
            return pygame.Rect(0, 0, 0, 0)
        return rect


class Repeater(AttackBotany):
    """双重射手"""
    def __init__(self, x, y):
        super().__init__(index=7, name="双重射手", ability=["attack"], sun_number=200, x=x, y=y, life=300,
                         attack_power=20, attack_interval=1400, attack_range="前方一行", speed=2.5, bullet_count=2)
        self.await_frame_count = 25
        self.attack_frame_count = 25
        self.await_frame_rate = 100
        self.attack_frame_rate = 100
        self.bullet_frame_count = 1
        self.bullet_frame_rate = 100
        self.await_animation_path = f"{Constants.REPEATER}await"
        self.attack_animation_path = f"{Constants.REPEATER}attack"
        self.bullet_animation_path = f"{Constants.REPEATER}bullet"
        self.cooldown_duration = 7500
        self.load_animations()
        self.rect = self.get_rect()


class Puffshroom(AttackBotany):
    """小喷菇"""
    def __init__(self, x, y):
        super().__init__(index=8, name="小喷菇", ability=["shroom"], sun_number=50, x=x, y=y, life=300,
                         attack_power=0, attack_interval=0, attack_range="自身", speed=0, bullet_count=0)
        self.state = "sleep"
        self.sleep_animation = []
        self.sleep_frame_positions = []
        self.sleep_frame_index = 0


class Sunshroom(ProduceBotany):
    """阳光菇"""
    def __init__(self, x, y):
        super().__init__(index=9, name="阳光菇", ability=["shroom"], sun_number=50, x=x, y=y, life=300, summon_count=1)
        self.state = "sleep"
        self.sleep_animation = []
        self.sleep_frame_positions = []
        self.sleep_frame_index = 0
        self.sleep_frame_count = 17


class Fumeshroom(AttackBotany):
    """大喷菇"""
    def __init__(self, x, y):
        super().__init__(index=10, name="大喷菇", ability=["attack", "shroom"], sun_number=75, x=x, y=y, life=300,
                         attack_power=20, attack_interval=1400, attack_range="前方4格", speed=0, bullet_count=1)
        self.state = "sleep"
        self.sleep_animation = []
        self.sleep_frame_positions = []
        self.sleep_frame_index = 0
        self.sleep_frame_count = 17
        self.sleep_frame_rate = 100
        self.await_frame_count = 17
        self.attack_frame_count = 30
        self.await_frame_rate = 100
        self.attack_frame_rate = 100
        self.bullet_frame_count = 8
        self.bullet_frame_rate = 200
        self.sleep_animation_path = f"{Constants.FUMESHROOM}sleep"
        self.await_animation_path = f"{Constants.FUMESHROOM}await"
        self.attack_animation_path = f"{Constants.FUMESHROOM}attack"
        self.bullet_animation_path = f"{Constants.FUMESHROOM}bullet"
        self.cooldown_duration = 7500
        self.load_animations()
        self.rect = self.get_rect()

    def draw(self, window):
        """绘制"""
        if self.state == "sleep":
            frame = self.sleep_animation[self.sleep_frame_index]
            x, y, width, height = self.sleep_frame_positions[self.sleep_frame_index]
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - x + 20, self.y - y, width, height), 2)
            window.blit(frame, (self.x - x + 20, self.y - y))
        elif self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            x, y, width, height = self.await_frame_positions[self.await_frame_index]
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - x + 20, self.y - y, width, height), 2)
            window.blit(frame, (self.x - x + 20, self.y - y))
        elif self.state == "attack":
            frame = self.attack_animation[self.attack_frame_index]
            x, y, width, height = self.attack_frame_positions[self.attack_frame_index]
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - x + 20, self.y - y, width, height), 2)
            window.blit(frame, (self.x - x + 20, self.y - y))
        self.rect = self.get_rect()

    def attack(self, current_time):
        if self.state == "attack" and self.attack_frame_index == 10:
            bullets = []
            for i in range(self.bullet_count):
                bullet = Bullet(self.x + 65, self.y - 75, self.row, self.speed, self.attack_power, self.name,
                                self.bullet_animation_path, self.bullet_frame_count, self.bullet_frame_rate, i)
                bullets.append(bullet)
                return bullets

    def update(self, current_time):
        if self.state == "sleep":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >=\
                    self.sleep_frame_rate:
                self.sleep_frame_index = (self.sleep_frame_index + 1) % self.sleep_frame_count
                self.last_update_frame_time = current_time
        elif self.state == "await":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >=\
                    self.await_frame_rate:
                self.await_frame_index = (self.await_frame_index + 1) % self.await_frame_count
                self.last_update_frame_time = current_time
        elif self.state == "attack":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >=\
                    self.attack_frame_rate:
                self.attack_frame_index = (self.attack_frame_index + 1) % self.attack_frame_count
                self.last_update_frame_time = current_time

    def load_animations(self):
        if self.sleep_animation_path:
            self.sleep_animation = self.image_loader.load_animation(f"{self.name}睡眠", self.sleep_animation_path,
                                                                    self.sleep_frame_count)
            self.sleep_frame_positions = self.image_loader.get_location(f"{self.name}睡眠", self.sleep_animation_path,
                                                                        self.sleep_frame_count)
        if self.await_animation_path:
            self.await_animation = self.image_loader.load_animation(f"{self.name}待机", self.await_animation_path,
                                                                    self.await_frame_count)
            self.await_frame_positions = self.image_loader.get_location(f"{self.name}待机", self.await_animation_path,
                                                                        self.await_frame_count)
        if self.attack_animation_path:
            self.attack_animation = self.image_loader.load_animation(f"{self.name}攻击", self.attack_animation_path,
                                                                     self.attack_frame_count)
            self.attack_frame_positions = self.image_loader.get_location(f"{self.name}攻击", self.attack_animation_path,
                                                                         self.attack_frame_count)
        if self.bullet_animation_path:
            self.bullet_animation = self.image_loader.load_animation(f"{self.name}子弹", self.bullet_animation_path,
                                                                     self.bullet_frame_count)

    def get_rect(self):
        """获取碰撞箱"""
        if self.state == "sleep":
            frame = self.sleep_animation[self.sleep_frame_index]
            x, y, width, height = self.sleep_frame_positions[self.sleep_frame_index]
        elif self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            x, y, width, height = self.await_frame_positions[self.await_frame_index]
        elif self.state == "attack":
            frame = self.attack_animation[self.attack_frame_index]
            x, y, width, height = self.attack_frame_positions[self.attack_frame_index]
        else:
            return pygame.Rect(0, 0, 0, 0)
        rect = frame.get_rect(topleft=(self.x - x + 20, self.y - y))
        return rect


class BraveBuster(FunctionalBotany):
    """咬咬碑"""
    def __init__(self, x, y):
        super().__init__(index=11, name="咬咬碑", ability=["attack"], sun_number=125, x=x, y=y, life=300)


class HypnoShroom(FunctionalBotany):
    """迷糊菇"""
    def __init__(self, x, y):
        super().__init__(index=12, name="迷糊菇", ability=["shroom"], sun_number=125, x=x, y=y, life=300)
        self.state = "sleep"
        self.sleep_animation = []
        self.sleep_frame_positions = []
        self.sleep_frame_count = 25


class Scaredyshroom(AttackBotany):
    """胆小菇"""
    def __init__(self, x, y):
        super().__init__(index=13, name="胆小菇", ability=["shroom"], sun_number=125, x=x, y=y, life=300,
                         attack_power=1800, attack_interval=0, speed=0, attack_range=None, bullet_count=1)
        self.state = "sleep"
        self.sleep_animation = []
        self.sleep_frame_positions = []
        self.sleep_frame_count = 25


class Iceshroom(AshBotany):
    """冰川菇"""
    def __init__(self, x, y):
        super().__init__(index=14, name="冰川菇", ability=["ash", "shroom"], sun_number=75, x=x, y=y, life=300,
                         attack_power=20, attack_range="全屏", effect_count=1)
        self.state = "sleep"
        self.sleep_animation = []
        self.sleep_frame_positions = []
        self.sleep_frame_count = 25


class Doomshroom(AshBotany):
    """末日菇"""
    def __init__(self, x, y):
        super().__init__(index=15, name="末日菇", ability=["ash", "shroom"], sun_number=125, x=x, y=y, life=300,
                         attack_power=1800, attack_range="半径3.5格", effect_count=1)
        self.state = "sleep"
        self.sleep_animation = []
        self.sleep_frame_positions = []
        self.sleep_frame_count = 25
        self.sleep_frame_rate = 100
        self.sleep_frame_index = 0
        self.await_frame_count = 20
        self.await_frame_rate = 20
        self.explore_animation = []
        self.explore_frame_count = 33
        self.explore_frame_rate = 20
        self.explore_frame_index = 0
        self.explore_center = (self.x + 30, self.y - 35)
        self.effect_frame_count = 10
        self.effect_frame_rate = 200
        self.sleep_animation_path = f"{Constants.DOOMSHROOM}sleep"
        self.await_animation_path = f"{Constants.DOOMSHROOM}await"
        self.explore_animation_path = f"{Constants.DOOMSHROOM}explore"
        self.effect_animation_path = f"{Constants.DOOMSHROOM}effect"
        self.cooldown_duration = 50000
        self.load_animations()
        self.rect = self.get_rect()

    def draw(self, window):
        """绘制"""
        if self.state == "sleep":
            frame = self.sleep_animation[self.sleep_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - width / 2 + 25, self.y - height, width, height), 2)
            window.blit(frame, (self.x - width / 2 + 25, self.y - height))
        elif self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - width / 2 + 25, self.y - height, width, height), 2)
            window.blit(frame, (self.x - width / 2 + 25, self.y - height))
        elif self.state == "explore":
            frame = self.explore_animation[self.explore_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - width / 2 + 25, self.y - height, width, height), 2)
            window.blit(frame, (self.x - width / 2 + 25, self.y - height))
        self.rect = self.get_rect()

    def update(self, current_time):
        if self.state == "sleep":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >=\
                    self.sleep_frame_rate:
                self.sleep_frame_index = (self.sleep_frame_index + 1) % self.sleep_frame_count
                self.last_update_frame_time = current_time
        if self.state == "await":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >=\
                    self.await_frame_rate:
                self.await_frame_index = (self.await_frame_index + 1) % self.await_frame_count
                self.last_update_frame_time = current_time
                if self.await_frame_index == self.await_frame_count - 1:
                    self.state = "explore"
        if self.state == "explore":
            if self.explore_frame_index == self.explore_frame_count - 1:
                self.kill()
            else:
                if self.last_update_frame_time is None or current_time - self.last_update_frame_time >=\
                        self.explore_frame_rate:
                    self.explore_frame_index = (self.explore_frame_index + 1) % self.explore_frame_count
                    self.last_update_frame_time = current_time

    def explore(self):
        """爆炸"""
        if self.explore_frame_index == self.explore_frame_count - 1:
            effects = []
            for i in range(self.effect_count):
                effect = Effect(self.x - 100, self.y - 300, self.name, self.attack_power, self.effect_animation_path,
                                self.effect_frame_count, i, self.explore_center, 300)
                effects.append(effect)
            return effects

    def get_rect(self):
        if self.state == "sleep":
            frame = self.sleep_animation[self.sleep_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            rect = frame.get_rect(topleft=(self.x - width / 2 + 25, self.y - height))
        elif self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            rect = frame.get_rect(topleft=(self.x - width / 2 + 25, self.y - height))
        elif self.state == "explore":
            frame = self.explore_animation[self.explore_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            rect = frame.get_rect(topleft=(self.x - width / 2 + 25, self.y - height))
        else:
            rect = pygame.Rect(0, 0, 0, 0)
        return rect

    def load_animations(self):
        if self.sleep_animation_path:
            self.sleep_animation = self.image_loader.load_animation(f"{self.name}睡眠", self.sleep_animation_path,
                                                                    self.sleep_frame_count)
        if self.await_animation_path:
            self.await_animation = self.image_loader.load_animation(f"{self.name}等待", self.await_animation_path,
                                                                    self.await_frame_count)
        if self.explore_animation_path:
            self.explore_animation = self.image_loader.load_animation(f"{self.name}爆炸", self.explore_animation_path,
                                                                      self.explore_frame_count)


class LilyPad(FunctionalBotany):
    """莲叶"""
    def __init__(self, x, y):
        super().__init__(index=16, name="莲叶", ability=["sleep"], sun_number=25, x=x, y=y, life=300)
        self.sleep_frame_count = 25
        self.sleep_frame_rate = 100
        self.sleep_animation_path = f"{Constants.LILY_PAD}sleep"
        self.load_animations()


class Squash(AshBotany):
    """窝瓜"""
    def __init__(self, x, y):
        super().__init__(index=17, name="窝瓜", ability=["ash"], sun_number=0, x=x, y=y, life=300,
                         attack_power=18000, attack_range="前方1.5格", effect_count=0)
        self.sleep_frame_count = 25
        self.sleep_frame_rate = 100
        self.sleep_animation_path = f"{Constants.SQUASH}"
        self.load_animations()


class Threepeater(AttackBotany):
    """三重射手"""
    def __init__(self, x, y):
        super().__init__(index=18, name="三重射手", ability=["attack"], sun_number=325, x=x, y=y, life=300,
                         attack_power=20, attack_interval=1400, attack_range="前方三行", speed=2.5, bullet_count=3)
        self.await_frame_count = 25
        self.attack_frame_count = 25
        self.await_frame_rate = 100
        self.attack_frame_rate = 100
        self.bullet_frame_count = 1
        self.bullet_frame_rate = 100
        self.await_animation_path = f"{Constants.THREEPEATER}await"
        self.attack_animation_path = f"{Constants.THREEPEATER}attack"
        self.bullet_animation_path = f"{Constants.THREEPEATER}bullet"
        self.cooldown_duration = 7500
        self.load_animations()
        self.rect = self.get_rect()

    def attack(self, current_time):
        """攻击"""
        if self.state == "attack" and self.attack_frame_index == 13:
            if self.last_attack_time is None or current_time - self.last_attack_time >= self.attack_interval:
                self.last_attack_time = current_time
                width = self.attack_animation[self.attack_frame_index].get_width()
                height = self.attack_animation[self.attack_frame_index].get_height()
                bullets = []
                for i in range(self.bullet_count):
                    bullet = None
                    if self.row == 0:
                        if i == 1:
                            bullet = Bullet(self.x + width - 30, self.y - height + 30, self.row, self.speed,
                                            self.attack_power, self.name, self.bullet_animation_path,
                                            self.bullet_frame_count, self.bullet_frame_rate, i)
                        elif i == 2:
                            bullet = Bullet(self.x + width - 30, self.y - height + 30, self.row + 1, self.speed,
                                            self.attack_power, self.name, self.bullet_animation_path,
                                            self.bullet_frame_count, self.bullet_frame_rate, i)
                    elif self.row == 4:
                        if i == 0:
                            bullet = Bullet(self.x + width - 30, self.y - height + 30, self.row - 1, self.speed,
                                            self.attack_power, self.name, self.bullet_animation_path,
                                            self.bullet_frame_count, self.bullet_frame_rate, i)
                        elif i == 1:
                            bullet = Bullet(self.x + width - 30, self.y - height + 30, self.row, self.speed,
                                            self.attack_power, self.name, self.bullet_animation_path,
                                            self.bullet_frame_count, self.bullet_frame_rate, i)
                    else:
                        if i == 0:
                            bullet = Bullet(self.x + width - 30, self.y - height + 30, self.row - 1, self.speed,
                                            self.attack_power, self.name, self.bullet_animation_path,
                                            self.bullet_frame_count, self.bullet_frame_rate, i)
                        elif i == 1:
                            bullet = Bullet(self.x + width - 30, self.y - height + 30, self.row, self.speed,
                                            self.attack_power, self.name, self.bullet_animation_path,
                                            self.bullet_frame_count, self.bullet_frame_rate, i)
                        else:
                            bullet = Bullet(self.x + width - 30, self.y - height + 30, self.row + 1, self.speed,
                                            self.attack_power, self.name, self.bullet_animation_path,
                                            self.bullet_frame_count, self.bullet_frame_rate, i)
                    if bullet is not None:
                        bullets.append(bullet)
                return bullets
            else:
                return None
        else:
            return None


class TangleKelp(AshBotany):
    """缠绕水草"""
    def __init__(self, x, y):
        super().__init__(index=19, name="缠绕水草", ability=["ash"], sun_number=25, x=x, y=y, life=300,
                         attack_power=0, attack_range="前后小范围", effect_count=1)


class Jalapeno(AshBotany):
    """火爆辣椒"""
    def __init__(self, x, y):
        super().__init__(index=20, name="火爆辣椒", ability=["ash"], sun_number=125, x=x, y=y, life=300,
                         attack_power=1800, attack_range="所在行", effect_count=1)
        self.await_frame_count = 7
        self.explore_frame_count = 13
        self.await_frame_rate = 50
        self.explore_frame_rate = 50
        self.effect_frame_count = 8
        self.effect_frame_rate = 100
        self.await_animation_path = f"{Constants.JALAPENO}await"
        self.explore_animation_path = f"{Constants.JALAPENO}explore"
        self.effect_animation_path = f"{Constants.JALAPENO}effect"
        self.cooldown_duration = 30000
        self.load_animations()
        self.rect = self.get_rect()

    def update(self, current_time):
        if self.state == "await":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >=\
                    self.await_frame_rate:
                self.await_frame_index += 1
                self.last_update_frame_time = current_time
                if self.await_frame_index == self.await_frame_count - 1:
                    self.state = "explore"
                    self.trigger_time = current_time
        elif self.state == "explore":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >=\
                    self.explore_frame_rate:
                self.explore_frame_index = (self.explore_frame_index + 1) % self.explore_frame_count
                self.last_update_frame_time = current_time

    def draw(self, window):
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x + 20, self.y - height, width, height), 2)
            window.blit(frame, (self.x + 20, self.y - height))
        if self.state == "explore":
            frame = self.explore_animation[self.explore_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x, self.y - height, width, height), 2)
            window.blit(frame, (self.x, self.y - height))

    def explore(self):
        """爆炸"""
        if self.explore_frame_index == self.effect_frame_count - 1:
                effects = []
                for i in range(self.effect_count):
                    bullet = Effect(102, 87 + 96 * self.row - 40, self.name, self.attack_power,
                                    self.effect_animation_path, self.effect_frame_count, i, self.row, None)
                    effects.append(bullet)
                    self.kill()
                return effects

    def get_rect(self):
        """获取矩形"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            x, y, width, height = self.await_frame_positions[self.await_frame_index]
        elif self.state == "explore":
            frame = self.explore_animation[self.explore_frame_index]
            x, y, width, height = self.attack_frame_positions[self.explore_frame_index]
        else:
            return pygame.Rect(0, 0, 0, 0)
        rect = frame.get_rect(topleft=(self.x + 20, self.y - height))
        return rect


class Spikeweed(AttackBotany):
    """地刺"""
    def __init__(self, x, y):
        super().__init__(index=21, name="地刺", ability=["attack"], sun_number=50, x=x, y=y, life=300,
                         attack_power=20, attack_interval=700, attack_range="所在格", speed=2.5, bullet_count=1)
        self.await_frame_count = 21
        self.attack_frame_count = 10
        self.await_frame_rate = 100
        self.attack_frame_rate = 70
        self.await_animation_path = f"{Constants.SPIKEWEED}await"
        self.attack_animation_path = f"{Constants.SPIKEWEED}attack"
        self.cooldown_duration = 7500
        self.load_animations()
        self.rect = self.get_rect()

    def attack(self, current_time):
        """攻击"""
        return

    def draw(self, window):
        """绘制"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 20, self.y - height, width, height), 2)
            window.blit(frame, (self.x - 20, self.y - height))
        elif self.state == "attack":
            frame = self.attack_animation[self.attack_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 20, self.y - height, width, height), 2)
            window.blit(frame, (self.x - 20, self.y - height))

    def get_rect(self):
        """获取矩形"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            x, y, width, height = self.await_frame_positions[self.await_frame_index]
        elif self.state == "attack":
            frame = self.attack_animation[self.attack_frame_index]
            x, y, width, height = self.attack_frame_positions[self.attack_frame_index]
        else:
            return pygame.Rect(0, 0, 0, 0)
        rect = frame.get_rect(topleft=(self.x - 20, self.y - height))
        return rect


class Torchwood(FunctionalBotany):
    """火炬树桩"""
    def __init__(self, x, y):
        super().__init__(index=22, name="火炬树桩", ability=["protect"], sun_number=125, x=x, y=y, life=4000)
        self.await_animation_path = f"{Constants.TORCHWOOD}await"
        self.await_frame_count = 17
        self.await_frame_rate = 100
        self.load_animations()


class Tallnut(ProtectBotany):
    """高坚果"""
    def __init__(self, x, y):
        super().__init__(index=23, name="高坚果", ability=["protect"], sun_number=125, x=x, y=y, life=8000)
        self.await_animation_path = f"{Constants.TALLNUT}await"
        self.await_frame_count = 17
        self.await_frame_rate = 100
        self.load_animations()
        self.rect = self.get_rect()
        self.cooldown_duration = 30000

    def draw(self, window):
        frame = self.await_animation[self.await_frame_index]
        width, height = frame.get_size()
        if Constants.BOTANY_COLLISION_BOX:
            pygame.draw.rect(window, (0, 0, 0), (self.x - 10, self.y - height, width, height), 2)
        window.blit(frame, (self.x - 10, self.y - height))

    def attack(self, current_time):
        return

    def get_rect(self):
        frame = self.await_animation[self.await_frame_index]
        width, height = frame.get_size()
        rect = frame.get_rect(topleft=(self.x - 10, self.y - height))
        return rect


class Seashroom(AttackBotany):
    """水兵菇"""
    def __init__(self, x, y):
        super().__init__(index=24, name="水兵菇", ability=["attack"], sun_number=125, x=x, y=y, life=300,
                         attack_power=20, attack_interval=1400, attack_range="所在格", speed=2.5, bullet_count=1)
        self.await_frame_count = 25
        self.attack_frame_count = 25
        self.await_frame_rate = 100
        self.attack_frame_rate = 100
        self.bullet_frame_count = 1


class Plantern(FunctionalBotany):
    """路灯花"""
    def __init__(self, x, y):
        super().__init__(index=25, name="路灯花", ability=["protect"], sun_number=125, x=x, y=y, life=4000)
        self.await_animation_path = f"{Constants.PLANTERN}await"
        self.await_frame_count = 17
        self.await_frame_rate = 100
        self.load_animations()


class Cactus(AttackBotany):
    """仙人掌"""
    def __init__(self, x, y):
        super().__init__(index=26, name="仙人掌", ability=["attack"], sun_number=125, x=x, y=y, life=4000,
                         attack_power=None, attack_interval=None, attack_range="前方一行", speed=None, bullet_count=None)
        self.await_animation_path = f"{Constants.CACTUS}await"
        self.await_frame_count = 17
        self.await_frame_rate = 100


class Blover(FunctionalBotany):
    """三叶草"""
    def __init__(self, x, y):
        super().__init__(index=27, name="三叶草", ability=["ash"], sun_number=100, x=x, y=y, life=300)
        self.await_animation_path = f"{Constants.BLOVER}await"
        self.await_frame_count = 17
        self.await_frame_rate = 100


class SplitPea(AttackBotany):
    """双向射手"""
    def __init__(self, x, y):
        super().__init__(index=28, name="双向射手", ability=["attack"], sun_number=125, x=x, y=y, life=300,
                         attack_power=20, attack_interval=1400, attack_range="前后一行", speed=2.5, bullet_count=3)
        self.await_frame_count = 25
        self.attack_frame_count = 25
        self.await_frame_rate = 100
        self.attack_frame_rate = 100
        self.bullet_frame_count = 1
        self.bullet_frame_rate = 100
        self.await_animation_path = f"{Constants.SPLIT_PEA}await"
        self.attack_animation_path = f"{Constants.SPLIT_PEA}attack"
        self.bullet_animation_path = f"{Constants.SPLIT_PEA}bullet"
        self.cooldown_duration = 7500
        self.load_animations()
        self.rect = self.get_rect()

    def attack(self, current_time):
        """攻击"""
        if self.state == "attack" and self.attack_frame_index == 13:
            if self.last_attack_time is None or current_time - self.last_attack_time >= self.attack_interval:
                self.last_attack_time = current_time
                width = self.attack_animation[self.attack_frame_index].get_width()
                height = self.attack_animation[self.attack_frame_index].get_height()
                bullets = []
                for i in range(self.bullet_count):
                    if i == 2:
                        bullet = Bullet(self.x + width - 30, self.y - height, self.row, self.speed, self.attack_power,
                                        self.name, self.bullet_animation_path, self.bullet_frame_count,
                                        self.bullet_frame_rate, i)
                    else:
                        bullet = Bullet(self.x + width - i * 30 - 130, self.y - height, self.row, self.speed,
                                        self.attack_power, self.name, self.bullet_animation_path,
                                        self.bullet_frame_count, self.bullet_frame_rate, i)
                    bullets.append(bullet)
                return bullets
            else:
                return None
        else:
            return None


class Starfruit(AttackBotany):
    """星星果"""
    def __init__(self, x, y):
        super().__init__(index=29, name="星星果", ability=["attack"], sun_number=125, x=x, y=y, life=300,
                         attack_power=20, attack_interval=1400, attack_range="全屏", speed=2.5, bullet_count=5)
        self.await_frame_count = 17
        self.attack_frame_count = 17
        self.await_frame_rate = 100
        self.attack_frame_rate = 100
        self.bullet_frame_count = 3
        self.bullet_frame_rate = 100
        self.await_animation_path = f"{Constants.STARFRUIT}await"
        self.attack_animation_path = f"{Constants.STARFRUIT}attack"
        self.bullet_animation_path = f"{Constants.STARFRUIT}bullet"
        self.cooldown_duration = 7500
        self.load_animations()
        self.rect = self.get_rect()

    def draw(self, window):
        """绘制"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 10, self.y - height, width, height), 2)
            window.blit(frame, (self.x - 10, self.y - height))
        if self.state == "attack":
            frame = self.attack_animation[self.attack_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 10, self.y - height, width, height), 2)
            window.blit(frame, (self.x - 10, self.y - height))

    def attack(self, current_time):
        """攻击"""
        if self.state == "attack" and self.attack_frame_index == 13:
            if self.last_attack_time is None or current_time - self.last_attack_time > self.attack_interval:
                self.last_attack_time = current_time
                # width = self.attack_animation[self.attack_frame_index].get_width()
                height = self.attack_animation[self.attack_frame_index].get_height()
                bullets = []
                for i in range(self.bullet_count):
                    bullet = Bullet(self.x + 5, self.y - height + 15, None, self.speed, self.attack_power, self.name,
                                    self.bullet_animation_path, self.bullet_frame_count, self.bullet_frame_rate, i)
                    bullets.append(bullet)
                return bullets
            else:
                return None
        else:
            return None


class Pumpkin(ProtectBotany):
    """南瓜头"""
    def __init__(self, x, y):
        super().__init__(index=30, name="南瓜头", ability=["attack"], sun_number=125, x=x, y=y, life=4000)
        self.await_frame_count = 21
        self.await_frame_rate = 100
        self.await_animation_path = f"{Constants.PUMPKIN}await"
        self.cooldown_duration = 30000
        self.load_animations()
        self.rect = self.get_rect()

    def draw(self, window):
        """绘制"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            x, y, width, height = self.await_frame_positions[self.await_frame_index]
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 20, self.y - y, width, height), 2)
            window.blit(frame, (self.x - 20, self.y - y))
        self.rect = self.get_rect()

    def get_rect(self):
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            x, y, width, height = self.await_frame_positions[self.await_frame_index]
            rect = frame.get_rect(topleft=(self.x - 20, self.y - y))
            return rect


class Magnetshroom(FunctionalBotany):
    """磁力菇"""
    def __init__(self, x, y):
        super().__init__(index=31, name="磁力菇", ability=["attack"], sun_number=125, x=x, y=y, life=4000)
        self.await_frame_count = 21
        self.await_frame_rate = 100
        self.await_animation_path = f"{Constants.MAGNET_SHROOM}await"
        self.cooldown_duration = 30000


class Cabbagepult(AttackBotany):
    """卷心菜投手"""
    def __init__(self, x, y):
        super().__init__(index=32, name="卷心菜投手", ability=["attack"], sun_number=125, x=x, y=y, life=4000,
                         attack_power=None, attack_interval=None, attack_range=None, speed=None, bullet_count=None)


class FlowerPot(FunctionalBotany):
    """花盆"""
    def __init__(self, x, y):
        super().__init__(index=33, name="花盆", ability=[""], sun_number=75, x=x, y=y, life=300)
        self.await_frame_count = 9
        self.await_frame_rate = 100
        self.crumble_frame_count = 15
        self.crumble_frame_rate = 100


class Kernelpult(AttackBotany):
    """玉米投手"""
    def __init__(self, x, y):
        super().__init__(index=34, name="玉米投手", ability=["attack"], sun_number=125, x=x, y=y, life=4000,
                         attack_power=None, attack_interval=None, attack_range=None, speed=None, bullet_count=None)


class CoffeeBean(FunctionalBotany):
    """咖啡豆"""
    def __init__(self, x, y):
        super().__init__(index=35, name="咖啡豆", ability=[""], sun_number=75, x=x, y=y, life=300)
        self.await_frame_count = 9
        self.await_frame_rate = 100
        self.crumble_frame_count = 15
        self.crumble_frame_rate = 100
        self.crumble_animation = []
        self.crumble_frame_index = 0
        self.await_animation_path = f"{Constants.COFFEE_BEAN}await"
        self.crumble_animation_path = f"{Constants.COFFEE_BEAN}crumble"
        self.cooldown_duration = 7500
        self.load_animations()
        self.rect = self.get_rect()

    def draw(self, window):
        """绘制"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x + 5, self.y - height - 30, width, height), 2)
            window.blit(frame, (self.x + 5, self.y - height - 30))
        if self.state == "crumble":
            frame = self.crumble_animation[self.crumble_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x + 5, self.y - height - 30, width, height), 2)
            window.blit(frame, (self.x + 5, self.y - height - 30))

    def update(self, current_time):
        if self.state == "await":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >=\
                    self.await_frame_rate:
                if self.await_frame_index == self.await_frame_count - 1:
                    self.state = "crumble"
                else:
                    self.await_frame_index += 1
                    self.last_update_frame_time = current_time
        if self.state == "crumble":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >=\
                    self.crumble_frame_rate:
                if self.crumble_frame_index == self.crumble_frame_count - 1:
                    self.kill()
                else:
                    self.crumble_frame_index += 1
                    self.last_update_frame_time = current_time

    def load_animations(self):
        if self.await_animation_path:
            self.await_animation = self.image_loader.load_animation("咖啡豆待机", self.await_animation_path,
                                                                    self.await_frame_count)
        if self.crumble_animation_path:
            self.crumble_animation = self.image_loader.load_animation("咖啡豆粉碎", self.crumble_animation_path,
                                                                      self.crumble_frame_count)


class Garlic(FunctionalBotany):
    """大蒜"""
    def __init__(self, x, y):
        super().__init__(index=36, name="大蒜", ability=["protect"], sun_number=50, x=x, y=y, life=400)
        self.await_frame_count = 9
        self.await_frame_rate = 100
        self.await_animation_path = f"{Constants.GARLIC}await"
        self.load_animations()
        self.cooldown_duration = 7500
        self.rect = self.get_rect()


class UmbrellaLeaf(ProtectBotany):
    """萝卜伞"""
    def __init__(self, x, y):
        super().__init__(index=37, name="萝卜伞", ability=["protect"], sun_number=100, x=x, y=y, life=300)
        self.await_frame_count = 9
        self.await_frame_rate = 100
        self.crumble_frame_count = 15
        self.crumble_frame_rate = 100
        self.cooldown_duration = 7500
        self.load_animations()
        self.rect = self.get_rect()


class Marigold(ProduceBotany):
    """金盏花"""
    def __init__(self, x, y):
        super().__init__(index=38, name="金盏花", ability=["produce"], sun_number=50, x=x, y=y, life=300, summon_count=1)
        self.await_frame_count = 9
        self.await_frame_rate = 100
        self.cooldown_duration = 30000
        self.load_animations()
        self.rect = self.get_rect()


class Melonpult(AttackBotany):
    """西瓜投手"""
    def __init__(self, x, y):
        super().__init__(index=39, name="西瓜投手", ability=["attack"], sun_number=125, x=x, y=y, life=4000,
                         attack_power=None, attack_interval=None, attack_range=None, speed=None, bullet_count=None)


class GatlingPea(AttackBotany):
    """机枪射手"""
    def __init__(self, x, y):
        super().__init__(index=40, name="机枪射手", ability=["attack"], sun_number=250, x=x, y=y, life=300,
                         attack_power=20, attack_interval=1400, attack_range="前方一行", speed=2.5, bullet_count=4)
        self.await_frame_count = 25
        self.attack_frame_count = 49
        self.await_frame_rate = 100
        self.attack_frame_rate = 20
        self.bullet_frame_count = 1
        self.bullet_frame_rate = 100
        self.await_animation_path = f"{Constants.GATLING_PEA}await"
        self.attack_animation_path = f"{Constants.GATLING_PEA}attack"
        self.bullet_animation_path = f"{Constants.GATLING_PEA}bullet"
        self.cooldown_duration = 50000
        self.load_animations()
        self.rect = self.get_rect()


class TwinSunflower(ProduceBotany):
    """双胞向日葵"""
    def __init__(self, x, y):
        super().__init__(index=41, name="双胞向日葵", ability=["produce"], sun_number=125, x=x, y=y, life=300,
                         summon_count=2)
        self.await_frame_count = 15
        self.attack_frame_count = 15
        self.await_frame_rate = 100
        self.attack_frame_rate = 66


class Gloomshroom(AttackBotany):
    """多嘴小喷菇"""
    def __init__(self, x, y):
        super().__init__(index=42, name="多嘴小喷菇", ability=["attack"], sun_number=125, x=x, y=y, life=300,
                         attack_power=None, attack_interval=None, attack_range=None, speed=None, bullet_count=None)
        self.await_frame_count = 15
        self.attack_frame_count = 15
        self.await_frame_rate = 100
        self.attack_frame_rate = 66


class Cattail(AttackBotany):
    """猫尾草"""
    def __init__(self, x, y):
        super().__init__(index=43, name="猫尾草", ability=["attack"], sun_number=125, x=x, y=y, life=300,
                         attack_power=None, attack_interval=None, attack_range=None, speed=None, bullet_count=None)
        self.await_frame_count = 15
        self.attack_frame_count = 15
        self.await_frame_rate = 100
        self.attack_frame_rate = 66


class WinterMelon(AttackBotany):
    """冰西瓜"""
    def __init__(self, x, y):
        super().__init__(index=44, name="冰西瓜", ability=["attack"], sun_number=125, x=x, y=y, life=300,
                         attack_power=None, attack_interval=None, attack_range=None, speed=None, bullet_count=None)
        self.await_frame_count = 15
        self.attack_frame_count = 15
        self.await_frame_rate = 100
        self.attack_frame_rate = 66


class GoldMagnet(FunctionalBotany):
    """吸金菇"""
    def __init__(self, x, y):
        super().__init__(index=45, name="吸金菇", ability=["attack"], sun_number=125, x=x, y=y, life=300)
        self.await_frame_count = 15
        self.attack_frame_count = 15
        self.await_frame_rate = 100
        self.attack_frame_rate = 66


class Spikerock(AttackBotany):
    """钢地刺"""
    def __init__(self, x, y):
        super().__init__(index=46, name="钢地刺", ability=["attack"], sun_number=125, x=x, y=y, life=450,
                         attack_power=20, attack_interval=1000, attack_range="所在格", speed=0, bullet_count=1)
        self.await_frame_count = 15
        self.attack_frame_count = 15
        self.await_frame_rate = 100
        self.attack_frame_rate = 66
        self.await_animation_path = f"{Constants.SPIKEROCK}await"
        self.attack_animation_path = f"{Constants.SPIKEROCK}attack"
        self.cooldown_duration = 50000
        self.load_animations()
        self.rect = self.get_rect()

    def draw(self, window):
        """绘制"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 20, self.y - height, width, height), 2)
            window.blit(frame, (self.x - 20, self.y - height))
        elif self.state == "attack":
            frame = self.attack_animation[self.attack_frame_index]
            width = frame.get_width()
            height = frame.get_height()
            if Constants.BOTANY_COLLISION_BOX:
                pygame.draw.rect(window, (0, 0, 0), (self.x - 20, self.y - height, width, height), 2)
            window.blit(frame, (self.x - 20, self.y - height))

    def attack(self, current_time):
        """攻击"""
        return None

    def get_rect(self):
        """获取碰撞箱"""
        if self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            x, y, width, height = self.await_frame_positions[self.await_frame_index]
        elif self.state == "attack":
            frame = self.attack_animation[self.attack_frame_index]
            x, y, width, height = self.attack_frame_positions[self.attack_frame_index]
        else:
            return pygame.Rect(0, 0, 0, 0)
        rect = frame.get_rect(topleft=(self.x - 20, self.y - height))
        return rect


class CobCannon(AttackBotany):
    """玉米加农炮"""
    def __init__(self, x, y):
        super().__init__(index=47, name="玉米加农炮", ability=["attack"], sun_number=125, x=x, y=y, life=300,
                         attack_power=None, attack_interval=None, attack_range=None, speed=None, bullet_count=None)


class Imitater(FunctionalBotany):
    """变身茄子"""
    def __init__(self, x, y):
        super().__init__(index=48, name="变身茄子", ability=["attack"], sun_number=125, x=x, y=y, life=300)


class Bullet(pygame.sprite.Sprite):
    """子弹类"""
    def __init__(self, x, y, row, speed, damage, name, animation_path, frame_count, frame_rate, i):
        super().__init__()
        self.start_pos = [x, y]
        self.end_pos = [x, y]
        self.row = row
        self.end_row = row
        self.name = f"{name}{i}"
        self.image_loader = ImageLoader()
        self.animation = self.image_loader.load_animation(f"{name}子弹", animation_path, frame_count)
        self.frame_index = 0
        self.rect = pygame.Rect(x, y, 0, 0)
        self.rect = self.get_rect()
        self.speed = speed
        self.damage = damage
        self.last_update_frame_time = None
        self.frame_rate = frame_rate
        self.damage_flag = False
        self.last_damage_time = None

    def draw(self, window):
        """绘制子弹"""
        frame = self.animation[self.frame_index]
        if Constants.BULLET_COLLISION_BOX:
            pygame.draw.rect(window, (0, 0, 255), self.rect, 1)
        window.blit(frame, self.end_pos)
        self.rect = self.get_rect()

    def update(self, current_time):
        """更新子弹位置和帧索引"""
        # 位置
        self.end_pos = self.calculate_bullet_trajectory(self.name, self.start_pos, self.end_pos, self.speed)
        if self.end_pos[0] <= 0 or self.end_pos[0] >= 900 or self.end_pos[1] <= 0 or self.end_pos[1] >= 600:
            if self.name != "火爆辣椒0" and self.name != "末日菇0" and self.name != "樱桃炸弹0" and self.name != "大喷菇0":
                self.kill()
        # 帧索引
        if self.last_update_frame_time is None or current_time - self.last_update_frame_time >= self.frame_rate:
            self.frame_index = (self.frame_index + 1) % len(self.animation)
            self.last_update_frame_time = current_time

    def get_rect(self):
        """获取碰撞箱"""
        if self.name == "末日菇0":
            frame = self.animation[self.frame_index]
            width = frame.get_width()
            height = frame.get_height()
            rect = pygame.Rect(self.end_pos[0] - 157, self.end_pos[1] - 80, width + 284, height + 360)
        else:
            frame = self.animation[self.frame_index]
            rect = frame.get_rect(topleft=self.end_pos)
        return rect

    def calculate_bullet_trajectory(self, name, start_pos, end_pos, speed):
        """计算子弹轨迹"""
        if name == "地刺0" or name == "钢地刺0":
            return [end_pos[0], end_pos[1]]
        elif name == "三重射手0" or name == "三重射手2":
            if name == "三重射手0":
                if end_pos[1] - start_pos[1] >= -91:
                    self.row = self.row + 1
                    end_pos = [end_pos[0] + speed, end_pos[1] - speed]
                    return end_pos
                else:
                    end_pos = [end_pos[0] + speed, end_pos[1]]
                    self.row = self.end_row
                    return end_pos
            elif name == "三重射手2":
                if end_pos[1] - start_pos[1] <= 91:
                    end_pos = [end_pos[0] + speed, end_pos[1] + speed]
                    self.row = self.row - 1
                    return end_pos
                else:
                    end_pos = [end_pos[0] + speed, end_pos[1]]
                    self.row = self.end_row
                    return end_pos
        elif name == "星星果0" or name == "星星果1" or name == "星星果2" or name == "星星果3" or name == "星星果4":
            if name == "星星果0":
                return [end_pos[0] - math.sin(np.deg2rad(20)) * speed, end_pos[1] - math.cos(np.deg2rad(20)) * speed]
            elif name == "星星果1":
                return [end_pos[0] + math.cos(np.deg2rad(20)) * speed, end_pos[1] - math.sin(np.deg2rad(20)) * speed]
            elif name == "星星果2":
                return [end_pos[0] + math.cos(np.deg2rad(35)) * speed, end_pos[1] + math.sin(np.deg2rad(35)) * speed]
            elif name == "星星果3":
                return [end_pos[0] - math.sin(np.deg2rad(10)) * speed, end_pos[1] + math.cos(np.deg2rad(10)) * speed]
            else:
                return [end_pos[0] - math.cos(np.deg2rad(1)) * speed, end_pos[1] - math.sin(np.deg2rad(1)) * speed]
        elif name == "双向射手0" or name == "双向射手1":
            return [end_pos[0] - speed, end_pos[1]]
        elif "投手" in name:
            pass
        else:
            return [end_pos[0] + speed, end_pos[1]]


class Summon(pygame.sprite.Sprite):
    """召唤物类"""
    def __init__(self, x, y, name, animation_path, frame_count):
        super().__init__()
        self.start_pos = [x, y - 50]
        self.end_pos = [x, y - 130]
        self.name = name
        self.image_loader = ImageLoader()
        self.animation = self.image_loader.load_animation(f"{name}", animation_path, frame_count)
        self.frame_index = 0
        self.rect = pygame.Rect(x, y, 0, 0)
        self.rect = self.get_rect()
        self.last_update_frame_time = None
        self.frame_rate = 0

    def draw(self, window):
        """绘制召唤物"""
        frame = self.animation[self.frame_index]
        window.blit(frame, self.start_pos)
        self.rect = self.get_rect()

    def update(self, current_time):
        """更新召唤物位置和帧索引"""
        if self.start_pos[1] >= self.end_pos[1]:
            self.start_pos[1] -= 5
        if self.last_update_frame_time is None or current_time - self.last_update_frame_time >= self.frame_rate:
            self.frame_index = (self.frame_index + 1) % len(self.animation)
            self.last_update_frame_time = current_time

    def get_rect(self):
        """获取碰撞箱"""
        frame = self.animation[self.frame_index]
        rect = frame.get_rect(topleft=self.start_pos)
        return rect


class Effect(pygame.sprite.Sprite):
    """特效类"""
    def __init__(self, x, y, name, damage, animation_path, frame_count, i, center_row, radius):
        super().__init__()
        # 坐标
        self.x, self.y = x, y
        # 名称
        self.name = name + str(i)
        # 伤害
        self.damage = damage
        # 中心坐标或行号
        self.center_row = center_row
        # 半径
        self.radius = radius

        self.image_loader = ImageLoader()
        # 特效动画
        self.effect_animation = self.image_loader.load_animation(f"{self.name}", animation_path, frame_count)
        # 帧索引
        self.frame_index = 0
        # 帧率
        self.frame_rate = 200
        # 上一次更新帧的时间
        self.last_update_frame_time = None

    def draw(self, window):
        frame = self.effect_animation[self.frame_index]
        window.blit(frame, (self.x, self.y))

    def update(self, current_time):
        if "土豆地雷" in self.name:
            if self.last_update_frame_time is None:
                self.last_update_frame_time = current_time
            else:
                if current_time - self.last_update_frame_time >= 2000:
                    self.kill()
        else:
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >= self.frame_rate:
                self.frame_index = (self.frame_index + 1) % len(self.effect_animation)
                self.last_update_frame_time = current_time
                if self.frame_index == len(self.effect_animation) - 1:
                    self.kill()
