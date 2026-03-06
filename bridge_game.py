"""
搭桥专家 - 关卡原型
使用 Pygame + Pymunk 实现
"""

import pygame
import pymunk
import pymunk.pygame_util
import sys
import math
from enum import Enum

# 初始化 Pygame
pygame.init()

# 屏幕尺寸
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("搭桥专家 - 关卡原型")
clock = pygame.time.Clock()
FPS = 60

# Pymunk 物理空间
space = pymunk.Space()
space.gravity = (0, 900)  # 重力向下

# 绘制选项
draw_options = pymunk.pygame_util.DrawOptions(screen)

# 材料类型枚举
class MaterialType(Enum):
    WOOD = 1      # 木材
    STEEL = 2     # 钢筋

# 材料属性
MATERIAL_PROPERTIES = {
    MaterialType.WOOD: {
        "name": "木材",
        "color": (139, 90, 43),   # 棕色
        "density": 0.5,
        "elasticity": 0.8,
        "cost_per_meter": 10,
        "strength": 1000,  # 最大受力
    },
    MaterialType.STEEL: {
        "name": "钢筋",
        "color": (192, 192, 192), # 银色
        "density": 2.0,
        "elasticity": 0.9,
        "cost_per_meter": 50,
        "strength": 5000,
    }
}

