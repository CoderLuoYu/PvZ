import pygame
import Constants
from image_loader import ImageLoader


class Zombie(pygame.sprite.Sprite):
    def __init__(self, index, name, x, y, life, attack_power, attack_interval, walk_speed):
        super().__init__()
        # 编号
        self.index = index
        # 名称
        self.name = name
        # 坐标
        self.x, self.y = x, y
        # 生命值
        self.life = life
        # 攻击力
        self.attack_power = attack_power
        # 攻击速度
        self.attack_interval = attack_interval
        # 行走速度
        self.walk_speed = walk_speed
        # 状态
        self.state = "walk"
        # 行号
        self.row = 0

        self.image_loader = ImageLoader()
        # 动画路径
        self.run_animation_path, self.await_animation_path, self.jump_animation_path,  self.walk_animation_path,\
            self.eat_animation_path, self.death_animation_path = None, None, None, None, None, None
        # 动画
        self.run_animation, self.await_animation, self.jump_animation, self.walk_animation, self.eat_animation,\
            self.death_animation = [], [], [], [], [], []
        # 动画帧索引
        self.run_frame_index, self.await_frame_index, self.jump_frame_index, self.walk_frame_index,\
            self.eat_frame_index, self.death_frame_index = 0, 0, 0, 0, 0, 0
        # 动画帧数
        self.run_frame_count, self.await_frame_count, self.jump_frame_count, self.walk_frame_count,\
            self.eat_frame_count, self.death_frame_count = 0, 0, 0, 0, 0, 0
        # 动画帧率
        self.run_frame_rate, self.await_frame_rate, self.jump_frame_rate, self.walk_frame_rate,\
            self.eat_frame_rate, self.death_frame_rate = 100, 100, 100, 100, 100, 100
        # 上一次更新帧的时间
        self.last_update_frame_time = None
        # 上一次攻击的时间
        self.last_eat_time = None
        # 添加 rect 属性
        self.rect = pygame.Rect(0, 0, 0, 0)

    def draw(self, window):
        if self.state == "walk":
            frame = self.walk_animation[self.walk_frame_index]
            width, height = frame.get_size()
            if Constants.ZOMBIE_COLLISION_BOX:
                pygame.draw.rect(window, (255, 0, 0), (self.x - width, self.y - height, width, height), 2)
            window.blit(frame, (self.x - width, self.y - height))
        elif self.state == "eat":
            frame = self.eat_animation[self.eat_frame_index]
            width, height = frame.get_size()
            if Constants.ZOMBIE_COLLISION_BOX:
                pygame.draw.rect(window, (255, 0, 0), (self.x - width, self.y - height, width, height), 2)
            window.blit(frame, (self.x - width, self.y - height))
        elif self.state == "death":
            frame = self.death_animation[self.death_frame_index]
            width, height = frame.get_size()
            if Constants.ZOMBIE_COLLISION_BOX:
                pygame.draw.rect(window, (255, 0, 0), (self.x - width, self.y - height, width, height), 2)
            window.blit(frame, (self.x - width, self.y - height))
        self.rect = self.get_rect()  # 更新 rect 属性

    def update(self, current_time):
        """更新位置和动画帧索引"""
        # 帧索引
        if self.state == "walk":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >= self.walk_frame_rate:
                self.walk_frame_index = (self.walk_frame_index + 1) % self.walk_frame_count
                self.last_update_frame_time = current_time
        elif self.state == "eat":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >= self.eat_frame_rate:
                self.eat_frame_index = (self.eat_frame_index + 1) % self.eat_frame_count
                self.last_update_frame_time = current_time
        elif self.state == "death":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >= self.death_frame_rate:
                self.death_frame_index = (self.death_frame_index + 1) % self.death_frame_count
                self.last_update_frame_time = current_time
                if self.death_frame_index == self.death_frame_count - 1:
                    self.kill()
        # 位置
        if self.state == "walk":
            self.x -= self.walk_speed
        if self.life <= 0:
            self.state = "death"

    def load_animations(self):
        """加载动画"""
        if self.run_animation_path:
            self.run_animation = self.image_loader.load_animation(f"{self.name}跑", self.run_animation_path,
                                                                  self.run_frame_count)
        if self.await_animation_path:
            self.await_animation = self.image_loader.load_animation(f"{self.name}等待", self.await_animation_path,
                                                                    self.await_frame_count)
        if self.jump_animation_path:
            self.jump_animation = self.image_loader.load_animation(f"{self.name}跳跃", self.jump_animation_path,
                                                                   self.jump_frame_count)
        if self.walk_animation_path:
            self.walk_animation = self.image_loader.load_animation(f"{self.name}行走", self.walk_animation_path,
                                                                   self.walk_frame_count)
        if self.eat_animation_path:
            self.eat_animation = self.image_loader.load_animation(f"{self.name}攻击", self.eat_animation_path,
                                                                  self.eat_frame_count)
        if self.death_animation_path:
            self.death_animation = self.image_loader.load_animation(f"{self.name}死亡", self.death_animation_path,
                                                                    self.death_frame_count)

    def get_rect(self):
        """获取碰撞箱"""
        if self.state == "walk":
            frame = self.walk_animation[self.walk_frame_index]
            width, height = frame.get_size()
        elif self.state == "eat":
            frame = self.eat_animation[self.eat_frame_index]
            width, height = frame.get_size()
        else:
            return pygame.Rect(0, 0, 0, 0)
        rect = frame.get_rect(topleft=(self.x - width, self.y - height))
        return rect


