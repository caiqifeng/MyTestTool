"""
创建示例图片
生成简单的占位图片，用于搭桥专家游戏
"""

import os
from PIL import Image, ImageDraw

# 确保images目录存在
image_dir = "images"
if not os.path.exists(image_dir):
    os.makedirs(image_dir)
    print(f"创建目录: {image_dir}")

def create_car_image():
    """创建车辆图片 (60x30)"""
    width, height = 60, 30
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 车身 (红色矩形)
    draw.rectangle([5, 5, width-5, height-5], fill=(255, 0, 0, 255))
    
    # 车窗 (蓝色)
    draw.rectangle([15, 8, width-15, 12], fill=(0, 100, 255, 255))
    
    # 车轮 (黑色)
    draw.ellipse([10, height-10, 20, height], fill=(0, 0, 0, 255))
    draw.ellipse([width-20, height-10, width-10, height], fill=(0, 0, 0, 255))
    
    # 保存
    path = os.path.join(image_dir, "car.png")
    img.save(path, "PNG")
    print(f"创建车辆图片: {path}")
    return path

def create_wood_image():
    """创建木材图片 (100x20)"""
    width, height = 100, 20
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 木材底色 (棕色)
    draw.rectangle([0, 0, width, height], fill=(139, 90, 43, 255))
    
    # 木纹 (深棕色线条)
    for i in range(5):
        y = i * 4 + 2
        draw.line([0, y, width, y], fill=(101, 67, 33, 255), width=1)
    
    # 边缘 (深色边框)
    draw.rectangle([0, 0, width-1, height-1], outline=(101, 67, 33, 255), width=2)
    
    # 保存
    path = os.path.join(image_dir, "wood.png")
    img.save(path, "PNG")
    print(f"创建木材图片: {path}")
    return path

def create_steel_image():
    """创建钢筋图片 (100x20)"""
    width, height = 100, 20
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 钢筋底色 (银色)
    draw.rectangle([0, 0, width, height], fill=(192, 192, 192, 255))
    
    # 金属纹理 (灰色线条)
    for i in range(8):
        x = i * 12 + 6
        draw.line([x, 0, x, height], fill=(150, 150, 150, 255), width=1)
    
    # 边缘 (深灰色边框)
    draw.rectangle([0, 0, width-1, height-1], outline=(128, 128, 128, 255), width=2)
    
    # 螺栓 (深灰色圆点)
    for i in range(3):
        x = 25 + i * 25
        draw.ellipse([x-3, height//2-3, x+3, height//2+3], fill=(64, 64, 64, 255))
    
    # 保存
    path = os.path.join(image_dir, "steel.png")
    img.save(path, "PNG")
    print(f"创建钢筋图片: {path}")
    return path

def main():
    """创建所有示例图片"""
    print("开始创建示例图片...")
    
    try:
        # 创建图片
        car_path = create_car_image()
        wood_path = create_wood_image()
        steel_path = create_steel_image()
        
        print("\n✅ 示例图片创建完成!")
        print(f"车辆图片: {car_path}")
        print(f"木材图片: {wood_path}")
        print(f"钢筋图片: {steel_path}")
        print("\n提示: 您可以随时用自己的图片替换这些示例图片")
        
    except Exception as e:
        print(f"❌ 创建图片失败: {e}")
        print("请确保已安装 Pillow 库: pip install Pillow")

if __name__ == "__main__":
    main()