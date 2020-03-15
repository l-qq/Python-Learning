import pygame
from plane_sprites import *

class PlaneGame(object):
    """飞机大战主游戏"""
    def __init__(self):
        print("游戏初始化")
        # 创建游戏窗口
        self.screen = pygame.display.set_mode(SCREEN_RECT.size)  # API: pygame.display.set_mode() Initialize a window or screen for display set_mode(size=(0, 0), flags=0, depth=0, display=0) -> Surface
        # 创建游戏时钟
        self.clock = pygame.time.Clock()
        # 调用私有方法，创建精灵、精灵组
        self.__create_sprites()
        # 设置定时器事件，创建敌机，间隔 1s
        pygame.time.set_timer(CREATE_ENEMY_EVENT, 1000)  # API: pygame.time.set_timer() repeatedly create an event on the event queue set_timer(eventid, milliseconds) -> None set_timer(eventid, milliseconds, once) -> None
        pygame.time.set_timer(HERO_FIRE_EVENT, 500)

    def __create_sprites(self):
        # 创建背景精灵和精灵组
        bg1 = Background()
        bg2 = Background(True)
        self.back_group = pygame.sprite.Group(bg1, bg2)  # API: pygame.sprite.Group A container class to hold and manage multiple Sprite objects. Group(*sprites) -> Group
        # 创建敌机的精灵组
        self.enemy_group = pygame.sprite.Group()
        # 创建英雄的精灵和精灵组
        self.hero = Hero()
        self.hero_group = pygame.sprite.Group(self.hero)

    def start_game(self):
        print("游戏开始......")

        # 无限循环
        while True:
            # 设置游戏刷新帧率
            self.clock.tick(FRAME_PER_SEC)  # API: tick() update the clock tick(framerate=0) -> milliseconds
            # 事件监听
            self.__event_handler()
            # 碰撞检测
            self.__check_collide()
            # 更新/绘制精灵组
            self.__update_sprites()
            # 更新屏幕显示
            pygame.display.update()  # API: pygame.display.update() Update portions of the screen for software displays update(rectangle=None) -> None update(rectangle_list) -> None

    def __event_handler(self):
        for event in pygame.event.get():  # API: pygame.event.get() get events from the queue get(eventtype=None) -> Eventlist get(eventtype=None, pump=True) -> Eventlist
            if event.type == pygame.QUIT :  ## pygame.QUIT = 12, type : int
                PlaneGame.__game_over()
            elif event.type == CREATE_ENEMY_EVENT:
                print("敌机出场......")
                # 创建敌机精灵
                enemy = Enemy()
                # 添加敌机精灵到精灵组
                self.enemy_group.add(enemy)
            elif event.type == HERO_FIRE_EVENT:
                self.hero.fire()
            # elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            #     print("向右移动......")
        # 使用键盘提供的方法获取按键
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_RIGHT]:
            print("持续向右移动......")
            self.hero.speed = 2
        elif keys_pressed[pygame.K_LEFT]:
            self.hero.speed = -2
        else:
            self.hero.speed = 0

    def __check_collide(self):
        # 子弹摧毁敌机
        pygame.sprite.groupcollide(self.hero.bullets, self.enemy_group, True, True)  # API: pygame.sprite.groupcollide() Find all sprites that collide between two groups. groupcollide(group1, group2, dokill1, dokill2, collided = None) -> Sprite_dict
        # 敌机撞毁英雄
        enemies = pygame.sprite.spritecollide(self.hero, self.enemy_group, True)
        # 判断列表内容
        if len(enemies) > 0:
            # 让英雄牺牲
            self.hero.kill()
            # 结束游戏
            PlaneGame.__game_over()

    def __update_sprites(self):
        self.back_group.update()  # API: pygame.sprite.Group.update call the update method on contained Sprites
        self.back_group.draw(self.screen)  # API: draw() blit the Sprite images draw(Surface) -> None
        self.enemy_group.update()
        self.enemy_group.draw(self.screen)
        self.hero_group.update()
        self.hero_group.draw(self.screen)
        self.hero.bullets.update()
        self.hero.bullets.draw(self.screen)


    @staticmethod
    def __game_over():
        print("游戏结束")
        pygame.quit()  # 卸载 pygame 模块并退出，没有使用类/实例的变量，故用静态方法
        exit()

if __name__ == "__main__":
    # 创建游戏对象
    game = PlaneGame()

    # 启动游戏
    game.start_game()