class CommonZombie(Zombie):
    """普通僵尸"""
    def __init__(self, x, y):
        super().__init__(index=0, name="普通僵尸", x=x, y=y, life=270, attack_power=4, attack_interval=1500, walk_speed=0.2)
        self.walk_frame_count = 47
        self.eat_frame_count = 40
        self.walk_frame_rate = 100
        self.eat_frame_rate = 100
        self.death_frame_count = 39
        self.death_frame_rate = 100
        self.walk_animation_path = f"{Constants.ZOMBIE}walk"
        self.eat_animation_path = f"{Constants.ZOMBIE}eat"
        self.death_animation_path = f"{Constants.ZOMBIE}death"
        self.load_animations()
        self.rect = self.get_rect()


class FlagZombie(Zombie):
    """旗帜僵尸"""
    def __init__(self, x, y):
        super().__init__(index=1, name="旗帜僵尸", x=x, y=y, life=270, attack_power=4, attack_interval=40, walk_speed=0.2)
        self.walk_frame_count = 47
        self.eat_frame_count = 40
        self.walk_frame_rate = 100
        self.eat_frame_rate = 100
        self.death_frame_count = 39
        self.death_frame_rate = 100
        self.walk_animation_path = f"{Constants.FLAG_ZOMBIE}walk"
        self.eat_animation_path = f"{Constants.FLAG_ZOMBIE}eat"
        self.death_animation_path = f"{Constants.FLAG_ZOMBIE}death"
        self.load_animations()
        self.rect = self.get_rect()


class ConeheadZombie(Zombie):
    """路障僵尸"""
    def __init__(self, x, y):
        super().__init__(index=2, name="路障僵尸", x=x, y=y, life=640, attack_power=4, attack_interval=40, walk_speed=0.2)
        self.walk_frame_count = 47
        self.eat_frame_count = 40
        self.walk_frame_rate = 100
        self.eat_frame_rate = 100
        self.death_frame_count = 39
        self.death_frame_rate = 100
        self.walk_animation_path = f"{Constants.CONEHEAD_ZOMBIE}walk"
        self.eat_animation_path = f"{Constants.CONEHEAD_ZOMBIE}eat"
        self.death_animation_path = f"{Constants.CONEHEAD_ZOMBIE}death"
        self.load_animations()
        self.rect = self.get_rect()


