#!/usr/bin/env python3
"""
生成现代化的面包店主题 Tabbar 图标
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math

# 配置
SIZE = 81  # 小程序图标标准尺寸
ACTIVE_COLOR = (255, 107, 53)    # #FF6B35 主色 (橙色)
NORMAL_COLOR = (153, 153, 153)   # #999999 非激活色 (灰色)
SECONDARY_COLOR = (255, 193, 7)  # #FFC107 强调色 (黄色)
TERTIARY_COLOR = (139, 195, 74)  # #8BC34A 辅助色 (绿色)
BG_ALPHA = 0  # 透明背景

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def create_canvas():
    """创建透明画布"""
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))

def draw_rounded_rect(draw, rect, radius, color):
    """绘制圆角矩形"""
    x1, y1, x2, y2 = rect
    r = radius

    # 绘制四个角的圆弧
    draw.ellipse([x1, y1, x1+2*r, y1+2*r], fill=color)
    draw.ellipse([x2-2*r, y1, x2, y1+2*r], fill=color)
    draw.ellipse([x1, y2-2*r, x1+2*r, y2], fill=color)
    draw.ellipse([x2-2*r, y2-2*r, x2, y2], fill=color)

    # 绘制矩形区域
    draw.rectangle([x1+r, y1, x2-r, y2], fill=color)
    draw.rectangle([x1, y1+r, x2, y2-r], fill=color)

def draw_bakery_home_icon(color, active=False):
    """绘制面包店首页图标 - 房子+面包"""
    img = create_canvas()
    draw = ImageDraw.Draw(img)

    # 房子主体
    house_width = 50
    house_height = 40
    house_x = (SIZE - house_width) // 2
    house_y = (SIZE - house_height) // 2

    # 屋顶
    roof_points = [
        (house_x, house_y + house_height * 0.3),
        (house_x + house_width // 2, house_y),
        (house_x + house_width, house_y + house_height * 0.3)
    ]
    draw.polygon(roof_points, fill=color)

    # 墙体
    wall_x1 = house_x + 10
    wall_y1 = house_y + house_height * 0.3
    wall_x2 = house_x + house_width - 10
    wall_y2 = house_y + house_height * 0.9

    if active:
        # 激活状态: 完整房子
        draw.rectangle([wall_x1, wall_y1, wall_x2, wall_y2], fill=color)

        # 窗户 (两个)
        window_size = 8
        window1_x = house_x + house_width // 4 - window_size // 2
        window1_y = house_y + house_height * 0.5
        draw.rectangle([window1_x, window1_y, window1_x + window_size, window1_y + window_size],
                      fill=(255, 255, 255, 200))

        window2_x = house_x + house_width * 3 // 4 - window_size // 2
        window2_y = house_y + house_height * 0.5
        draw.rectangle([window2_x, window2_y, window2_x + window_size, window2_y + window_size],
                      fill=(255, 255, 255, 200))

        # 门
        door_width = 12
        door_height = 20
        door_x = (SIZE - door_width) // 2
        door_y = wall_y2 - door_height
        draw.rectangle([door_x, door_y, door_x + door_width, door_y + door_height],
                      fill=(255, 255, 255, 180))

        # 门把手
        handle_x = door_x + door_width - 3
        handle_y = door_y + door_height // 2
        draw.ellipse([handle_x-2, handle_y-2, handle_x+2, handle_y+2],
                     fill=(200, 200, 200, 220))

    else:
        # 非激活状态: 简约房子轮廓
        # 墙体轮廓
        outline_width = 4
        draw_rounded_rect(draw, [wall_x1, wall_y1, wall_x2, wall_y2], outline_width, color)

    # 添加面包元素 (左上角)
    bread_x = SIZE * 0.2
    bread_y = SIZE * 0.2
    bread_r = 6
    draw.ellipse([bread_x-bread_r, bread_y-bread_r, bread_x+bread_r, bread_y+bread_r],
                 fill=color)

    # 面包顶部波浪线
    for i in range(3):
        draw.ellipse([bread_x - bread_r + i*4, bread_y - bread_r - 2,
                      bread_x - bread_r + i*4 + 4, bread_y - bread_r + 2],
                     fill=color)

    return img

def draw_bakery_cart_icon(color, active=False):
    """绘制面包店购物车图标 - 购物篮+面包"""
    img = create_canvas()
    draw = ImageDraw.Draw(img)

    # 购物篮主体
    basket_width = 45
    basket_height = 35
    basket_x = (SIZE - basket_width) // 2
    basket_y = (SIZE - basket_height) // 2 + 5

    # 篮子底部 (圆角矩形)
    bottom_rect = [basket_x, basket_y + basket_height * 0.4,
                   basket_x + basket_width, basket_y + basket_height]
    draw_rounded_rect(draw, bottom_rect, 4, color)

    # 篮子把手
    handle_y = basket_y
    handle_points = [
        (basket_x, handle_y),
        (basket_x + basket_width // 4, handle_y - 5),
        (basket_x + basket_width * 3 // 4, handle_y - 5),
        (basket_x + basket_width, handle_y)
    ]
    draw.line(handle_points, fill=color, width=3)

    # 添加面包元素
    if active:
        # 激活状态: 篮子有面包
        # 法棍面包
        baguette_x = basket_x + basket_width // 2
        baguette_y = basket_y + basket_height // 2
        draw.ellipse([baguette_x-8, baguette_y-4, baguette_x+8, baguette_y+4],
                     fill=color)
        # 面包上的切割线
        for i in range(3):
            draw.line([(baguette_x-6+i*3, baguette_y), (baguette_x-6+i*3, baguette_y-3)],
                     fill=(255, 255, 255, 180), width=1)
    else:
        # 非激活状态: 空篮子
        pass

    return img

def draw_bakery_user_icon(color, active=False):
    """绘制面包店用户图标 - 厨师帽+头像"""
    img = create_canvas()
    draw = ImageDraw.Draw(img)

    # 厨师帽
    hat_width = 40
    hat_height = 20
    hat_x = (SIZE - hat_width) // 2
    hat_y = SIZE * 0.25

    # 帽顶 (波浪形)
    for i in range(5):
        draw.ellipse([hat_x + i*8, hat_y, hat_x + i*8 + 8, hat_y + 8],
                     fill=color)

    # 帽檐
    brim_y = hat_y + 8
    draw.rectangle([hat_x, brim_y, hat_x + hat_width, brim_y + 2],
                   fill=color)

    # 用户头像 (圆形)
    face_radius = 15
    face_x = SIZE // 2
    face_y = SIZE * 0.6

    draw.ellipse([face_x - face_radius, face_y - face_radius,
                   face_x + face_radius, face_y + face_radius],
                  fill=color)

    # 眼睛 (两个小圆)
    eye_radius = 3
    left_eye_x = face_x - 6
    right_eye_x = face_x + 6
    eye_y = face_y - 3

    draw.ellipse([left_eye_x - eye_radius, eye_y - eye_radius,
                   left_eye_x + eye_radius, eye_y + eye_radius],
                  fill=(255, 255, 255, 255))
    draw.ellipse([right_eye_x - eye_radius, eye_y - eye_radius,
                   right_eye_x + eye_radius, eye_y + eye_radius],
                  fill=(255, 255, 255, 255))

    # 嘴巴 (微笑弧线)
    mouth_y = face_y + 8
    mouth_width = 10

    for i in range(5):
        draw.ellipse([face_x - mouth_width + i*4, mouth_y - 2,
                       face_x - mouth_width + i*4 + 4, mouth_y + 2],
                      fill=(255, 255, 255, 255))

    return img

def generate_all_icons():
    """生成所有图标"""

    icons = [
        ("home.png", draw_bakery_home_icon(NORMAL_COLOR, active=False)),
        ("home-active.png", draw_bakery_home_icon(ACTIVE_COLOR, active=True)),
        ("cart.png", draw_bakery_cart_icon(NORMAL_COLOR, active=False)),
        ("cart-active.png", draw_bakery_cart_icon(ACTIVE_COLOR, active=True)),
        ("user.png", draw_bakery_user_icon(NORMAL_COLOR, active=False)),
        ("user-active.png", draw_bakery_user_icon(ACTIVE_COLOR, active=True)),
    ]

    # 备份原文件
    backup_dir = os.path.join(OUTPUT_DIR, "backup")
    os.makedirs(backup_dir, exist_ok=True)

    for name, _ in icons:
        src_path = os.path.join(OUTPUT_DIR, name)
        if os.path.exists(src_path):
            backup_path = os.path.join(backup_dir, name)
            import shutil
            shutil.copy2(src_path, backup_path)
            print(f"Backed up: {backup_path}")

    # 生成新图标
    for name, img in icons:
        output_path = os.path.join(OUTPUT_DIR, name)
        img.save(output_path, "PNG")
        print(f"Generated: {output_path}")

    print(f"\nGenerated {len(icons)} icons.")

if __name__ == "__main__":
    generate_all_icons()