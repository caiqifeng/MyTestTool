# 游戏图片资源

此目录用于存放游戏的图片资源。增强版游戏 (`bridge_game_enhanced.py`) 会自动加载此目录中的图片。

## 示例图片说明

本目录已包含三张示例图片（自动生成）：
- `car.png` - 简单的车辆图标（红色车身，蓝色车窗）
- `wood.png` - 木材纹理（棕色木纹）
- `steel.png` - 钢筋纹理（银色金属）

您可以随时用自己的图片替换这些示例图片。游戏会优先使用您提供的图片。

## 所需图片文件

| 文件名 | 用途 | 建议尺寸 | 说明 |
|--------|------|----------|------|
| `car.png` | 车辆图片 | 60×30 像素 | 车辆图标，建议使用俯视图 |
| `wood.png` | 木材图片 | 任意尺寸 | 木材纹理，会自动拉伸 |
| `steel.png` | 钢筋图片 | 任意尺寸 | 钢筋/金属纹理，会自动拉伸 |

## 图片要求

1. **格式**：PNG 格式（支持透明度）
2. **背景**：建议使用透明背景
3. **尺寸**：无严格要求，游戏会自动缩放
4. **颜色**：无特殊要求

## 图片获取建议

### 方法一：在线搜索（免费资源）
- **车辆图片**：搜索 "top view car png" 或 "car icon top view png"
- **木材纹理**：搜索 "wood texture png" 或 "wood beam png"
- **钢筋纹理**：搜索 "steel texture png" 或 "metal beam png"

推荐网站：
- [Flaticon](https://www.flaticon.com) - 图标资源
- [Freepik](https://www.freepik.com) - 免费素材
- [Pngtree](https://pngtree.com) - PNG 素材

### 方法二：使用 AI 生成
- 使用 AI 工具生成简单的 2D 图标
- 提示词示例：
  - "A top view of a simple car icon, 2D flat design, transparent background"
  - "Wooden beam texture, seamless pattern, transparent background"
  - "Steel beam texture, metallic surface, transparent background"

### 方法三：自己绘制
- 使用绘图软件（如 Photoshop、GIMP、Krita）
- 或使用在线绘图工具（如 Figma、Canva）

## 备用方案

如果此目录中没有图片，游戏会自动使用几何图形：
- **车辆**：红色矩形 + 黑色车轮
- **木材**：棕色线段
- **钢筋**：银色线段

## 使用步骤

1. 将下载或制作的图片放入此目录
2. 确保文件名完全匹配（小写）
3. 运行增强版游戏：
   ```bash
   python bridge_game_enhanced.py
   ```
4. 游戏启动时会显示图片加载状态

## 注意事项

- 图片文件大小建议不超过 500KB
- 避免使用过大的图片，以免影响性能
- 如果图片加载失败，游戏会自动回退到几何图形
- 可以随时更换图片，游戏会在下次启动时重新加载