class BucketheadZombie(Zombie):
    """铁桶僵尸"""
    def __init__(self, x, y):
        super().__init__(index=3, name="铁桶僵尸", x=x, y=y, life=1370, attack_power=4, attack_interval=40, walk_speed=0.2)
        self.walk_frame_count = 47
        self.eat_frame_count = 40
        self.walk_frame_rate = 100
        self.eat_frame_rate = 100
        self.death_frame_count = 39
        self.death_frame_rate = 100
        self.walk_animation_path = f"{Constants.BUCKETHEAD_ZOMBIE}walk"
        self.eat_animation_path = f"{Constants.BUCKETHEAD_ZOMBIE}eat"
        self.death_animation_path = f"{Constants.BUCKETHEAD_ZOMBIE}death"
        self.load_animations()
        self.rect = self.get_rect()


class PoleVaultingZombie(Zombie):
    """撑杆僵尸"""
    def __init__(self, x, y):
        super().__init__(index=4, name="撑杆僵尸", x=x, y=y, life=270, attack_power=4, attack_interval=40, walk_speed=0.8)
        self.run_speed = 0.5
        self.state = "run"
        self.run_frame_count = 37
        self.await_frame_count = 13
        self.jump_frame_count = 43
        self.walk_frame_count = 45
        self.eat_frame_count = 28
        self.death_frame_count = 27
        self.run_frame_rate = 50
        self.await_frame_rate = 50
        self.jump_frame_rate = 50
        self.walk_frame_rate = 100
        self.eat_frame_rate = 100
        self.death_frame_rate = 100
        self.run_animation_path = f"{Constants.POLE_VAULTING_ZOMBIE}run"
        self.await_animation_path = f"{Constants.POLE_VAULTING_ZOMBIE}await"
        self.jump_animation_path = f"{Constants.POLE_VAULTING_ZOMBIE}jump"
        self.walk_animation_path = f"{Constants.POLE_VAULTING_ZOMBIE}walk"
        self.eat_animation_path = f"{Constants.POLE_VAULTING_ZOMBIE}eat"
        self.death_animation_path = f"{Constants.POLE_VAULTING_ZOMBIE}death"
        self.load_animations()

    def update(self, current_time):
        """更新位置和动画帧索引"""
        # 帧索引
        if self.state == "run":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >= self.run_frame_rate:
                self.run_frame_index = (self.run_frame_index + 1) % self.run_frame_count
                self.last_update_frame_time = current_time
            self.x -= self.run_speed
        elif self.state == "await":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >= self.await_frame_rate:
                self.await_frame_index = (self.await_frame_index + 1) % self.await_frame_count
                self.last_update_frame_time = current_time
                if self.await_frame_index == self.await_frame_count - 1:
                    self.state = "jump"
        elif self.state == "jump":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >= self.jump_frame_rate:
                self.jump_frame_index = (self.jump_frame_index + 1) % self.jump_frame_count
                self.last_update_frame_time = current_time
                if self.jump_frame_index == 15:
                    self.x_ = self.x
                    self.x_ -= 2.5
                elif self.jump_frame_index > 15:
                    self.x_ -= 2.5
                if 18 <= self.jump_frame_index <= 34:
                    self.x -= self.jump_frame_index - 17
                elif self.jump_frame_index > 34:
                    self.x = self.x_
                if self.jump_frame_index == self.jump_frame_count - 1:
                    self.state = "walk"
        elif self.state == "walk":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >= self.walk_frame_rate:
                self.walk_frame_index = (self.walk_frame_index + 1) % self.walk_frame_count
                self.last_update_frame_time = current_time
                self.x -= self.walk_speed
        elif self.state == "eat":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >= self.eat_frame_rate:
                self.eat_frame_index = (self.eat_frame_index + 1) % self.eat_frame_count
                self.last_update_frame_time = current_time
        elif self.state == "death":
            if self.last_update_frame_time is None or current_time - self.last_update_frame_time >= self.death_frame_rate:
                self.death_frame_index = (self.death_frame_index + 1) % self.death_frame_count
                self.last_update_frame_time = current_time
                if self.death_frame_index == self.death_frame_count - 1:
                    self.kill()
        if self.life <= 0:
            self.state = "death"

    def draw(self, window):
        """绘制僵尸"""
        if self.state == "run":
            frame = self.run_animation[self.run_frame_index]
            width, height = frame.get_size()
            window.blit(frame, (self.x, self.y - height))
            if Constants.ZOMBIE_COLLISION_BOX:
                pygame.draw.rect(window, (255, 0, 0), (self.x + 75, self.y - height, width - 75, height), 2)
        elif self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            width, height = frame.get_size()
            window.blit(frame, (self.x, self.y - height))
            if Constants.ZOMBIE_COLLISION_BOX:
                pygame.draw.rect(window, (255, 0, 0), (self.x, self.y - height, width, height), 2)
        elif self.state == "jump":
            frame = self.jump_animation[self.jump_frame_index]
            width, height = frame.get_size()
            window.blit(frame, (self.x, self.y - height))
            if Constants.ZOMBIE_COLLISION_BOX:
                pygame.draw.rect(window, (255, 0, 0), (self.x, self.y - height, width, height), 2)
        elif self.state == "walk":
            frame = self.walk_animation[self.walk_frame_index]
            width, height = frame.get_size()
            window.blit(frame, (self.x, self.y - height))
            if Constants.ZOMBIE_COLLISION_BOX:
                pygame.draw.rect(window, (255, 0, 0), (self.x, self.y - height, width, height), 2)
        elif self.state == "eat":
            frame = self.eat_animation[self.eat_frame_index]
            width, height = frame.get_size()
            window.blit(frame, (self.x, self.y - height))
            if Constants.ZOMBIE_COLLISION_BOX:
                pygame.draw.rect(window, (255, 0, 0), (self.x, self.y - height, width, height), 2)
        elif self.state == "death":
            frame = self.death_animation[self.death_frame_index]
            width, height = frame.get_size()
            window.blit(frame, (self.x + 80, self.y - height))
            if Constants.ZOMBIE_COLLISION_BOX:
                pygame.draw.rect(window, (255, 0, 0), (self.x + 80, self.y - height, width, height), 2)
        self.rect = self.get_rect()

    def get_rect(self):
        if self.state == "run":
            frame = self.run_animation[self.run_frame_index]
            width, height = frame.get_size()
            return pygame.Rect(self.x + 75, self.y - height, width - 75, height)
        elif self.state == "await":
            frame = self.await_animation[self.await_frame_index]
            width, height = frame.get_size()
        elif self.state == "jump":
            frame = self.jump_animation[self.jump_frame_index]
            width, height = frame.get_size()
        elif self.state == "walk":
            frame = self.walk_animation[self.walk_frame_index]
            width, height = frame.get_size()
        elif self.state == "eat":
            frame = self.eat_animation[self.eat_frame_index]
            width, height = frame.get_size()
        elif self.state == "death":
            frame = self.death_animation[self.death_frame_index]
            width, height = frame.get_size()
        else:
            return pygame.Rect(0, 0, 0, 0)
        return pygame.Rect(self.x, self.y - height, width, height)


class FootballZombie(Zombie):
    """橄榄球僵尸"""
    def __init__(self, x, y):
        super().__init__(index=4, name="橄榄球僵尸", x=x, y=y, life=270, attack_power=4, attack_interval=40, walk_speed=1)
        self.walk_animation_path = f"{Constants.FOOTBALL_ZOMBIE}walk"
        self.walk_nohelmet_animation_path = f"{Constants.FOOTBALL_ZOMBIE}walk_nohelmet"
        self.eat_animation_path = f"{Constants.FOOTBALL_ZOMBIE}eat"
        self.death_animation_path = f"{Constants.FOOTBALL_ZOMBIE}death"