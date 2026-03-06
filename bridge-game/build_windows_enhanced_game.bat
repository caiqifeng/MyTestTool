@echo off
chcp 65001 > nul
echo ========================================
echo   搭桥专家增强版 - Windows 打包脚本
echo   修复车辆移动，支持图片替换
echo ========================================
echo.

REM 检查 Python 是否安装
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查 pip 是否安装
where pip >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到 pip，请确保 Python 安装时勾选了 "Add Python to PATH"
    pause
    exit /b 1
)

REM 显示 Python 版本
echo [信息] Python 版本:
python --version

REM 安装依赖
echo.
echo [步骤1] 正在安装 Python 依赖...
echo pygame, pymunk, pyinstaller
pip install pygame pymunk pyinstaller

if %errorlevel% neq 0 (
    echo [警告] 依赖安装失败，尝试使用管理员权限或虚拟环境
    echo 手动安装命令: pip install pygame pymunk pyinstaller
    pause
)

REM 检查 bridge_game_enhanced.py 是否存在
if not exist "bridge_game_enhanced.py" (
    echo [错误] 未找到 bridge_game_enhanced.py 文件
    echo 请确保脚本在游戏目录中运行
    dir *.py
    pause
    exit /b 1
)

echo.
echo [步骤2] 正在打包增强版游戏...
echo 使用命令: pyinstaller --onefile --console --name "BridgeMaster_Enhanced" bridge_game_enhanced.py

REM 使用控制台模式便于调试
pyinstaller --onefile --console --name "BridgeMaster_Enhanced" bridge_game_enhanced.py

if %errorlevel% neq 0 (
    echo [错误] 打包失败，请检查以上错误信息
    echo 常见问题:
    echo 1. 缺少管理员权限
    echo 2. Python 环境问题
    echo 3. 依赖包未正确安装
    pause
    exit /b 1
)

echo.
echo ========================================
echo [成功] 增强版打包完成！
echo EXE 文件位置: %cd%\dist\BridgeMaster_Enhanced.exe
echo.
echo 增强版改进:
echo 1. 修复车辆移动问题，不会卡住
echo 2. 支持图片替换（可将图片放入 images/ 目录）
echo 3. 防卡住检测，车辆低速时自动施加推力
echo 4. 物理参数优化，游戏体验更好
echo.
echo 运行方法:
echo 1. 双击运行: dist\BridgeMaster_Enhanced.exe
echo 2. 命令行运行: dist\BridgeMaster_Enhanced.exe
echo.
echo 图片支持:
echo 1. 创建 images/ 目录
echo 2. 放入图片: car.png, wood.png, steel.png
echo 3. 如果无图片，自动使用几何图形
echo.
echo 如果游戏无法运行，请尝试:
echo 1. 安装 Visual C++ Redistributable
echo 2. 确保显卡驱动更新
echo 3. 使用管理员权限运行
echo ========================================
echo.
pause