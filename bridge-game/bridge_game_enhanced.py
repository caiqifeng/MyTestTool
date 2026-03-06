"""
搭桥专家 - 增强版本
修复车辆移动问题，支持图片替换
"""

import pygame
import pymunk
import pymunk.pygame_util
import sys
import math
import traceback
import os
from enum import Enum

# ========== 配置 ==========
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60
GRAVITY = 900

# 颜色定义
WOOD_COLOR = (139, 90, 43, 255)    # 棕色，RGBA
STEEL_COLOR = (192, 192, 192, 255) # 银色，RGBA
RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)
BLUE = (0, 100, 255, 255)
YELLOW = (255, 255, 0, 255)
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
DARK_GRAY = (50, 50, 50, 255)
LIGHT_BLUE = (240, 248, 255, 255)

# 图片配置
USE_IMAGES = True  # 是否使用图片（如果找不到图片则自动使用几何图形）
IMAGE_DIR = "images"  # 图片目录

# ========== 初始化 Pygame ==========
try:
    pygame.init()
    print("Pygame 初始化成功")
except Exception as e:
    print(f"Pygame 初始化失败: {e}")
    print("请安装: pip install pygame")
    sys.exit(1)

# 创建窗口
try:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("搭桥专家 - 增强版本")
    print(f"屏幕尺寸: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
except Exception as e:
    print(f"显示设置失败: {e}")
    sys.exit(1)

clock = pygame.time.Clock()

# ========== 初始化 Pymunk ==========
try:
    space = pymunk.Space()
    space.gravity = (0, GRAVITY)
    print("物理引擎就绪")
except Exception as e:
    print(f"物理引擎初始化失败: {e}")
    print("请安装: pip install pymunk")
    sys.exit(1)

# 绘制选项
draw_options = pymunk.pygame_util.DrawOptions(screen)

# ========== 材料类型 ==========
class MaterialType(Enum):
    WOOD = 1
    STEEL = 2

# ========== 图片管理器 ==========
class ImageManager:
    """管理游戏图片"""
    def __init__(self):
        self.images = {}
        self.use_images = USE_IMAGES
        
        # 创建图片目录
        if not os.path.exists(IMAGE_DIR):
            os.makedirs(IMAGE_DIR)
            print(f"创建图片目录: {IMAGE_DIR}")
            print("请将以下图片放入此目录:")
            print("1. car.png - 车辆图片 (建议尺寸: 60x30)")
            print("2. wood.png - 木材图片 (建议尺寸: 任意)")
            print("3. steel.png - 钢筋图片 (建议尺寸: 任意)")
        
        # 尝试加载图片
        self.load_images()
    
    def load_images(self):
        """加载所有图片"""
        if not self.use_images:
            print("图片功能已禁用，使用几何图形")
            return
            
        image_files = {
            "car": "car.png",
            "wood": "wood.png", 
            "steel": "steel.png"
        }
        
        for name, filename in image_files.items():
            path = os.path.join(IMAGE_DIR, filename)
            try:
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    self.images[name] = img
                    print(f"✓ 加载图片: {filename}")
                else:
                    print(f"✗ 图片不存在: {filename}，将使用几何图形")
                    self.images[name] = None
            except Exception as e:
                print(f"✗ 加载图片失败 {filename}: {e}")
                self.images[name] = None
        
        # 如果没有任何图片，禁用图片功能
        if all(img is None for img in self.images.values()):
            print("未找到任何图片，禁用图片功能")
            self.use_images = False
    
    def get_image(self, name):
        """获取图片，如果不存在则返回None"""
        if not self.use_images:
            return None
        return self.images.get(name)
    
    def draw_beam(self, screen, start, end, material_type, width=10):
        """绘制梁（使用图片或几何图形）"""
        length = math.hypot(end[0] - start[0], end[1] - start[1])
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        center = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
        
        # 尝试使用图片
        if material_type == MaterialType.WOOD:
            img = self.get_image("wood")
        else:
            img = self.get_image("steel")
        
        if img is not None:
            # 缩放图片到合适尺寸
            scaled_length = max(int(length), 10)
            scaled_width = max(int(width), 5)
            
            try:
                # 创建缩放后的图片
                scaled_img = pygame.transform.scale(img, (scaled_length, scaled_width))
                # 旋转图片
                rotated_img = pygame.transform.rotate(scaled_img, -angle * 180 / math.pi)
                # 计算绘制位置
                rect = rotated_img.get_rect(center=center)
                screen.blit(rotated_img, rect.topleft)
                return True
            except Exception as e:
                print(f"图片绘制失败: {e}")
        
        # 使用几何图形作为回退
        if material_type == MaterialType.WOOD:
            color = WOOD_COLOR[:3]
        else:
            color = STEEL_COLOR[:3]
        
        pygame.draw.line(screen, color, start, end, width)
        return False
    
    def draw_car(self, screen, position, angle=0):
        """绘制车辆（使用图片或几何图形）"""
        img = self.get_image("car")
        
        if img is not None:
            try:
                # 缩放图片
                scaled_img = pygame.transform.scale(img, (60, 30))
                # 旋转图片
                rotated_img = pygame.transform.rotate(scaled_img, -angle * 180 / math.pi)
                # 计算绘制位置
                rect = rotated_img.get_rect(center=position)
                screen.blit(rotated_img, rect.topleft)
                return True
            except Exception as e:
                print(f"车辆图片绘制失败: {e}")
        
        # 使用几何图形作为回退
        pygame.draw.rect(screen, RED[:3], 
                        (position[0] - 30, position[1] - 15, 60, 30))
        # 绘制车轮
        pygame.draw.circle(screen, BLACK[:3], (position[0] - 15, position[1] + 5), 5)
        pygame.draw.circle(screen, BLACK[:3], (position[0] + 15, position[1] + 5), 5)
        return False

# 初始化图片管理器
image_manager = ImageManager()

# 材料属性
MATERIALS = {
    MaterialType.WOOD: {
        "name": "木材",
        "color": WOOD_COLOR,
        "density": 0.5,
        "elasticity": 0.8,
        "cost": 10,            # 每100像素成本
        "strength": 1000,
    },
    MaterialType.STEEL: {
        "name": "钢筋",
        "color": STEEL_COLOR,
        "density": 2.0,
        "elasticity": 0.9,
        "cost": 50,            # 每100像素成本
        "strength": 5000,
    }
}

# ========== 游戏状态 ==========
class GameState:
    def __init__(self):
        self.mode = "build"  # build / test / result
        self.materials = []
        self.total_cost = 0
        self.selected = MaterialType.WOOD
        self.dragging = False
        self.drag_start = None
        self.drag_end = None
        self.car = None
        self.car_moving = False
        self.car_speed = 200
        self.car_force = 5000  # 车辆驱动力
        self.success = False
        self.failed = False
        
        # 起点和终点
        self.start_pos = (200, 500)
        self.end_pos = (1000, 500)
        
        # 创建地形和车辆
        self.create_terrain()
        self.create_car()
        print("游戏就绪 - 拖拽建造，点击按钮测试")
    
    def create_terrain(self):
        """创建地形"""
        # 左边平台（降低摩擦，避免车辆卡住）
        left = pymunk.Segment(space.static_body, (0, 550), (400, 550), 20)
        left.friction = 0.3  # 降低摩擦
        left.elasticity = 0.5
        space.add(left)
        
        # 右边平台
        right = pymunk.Segment(space.static_body, (800, 550), (SCREEN_WIDTH, 550), 20)
        right.friction = 1.0
        right.elasticity = 0.5
        space.add(right)
        
        self.left_edge = (400, 550)
        self.right_edge = (800, 550)
    
    def create_car(self):
        """创建车辆"""
        mass = 100
        size = (60, 30)
        moment = pymunk.moment_for_box(mass, size)
        body = pymunk.Body(mass, moment)
        body.position = self.start_pos
        shape = pymunk.Poly.create_box(body, size)
        shape.friction = 0.5  # 适中摩擦
        shape.elasticity = 0.3
        shape.color = RED
        space.add(body, shape)
        self.car = body
        
        # 初始静止
        self.car.velocity = (0, 0)
        self.car.angular_velocity = 0
        
        # 设置车辆为可旋转但有限制
        self.car.moment = moment
    
    def add_material(self, start, end, material_type):
        """添加材料"""
        length = math.hypot(end[0] - start[0], end[1] - start[1])
        if length < 10:
            return None
            
        props = MATERIALS[material_type]
        
        # 创建刚体
        body = pymunk.Body()
        body.position = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
        
        # 计算角度
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        
        # 创建线段
        shape = pymunk.Segment(body, (-length/2, 0), (length/2, 0), 8)  # 加粗
        shape.density = props["density"]
        shape.elasticity = props["elasticity"]
        shape.friction = 0.7  # 材料摩擦
        shape.material_type = material_type
        shape.color = props["color"]
        
        # 设置旋转
        body.angle = angle
        
        space.add(body, shape)
        
        # 计算成本
        cost = length * props["cost"] / 100
        
        # 记录
        material = {
            "body": body,
            "shape": shape,
            "start": start,
            "end": end,
            "type": material_type,
            "cost": cost,
            "length": length
        }
        self.materials.append(material)
        self.total_cost += cost
        
        print(f"添加: {props['name']} 长度:{length:.0f} 成本:{cost:.0f}")
        return material
    
    def start_test(self):
        """开始测试"""
        self.mode = "test"
        self.car_moving = True
        
        # 重置车辆位置和状态
        self.car.position = self.start_pos
        self.car.angle = 0
        self.car.angular_velocity = 0
        
        # 设置初始速度
        self.car.velocity = (self.car_speed * 0.5, 0)  # 初始速度
        
        self.success = False
        self.failed = False
        print("开始测试桥梁...")
    
    def update(self, dt):
        """更新状态"""
        if self.mode == "test" and self.car_moving:
            # 持续施加驱动力，防止车辆停止
            self.car.apply_force_at_local_point((self.car_force, 0), (0, 0))
            
            # 限制车辆最大速度
            current_speed_x = self.car.velocity.x
            if abs(current_speed_x) > self.car_speed:
                self.car.velocity = (self.car_speed * (1 if current_speed_x > 0 else -1), 
                                   self.car.velocity.y)
            
            # 显示速度信息（调试用）
            speed = math.hypot(self.car.velocity.x, self.car.velocity.y)
            if int(pygame.time.get_ticks() / 500) % 2 == 0:  # 每0.5秒显示一次
                print(f"车辆速度: {speed:.1f}, 位置: ({self.car.position.x:.0f}, {self.car.position.y:.0f})")
            
            # 检查是否到达终点
            if self.car.position.x > self.end_pos[0]:
                self.car_moving = False
                self.success = True
                self.mode = "result"
                print(f"成功! 总成本: {self.total_cost:.0f}")
            # 检查是否掉落
            elif self.car.position.y > 650:  # 降低掉落阈值
                self.car_moving = False
                self.failed = True
                self.mode = "result"
                print("失败: 车辆掉落")
            # 检查是否卡住（长时间不移动）
            elif abs(self.car.velocity.x) < 10 and self.car.position.x < 800:
                # 如果速度很低且还没过桥，施加额外力
                self.car.apply_force_at_local_point((self.car_force * 2, 0), (0, 0))
                print("警告: 车辆可能卡住，施加额外推力")
        
        # 物理更新
        space.step(dt)
    
    def draw(self):
        """绘制游戏"""
        # 清屏
        screen.fill(LIGHT_BLUE)
        
        # 绘制地形
        pygame.draw.line(screen, DARK_GRAY, (0, 550), (400, 550), 5)
        pygame.draw.line(screen, DARK_GRAY, (800, 550), (SCREEN_WIDTH, 550), 5)
        
        # 绘制缺口
        pygame.draw.line(screen, BLUE, (400, 550), (400, 600), 3)
        pygame.draw.line(screen, BLUE, (800, 550), (800, 600), 3)
        
        # 绘制起点和终点
        pygame.draw.circle(screen, GREEN[:3], self.start_pos, 12)  # 绿色起点
        pygame.draw.circle(screen, RED[:3], self.end_pos, 12)      # 红色终点
        
        # 绘制材料（使用图片或几何图形）
        for material in self.materials:
            shape = material["shape"]
            body = material["body"]
            
            # 计算线段端点
            a = body.local_to_world(shape.a)
            b = body.local_to_world(shape.b)
            
            # 使用图片管理器绘制
            image_manager.draw_beam(screen, 
                                  (int(a.x), int(a.y)), 
                                  (int(b.x), int(b.y)), 
                                  material["type"],
                                  width=int(shape.radius*1.5))
        
        # 绘制物理调试信息（安全）
        try:
            space.debug_draw(draw_options)
        except:
            pass  # 忽略绘制错误
        
        # 绘制车辆
        if self.car:
            image_manager.draw_car(screen, 
                                 (int(self.car.position.x), int(self.car.position.y)),
                                 self.car.angle)
        
        # 绘制拖拽预览
        if self.dragging and self.drag_start and self.drag_end:
            if self.selected == MaterialType.WOOD:
                color = WOOD_COLOR[:3]
            else:
                color = STEEL_COLOR[:3]
            
            pygame.draw.line(screen, color, self.drag_start, self.drag_end, 8)
            
            # 显示长度和成本
            length = math.hypot(self.drag_end[0] - self.drag_start[0], self.drag_end[1] - self.drag_start[1])
            cost = length * MATERIALS[self.selected]["cost"] / 100
            
            # 绘制预览文字
            font = pygame.font.Font(None, 24)
            text = f"长度:{length:.0f} 成本:{cost:.0f}"
            text_surface = font.render(text, True, BLACK[:3])
            screen.blit(text_surface, (self.drag_start[0], self.drag_start[1] - 25))
        
        # 绘制UI
        self.draw_ui()
        
        # 绘制结果
        if self.mode == "result":
            self.draw_result()
    
    def draw_ui(self):
        """绘制用户界面"""
        # 顶部状态栏
        pygame.draw.rect(screen, DARK_GRAY[:3], (0, 0, SCREEN_WIDTH, 50))
        
        # 模式指示器
        if self.mode == "build":
            mode_text = "建造模式"
            mode_color = GREEN[:3]
        elif self.mode == "test":
            mode_text = "测试模式"
            mode_color = YELLOW[:3]
        else:
            mode_text = "结果"
            mode_color = BLUE[:3]
        
        font = pygame.font.Font(None, 36)
        mode_surface = font.render(mode_text, True, mode_color)
        screen.blit(mode_surface, (20, 10))
        
        # 成本显示
        cost_text = f"总成本: {self.total_cost:.0f}"
        cost_surface = font.render(cost_text, True, YELLOW[:3])
        screen.blit(cost_surface, (300, 10))
        
        # 材料选择按钮
        wood_color = WOOD_COLOR[:3]
        steel_color = STEEL_COLOR[:3]
        
        # 木材按钮
        wood_rect = pygame.Rect(500, 10, 100, 30)
        pygame.draw.rect(screen, wood_color if self.selected == MaterialType.WOOD else (200, 200, 200), wood_rect)
        wood_text = font.render("木材", True, BLACK[:3])
        screen.blit(wood_text, (525, 10))
        
        # 钢筋按钮
        steel_rect = pygame.Rect(610, 10, 100, 30)
        pygame.draw.rect(screen, steel_color if self.selected == MaterialType.STEEL else (200, 200, 200), steel_rect)
        steel_text = font.render("钢筋", True, BLACK[:3])
        screen.blit(steel_text, (635, 10))
        
        # 测试/重置按钮
        if self.mode == "build":
            test_rect = pygame.Rect(SCREEN_WIDTH - 150, 10, 130, 30)
            pygame.draw.rect(screen, GREEN[:3], test_rect)
            test_text = font.render("开始测试", True, WHITE[:3])
            screen.blit(test_text, (SCREEN_WIDTH - 140, 10))
        elif self.mode == "result":
            reset_rect = pygame.Rect(SCREEN_WIDTH - 150, 10, 130, 30)
            pygame.draw.rect(screen, BLUE[:3], reset_rect)
            reset_text = font.render("重新建造", True, WHITE[:3])
            screen.blit(reset_text, (SCREEN_WIDTH - 140, 10))
        
        # 操作提示
        tips = [
            "操作说明:",
            "1. 拖拽鼠标放置材料",
            "2. 点击按钮选择木材/钢筋", 
            "3. 点击'开始测试'测试桥梁",
            "4. 目标: 最低成本让车辆通过"
        ]
        small_font = pygame.font.Font(None, 24)
        for i, tip in enumerate(tips):
            tip_surface = small_font.render(tip, True, DARK_GRAY[:3])
            screen.blit(tip_surface, (20, SCREEN_HEIGHT - 120 + i * 25))
    
    def draw_result(self):
        """绘制结果界面"""
        # 半透明覆盖
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        large_font = pygame.font.Font(None, 72)
        medium_font = pygame.font.Font(None, 48)
        
        if self.success:
            # 成功
            text = large_font.render("成功通过！", True, GREEN[:3])
            screen.blit(text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100))
            result_text = f"总成本: {self.total_cost:.0f}"
            result_surface = medium_font.render(result_text, True, WHITE[:3])
            screen.blit(result_surface, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2))
        else:
            # 失败
            text = large_font.render("桥梁坍塌！", True, RED[:3])
            screen.blit(text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100))
            result_surface = medium_font.render("车辆掉落，请加固桥梁", True, WHITE[:3])
            screen.blit(result_surface, (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2))
        
        hint = medium_font.render("点击'重新建造'继续挑战", True, YELLOW[:3])
        screen.blit(hint, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 100))

