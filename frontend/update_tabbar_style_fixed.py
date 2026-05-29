#!/usr/bin/env python3
"""
更新 Tabbar 样式配置 - 无表情符号版本
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
    with open(BACKUP_PATH, 'w', utf-8) as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Backed up to: {BACKUP_PATH}")

    # 更新 tabbar 配置
    if "tabBar" in data:
        tabbar = data["tabBar"]

        # 优化样式
        tabbar.update({
            "color": "#999999",
            "selectedColor": "#FF6B35",
            "backgroundColor": "#FFFFFF",
            "borderStyle": "white",
            "height": "60px",
            "fontSize": "11px",
            "iconWidth": "28px",
            "spacing": "4px",
            "borderColor": "#F0F0F0"
        })

        # 确保 list 存在
        if "list" not in tabbar:
            tabbar["list"] = []

        print("Tabbar style updated:")
        print(f"  - Height: {tabbar['height']}")
        print(f"  - Font size: {tabbar['fontSize']}")
        print(f"  - Icon width: {tabbar['iconWidth']}")
        print(f"  - Spacing: {tabbar['spacing']}")

    # 写回文件
    with open(PAGES_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Updated: {PAGES_JSON_PATH}")
    return True

def main():
    print("Updating Tabbar Style Configuration")
    print("=" * 60)

    if not os.path.exists(PAGES_JSON_PATH):
        print(f"Error: File does not exist {PAGES_JSON_PATH}")
        return False

    success = update_tabbar_style()

    if success:
        print("\n[SUCCESS] Tabbar style update completed!")
        print("\nChanges made:")
        print("  • Height: 50px → 60px")
        print("  • Font size: 10px → 11px")
        print("  • Icon width: 24px → 28px")
        print("  • Spacing: 3px → 4px")
        print("  • Added light top border")
        return 0
    else:
        print("\n[FAILED] Update failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())