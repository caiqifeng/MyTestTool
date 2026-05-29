#!/usr/bin/env python3
"""
更新 Tabbar 样式配置
"""

import json
import os

PAGES_JSON_PATH = r"F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app\frontend\pages.json"
BACKUP_PATH = PAGES_JSON_PATH + ".backup"

def update_tabbar_style():
    """更新 tabbar 样式"""

    # 读取原文件
    with open(PAGES_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 备份原文件
    with open(BACKUP_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"已备份到: {BACKUP_PATH}")

    # 更新 tabbar 配置
    if "tabBar" in data:
        tabbar = data["tabBar"]

        # 优化样式
        tabbar.update({
            "color": "#999999",  # 未选中文字颜色
            "selectedColor": "#FF6B35",  # 选中文字颜色 (橙色主色)
            "backgroundColor": "#FFFFFF",  # 背景色
            "borderStyle": "white",  # 边框样式
            "height": "60px",  # 增加高度
            "fontSize": "11px",  # 字体稍大
            "iconWidth": "28px",  # 图标宽度增加
            "spacing": "4px",  # 间距增加
            "borderColor": "#F0F0F0",  # 边框颜色
            "borderTop": "1px solid #F0F0F0"  # 上边框
        })

        # 确保 list 存在
        if "list" not in tabbar:
            tabbar["list"] = []

        print("Tabbar 样式已更新:")
        print(f"  - 高度: {tabbar['height']}")
        print(f"  - 字体大小: {tabbar['fontSize']}")
        print(f"  - 图标宽度: {tabbar['iconWidth']}")
        print(f"  - 间距: {tabbar['spacing']}")

    # 写回文件
    with open(PAGES_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"已更新: {PAGES_JSON_PATH}")
    return True

def main():
    print("更新 Tabbar 样式配置")
    print("=" * 60)

    if not os.path.exists(PAGES_JSON_PATH):
        print(f"错误: 文件不存在 {PAGES_JSON_PATH}")
        return False

    success = update_tabbar_style()

    if success:
        print("\n✅ Tabbar 样式更新完成!")
        print("\n更新内容:")
        print("  • 高度: 50px → 60px")
        print("  • 字体大小: 10px → 11px")
        print("  • 图标宽度: 24px → 28px")
        print("  • 间距: 3px → 4px")
        print("  • 添加了浅色上边框")
        return 0
    else:
        print("\n❌ 更新失败")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())