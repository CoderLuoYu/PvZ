import pygame
import sys
import Constants
import System
import tools


def main():
    # 初始化游戏
    try:
        pygame.init()
    except pygame.error:
        print("Pygame初始化失败")
        sys.exit()
    # 初始化音乐
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(f"{Constants.PLAYGROUND_SOUND_3}")
        pygame.mixer.music.play(-1)
    except pygame.error:
        print("Pygame音乐初始化失败")
        sys.exit()
    # 窗口大小
    screen = pygame.display.set_mode((Constants.GAME_WINDOW_WIDTH, Constants.GAME_WINDOW_HEIGHT), 0, 32)
    # 实例化系统类
    system = System.System()
    # 设置窗口标题
    pygame.display.set_caption("植物大战僵尸")
    # 时钟
    clock = pygame.time.Clock()
    # 游戏主循环
    while True:
        # 绘制窗口元素
        system.draw_window_element(screen)
        for event in pygame.event.get():
            """事件捕捉循环"""
            if event.type == pygame.QUIT:
                """检测退出事件"""
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                """检测鼠标事件"""
                # 得到鼠标按钮状态，返回一个序列代表所有mousebuttons状态的布尔值
                pressed_array = pygame.mouse.get_pressed()
                for index in range(len(pressed_array)):
                    if pressed_array[index]:
                        if index == 0:  # 当鼠标左键按下值为0
                            # 选择植物
                            if 76 <= event.pos[0] <= 585 and 9 <= event.pos[1] <= 78:
                                system.choose_botany(event.pos)
                            # 种植、铲除植物
                            if 102 <= event.pos[0] <= 831 and 87 <= event.pos[1] <= 568:
                                system.plant_botany(event.pos)
                                system.shovel_botany(event.pos)
                            # 选择铲子
                            if 598 <= event.pos[0] <= 673 and 0 <= event.pos[1] <= 75:
                                system.click_shovel()
                            # 暂停游戏
                            if 750 <= event.pos[0] <= 792 and 0 <= event.pos[1] <= 45:
                                system.pause(screen)
                            # 收集阳光
                            system.collect_sun(event.pos)
                            # print(event.pos)
        # 生成阳光
        system.produce_sun(pygame.time.get_ticks())
        # 生成僵尸
        system.create_zombie(pygame.time.get_ticks())
        # 显示所有精灵
        system.show_all_sprite(screen, pygame.time.get_ticks())
        # 植物与僵尸之间的碰撞检测
        system.check_collision(pygame.time.get_ticks())
        # 爆炸伤害结算
        system.apply_explosion_damage()
        # 唤醒植物
        system.wake_up_botany()
        # 植物攻击判断
        system.botany_attack_judge()
        # 植物攻击
        system.botany_attack(pygame.time.get_ticks())
        # 删除植物
        system.remove_botany()
        # 显示阳光
        system.show_sun(screen)
        # 阳光回收动画
        system.sun_animation(screen)
        # 铲子动画
        system.shovel_animation(screen, pygame.mouse.get_pos())
        # 拖动植物
        system.drag_botany_animation(screen, pygame.mouse.get_pos())
        # print(clock.get_fps())
        # 开启区域显示
        # tools.show_area_division(screen)
        # 设置帧率
        clock.tick(60)
        # 刷新屏幕
        pygame.display.flip()


if __name__ == "__main__":
    main()