def main():
    """主游戏循环"""
    try:
        print("=" * 50)
        print("搭桥专家 - 增强版本")
        print("修复车辆移动问题，支持图片替换")
        print("=" * 50)
        
        game = GameState()
        running = True
        
        print("\n操作说明:")
        print("1. 拖拽鼠标放置材料")
        print("2. 点击按钮选择材料类型")
        print("3. 点击'开始测试'测试桥梁")
        print("4. 按ESC键退出游戏")
        print("\n提示: 如果车辆卡住，会显示速度信息")
        
        while running:
            dt = 1.0 / FPS
            mouse_pos = pygame.mouse.get_pos()
            
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_t and game.mode == "build":
                        game.start_test()
                    elif event.key == pygame.K_w:
                        game.selected = MaterialType.WOOD
                        print("选择材料: 木材")
                    elif event.key == pygame.K_s:
                        game.selected = MaterialType.STEEL
                        print("选择材料: 钢筋")
                    elif event.key == pygame.K_r and game.mode == "result":
                        # 重置游戏
                        game = GameState()
                        print("重新开始游戏")
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左键
                        # 检查按钮点击
                        if game.mode == "build":
                            # 材料选择按钮
                            if 500 <= mouse_pos[0] <= 600 and 10 <= mouse_pos[1] <= 40:
                                game.selected = MaterialType.WOOD
                                print("选择材料: 木材")
                            elif 610 <= mouse_pos[0] <= 710 and 10 <= mouse_pos[1] <= 40:
                                game.selected = MaterialType.STEEL
                                print("选择材料: 钢筋")
                            # 开始测试按钮
                            elif SCREEN_WIDTH - 150 <= mouse_pos[0] <= SCREEN_WIDTH - 20 and 10 <= mouse_pos[1] <= 40:
                                game.start_test()
                            # 开始拖拽
                            else:
                                game.dragging = True
                                game.drag_start = mouse_pos
                                game.drag_end = mouse_pos
                                print("开始拖拽放置材料...")
                        
                        elif game.mode == "result":
                            # 重新建造按钮
                            if SCREEN_WIDTH - 150 <= mouse_pos[0] <= SCREEN_WIDTH - 20 and 10 <= mouse_pos[1] <= 40:
                                game = GameState()
                                print("重新开始游戏")
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and game.dragging and game.mode == "build":
                        game.dragging = False
                        if game.drag_start and game.drag_end:
                            game.add_material(game.drag_start, game.drag_end, game.selected)
                        game.drag_start = None
                        game.drag_end = None
                
                elif event.type == pygame.MOUSEMOTION:
                    if game.dragging:
                        game.drag_end = mouse_pos
            
            # 更新游戏
            game.update(dt)
            
            # 绘制
            game.draw()
            
            # 刷新屏幕
            pygame.display.flip()
            clock.tick(FPS)
        
        print("游戏退出")
        
    except Exception as e:
        print(f"游戏运行错误: {e}")
        traceback.print_exc()
        print("\n故障排除:")
        print("1. 确保已安装依赖: pip install pygame pymunk")
        print("2. 如果车辆卡住，请检查桥梁是否连接牢固")
        print("3. 可以尝试降低材料摩擦系数")
    
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    # 设置控制台编码
    try:
        if sys.platform == "win32":
            import os
            os.system("chcp 65001 > nul")
    except:
        pass
    
    main()