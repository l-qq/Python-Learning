# 飞机大战项目

## 项目概述

基于 python3，使用面向对象的思路，开发飞机大战游戏

### 效果图

### 文件说明

plane_main.py 主程序
plane_sprites.py 精灵工具类

## 开发流程

- 安装 [pygame](https://www.pygame.org/) 第三方包，`sudo pip3 install pygame`
- 验证 pygame 包安装成功，`python3 -m pygame.examples.aliens`
- 游戏开发原理
  - 把**静止的图像**绘制到**游戏窗口**中
  - 根据**用户交互**或者**移动**图像，产生**动画效果**
  - 判断**图像之间**是否重叠（飞机坠毁）
- 框架搭建
  - plane_main.py 主程序
    - 初始化
    - 游戏主循环
      - 事件监听
      - 碰撞检测
      - 更新精灵组的内容
      - 屏幕显示 pygame.display.update()
  - plane_sprites.py 精灵工具类
    - 基本精灵
    - 背景图片
    - 敌机
    - 英雄
    - 子弹
- 背景图像
  - 创建 class Background(GameSprite)
  - 主程序初始化添加两张背景精灵
  - 更新精灵组的内容
- 敌人飞机
  - 创建 class Enemy(GameSprite)
  - 主程序初始化添加敌机精灵组
  - 主程序初始化添加出现敌机定时器事件
  - 主程序事件监听响应
  - 添加并更新精灵组的内容
- 英雄飞机
  - 创建 class Hero(GameSprite)
  - 主程序初始化添加英雄精灵组
  - 主程序事件监听键盘响应
  - 更新英雄 精灵组的内容
- 发射子弹
  - 主程序初始化添加发射子弹定时器事件
  - 主程序事件监听响应
  - 创建 class Bullet(GameSprite)
  - 英雄添加子弹精灵
- 碰撞检测
  - 主程序碰撞检测
    - 子弹碰撞检测
    - 英雄撞毁检测

## 学习笔记

[文档：飞机大战.note](http://note.youdao.com/noteshare?id=b34edffb163f1e09502d97425ec8e4ea&sub=BC0EF876FC1B4189B4E1A7D96BDC9502)

### 包和模块的不同导入方式，决定了使用时的不同前缀，例如

``` txt
|- pygame（文件夹）
    |- __init__.py
    |- base.py（该模块包含 init() 函数，windows 平台上为 base.xxx.pyd）
    ...
```

包 `pygame` 的 `__init__.py` 包含了 `from pygame.base import *`，所以 `import pygame` 后，可以直接使用 `pygame.init()`

``` txt
|- package（文件夹）
    |- __init__.py
    |- module.py（该模块包含 f1() 函数）
    ...
```

包 `package` 的 `__init__.py` 包含了 `from . import module`，所以 `import package` 后，需要使用 `package.module.f1()`

### 包和模块的属性列表中，`__file__` 和 `__path__` 有区别，例如

包的属性列表（可以使用`dir()`函数查看）既有 `__file__` 又有 `__path__`，如 `pygame` 包

``` powershell
>>> pygame.__file__
'C:\\Users\\A1718\\scoop\\apps\\python\\current\\lib\\site-packages\\pygame\\__init__.py'
>>> pygame.__path__
['C:\\Users\\A1718\\scoop\\apps\\python\\current\\lib\\site-packages\\pygame']
>>> pygame.__package__
'pygame'
>>> pygame
<module 'pygame' from 'C:\\Users\\A1718\\scoop\\apps\\python\\current\\lib\\site-packages\\pygame\\__init__.py'>
```

模块的属性列表（可以使用`dir()`函数查看）没有 `__path__`，如 `pygame。base` 模块

``` powershell
>>> pygame.base.__file__
'C:\\Users\\A1718\\scoop\\apps\\python\\current\\lib\\site-packages\\pygame\\base.cp38-win_amd64.pyd'
>>> pygame.base.__path__
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: module 'pygame.base' has no attribute '__path__'
>>> pygame.base.__package__
'pygame'
>>> pygame.base
<module 'pygame.base' from 'C:\\Users\\A1718\\scoop\\apps\\python\\current\\lib\\site-packages\\pygame\\base.cp38-win_amd64.pyd'>
```
