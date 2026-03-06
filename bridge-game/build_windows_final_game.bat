@echo off
chcp 65001 > nul
echo ========================================
echo   搭桥专家最终版 - Windows 打包脚本
echo   修复图片应用和桥梁高度问题
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

REM 检查 bridge_game_final.py 是否存在
if not exist "bridge_game_final.py" (
    echo [错误] 未找到 bridge_game_final.py 文件
    echo 请确保脚本在游戏目录中运行
    dir *.py
    pause
    exit /b 1
)

echo.
echo [步骤2] 正在打包最终版游戏...
echo 使用命令: pyinstaller --onefile --console --name "BridgeMaster_Final" bridge_game_final.py

REM 使用控制台模式便于调试
pyinstaller --onefile --console --name "BridgeMaster_Final" bridge_game_final.py

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
echo [成功] 最终版打包完成！
echo EXE 文件位置: %cd%\dist\BridgeMaster_Final.exe
echo.
echo 最终版改进:
echo 1. ✅ 修复图片应用问题，确保图片正确加载和显示
echo 2. ✅ 修复桥梁高度问题，确保车辆能顺利上桥
echo 3. ✅ 详细的图片加载状态报告
echo 4. ✅ 加厚桥梁（12像素）以更好支撑车辆
echo 5. ✅ 车辆与路面平齐，无高度差问题
echo.
echo 运行方法:
echo 1. 双击运行: dist\BridgeMaster_Final.exe
echo 2. 命令行运行: dist\BridgeMaster_Final.exe
echo.
echo 图片支持:
echo 1. 游戏会自动加载 images/ 目录中的图片
echo 2. 控制台会显示图片加载状态
echo 3. 如果无图片，自动使用几何图形
echo.
echo 如果游戏无法运行，请尝试:
echo 1. 安装 Visual C++ Redistributable
echo 2. 确保显卡驱动更新
echo 3. 使用管理员权限运行
echo ========================================
echo.
pause