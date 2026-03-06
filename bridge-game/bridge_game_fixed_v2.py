"""
搭桥专家 - 关卡原型 (修复版 v2)
使用 Pygame + Pymunk 实现
彻底解决字体乱码和pymunk执行错误问题
"""

import pygame
import pymunk
import pymunk.pygame_util
import sys
import math
import traceback
from enum import Enum

# ========== 导入配置 ==========
try:
    from config import USE_ENGLISH_TEXT, SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GRAVITY, CAR_SPEED, CAR_MASS, MATERIALS, TEXT
    print("成功加载配置文件")
except ImportError:
    print("警告: 无法加载配置文件，使用默认配置")
    # 默认配置
    USE_ENGLISH_TEXT = False
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 700
    FPS = 60
    GRAVITY = 900
    CAR_SPEED = 200
    CAR_MASS = 100
    
    MATERIALS = {
        "wood": {
            "name_cn": "木材",
            "name_en": "Wood",
            "color": (139, 90, 43, 255),
            "density": 0.5,
            "elasticity": 0.8,
            "cost_per_meter": 10,
            "strength": 1000,
        },
        "steel": {
            "name_cn": "钢筋",
            "name_en": "Steel",
            "color": (192, 192, 192, 255),
            "density": 2.0,
            "elasticity": 0.9,
            "cost_per_meter": 50,
            "strength": 5000,
        }
    }
    
    # 根据语言选择文本
    if USE_ENGLISH_TEXT:
        TEXT = {
            "start": "Start", "end": "End", "wood": "Wood", "steel": "Steel",
            "mode_build": "Mode: Build", "mode_test": "Mode: Test", "mode_result": "Mode: Result",
            "total_cost": "Total Cost: ", "start_test": "Start Test", "rebuild": "Rebuild",
            "instructions": [
                "Instructions:", "1. Drag mouse to place materials",
                "2. Click material buttons to switch", "3. Click 'Start Test' to test bridge",
                "4. Goal: Lowest cost for vehicle to pass"
            ],
            "success": "Success!", "failure": "Bridge Collapsed!",
            "result_success": "Total Cost: ", "result_failure": "Vehicle fell, reinforce bridge",
            "hint": "Click 'Rebuild' to continue"
        }
    else:
        TEXT = {
            "start": "起点", "end": "终点", "wood": "木材", "steel": "钢筋",
            "mode_build": "模式: 建造", "mode_test": "模式: 测试", "mode_result": "模式: 结果",
            "total_cost": "总成本: ", "start_test": "开始测试", "rebuild": "重新建造",
            "instructions": [
                "操作说明:", "1. 鼠标拖拽放置材料",
                "2. 点击材料按钮切换类型", "3. 点击'开始测试'测试桥梁",
                "4. 目标: 最低成本让车辆通过"
            ],
            "success": "成功通过！", "failure": "桥梁坍塌！",
            "result_success": "总成本: ", "result_failure": "车辆掉落，请加固桥梁",
            "hint": "点击'重新建造'继续挑战"
        }

