"""
搭桥专家 - 配置文件
用户可以在这里修改游戏设置
"""

# ========== 游戏配置 ==========

# 语言设置：True使用英文，False使用中文
# 如果遇到字体乱码问题，请设置为True
USE_ENGLISH_TEXT = False

# 显示设置
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

# 物理设置
GRAVITY = 900  # 重力大小
CAR_SPEED = 200  # 车辆速度（像素/秒）
CAR_MASS = 100  # 车辆质量

# 材料属性
MATERIALS = {
    "wood": {
        "name_cn": "木材",
        "name_en": "Wood",
        "color": (139, 90, 43, 255),   # RGBA格式
        "density": 0.5,
        "elasticity": 0.8,
        "cost_per_meter": 10,
        "strength": 1000,
    },
    "steel": {
        "name_cn": "钢筋",
        "name_en": "Steel",
        "color": (192, 192, 192, 255), # RGBA格式
        "density": 2.0,
        "elasticity": 0.9,
        "cost_per_meter": 50,
        "strength": 5000,
    }
}

# 调试设置
SHOW_PHYSICS_DEBUG = True  # 显示物理调试信息
SHOW_CONSOLE_LOG = True    # 显示控制台日志

# ========== 快捷键设置 ==========
KEY_QUIT = "escape"        # 退出游戏
KEY_TEST = "t"            # 快速测试
KEY_RESET = "r"           # 重置游戏

# ========== 文字配置（自动根据语言设置选择） ==========
def get_text_config(use_english):
    """获取文字配置"""
    if use_english:
        return {
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
        return {
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

# 导出当前文本配置
TEXT = get_text_config(USE_ENGLISH_TEXT)

# ========== 打印配置信息 ==========
if __name__ == "__main__":
    print("搭桥专家 - 当前配置")
    print("=" * 40)
    print(f"语言: {'英文' if USE_ENGLISH_TEXT else '中文'}")
    print(f"屏幕尺寸: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    print(f"帧率: {FPS}")
    print(f"重力: {GRAVITY}")
    print(f"材料数量: {len(MATERIALS)}")
    print("=" * 40)