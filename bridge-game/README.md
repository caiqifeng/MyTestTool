# 搭桥专家 - 关卡原型

基于 Python + Pygame + Pymunk 实现的搭桥游戏原型。

## 功能特点

1. **物理模拟**：使用 Pymunk 物理引擎模拟桥梁受力
2. **材料系统**：木材和钢筋两种材料，不同成本与强度
3. **建造模式**：鼠标拖拽放置桥梁材料
4. **测试模式**：车辆自动通过桥梁，检测是否成功
5. **成本计算**：实时计算桥梁总成本
6. **结果评估**：成功/失败反馈，成本显示

## 运行要求

- Python 3.7+
- Pygame 2.6.1+
- Pymunk 7.2.0+

## 安装依赖

```bash
pip install pygame pymunk
```

## 运行游戏

### 原版（可能出现乱码）
```bash
python bridge_game.py
```

### 修复版（解决乱码和执行错误）
```bash
python bridge_game_fixed.py
```

**修复版改进**：
1. **字体兼容性**：自动尝试多种中文字体，解决乱码问题
2. **错误处理**：详细的错误信息和调试输出
3. **控制台编码**：支持UTF-8编码输出
4. **系统兼容性**：更好的跨平台支持

### 问题诊断
如果游戏运行失败，修复版会显示具体错误原因，常见问题：
1. **缺少依赖**：运行 `pip install pygame pymunk`
2. **字体问题**：修复版自动尝试多种字体
3. **显示问题**：尝试以管理员身份运行或更新显卡驱动

## Windows 打包指南

### 重要提示：编码问题修复
原 `build_windows_exe.bat` 脚本可能出现乱码或执行错误，原因是 Windows 命令行编码问题。我们提供了修复版本：

### 推荐使用修复版本

**修复版脚本**（解决乱码问题）：
1. 下载以下文件到游戏目录：
   - `bridge_game.py` (主游戏代码)
   - `build_windows_exe_fixed.bat` (修复版中文脚本)
   - 或 `build_windows_simple.bat` (英文简化版)

2. 双击运行 `build_windows_exe_fixed.bat` 或 `build_windows_simple.bat`

3. 生成的 EXE 位于 `dist\BridgeMaster.exe` 或 `dist\bridge_game.exe`

### 各版本说明

| 脚本文件 | 特点 | 适用场景 |
|----------|------|----------|
| `build_windows_exe.bat` | 原始版本，可能乱码 | 不推荐使用 |
| `build_windows_exe_fixed.bat` | **推荐**，中文提示，修复编码 | 中文 Windows 系统 |
| `build_windows_simple.bat` | **推荐**，英文提示，兼容性好 | 所有 Windows 系统 |
| `build_windows_fixed_game.bat` | **最新推荐**，打包修复版游戏，解决字体乱码 | 所有出现乱码问题的系统 |

### 修复版游戏打包
如果您遇到游戏内文字乱码或执行错误，请使用修复版游戏：

**方法一：使用专用打包脚本**
1. 下载 `bridge_game_fixed.py` 和 `build_windows_fixed_game.bat`
2. 双击运行 `build_windows_fixed_game.bat`
3. 生成的 EXE: `dist\BridgeMaster_Fixed.exe`

**方法二：手动打包修复版**
```bash
pyinstaller --onefile --console --name "BridgeMaster_Fixed" bridge_game_fixed.py
```

### 手动打包（如果脚本仍失败）
```bash
# 1. 安装 Python 3.7+（安装时勾选 "Add Python to PATH"）
# 2. 打开命令提示符（CMD）或 PowerShell
# 3. 安装依赖
pip install pygame pymunk pyinstaller

# 4. 切换到游戏目录
cd "你的游戏文件夹路径"

# 5. 打包为 EXE（控制台模式，便于调试）
pyinstaller --onefile --console bridge_game.py

# 6. 运行游戏
dist\bridge_game.exe
```

### 常见问题解决

**问题1**："不是内部或外部命令，也不是可运行的程序"
- **原因**：脚本编码问题或路径问题
- **解决**：使用修复版脚本或手动打包

**问题2**：乱码显示
- **原因**：Windows 控制台编码不匹配
- **解决**：使用 `build_windows_simple.bat`（英文版）

**问题3**：依赖安装失败
- **解决**：以管理员身份运行命令提示符，或使用：
  ```bash
  pip install --user pygame pymunk pyinstaller
  ```

**问题4**：打包后 EXE 无法运行
- **解决**：安装 [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

## 操作说明

1. **选择材料**：
   - 点击顶部"木材"或"钢筋"按钮切换当前材料
   - 木材成本低但强度较低
   - 钢筋成本高但强度高

2. **建造桥梁**：
   - 在建造模式下，鼠标左键拖拽放置材料
   - 连接左侧平台(400,550)和右侧平台(800,550)
   - 实时显示材料长度和成本

3. **测试桥梁**：
   - 点击顶部"开始测试"按钮
   - 红色车辆将从起点驶向终点
   - 如果车辆安全通过，显示成功和总成本
   - 如果桥梁坍塌或车辆掉落，显示失败

4. **重新挑战**：
   - 测试结束后，点击"重新建造"按钮重置关卡

## 关卡设计

- **地形**：宽400像素的缺口（左侧平台0-400，右侧平台800-1200）
- **起点**：(200, 500) - 绿色圆圈
- **终点**：(1000, 500) - 红色圆圈
- **目标**：用最低成本搭建能让车辆通过的桥梁

## 代码结构

```
bridge_game.py
├── MaterialType 枚举（木材、钢筋）
├── MATERIAL_PROPERTIES 材料属性字典
├── GameState 游戏状态类
│   ├── create_terrain() 创建地形
│   ├── create_car() 创建车辆
│   ├── add_material() 添加材料到物理空间
│   ├── start_test() 开始测试
│   ├── update() 更新游戏状态
│   ├── draw() 绘制游戏画面
│   └── draw_ui() 绘制用户界面
└── main() 主游戏循环
```

## 扩展建议

1. **更多材料**：添加混凝土、绳索、铰链等
2. **连接点**：实现材料之间的连接点（焊接、螺栓）
3. **应力显示**：实时显示材料受力情况
4. **更多关卡**：不同跨度、高度、环境因素
5. **成本排行榜**：记录最低成本解决方案
6. **材料切割**：允许切割材料到指定长度
7. **环境因素**：添加风力、水流等干扰

## 物理参数调整

在 `MATERIAL_PROPERTIES` 中可以调整：
- `density`：密度（影响重量）
- `elasticity`：弹性（影响反弹）
- `cost_per_meter`：每米成本
- `strength`：最大受力（暂未实现断裂检测）

## 已知限制

1. 材料连接点简单，未实现真实连接约束
2. 材料强度检测未实现（不会断裂）
3. 车辆与桥梁的交互简单
4. 2D简化模拟，非真实3D桥梁

## 截图

（运行游戏后可查看实际效果）

## 下一步开发

1. 实现材料断裂检测
2. 添加材料连接点系统
3. 实现多关卡选择
4. 添加材料库存限制
5. 实现成本排行榜
6. 添加声音效果
7. 优化UI/UX设计