@echo off
REM Windows 打包脚本 - 搭桥专家
echo 正在安装 Python 依赖...
pip install pygame pymunk pyinstaller

echo 正在打包为 Windows EXE...
pyinstaller --onefile --windowed --name "搭桥专家" bridge_game.py

echo 打包完成！
echo EXE 文件位置: dist\搭桥专家.exe
echo 按任意键退出...
pause > nul