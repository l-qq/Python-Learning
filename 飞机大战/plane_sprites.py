import random
import pygame

# 屏幕大小的常量
SCREEN_RECT = pygame.Rect(0, 0, 480, 700)  # API: pygame.Rect pygame object for storing rectangular coordinates Rect(left, top, width, height) -> Rect Rect((left, top), (width, height)) -> Rect Rect(object) -> Rect
# 刷新的帧率
FRAME_PER_SEC = 60
# 创建敌机的定时器常量
CREATE_ENEMY_EVENT = pygame.USEREVENT
# 英雄发射子弹事件
HERO_FIRE_EVENT = pygame.USEREVENT + 1

class GameSprite(pygame.sprite.Sprite):
    """飞机大战游戏精灵"""
    def __init__(self, image_name, speed=1):
        # 调用父类的初始化方法
        super().__init__()
        # 定义对象的属性
        self.image = pygame.image.load(image_name)  # API: pygame.image.load() load new image from a file load(filename) -> Surface load(fileobj, namehint="") -> Surface
        self.rect = self.image.get_rect()  # API: get_rect() get the rectangular area of the Surface get_rect(**kwargs) -> Rect
        self.speed = speed
        
    def update(self):
        # 在屏幕的垂直方向上移动
        self.rect.y += self.speed

class Background(GameSprite):
    """游戏背景精灵"""
    def __init__(self, is_alt=False):
        # 调用父类方法实现精灵创建
        super().__init__("./images/background.png")
        # 设置背景图片初始位置
        if is_alt:
            self.rect.y = -self.rect.height

    def update(self):
        # 调用父类方法实现
        super().update()
        # 如果移出屏幕，将图像设置到屏幕上方
        if self.rect.y >= SCREEN_RECT.height:
            self.rect.y = -self.rect.height

class Enemy(GameSprite):
    """敌机精灵"""
    def __init__(self):
        # 调用父类方法创建敌机精灵，同时指定图片
        super().__init__("./images/enemy1.png")
        # 指定初始随机速度
        self.speed = random.randint(1, 3)
        # 指定初始随机位置
        self.rect.bottom = 0
        max_x = SCREEN_RECT.width - self.rect.width
        self.rect.x = random.randint(0, max_x)


    def update(self):
        # 调用父类方法保持垂直方向飞行
        super().update()
        # 判断是否飞出屏幕，如果是，需要从精灵组中删除敌机
        if self.rect.y >= SCREEN_RECT.height:
            print("飞机飞出屏幕了，需要删除......")
            self.kill()  # API: pygame.sprite.Sprite.kill kill() remove the Sprite from all Groups kill() -> None

    def __del__(self):
        print("敌机挂了 %s" % self.rect)

class Hero(GameSprite):
    """英雄精灵"""
    def __init__(self):
        # 调用父类方法，设置image&speed
        super().__init__("./images/me1.png", 0)
        # 设置初始位置
        self.rect.centerx = SCREEN_RECT.centerx
        self.rect.bottom = SCREEN_RECT.bottom - 120
        # 创建子弹精灵组
        self.bullets = pygame.sprite.Group()

    def update(self):
        # 英雄在水平方向移动
        self.rect.x += self.speed
        # 控制英雄不能离开屏幕
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.right > SCREEN_RECT.right:
            self.rect.right = SCREEN_RECT.right

    def fire(self):
        print("发射子弹...")
        for i in (0, 1, 2):
            # 创建子弹精灵
            bullet = Bullet()
            # 设置精灵位置
            bullet.rect.bottom = self.rect.y - i * 20
            bullet.rect.centerx = self.rect.centerx
            # 将精灵添加到精灵组
            self.bullets.add(bullet)

class Bullet(GameSprite):
    """子弹精灵"""
    def __init__(self):
        # 调用父类方法，设置子弹图片，设置初始速度
        super().__init__("./images/bullet1.png", -2)

    def update(self):
        # 调用父类方法，让子弹垂直飞行
        super().update()
        # 判断子弹是否飞出屏幕
        if self.rect.bottom < 0:
            self.kill()

    def __del__(self):
        print("子弹飞出屏幕")