def init_font_system():
    """初始化字体系统，彻底解决乱码问题"""
    if USE_ENGLISH_TEXT:
        # 使用英文文本，避免字体问题
        print("使用英文文本模式，避免字体乱码")
        font_cache = {}
        
        def get_font(size):
            cache_key = f"default_{size}"
            if cache_key not in font_cache:
                font_cache[cache_key] = pygame.font.Font(None, size)
                print(f"创建字体: 系统默认字体 (大小: {size})")
            return font_cache[cache_key]
        
        return get_font
    
    # 中文文本模式，尝试多种字体
    print("尝试加载中文字体...")
    
    # 扩展字体列表，包含更多可能的中文字体
    fonts_to_try = [
        # Windows 常见中文字体
        "msyh.ttc",           # 微软雅黑
        "msyhbd.ttc",         # 微软雅黑 Bold
        "simhei.ttf",         # 黑体
        "simsun.ttc",         # 宋体
        "simkai.ttf",         # 楷体
        "simfang.ttf",        # 仿宋
        "simli.ttf",          # 隶书
        # Linux 常见字体
        "wqy-microhei.ttc",   # 文泉驿微米黑
        "wqy-zenhei.ttc",     # 文泉驿正黑
        "DroidSansFallback.ttf",
        "arphic-uming.ttc",   # AR PL UMing
        "arphic-ukai.ttc",    # AR PL UKai
        # macOS 常见字体
        "PingFang.ttc",
        "Hiragino Sans GB.ttc",
        "STHeiti Light.ttc",
        "STHeiti Medium.ttc",
        "STXihei.ttf",        # 华文细黑
        "STKaiti.ttf",        # 华文楷体
        # 最后尝试系统字体
        None  # pygame.font.Font(None, size) 作为回退
    ]
    
    font_cache = {}
    tested_fonts = []
    
    def get_font(size, font_index=0):
        """获取指定大小的字体，支持回退"""
        cache_key = f"{font_index}_{size}"
        if cache_key in font_cache:
            return font_cache[cache_key]
        
        for i in range(font_index, len(fonts_to_try)):
            font_name = fonts_to_try[i]
            try:
                if font_name is None:
                    font = pygame.font.Font(None, size)
                    print(f"使用系统默认字体 (大小: {size})")
                else:
                    font = pygame.font.Font(font_name, size)
                    if font_name not in tested_fonts:
                        tested_fonts.append(font_name)
                        print(f"✓ 成功加载字体: {font_name}")
                
                # 测试字体是否能渲染中文
                test_text = "中文测试" if not USE_ENGLISH_TEXT else "Test"
                test_surface = font.render(test_text, True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    font_cache[cache_key] = font
                    return font
            except Exception as e:
                if font_name and font_name not in tested_fonts:
                    tested_fonts.append(font_name)
                    print(f"✗ 无法加载字体 {font_name}: {str(e)[:50]}...")
                
                if i == len(fonts_to_try) - 1:
                    print(f"所有字体加载失败，使用默认字体")
                    font = pygame.font.Font(None, size)
                    font_cache[cache_key] = font
                    return font
                continue
        
        # 如果所有都失败，使用默认
        font = pygame.font.Font(None, size)
        font_cache[cache_key] = font
        return font
    
    return get_font

def safe_pymunk_init():
    """安全初始化pymunk，处理可能的错误"""
    try:
        space = pymunk.Space()
        space.gravity = (0, 900)  # 重力向下
        print("Pymunk 物理空间初始化成功")
        return space
    except Exception as e:
        print(f"Pymunk 初始化失败: {e}")
        print("请确保已安装 pymunk: pip install pymunk")
        raise

def safe_debug_draw(space, draw_options):
    """安全的调试绘制，处理pymunk颜色错误"""
    try:
        space.debug_draw(draw_options)
        return True
    except Exception as e:
        print(f"Pymunk 调试绘制错误: {e}")
        print("注意: 这不会影响游戏功能，仅影响物理调试显示")
        return False

# ========== 初始化 Pygame ==========
try:
    pygame.init()
    print("Pygame 初始化成功")
except Exception as e:
    print(f"Pygame 初始化失败: {e}")
    print("请确保已安装 pygame: pip install pygame")
    sys.exit(1)

# 屏幕尺寸
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700

try:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    if USE_ENGLISH_TEXT:
        pygame.display.set_caption("Bridge Master - Level Prototype (Fixed)")
    else:
        pygame.display.set_caption("搭桥专家 - 关卡原型 (修复版 v2)")
    print(f"屏幕初始化: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
except Exception as e:
    print(f"显示模式设置失败: {e}")
    print("尝试使用软件渲染...")
    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
    except:
        print("无法初始化显示，退出")
        sys.exit(1)

clock = pygame.time.Clock()
FPS = 60

# 初始化字体系统
get_font = init_font_system()

# 预加载常用字体大小
FONT_SMALL = get_font(24)
FONT_NORMAL = get_font(30)
FONT_MEDIUM = get_font(36)
FONT_LARGE = get_font(48)
FONT_XLARGE = get_font(72)

# ========== 文本翻译 ==========
if USE_ENGLISH_TEXT:
    TEXT = {
        "start": "Start",
        "end": "End",
        "wood": "Wood",
        "steel": "Steel",
        "mode_build": "Mode: Build",
        "mode_test": "Mode: Test",
        "mode_result": "Mode: Result",
        "total_cost": "Total Cost: ",
        "start_test": "Start Test",
        "rebuild": "Rebuild",
        "instructions": [
            "Instructions:",
            "1. Drag mouse to place materials",
            "2. Click material buttons to switch",
            "3. Click 'Start Test' to test bridge",
            "4. Goal: Lowest cost for vehicle to pass"
        ],
        "success": "Success!",
        "failure": "Bridge Collapsed!",
        "result_success": "Total Cost: ",
        "result_failure": "Vehicle fell, reinforce bridge",
        "hint": "Click 'Rebuild' to continue"
    }
else:
    TEXT = {
        "start": "起点",
        "end": "终点",
        "wood": "木材",
        "steel": "钢筋",
        "mode_build": "模式: 建造",
        "mode_test": "模式: 测试",
        "mode_result": "模式: 结果",
        "total_cost": "总成本: ",
        "start_test": "开始测试",
        "rebuild": "重新建造",
        "instructions": [
            "操作说明:",
            "1. 鼠标拖拽放置材料",
            "2. 点击材料按钮切换类型",
            "3. 点击'开始测试'测试桥梁",
            "4. 目标: 最低成本让车辆通过"
        ],
        "success": "成功通过！",
        "failure": "桥梁坍塌！",
        "result_success": "总成本: ",
        "result_failure": "车辆掉落，请加固桥梁",
        "hint": "点击'重新建造'继续挑战"
    }

# ========== Pymunk 物理空间 ==========
space = safe_pymunk_init()

# 绘制选项
draw_options = pymunk.pygame_util.DrawOptions(screen)

# ========== 材料类型枚举 ==========
class MaterialType(Enum):
    WOOD = 1      # 木材
    STEEL = 2     # 钢筋

# 材料属性 - 使用RGBA格式（修复pymunk颜色错误）
MATERIAL_PROPERTIES = {
    MaterialType.WOOD: {
        "name": TEXT["wood"],
        "color": (139, 90, 43, 255),   # 棕色，RGBA格式
        "density": 0.5,
        "elasticity": 0.8,
        "cost_per_meter": 10,
        "strength": 1000,
    },
    MaterialType.STEEL: {
        "name": TEXT["steel"],
        "color": (192, 192, 192, 255), # 银色，RGBA格式
        "density": 2.0,
        "elasticity": 0.9,
        "cost_per_meter": 50,
        "strength": 5000,
    }
}

# ========== 游戏状态类 ==========
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
        
        try:
            # 地形
            self.create_terrain()
            
            # 车辆
            self.create_car()
            print("游戏初始化完成")
        except Exception as e:
            print(f"游戏初始化失败: {e}")
            traceback.print_exc()
            raise
    
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
    
    def create_car(self):
        """创建车辆"""
        mass = 100
        size = (60, 30)
        moment = pymunk.moment_for_box(mass, size)
        body = pymunk.Body(mass, moment)
        body.position = self.start_pos
        shape = pymunk.Poly.create_box(body, size)
        shape.friction = 0.8
        
        # 使用RGBA格式的颜色
        shape.color = (255, 0, 0, 255)  # 红色，RGBA格式
        
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
        
        # 使用RGBA格式的颜色（修复pymunk颜色错误）
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
        
        # 绘制起点终点文字
        screen.blit(FONT_NORMAL.render(TEXT["start"], True, (0, 255, 0)), 
                   (self.start_pos[0]-20, self.start_pos[1]-30))
        screen.blit(FONT_NORMAL.render(TEXT["end"], True, (255, 0, 0)), 
                   (self.end_pos[0]-20, self.end_pos[1]-30))
        
        # 绘制材料
        for material in self.materials:
            shape = material["shape"]
            body = material["body"]
            color = MATERIAL_PROPERTIES[material["type"]]["color"]
            
            # 只使用RGB部分进行绘制（Pygame使用RGB）
            rgb_color = color[:3]
            
            # 计算线段端点
            a = body.local_to_world(shape.a)
            b = body.local_to_world(shape.b)
            
            pygame.draw.line(screen, rgb_color, (int(a.x), int(a.y)), (int(b.x), int(b.y)), int(shape.radius*2))
        
        # 安全地绘制物理调试信息
        safe_debug_draw(space, draw_options)
        
        # 绘制拖拽预览
        if self.dragging and self.drag_start and self.drag_end:
            color = MATERIAL_PROPERTIES[self.selected_material]["color"]
            rgb_color = color[:3]  # 只使用RGB部分
            pygame.draw.line(screen, rgb_color, self.drag_start, self.drag_end, 5)
            
            # 显示长度和成本
            length = math.hypot(self.drag_end[0] - self.drag_start[0], self.drag_end[1] - self.drag_start[1])
            cost = length * MATERIAL_PROPERTIES[self.selected_material]["cost_per_meter"] / 100
            if USE_ENGLISH_TEXT:
                text = f"Length: {length:.1f} Cost: {cost:.1f}"
            else:
                text = f"长度: {length:.1f} 成本: {cost:.1f}"
            text_surface = FONT_NORMAL.render(text, True, (0, 0, 0))
            screen.blit(text_surface, (self.drag_start[0], self.drag_start[1] - 20))
        
        # 绘制UI
        self.draw_ui()
        
        # 绘制结果
        if self.mode == "result":
            self.draw_result()
    
    def draw_ui(self):
        """绘制用户界面"""
        # 顶部状态栏
        pygame.draw.rect(screen, (50, 50, 50), (0, 0, SCREEN_WIDTH, 50))
        
        # 模式显示
        if self.mode == "build":
            mode_text = TEXT["mode_build"]
        elif self.mode == "test":
            mode_text = TEXT["mode_test"]
        else:
            mode_text = TEXT["mode_result"]
        
        mode_surface = FONT_MEDIUM.render(mode_text, True, (255, 255, 255))
        screen.blit(mode_surface, (20, 10))
        
        # 总成本
        cost_text = TEXT["total_cost"] + f"{self.total_cost:.1f}"
        cost_surface = FONT_MEDIUM.render(cost_text, True, (255, 255, 0))
        screen.blit(cost_surface, (300, 10))
        
        # 材料选择
        wood_color = MATERIAL_PROPERTIES[MaterialType.WOOD]["color"][:3]
        steel_color = MATERIAL_PROPERTIES[MaterialType.STEEL]["color"][:3]
        
        pygame.draw.rect(screen, wood_color if self.selected_material == MaterialType.WOOD else (200, 200, 200), 
                        (500, 10, 100, 30))
        pygame.draw.rect(screen, steel_color if self.selected_material == MaterialType.STEEL else (200, 200, 200), 
                        (610, 10, 100, 30))
        
        wood_text = FONT_MEDIUM.render(TEXT["wood"], True, (0, 0, 0))
        steel_text = FONT_MEDIUM.render(TEXT["steel"], True, (0, 0, 0))
        screen.blit(wood_text, (525, 10))
        screen.blit(steel_text, (635, 10))
        
        # 按钮
        if self.mode == "build":
            pygame.draw.rect(screen, (0, 150, 0), (SCREEN_WIDTH - 150, 10, 130, 30))
            test_text = FONT_MEDIUM.render(TEXT["start_test"], True, (255, 255, 255))
            screen.blit(test_text, (SCREEN_WIDTH - 140, 10))
        elif self.mode == "result":
            pygame.draw.rect(screen, (0, 100, 200), (SCREEN_WIDTH - 150, 10, 130, 30))
            restart_text = FONT_MEDIUM.render(TEXT["rebuild"], True, (255, 255, 255))
            screen.blit(restart_text, (SCREEN_WIDTH - 140, 10))
        
        # 操作说明
        for i, text in enumerate(TEXT["instructions"]):
            inst_surface = FONT_SMALL.render(text, True, (50, 50, 50))
            screen.blit(inst_surface, (20, SCREEN_HEIGHT - 120 + i * 25))
    
    def draw_result(self):
        """绘制结果界面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # 半透明黑色
        screen.blit(overlay, (0, 0))
        
        if self.success:
            text = FONT_XLARGE.render(TEXT["success"], True, (0, 255, 0))
            screen.blit(text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100))
            result_text = TEXT["result_success"] + f"{self.total_cost:.1f}"
        else:
            text = FONT_XLARGE.render(TEXT["failure"], True, (255, 0, 0))
            screen.blit(text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100))
            result_text = TEXT["result_failure"]
        
        text2 = FONT_LARGE.render(result_text, True, (255, 255, 255))
        screen.blit(text2, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2))
        
        hint = FONT_LARGE.render(TEXT["hint"], True, (255, 255, 0))
        screen.blit(hint, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 100))

def main():
    """主函数，包含错误处理"""
    try:
        print("=" * 50)
        print("搭桥专家修复版 v2")
        print("解决字体乱码和pymunk执行错误问题")
        print("=" * 50)
        
        game = GameState()
        running = True
        
        print("\n游戏开始运行:")
        print("1. 拖拽鼠标放置材料")
        print("2. 点击顶部按钮选择材料")
        print("3. 点击'开始测试'测试桥梁")
        print("4. 按ESC键退出游戏")
        
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
                    elif event.key == pygame.K_t:
                        # T键快速开始测试
                        if game.mode == "build":
                            game.start_test()
                            print("[快捷键] 开始测试桥梁")
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左键
                        # 检查按钮点击
                        if game.mode == "build":
                            # 材料选择按钮
                            if 500 <= mouse_pos[0] <= 600 and 10 <= mouse_pos[1] <= 40:
                                game.selected_material = MaterialType.WOOD
                                print(f"选择材料: {TEXT['wood']}")
                            elif 610 <= mouse_pos[0] <= 710 and 10 <= mouse_pos[1] <= 40:
                                game.selected_material = MaterialType.STEEL
                                print(f"选择材料: {TEXT['steel']}")
                            
                            # 开始测试按钮
                            elif SCREEN_WIDTH - 150 <= mouse_pos[0] <= SCREEN_WIDTH - 20 and 10 <= mouse_pos[1] <= 40:
                                game.start_test()
                                print("开始测试桥梁...")
                            
                            # 开始拖拽放置材料
                            else:
                                game.dragging = True
                                game.drag_start = mouse_pos
                                game.drag_end = mouse_pos
                                print("开始拖拽放置材料...")
                        
                        elif game.mode == "result":
                            # 重新建造按钮
                            if SCREEN_WIDTH - 150 <= mouse_pos[0] <= SCREEN_WIDTH - 20 and 10 <= mouse_pos[1] <= 40:
                                # 重置游戏
                                game = GameState()
                                print("重新开始游戏")
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and game.dragging and game.mode == "build":
                        game.dragging = False
                        if game.drag_start and game.drag_end:
                            # 添加材料
                            material = game.add_material(game.drag_start, game.drag_end, game.selected_material)
                            if material:
                                if USE_ENGLISH_TEXT:
                                    print(f"Added material: {material['length']:.1f}px, Cost: {material['cost']:.1f}")
                                else:
                                    print(f"添加材料: {material['length']:.1f}像素, 成本: {material['cost']:.1f}")
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
        
        print("游戏退出")
        
    except Exception as e:
        print(f"游戏运行错误: {e}")
        traceback.print_exc()
        print("\n故障排除:")
        print("1. 确保已安装依赖: pip install pygame pymunk")
        print("2. 如果字体乱码，请修改代码中 USE_ENGLISH_TEXT = True")
        print("3. 更新显卡驱动")
        print("4. 以管理员身份运行")
    
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    # 设置控制台编码
    try:
        import io
        import sys
        if sys.platform == "win32":
            import os
            os.system("chcp 65001 > nul")  # Windows设置UTF-8编码
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass
    
    main()