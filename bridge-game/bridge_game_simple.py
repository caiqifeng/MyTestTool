"""
搭桥专家 - 最简版本 (解决字体乱码问题)
使用图像和符号替代文字，彻底避免字体问题
"""

import pygame
import pymunk
import pymunk.pygame_util
import sys
import math
import traceback
from enum import Enum

# ========== 配置 ==========
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60
GRAVITY = 900

# 使用符号和颜色替代文字
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

# ========== 初始化 Pygame ==========
try:
    pygame.init()
    print("Pygame initialized")
except Exception as e:
    print(f"Pygame init failed: {e}")
    print("Install: pip install pygame")
    sys.exit(1)

# 创建窗口
try:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bridge Master - Simple Version")
    print(f"Screen: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
except Exception as e:
    print(f"Display failed: {e}")
    sys.exit(1)

clock = pygame.time.Clock()

# ========== 初始化 Pymunk ==========
try:
    space = pymunk.Space()
    space.gravity = (0, GRAVITY)
    print("Physics engine ready")
except Exception as e:
    print(f"Physics init failed: {e}")
    print("Install: pip install pymunk")
    sys.exit(1)

# 绘制选项
draw_options = pymunk.pygame_util.DrawOptions(screen)

# ========== 材料类型 ==========
class MaterialType(Enum):
    WOOD = 1
    STEEL = 2

# 材料属性
MATERIALS = {
    MaterialType.WOOD: {
        "symbol": "W",          # 木材符号
        "color": WOOD_COLOR,
        "density": 0.5,
        "elasticity": 0.8,
        "cost": 10,            # 每100像素成本
    },
    MaterialType.STEEL: {
        "symbol": "S",          # 钢筋符号
        "color": STEEL_COLOR,
        "density": 2.0,
        "elasticity": 0.9,
        "cost": 50,            # 每100像素成本
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
        self.success = False
        self.failed = False
        
        # 起点和终点
        self.start_pos = (200, 500)
        self.end_pos = (1000, 500)
        
        # 创建地形和车辆
        self.create_terrain()
        self.create_car()
        print("Game ready - Drag to build, click buttons to test")
    
    def create_terrain(self):
        """创建地形"""
        # 左边平台
        left = pymunk.Segment(space.static_body, (0, 550), (400, 550), 20)
        left.friction = 1.0
        space.add(left)
        
        # 右边平台
        right = pymunk.Segment(space.static_body, (800, 550), (SCREEN_WIDTH, 550), 20)
        right.friction = 1.0
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
        shape.friction = 0.8
        shape.color = RED
        space.add(body, shape)
        self.car = body
        
        # 初始静止
        self.car.velocity = (0, 0)
        self.car.angular_velocity = 0
    
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
        shape = pymunk.Segment(body, (-length/2, 0), (length/2, 0), 5)
        shape.density = props["density"]
        shape.elasticity = props["elasticity"]
        shape.friction = 0.8
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
        
        print(f"Added: {props['symbol']} L:{length:.0f} C:{cost:.0f}")
        return material
    
    def start_test(self):
        """开始测试"""
        self.mode = "test"
        self.car_moving = True
        self.car.velocity = (self.car_speed, 0)
        self.success = False
        self.failed = False
        print("Testing bridge...")
    
    def update(self, dt):
        """更新状态"""
        if self.mode == "test" and self.car_moving:
            # 检查是否到达终点
            if self.car.position.x > self.end_pos[0]:
                self.car_moving = False
                self.success = True
                self.mode = "result"
                print(f"SUCCESS! Cost: {self.total_cost:.0f}")
            # 检查是否掉落
            elif self.car.position.y > 600:
                self.car_moving = False
                self.failed = True
                self.mode = "result"
                print("FAILED: Car fell")
        
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
        
        # 绘制起点和终点（使用颜色和形状）
        pygame.draw.circle(screen, GREEN, self.start_pos, 10)  # 绿色起点
        pygame.draw.circle(screen, RED, self.end_pos, 10)      # 红色终点
        
        # 绘制材料
        for material in self.materials:
            shape = material["shape"]
            body = material["body"]
            color = MATERIALS[material["type"]]["color"]
            
            # 转换为RGB（Pygame使用RGB）
            rgb_color = color[:3]
            
            # 计算端点
            a = body.local_to_world(shape.a)
            b = body.local_to_world(shape.b)
            
            pygame.draw.line(screen, rgb_color, (int(a.x), int(a.y)), (int(b.x), int(b.y)), int(shape.radius*2))
        
        # 绘制物理调试信息（安全）
        try:
            space.debug_draw(draw_options)
        except:
            pass  # 忽略绘制错误
        
        # 绘制拖拽预览
        if self.dragging and self.drag_start and self.drag_end:
            color = MATERIALS[self.selected]["color"]
            rgb_color = color[:3]
            pygame.draw.line(screen, rgb_color, self.drag_start, self.drag_end, 5)
            
            # 显示长度和成本
            length = math.hypot(self.drag_end[0] - self.drag_start[0], self.drag_end[1] - self.drag_start[1])
            cost = length * MATERIALS[self.selected]["cost"] / 100
            # 使用简单文本
            self.draw_text(f"L:{length:.0f} C:{cost:.0f}", 
                          self.drag_start[0], self.drag_start[1] - 20, 
                          BLACK, 20)
        
        # 绘制UI
        self.draw_ui()
        
        # 绘制结果
        if self.mode == "result":
            self.draw_result()
    
    def draw_text(self, text, x, y, color, size=24):
        """绘制文本（使用默认字体）"""
        try:
            font = pygame.font.Font(None, size)
            surface = font.render(text, True, color)
            screen.blit(surface, (x, y))
        except:
            # 如果字体失败，至少绘制一个矩形
            pygame.draw.rect(screen, color, (x, y, len(text)*10, 20))
    
    def draw_ui(self):
        """绘制用户界面"""
        # 顶部状态栏
        pygame.draw.rect(screen, DARK_GRAY, (0, 0, SCREEN_WIDTH, 50))
        
        # 模式指示器
        if self.mode == "build":
            mode_text = "BUILD"
            mode_color = GREEN
        elif self.mode == "test":
            mode_text = "TEST"
            mode_color = YELLOW
        else:
            mode_text = "RESULT"
            mode_color = BLUE
        
        self.draw_text(mode_text, 20, 10, mode_color, 36)
        
        # 成本显示
        cost_text = f"COST: {self.total_cost:.0f}"
        self.draw_text(cost_text, 300, 10, YELLOW, 36)
        
        # 材料选择按钮
        wood_color = MATERIALS[MaterialType.WOOD]["color"][:3]
        steel_color = MATERIALS[MaterialType.STEEL]["color"][:3]
        
        # 木材按钮
        wood_rect = pygame.Rect(500, 10, 100, 30)
        pygame.draw.rect(screen, wood_color if self.selected == MaterialType.WOOD else (200, 200, 200), wood_rect)
        self.draw_text("W", 540, 10, BLACK, 36)
        
        # 钢筋按钮
        steel_rect = pygame.Rect(610, 10, 100, 30)
        pygame.draw.rect(screen, steel_color if self.selected == MaterialType.STEEL else (200, 200, 200), steel_rect)
        self.draw_text("S", 650, 10, BLACK, 36)
        
        # 测试/重置按钮
        if self.mode == "build":
            test_rect = pygame.Rect(SCREEN_WIDTH - 150, 10, 130, 30)
            pygame.draw.rect(screen, GREEN, test_rect)
            self.draw_text("TEST", SCREEN_WIDTH - 120, 10, WHITE, 36)
        elif self.mode == "result":
            reset_rect = pygame.Rect(SCREEN_WIDTH - 150, 10, 130, 30)
            pygame.draw.rect(screen, BLUE, reset_rect)
            self.draw_text("RESET", SCREEN_WIDTH - 120, 10, WHITE, 36)
        
        # 操作提示（使用符号和简单文本）
        tips = [
            "CONTROLS:",
            "1. Drag = Place material",
            "2. Click W/S = Wood/Steel",
            "3. Click TEST = Test bridge",
            "4. Goal = Min cost to pass"
        ]
        for i, tip in enumerate(tips):
            self.draw_text(tip, 20, SCREEN_HEIGHT - 120 + i * 25, DARK_GRAY, 20)
    
    def draw_result(self):
        """绘制结果界面"""
        # 半透明覆盖
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        if self.success:
            # 成功
            self.draw_text("SUCCESS!", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 100, GREEN, 72)
            result_text = f"COST: {self.total_cost:.0f}"
            self.draw_text(result_text, SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2, WHITE, 48)
        else:
            # 失败
            self.draw_text("FAILED!", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 100, RED, 72)
            self.draw_text("Bridge too weak", SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2, WHITE, 48)
        
        self.draw_text("Click RESET to retry", SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 100, YELLOW, 36)

def main():
    """主游戏循环"""
    try:
        game = GameState()
        running = True
        
        print("\n=== Bridge Master - Simple Version ===")
        print("Controls:")
        print("  - Drag mouse: Place material")
        print("  - Click W/S: Select Wood/Steel")
        print("  - Click TEST: Test bridge")
        print("  - ESC: Exit")
        print("Goal: Build bridge with lowest cost")
        print("=" * 40)
        
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
                    elif event.key == pygame.K_w:
                        game.selected = MaterialType.WOOD
                        print("Selected: Wood")
                    elif event.key == pygame.K_s:
                        game.selected = MaterialType.STEEL
                        print("Selected: Steel")
                    elif event.key == pygame.K_t and game.mode == "build":
                        game.start_test()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左键
                        # 检查按钮点击
                        if game.mode == "build":
                            # 木材按钮 (500-600, 10-40)
                            if 500 <= mouse_pos[0] <= 600 and 10 <= mouse_pos[1] <= 40:
                                game.selected = MaterialType.WOOD
                                print("Selected: Wood")
                            # 钢筋按钮 (610-710, 10-40)
                            elif 610 <= mouse_pos[0] <= 710 and 10 <= mouse_pos[1] <= 40:
                                game.selected = MaterialType.STEEL
                                print("Selected: Steel")
                            # 测试按钮
                            elif SCREEN_WIDTH - 150 <= mouse_pos[0] <= SCREEN_WIDTH - 20 and 10 <= mouse_pos[1] <= 40:
                                game.start_test()
                            # 开始拖拽
                            else:
                                game.dragging = True
                                game.drag_start = mouse_pos
                                game.drag_end = mouse_pos
                        
                        elif game.mode == "result":
                            # 重置按钮
                            if SCREEN_WIDTH - 150 <= mouse_pos[0] <= SCREEN_WIDTH - 20 and 10 <= mouse_pos[1] <= 40:
                                # 重新开始
                                game = GameState()
                                print("Game reset")
                
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
        
        print("Game exited")
        
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        print("\nTROUBLESHOOTING:")
        print("1. Install: pip install pygame pymunk")
        print("2. Run as Administrator")
        print("3. Update graphics drivers")
    
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