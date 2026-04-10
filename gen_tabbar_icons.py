"""
生成面包店小程序 Tabbar 图标
使用 Pillow 绘制矢量风格图标
"""
from PIL import Image, ImageDraw
import os

SIZE = 81  # 标准小程序 tabbar 图标尺寸
ACTIVE_COLOR = (255, 107, 53)    # #FF6B35 主色
NORMAL_COLOR = (153, 153, 153)   # #999999 非激活色
BG_ALPHA = 0  # 透明背景

OUTPUT_DIR = r"F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app\frontend\static\tabbar"

def new_img():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    return img, draw

def save(img, name):
    path = os.path.join(OUTPUT_DIR, name)
    img.save(path, "PNG")
    print(f"Saved: {path}")

def draw_home_icon(color):
    """绘制房子图标"""
    img, draw = new_img()
    r, g, b = color

    # 屋顶三角形
    roof_points = [(SIZE//2, 10), (10, 40), (SIZE-10, 40)]
    draw.polygon(roof_points, fill=(r, g, b, 255))

    # 墙体矩形
    wall_x1, wall_y1 = 18, 38
    wall_x2, wall_y2 = SIZE-18, SIZE-10
    draw.rectangle([wall_x1, wall_y1, wall_x2, wall_y2], fill=(r, g, b, 255))

    # 门 (白色)
    door_w = 10
    door_h = 16
    door_x = SIZE//2 - door_w//2
    door_y = wall_y2 - door_h
    draw.rectangle([door_x, door_y, door_x+door_w, door_y+door_h], fill=(255, 255, 255, 200))

    return img

def draw_cart_icon(color):
    """绘制购物车图标"""
    img, draw = new_img()
    r, g, b = color

    # 购物车主体 (梯形)
    body_points = [
        (20, 25), (60, 25), (65, 55), (15, 55)
    ]
    draw.polygon(body_points, fill=(r, g, b, 255))

    # 手柄线条
    draw.line([(8, 12), (20, 12), (20, 25)], fill=(r, g, b, 255), width=4)

    # 车轮
    wheel_r = 5
    draw.ellipse([22-wheel_r, 57-wheel_r, 22+wheel_r, 57+wheel_r], fill=(r, g, b, 255))
    draw.ellipse([58-wheel_r, 57-wheel_r, 58+wheel_r, 57+wheel_r], fill=(r, g, b, 255))

    # 白色线条分割购物车
    draw.line([(15, 40), (65, 40)], fill=(255, 255, 255, 180), width=2)

    return img

def draw_user_icon(color):
    """绘制用户头像图标"""
    img, draw = new_img()
    r, g, b = color

    # 头部圆形
    head_r = 16
    head_cx, head_cy = SIZE//2, 25
    draw.ellipse([head_cx-head_r, head_cy-head_r, head_cx+head_r, head_cy+head_r],
                 fill=(r, g, b, 255))

    # 身体 (半圆弧)
    body_x1, body_y1 = 12, 48
    body_x2, body_y2 = SIZE-12, SIZE+10  # 超出底部
    draw.ellipse([body_x1, body_y1, body_x2, body_y2], fill=(r, g, b, 255))

    # 遮住下半部超出区域
    draw.rectangle([0, SIZE-8, SIZE, SIZE], fill=(0, 0, 0, 0))

    return img


# 生成所有图标
icons = [
    ("home.png", draw_home_icon(NORMAL_COLOR)),
    ("home-active.png", draw_home_icon(ACTIVE_COLOR)),
    ("cart.png", draw_cart_icon(NORMAL_COLOR)),
    ("cart-active.png", draw_cart_icon(ACTIVE_COLOR)),
    ("user.png", draw_user_icon(NORMAL_COLOR)),
    ("user-active.png", draw_user_icon(ACTIVE_COLOR)),
]

for name, img in icons:
    save(img, name)

print("\nAll tabbar icons generated!")