# 游戏状态
class GameState:
    def __init__(self):
        self.mode = "build"  # build / test / result
        self.materials = []  # 已放置的材料
        self.total_cost = 0
        self.selected_material = MaterialType.WOOD
        self.dragging = False
        self.drag_start = None
        self.drag_end = None
        self.car = None
        self.car_moving = False
        self.car_speed = 200  # 像素/秒
        self.success = False
        self.failed = False
        
        # 起点和终点
        self.start_pos = (200, 500)
        self.end_pos = (1000, 500)
        
        # 地形
        self.create_terrain()
        
        # 车辆
        self.create_car()
    
    def create_terrain(self):
        """创建地形（两边平台，中间缺口）"""
        # 左边平台
        left_ground = pymunk.Segment(space.static_body, (0, 550), (400, 550), 20)
        left_ground.friction = 1.0
        space.add(left_ground)
        
        # 右边平台
        right_ground = pymunk.Segment(space.static_body, (800, 550), (SCREEN_WIDTH, 550), 20)
        right_ground.friction = 1.0
        space.add(right_ground)
        
        # 缺口边缘（可连接点）
        self.left_edge = (400, 550)
        self.right_edge = (800, 550)
        
        # 绘制参考线
        pygame.draw.line(screen, (100, 100, 100), (0, 550), (400, 550), 5)
        pygame.draw.line(screen, (100, 100, 100), (800, 550), (SCREEN_WIDTH, 550), 5)
    
    def create_car(self):
        """创建车辆"""
        mass = 100
        size = (60, 30)
        moment = pymunk.moment_for_box(mass, size)
        body = pymunk.Body(mass, moment)
        body.position = self.start_pos
        shape = pymunk.Poly.create_box(body, size)
        shape.friction = 0.8
        shape.color = pygame.Color("red")
        space.add(body, shape)
        self.car = body
        
        # 初始静止
        self.car.velocity = (0, 0)
        self.car.angular_velocity = 0
    
    def add_material(self, start, end, material_type):
        """添加一段材料到物理空间"""
        length = math.hypot(end[0] - start[0], end[1] - start[1])
        if length < 10:  # 太短忽略
            return None
            
        props = MATERIAL_PROPERTIES[material_type]
        
        # 创建刚体
        body = pymunk.Body()
        body.position = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
        
        # 计算角度
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        
        # 创建线段形状
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
        cost = length * props["cost_per_meter"] / 100  # 按像素比例折算
        
        # 记录材料
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
        
        return material
    
    def connect_materials(self):
        """连接相邻材料（简单实现：所有材料与起点/终点连接）"""
        pass  # 暂不实现复杂连接
    
    def start_test(self):
        """开始测试车辆通过"""
        self.mode = "test"
        self.car_moving = True
        self.car.velocity = (self.car_speed, 0)
        self.success = False
        self.failed = False
    
    def update(self, dt):
        """更新游戏状态"""
        if self.mode == "test" and self.car_moving:
            # 检查车辆是否到达终点
            if self.car.position.x > self.end_pos[0]:
                self.car_moving = False
                self.success = True
                self.mode = "result"
            # 检查车辆是否掉落（y > 600）
            elif self.car.position.y > 600:
                self.car_moving = False
                self.failed = True
                self.mode = "result"
        
        # 更新物理空间
        space.step(dt)
    
    def draw(self):
        """绘制游戏"""
        # 清屏
        screen.fill((240, 248, 255))  # 淡蓝色背景
        
        # 绘制地形
        pygame.draw.line(screen, (100, 100, 100), (0, 550), (400, 550), 5)
        pygame.draw.line(screen, (100, 100, 100), (800, 550), (SCREEN_WIDTH, 550), 5)
        
        # 绘制缺口
        pygame.draw.line(screen, (70, 130, 180), (400, 550), (400, 600), 3)
        pygame.draw.line(screen, (70, 130, 180), (800, 550), (800, 600), 3)
        
        # 绘制起点和终点
        pygame.draw.circle(screen, (0, 255, 0), self.start_pos, 10)
        pygame.draw.circle(screen, (255, 0, 0), self.end_pos, 10)
        font = pygame.font.Font(None, 30)
        screen.blit(font.render("起点", True, (0, 255, 0)), (self.start_pos[0]-20, self.start_pos[1]-30))
        screen.blit(font.render("终点", True, (255, 0, 0)), (self.end_pos[0]-20, self.end_pos[1]-30))
        
        # 绘制材料（自定义绘制，因为 pymunk 绘制颜色需要调整）
        for material in self.materials:
            shape = material["shape"]
            body = material["body"]
            color = MATERIAL_PROPERTIES[material["type"]]["color"]
            
            # 计算线段端点（世界坐标转屏幕坐标）
            a = body.local_to_world(shape.a)
            b = body.local_to_world(shape.b)
            
            pygame.draw.line(screen, color, (int(a.x), int(a.y)), (int(b.x), int(b.y)), int(shape.radius*2))
        
        # 绘制物理对象（车辆等）
        space.debug_draw(draw_options)
        
        # 绘制拖拽预览
        if self.dragging and self.drag_start and self.drag_end:
            color = MATERIAL_PROPERTIES[self.selected_material]["color"]
            pygame.draw.line(screen, color, self.drag_start, self.drag_end, 5)
            # 显示长度和成本
            length = math.hypot(self.drag_end[0] - self.drag_start[0], self.drag_end[1] - self.drag_start[1])
            cost = length * MATERIAL_PROPERTIES[self.selected_material]["cost_per_meter"] / 100
            text = f"长度: {length:.1f} 成本: {cost:.1f}"
            text_surface = font.render(text, True, (0, 0, 0))
            screen.blit(text_surface, (self.drag_start[0], self.drag_start[1] - 20))
        
        # 绘制UI
        self.draw_ui()
        
        # 绘制结果
        if self.mode == "result":
            self.draw_result()
    
    def draw_ui(self):
        """绘制用户界面"""
        font = pygame.font.Font(None, 36)
        
        # 顶部状态栏
        pygame.draw.rect(screen, (50, 50, 50), (0, 0, SCREEN_WIDTH, 50))
        
        # 模式显示
        mode_text = f"模式: {'建造' if self.mode == 'build' else '测试' if self.mode == 'test' else '结果'}"
        mode_surface = font.render(mode_text, True, (255, 255, 255))
        screen.blit(mode_surface, (20, 10))
        
        # 总成本
        cost_text = f"总成本: {self.total_cost:.1f}"
        cost_surface = font.render(cost_text, True, (255, 255, 0))
        screen.blit(cost_surface, (300, 10))
        
        # 材料选择
        wood_color = MATERIAL_PROPERTIES[MaterialType.WOOD]["color"]
        steel_color = MATERIAL_PROPERTIES[MaterialType.STEEL]["color"]
        
        pygame.draw.rect(screen, wood_color if self.selected_material == MaterialType.WOOD else (200, 200, 200), 
                        (500, 10, 100, 30))
        pygame.draw.rect(screen, steel_color if self.selected_material == MaterialType.STEEL else (200, 200, 200), 
                        (610, 10, 100, 30))
        
        wood_text = font.render("木材", True, (0, 0, 0))
        steel_text = font.render("钢筋", True, (0, 0, 0))
        screen.blit(wood_text, (525, 10))
        screen.blit(steel_text, (635, 10))
        
        # 按钮
        if self.mode == "build":
            pygame.draw.rect(screen, (0, 150, 0), (SCREEN_WIDTH - 150, 10, 130, 30))
            test_text = font.render("开始测试", True, (255, 255, 255))
            screen.blit(test_text, (SCREEN_WIDTH - 140, 10))
        elif self.mode == "result":
            pygame.draw.rect(screen, (0, 100, 200), (SCREEN_WIDTH - 150, 10, 130, 30))
            restart_text = font.render("重新建造", True, (255, 255, 255))
            screen.blit(restart_text, (SCREEN_WIDTH - 140, 10))
        
        # 操作说明
        small_font = pygame.font.Font(None, 24)
        instructions = [
            "操作说明:",
            "1. 鼠标拖拽放置材料",
            "2. 点击材料按钮切换类型",
            "3. 点击'开始测试'测试桥梁",
            "4. 目标: 最低成本让车辆通过"
        ]
        for i, text in enumerate(instructions):
            inst_surface = small_font.render(text, True, (50, 50, 50))
            screen.blit(inst_surface, (20, SCREEN_HEIGHT - 120 + i * 25))
    
    def draw_result(self):
        """绘制结果界面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # 半透明黑色
        screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 48)
        
        if self.success:
            text = font_large.render("成功通过！", True, (0, 255, 0))
            screen.blit(text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100))
            result_text = f"总成本: {self.total_cost:.1f}"
        else:
            text = font_large.render("桥梁坍塌！", True, (255, 0, 0))
            screen.blit(text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100))
            result_text = "车辆掉落，请加固桥梁"
        
        text2 = font_medium.render(result_text, True, (255, 255, 255))
        screen.blit(text2, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2))
        
        hint = font_medium.render("点击'重新建造'继续挑战", True, (255, 255, 0))
        screen.blit(hint, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 100))

def main():
    game = GameState()
    running = True
    
    while running:
        dt = 1.0 / FPS
        mouse_pos = pygame.mouse.get_pos()
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键
                    # 检查按钮点击
                    if game.mode == "build":
                        # 材料选择按钮
                        if 500 <= mouse_pos[0] <= 600 and 10 <= mouse_pos[1] <= 40:
                            game.selected_material = MaterialType.WOOD
                        elif 610 <= mouse_pos[0] <= 710 and 10 <= mouse_pos[1] <= 40:
                            game.selected_material = MaterialType.STEEL
                        
                        # 开始测试按钮
                        elif SCREEN_WIDTH - 150 <= mouse_pos[0] <= SCREEN_WIDTH - 20 and 10 <= mouse_pos[1] <= 40:
                            game.start_test()
                        
                        # 开始拖拽放置材料
                        else:
                            game.dragging = True
                            game.drag_start = mouse_pos
                            game.drag_end = mouse_pos
                    
                    elif game.mode == "result":
                        # 重新建造按钮
                        if SCREEN_WIDTH - 150 <= mouse_pos[0] <= SCREEN_WIDTH - 20 and 10 <= mouse_pos[1] <= 40:
                            # 重置游戏
                            game = GameState()
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and game.dragging and game.mode == "build":
                    game.dragging = False
                    if game.drag_start and game.drag_end:
                        # 添加材料
                        game.add_material(game.drag_start, game.drag_end, game.selected_material)
                    game.drag_start = None
                    game.drag_end = None
            
            elif event.type == pygame.MOUSEMOTION:
                if game.dragging:
                    game.drag_end = mouse_pos
        
        # 更新游戏状态
        game.update(dt)
        
        # 绘制
        game.draw()
        
        # 刷新屏幕
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()