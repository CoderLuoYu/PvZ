import Others
import pygame
import random
import sys
import Constants
from image_loader import ImageLoader
import Botany
import Zombie


class System:
    def __init__(self):
        # 关卡索引
        self.level = 0
        # 僵尸列表
        self.Zombie_List = [Zombie.PoleVaultingZombie]
        # 植物卡牌列表
        self.botany_card_list = [Botany.Jalapeno, Botany.CoffeeBean, Botany.Repeater, Botany.Doomshroom,
                                 Botany.Threepeater, Botany.Wallnut, Botany.PotatoMine, Botany.Fumeshroom,
                                 Botany.Peashooter, Botany.Chomper]
        # 生成的阳光列表
        self.sun_list = []
        # 收集的阳光列表
        self.collected_sun_list = []
        # 阳光数量
        self.Sun_Number = 50
        # 全局精灵组
        self.all_sprite_group = pygame.sprite.Group()
        # 植物位置列表
        self.botany_position_list = [[[], [], [], [], [], [], [], [], []],
                                     [[], [], [], [], [], [], [], [], []],
                                     [[], [], [], [], [], [], [], [], []],
                                     [[], [], [], [], [], [], [], [], []],
                                     [[], [], [], [], [], [], [], [], []]]
        # 植物索引
        self.botany_index = None
        # 生成的僵尸列表
        self.zombie_list = []
        # 僵尸行列表
        self.zombie_row_list = [[], [], [], [], []]
        # 植物精灵组
        self.botany_sprite_group = pygame.sprite.Group()
        # 僵尸精灵组
        self.zombie_sprite_group = pygame.sprite.Group()
        # 子弹精灵组
        self.bullet_sprite_group = pygame.sprite.Group()
        # 召唤物精灵组
        self.summon_sprite_group = pygame.sprite.Group()
        # 效果精灵组
        self.effect_sprite_group = pygame.sprite.Group()
        # 小推车精灵组
        self.lawnmower_sprite_group = pygame.sprite.Group()
        for i in range(5):
            lawnmower = Others.LawnMower(0, 88 + 96 * i, i)
            self.lawnmower_sprite_group.add(lawnmower)
            self.all_sprite_group.add(lawnmower)
        # 植物拖动动画
        self.botany_drag_animation = None
        # 爆炸中心坐标
        self.explosion_center = []
        # 上一次生成僵尸的时间
        self.last_time = None
        # 僵尸生成间隔
        self.zombie_spawn_interval = 6000
        # 上一次生成阳光的时间
        self.last_sun_time = None
        # 铲子点击标记
        self.Shovel_Flag = False
        # 图像类
        self.image = ImageLoader()
        self.scene = self.image.load_image("白天", Constants.DAYTIME)
        self.card_slot = self.image.load_image("卡槽", Constants.CARD_SLOT)
        self.botany_card = self.image.load_card_images(Constants.BOTANY_CARD)
        self.LawnMower = self.image.load_animation("小推车", Constants.LAWNMOWER, 17)
        self.sun = self.image.load_animation("阳光", Constants.SUN, 29)
        self.shovel_slot = self.image.load_image("铲子槽", Constants.SHOVEL_SLOT)
        self.shovel = self.image.load_image("铲子", Constants.SHOVEL)
        self.progress_bar_frame = self.image.load_image("进度条框", f"{Constants.Level_PROGRESS_BAR}frame.jpg")
        self.money_frame = self.image.load_image("钱框", f"{Constants.Money}frame.png")
        self.pause_button = self.image.load_image("暂停按钮", f"{Constants.BUTTON}pause_button.png")
        self.continue_button = self.image.load_image("继续按钮", f"{Constants.BUTTON}continue_button.png")
        self.option_box = pygame.transform.scale(self.image.load_image("选项框", f"{Constants.BUTTON}option_box.jpg"),
                                                 (420, 300))
        # 声音
        self.button_clicked = pygame.mixer.Sound(Constants.CLICK_BUTTON)
        self.plant_sound = pygame.mixer.Sound(Constants.PLANT_SOUND)
        self.zombie_eat_sound = pygame.mixer.Sound(Constants.ZOMBIE_EAT_SOUND)
        self.lawnmower_sound = pygame.mixer.Sound(Constants.LAWNMOWER_SOUND)

    def draw_window_element(self, window):
        """绘制游戏窗口元素"""
        # 场景图片
        window.blit(self.scene, (0, 0), (150, 0, Constants.GAME_WINDOW_WIDTH, Constants.GAME_WINDOW_HEIGHT))
        # 卡槽
        window.blit(self.card_slot, (Constants.CARD_SLOT_LOCATION[0], Constants.CARD_SLOT_LOCATION[1]))
        window.blit(self.botany_card["Jalapeno"], (76, 9))
        window.blit(self.botany_card["CoffeeBean"], (127, 9))
        window.blit(self.botany_card["Repeater"], (178, 9))
        window.blit(self.botany_card["Doomshroom"], (229, 9))
        window.blit(self.botany_card["Threepeater"], (280, 9))
        window.blit(self.botany_card["Wallnut"], (331, 9))
        window.blit(self.botany_card["PotatoMine"], (382, 9))
        window.blit(self.botany_card["Fumeshroom"], (433, 9))
        window.blit(self.botany_card["Peashooter"], (484, 9))
        window.blit(self.botany_card["Chomper"], (535, 9))
        # 阳光数量
        font = pygame.font.SysFont("", 30)
        sunny_text = font.render(str(self.Sun_Number), True, (0, 0, 0))
        window.blit(sunny_text, (39 - sunny_text.get_width() / 2, 65))
        # 暂停按钮
        window.blit(self.pause_button, (750, 0))
        # 铲子槽
        shovel_slot = pygame.transform.scale(self.shovel_slot, (75, 75))
        window.blit(shovel_slot, (598, 0))
        # 关卡进度条
        window.blit(self.progress_bar_frame, (600, 570))
        # 钱
        window.blit(self.money_frame, (190, 565))
        money_text = font.render("103422", True, (255, 255, 0))
        window.blit(money_text, (240, 575))

    def pause(self, window):
        """暂停游戏"""
        self.button_clicked.play()
        continue_flag = False
        while True:
            self.draw_window_element(window)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    """检测鼠标事件"""
                    # 得到鼠标按钮状态，返回一个序列代表所有mousebuttons状态的布尔值
                    pressed_array = pygame.mouse.get_pressed()
                    for index in range(len(pressed_array)):
                        if pressed_array[index]:
                            if index == 0:  # 当鼠标左键按下值为0
                                # 继续游戏
                                if 308 <= event.pos[0] <= 440 and 341 <= event.pos[1] <= 376:
                                    continue_flag = True
                                    self.button_clicked.play()
            if continue_flag:
                break
            for i in range(len(self.sun_list)):
                self.sun_list[i].draw(window)
            for i in range(5):
                for j in range(9):
                    if self.botany_position_list[i][j]:
                        for botany in self.botany_position_list[i][j]:
                            if not self.botany_sprite_group.has(botany):
                                self.botany_position_list[i][j].remove(botany)
            for i in range(5):
                for j in range(9):
                    if len(self.botany_position_list[i][j]) == 1:
                        botany = self.botany_position_list[i][j][0]
                        if self.botany_sprite_group.has(botany):
                            botany.draw(window)
                        else:
                            self.botany_position_list[i][j].remove(botany)
                    elif len(self.botany_position_list[i][j]) == 2:
                        botany_1, botany_2 = self.botany_position_list[i][j]
                        if botany_1.name == "南瓜头":
                            botany_2.draw(window)
                            botany_1.draw(window)
                        else:
                            botany_1.draw(window)
                            botany_2.draw(window)
                    elif len(self.botany_position_list[i][j]) == 3:
                        botany_1, botany_2, botany_3 = self.botany_position_list[i][j]
                        if botany_1.name == "南瓜头":
                            botany_2.draw(window)
                            botany_1.draw(window)
                            botany_3.draw(window)
                        elif botany_2.name == "南瓜头":
                            botany_3.draw(window)
                            botany_2.draw(window)
                            botany_1.draw(window)
                        else:
                            botany_2.draw(window)
                            botany_3.draw(window)
                            botany_1.draw(window)
            for bullet in self.bullet_sprite_group:
                bullet.draw(window)
            for i in range(5):
                if self.zombie_row_list[i]:
                    for zombie in self.zombie_row_list[i]:
                        if self.zombie_sprite_group.has(zombie):
                            zombie.draw(window)
                        else:
                            self.zombie_row_list[i].remove(zombie)
            for summon in self.summon_sprite_group:
                summon.draw(window)
            for lawnmower in self.lawnmower_sprite_group:
                lawnmower.draw(window)
            for effect in self.effect_sprite_group:
                effect.draw(window)
            for sun in self.sun_list:
                sun.draw(window)
            # 创建一个与窗口大小相同的Surface对象，并设置其为半透明
            overlay = pygame.Surface((Constants.GAME_WINDOW_WIDTH, Constants.GAME_WINDOW_HEIGHT), pygame.SRCALPHA)
            # 填充灰色，透明度为128（50%透明）
            overlay.fill((0, 0, 0, 128))
            window.blit(overlay, (0, 0))
            window.blit(self.option_box, (240, 100))
            pygame.draw.rect(window, (255, 0, 0), (308, 260, 132, 35), 2)
            # pygame.draw.rect(window, (255, 0, 0), (308, 341, 132, 35), 2)
            pygame.display.flip()

    def produce_sun(self, current_time):
        """生成阳光"""
        if self.last_sun_time is None or current_time - self.last_sun_time >= Constants.SUN_PRODUCE_INTERVAL:
            x = random.randint(50, 750)
            y = -200
            end_y = random.randint(50, 500)
            sun = Others.Sun(x, y, end_y)
            self.sun_list.append(sun)
            self.last_sun_time = current_time

    def show_sun(self, window):
        """显示阳光"""
        for sun in self.sun_list:
            # 清除
            sun.delete()
            # 更新状态
            sun.update()
            # 绘制
            sun.draw(window)

    def delete_sun(self):
        """清除阳光"""
        for sun in self.sun_list:
            if sun.delete_flag:
                self.sun_list.pop(self.sun_list.index(sun))

    def collect_sun(self, pos):
        """收集阳光"""
        x, y = pos
        if self.sun_list:
            for sun in self.sun_list:
                if sun.rect.x <= x <= sun.rect.x + 79 and sun.rect.y <= y <= sun.rect.y + 79:
                    self.collected_sun_list.append([sun.rect.x, sun.rect.y, 0, 0])
                    self.sun_list.pop(self.sun_list.index(sun))
                    self.Sun_Number += 25

    def sun_animation(self, window):
        """阳光动画"""
        if self.collected_sun_list:
            for sun in self.collected_sun_list:
                if sun[2] == 0 and sun[3] == 0:
                    sun[2] = int(sun[0] * 0.1)
                    sun[3] = int(sun[1] * 0.1)
                sun[0] -= sun[2]
                sun[1] -= sun[3]
                window.blit(self.sun[0], (sun[0], sun[1]))
                if sun[0] <= 10:
                    self.collected_sun_list.pop(self.collected_sun_list.index(sun))

    def create_zombie(self, current_time):
        """生成僵尸"""
        if current_time >= 0 and (self.last_time is None or current_time - self.last_time >= 6000):
            numbers = [165, 265, 365, 465, 565]
            index = random.randint(0, len(self.Zombie_List) - 1)
            zombie_type = self.Zombie_List[index]
            x = 900
            y = random.choice(numbers)
            zombie = zombie_type(x, y)
            zombie.row = numbers.index(y)
            self.zombie_list.append(zombie)
            self.zombie_sprite_group.add(zombie)
            self.all_sprite_group.add(zombie)
            self.zombie_row_list[zombie.row].append(zombie)
            self.last_time = current_time

    def adjust_spawn_interval(self, current_time):
        """调整僵尸生成间隔"""
        # 根据游戏时间调整生成间隔
        if current_time < 60000:  # 前1分钟
            self.zombie_spawn_interval = 6000
        elif current_time < 120000:  # 1-2分钟
            self.zombie_spawn_interval = 5000
        elif current_time < 180000:  # 2-3分钟
            self.zombie_spawn_interval = 4000
        elif current_time < 240000:  # 3-4分钟
            self.zombie_spawn_interval = 3000
        else:  # 4分钟以后
            self.zombie_spawn_interval = 2000

    def choose_zombie_type(self, current_time):
        """选择僵尸类型"""
        # 根据游戏时间调整僵尸类型概率
        if current_time < 60000:  # 前1分钟
            probabilities = [0.8, 0.1, 0.05, 0.03, 0.02]
        elif current_time < 120000:  # 1-2分钟
            probabilities = [0.6, 0.2, 0.1, 0.08, 0.02]
        elif current_time < 180000:  # 2-3分钟
            probabilities = [0.4, 0.3, 0.2, 0.08, 0.04]
        elif current_time < 240000:  # 3-4分钟
            probabilities = [0.3, 0.3, 0.25, 0.1, 0.05]
        else:  # 4分钟以后
            probabilities = [0.2, 0.3, 0.25, 0.15, 0.1]

        # 根据概率选择僵尸类型
        zombie_type = random.choices(self.Zombie_List, probabilities)[0]
        return zombie_type

    def grid_location(self, pos):
        """计算格子位置"""
        x, y = pos
        for i in range(9):
            for j in range(5):
                if 102 + 81 * i <= x <= 102 + 81 * (i + 1) and 87 + 96 * j <= y <= 87 + 96 * (j + 1):
                    return i, j

    def choose_botany(self, pos):
        """选择植物"""
        if self.botany_index is None:
            x, y = pos
            for i in range(10):
                if 76 + 51 * i <= x <= 126 + 51 * i:
                    self.botany_index = i
        else:
            self.botany_index = None
            self.botany_drag_animation = None

    def drag_botany_animation(self, window, pos):
        """拖动植物动画"""
        if self.botany_index is not None:
            x, y = pos
            for i in range(9):
                for j in range(5):
                    left = 102 + 81 * i
                    right = 102 + 81 * (i + 1)
                    top = 87 + 96 * j
                    bottom = 87 + 96 * (j + 1)
                    if left <= x <= right and top <= y <= bottom:
                        s = pygame.Surface((81, 96), pygame.SRCALPHA)
                        s.fill((255, 255, 255, 79))  # 白色，30%透明度
                        # 绘制整行和整列的透明层
                        for col in range(9):
                            window.blit(s, (102 + 81 * col, top))
                        for row in range(5):
                            window.blit(s, (left, 87 + 96 * row))
                        break
                else:
                    continue
                break
            if not self.botany_drag_animation:
                botany = self.botany_card_list[self.botany_index](0, 0)
                self.botany_drag_animation = botany.await_animation[0]
            if self.botany_drag_animation:
                window.blit(self.botany_drag_animation, (x - self.botany_drag_animation.get_width() / 2,
                                                         y - self.botany_drag_animation.get_height() / 2))

    def plant_botany(self, pos):
        """植物种植"""
        if self.botany_index is not None:
            i, j = self.grid_location(pos)
            botany = self.botany_card_list[self.botany_index](110 + 83 * i, 165 + 100 * j)
            if botany.name == "咖啡豆":
                if self.botany_position_list[j][i]:
                    for botany_1 in self.botany_position_list[j][i]:
                        if "shroom" in botany_1.ability:
                            botany.row = j
                            botany.column = i
                            self.botany_index = None
                            self.botany_sprite_group.add(botany)
                            self.all_sprite_group.add(botany)
                            self.botany_position_list[j][i].append(botany)
                            self.Sun_Number -= botany.sun_number
                            self.botany_drag_animation = []
                        else:
                            self.botany_index = None
                            self.botany_drag_animation = None
                else:
                    self.botany_index = None
                    self.botany_drag_animation = None
            else:
                botany.row = j
                botany.column = i
                self.botany_index = None
                self.botany_sprite_group.add(botany)
                self.all_sprite_group.add(botany)
                self.botany_position_list[j][i].append(botany)
                self.Sun_Number -= botany.sun_number
                self.botany_drag_animation = None
                self.plant_sound.play()

    def botany_attack_judge(self):
        """植物攻击判断"""
        for botany in self.botany_sprite_group:
            if "attack" in botany.ability:
                if botany.attack_range == "前方一行":
                    if self.zombie_row_list[botany.row]:
                        count_1 = 0
                        for zombie in self.zombie_row_list[botany.row]:
                            if zombie.state != "death":
                                if botany.x <= zombie.x:
                                    botany.state = "attack"
                                    break
                                else:
                                    count_1 += 1
                            else:
                                count_1 += 1
                        if count_1 == len(self.zombie_row_list[botany.row]):
                            botany.state = "await"
                    else:
                        botany.state = "await"
                elif botany.attack_range == "前方三行":
                    if botany.row == 1 or botany.row == 2 or botany.row == 3:
                        count_1, count_2 = 0, 0
                        for i in range(-1, 2):
                            if self.zombie_row_list[botany.row + i]:
                                for zombie in self.zombie_row_list[botany.row + i]:
                                    if zombie.state != "death":
                                        if botany.x <= zombie.x:
                                            botany.state = "attack"
                                            break
                                        else:
                                            count_2 += 1
                                    else:
                                        count_2 += 1
                            else:
                                count_1 += 1
                        if count_1 == 3 or count_2 == len(self.zombie_row_list) +\
                                len(self.zombie_row_list[botany.row - 1]) +\
                                len(self.zombie_row_list[botany.row + 1]):
                            botany.state = "await"
                    elif botany.row == 0:
                        count_1, count_2 = 0, 0
                        for i in range(2):
                            if self.zombie_row_list[botany.row + i]:
                                for zombie in self.zombie_row_list[botany.row + i]:
                                    if zombie.state != "death":
                                        if botany.x <= zombie.x:
                                            botany.state = "attack"
                                            break
                                        else:
                                            count_2 += 1
                                    else:
                                        count_2 += 1
                            else:
                                count_1 += 1
                        if count_1 == 2 or count_2 == len(self.zombie_row_list) +\
                                len(self.zombie_row_list[botany.row + 1]):
                            botany.state = "await"
                    elif botany.row == 4:
                        count_1, count_2 = 0, 0
                        for i in range(-1, 1):
                            if self.zombie_row_list[botany.row + i]:
                                for zombie in self.zombie_row_list[botany.row + i]:
                                    if zombie.state != "death":
                                        if botany.x <= zombie.x:
                                            botany.state = "attack"
                                            break
                                        else:
                                            count_2 += 1
                                    else:
                                        count_2 += 1
                            else:
                                count_1 += 1
                        if count_1 == 2 or count_2 == len(self.zombie_row_list) +\
                                len(self.zombie_row_list[botany.row - 1]):
                            botany.state = "await"
                elif botany.attack_range == "前后一行":
                    if self.zombie_row_list[botany.row]:
                        for zombie in self.zombie_row_list[botany.row]:
                            if zombie.state != "death":
                                botany.state = "attack"
                            else:
                                botany.state = "await"
                    else:
                        botany.state = "await"
                elif botany.attack_range == "全屏":
                    if self.zombie_sprite_group:
                        botany.state = "attack"
                    else:
                        botany.state = "await"
                elif botany.attack_range == "所在格":
                    pass
                elif botany.attack_range == "前方1.5格":
                    if botany.state == "await":
                        if self.zombie_row_list[botany.row]:
                            for zombie in self.zombie_row_list[botany.row]:
                                if 0 <= zombie.x - botany.x <= 190:
                                    if zombie.state != "death":
                                        botany.state = "attack"
                                        break
                elif botany.attack_range == "前方4格":
                    if botany.state == "await":
                        if self.zombie_row_list[botany.row]:
                            for zombie in self.zombie_row_list[botany.row]:
                                if 0 <= zombie.x - botany.x <= 450:
                                    if zombie.state != "death":
                                        botany.state = "attack"
                                        break
                    elif botany.state == "attack":
                        if not self.zombie_row_list[botany.row]:
                            botany.state = "await"
                        else:
                            count = 0
                            for zombie in self.zombie_row_list[botany.row]:
                                if zombie.x - botany.x > 450 or zombie.x - botany.x < 0:
                                    count += 1
                                elif zombie.state == "death":
                                    count += 1
                            if count == len(self.zombie_row_list[botany.row]):
                                botany.state = "await"

    def botany_attack(self, current_time):
        """植物攻击"""
        for botany in self.botany_sprite_group:
            if "attack" in botany.ability:
                if botany.state == "attack":
                    bullets = botany.attack(current_time)
                    if bullets:
                        for bullet in bullets:
                            self.bullet_sprite_group.add(bullet)
                            self.all_sprite_group.add(bullet)
            elif "produce" in botany.ability:
                summon = botany.produce(current_time)
                if summon:
                    self.summon_sprite_group.add(summon)
                    self.all_sprite_group.add(summon)
            elif "ash" in botany.ability:
                if botany.state == "explore":
                    effects = botany.explore()
                    if effects:
                        for effect in effects:
                            self.effect_sprite_group.add(effect)
                            self.all_sprite_group.add(effect)

    def wake_up_botany(self):
        """唤醒植物"""
        if Botany.CoffeeBean in self.botany_card_list:
            for botany_1 in self.botany_sprite_group:
                if botany_1.name == "咖啡豆":
                    if botany_1.state == "crumble" and botany_1.crumble_frame_index == 14:
                        for botany_2 in self.botany_sprite_group:
                            if "shroom" in botany_2.ability:
                                if botany_1.row == botany_2.row and botany_1.column == botany_2.column:
                                    botany_2.state = "await"
                                    botany_1.kill()
                                else:
                                    botany_1.kill()

    def show_all_sprite(self, window, current_time):
        """显示所有精灵"""
        # 先绘制植物后绘制子弹，最后绘制僵尸，绘制植物时按行索引升序绘制
        for i in range(5):
            for j in range(9):
                if self.botany_position_list[i][j]:
                    for botany in self.botany_position_list[i][j]:
                        if not self.botany_sprite_group.has(botany):
                            self.botany_position_list[i][j].remove(botany)
        for i in range(5):
            for j in range(9):
                if len(self.botany_position_list[i][j]) == 1:
                    botany = self.botany_position_list[i][j][0]
                    if self.botany_sprite_group.has(botany):
                        botany.update(current_time)
                        botany.draw(window)
                    else:
                        self.botany_position_list[i][j].remove(botany)
                elif len(self.botany_position_list[i][j]) == 2:
                    botany_1, botany_2 = self.botany_position_list[i][j]
                    botany_1.update(current_time)
                    botany_2.update(current_time)
                    if botany_1.name == "南瓜头":
                        botany_2.draw(window)
                        botany_1.draw(window)
                    else:
                        botany_1.draw(window)
                        botany_2.draw(window)
                elif len(self.botany_position_list[i][j]) == 3:
                    botany_1, botany_2, botany_3 = self.botany_position_list[i][j]
                    botany_1.update(current_time)
                    botany_2.update(current_time)
                    botany_3.update(current_time)
                    if botany_1.name == "南瓜头":
                        botany_2.draw(window)
                        botany_1.draw(window)
                        botany_3.draw(window)
                    elif botany_2.name == "南瓜头":
                        botany_3.draw(window)
                        botany_2.draw(window)
                        botany_1.draw(window)
                    else:
                        botany_2.draw(window)
                        botany_3.draw(window)
                        botany_1.draw(window)
        for bullet in self.bullet_sprite_group:
            bullet.update(current_time)
            bullet.draw(window)
        for i in range(5):
            if self.zombie_row_list[i]:
                for zombie in self.zombie_row_list[i]:
                    if self.zombie_sprite_group.has(zombie):
                        zombie.update(current_time)
                        zombie.draw(window)
                    else:
                        self.zombie_row_list[i].remove(zombie)
        for summon in self.summon_sprite_group:
            summon.update(current_time)
            summon.draw(window)
        for lawnmower in self.lawnmower_sprite_group:
            lawnmower.update(current_time)
            lawnmower.draw(window)
        for effect in self.effect_sprite_group:
            effect.update(current_time)
            effect.draw(window)

    def remove_botany(self):
        """删除已死亡的植物"""
        for botany in self.botany_sprite_group.copy():
            if botany.life <= 0:
                self.botany_sprite_group.remove(botany)
                self.all_sprite_group.remove(botany)
                self.botany_position_list[botany.row][botany.column].remove(botany)

    def check_collision(self, current_time):
        """碰撞检测"""
        # 僵尸与植物
        collisions = pygame.sprite.groupcollide(self.zombie_sprite_group, self.botany_sprite_group, False, False)
        for zombie, botanys in collisions.items():
            count = 0
            for botany in botanys:
                if botany.row == zombie.row:
                    if zombie.name == "撑杆僵尸":
                        if zombie.state == "run":
                            zombie.state = "await"
                        elif zombie.state == "walk":
                            zombie.state = "eat"
                            if zombie.last_eat_time is None or current_time - zombie.last_eat_time >= zombie.attack_interval:
                                botany.life -= zombie.attack_power
                                zombie.last_eat_time = current_time
                                self.zombie_eat_sound.play()
                    else:
                        if botany.name == "地刺" or botany.name == "钢地刺":
                            botany.state = "attack"
                            if botany.last_attack_time is None or current_time - botany.last_attack_time >= botany.attack_interval:
                                zombie.life -= botany.attack_power
                                botany.last_attack_time = current_time
                        elif botany.name == "大嘴花":
                            if botany.state == "attack":
                                if botany.last_attack_time is None or current_time - botany.last_attack_time >=\
                                        botany.attack_interval:
                                    botany.last_attack_time = current_time
                                    zombie.life -= botany.attack_power
                                if zombie.life <= 0 and botany.attack_frame_index == botany.attack_frame_count - 1:
                                    botany.state = "chew"
                            else:
                                zombie.state = "eat"
                                botany.life -= zombie.attack_power
                        elif botany.name == "土豆地雷":
                            if botany.state == "await":
                                botany.state = "explore"
                            elif botany.state == "rise":
                                zombie.state = "eat"
                                if zombie.last_eat_time is None or current_time - zombie.last_eat_time >=\
                                        zombie.attack_interval:
                                    botany.life -= zombie.attack_power
                                    zombie.last_eat_time = current_time
                                    self.zombie_eat_sound.play()
                        else:
                            zombie.state = "eat"
                            if zombie.last_eat_time is None or current_time - zombie.last_eat_time >=\
                                    zombie.attack_interval:
                                botany.life -= zombie.attack_power
                                zombie.last_eat_time = current_time
                                self.zombie_eat_sound.play()
                else:
                    count += 1
            if count == len(botanys):
                if zombie.name == "撑杆僵尸":
                    if zombie.state == "eat":
                        zombie.state = "walk"
                else:
                    zombie.state = "walk"
        # 把没有与植物碰撞的僵尸改为walk状态
        for zombie in self.zombie_sprite_group:
            if zombie.state == "eat" and zombie not in collisions:
                zombie.state = "walk"
                # 重置上次吃僵尸的时间
                zombie.last_eat_time = None
        # 把没有与僵尸碰撞的地刺和钢地刺改为await状态
        for botany in self.botany_sprite_group:
            if "地刺" in botany.name and botany.state == "attack" and all(botany not in botanys for botanys in collisions.values()):
                botany.state = "await"
        # 僵尸与子弹
        collisions = pygame.sprite.groupcollide(self.zombie_sprite_group, self.bullet_sprite_group, False, False)
        for zombie, bullets in collisions.items():
            for bullet in bullets:
                # 范围伤害
                if "星星果" in bullet.name:
                    zombie.life -= bullet.damage
                    bullet.kill()
                # 穿透伤害
                elif "大喷菇" in bullet.name:
                    pass
                else:
                    if zombie.row == bullet.row:
                        zombie.life -= bullet.damage
                        bullet.kill()
        # 子弹与僵尸
        collisions = pygame.sprite.groupcollide(self.bullet_sprite_group, self.zombie_sprite_group, False, False)
        for bullet, zombies in collisions.items():
            if "大喷菇" in bullet.name:
                if not bullet.damage_flag:
                    for zombie in zombies:
                        if zombie.row == bullet.row:
                            zombie.life -= bullet.damage
                    bullet.damage_flag = True
        # 植物与子弹
        collisions = pygame.sprite.groupcollide(self.botany_sprite_group, self.bullet_sprite_group, False, False)
        for botany, bullets in collisions.items():
            if botany.name == "火炬树桩":
                for bullet in bullets:
                    if bullet.row == botany.row:
                        if "射手" in bullet.name:
                            if "寒冰" in bullet.name:
                                bullet_1 = Botany.Bullet(bullet.x, bullet.y, bullet.row, bullet.speed, 20, bullet.name,
                                                         f"{Constants.PEASHOOTER}bullet", 1, bullet.frame_rate,
                                                         bullet.i)
                            else:
                                bullet_1 = Botany.Bullet(bullet.x, bullet.y, bullet.row, bullet.speed, 40, bullet.name,
                                                         f"{Constants.PEASHOOTER}bullet_1", 25, bullet.frame_rate,
                                                         bullet.i)
                            self.all_sprite_group.add(bullet_1)
                            self.bullet_sprite_group.add(bullet_1)
                            bullet.kill()
        # 僵尸与小推车
        collisions = pygame.sprite.groupcollide(self.lawnmower_sprite_group, self.zombie_sprite_group, False, False)
        for lawnmower, zombies in collisions.items():
            for zombie in zombies:
                if zombie.row == lawnmower.row and zombie.rect.x - lawnmower.rect.x <= 30:
                    zombie.kill()
                    if lawnmower.state == "await":
                        self.lawnmower_sound.play()
                    lawnmower.state = "trigger"

    def apply_explosion_damage(self):
        """灰烬植物对半径范围内的僵尸造成爆炸伤害"""
        for effect in self.effect_sprite_group:
            if "火爆辣椒" in effect.name:
                for zombie in self.zombie_sprite_group:
                    if zombie.row == effect.center_row:
                        zombie.life -= effect.damage
            elif "末日菇" in effect.name or "樱桃炸弹" in effect.name or "土豆地雷" in effect.name:
                for zombie in self.zombie_sprite_group:
                    if ((zombie.rect.x - effect.center_row[0]) ** 2 + (zombie.rect.y - effect.center_row[1]) ** 2) \
                            ** 0.5 <= effect.radius:
                        zombie.life -= effect.damage

    def click_shovel(self):
        """点击铲子"""
        if self.Shovel_Flag:
            self.Shovel_Flag = False
        elif not self.Shovel_Flag:
            self.Shovel_Flag = True

    def shovel_animation(self, window, pos):
        """铲子动画"""
        x, y = pos
        if self.Shovel_Flag:
            for i in range(9):
                for j in range(5):
                    left = 102 + 81 * i
                    right = 102 + 81 * (i + 1)
                    top = 87 + 96 * j
                    bottom = 87 + 96 * (j + 1)
                    if left <= x <= right and top <= y <= bottom:
                        s = pygame.Surface((81, 96), pygame.SRCALPHA)
                        s.fill((255, 255, 255, 79))  # 白色，30%透明度
                        # 绘制整行和整列的透明层
                        for col in range(9):
                            window.blit(s, (102 + 81 * col, top))
                        for row in range(5):
                            window.blit(s, (left, 87 + 96 * row))
                        break
                else:
                    continue
                break
            window.blit(self.shovel, (x - 40, y - 40))

    def shovel_botany(self, pos):
        """铲除植物"""
        if self.Shovel_Flag:
            i, j = self.grid_location(pos)
            for botany in self.botany_position_list[j][i]:
                if botany.x == 110 + 83 * i and botany.y == 165 + 100 * j:
                    self.botany_sprite_group.remove(botany)
                    self.botany_position_list[j][i].remove(botany)
                    self.all_sprite_group.remove(botany)
                    self.Shovel_Flag = False
                    break
