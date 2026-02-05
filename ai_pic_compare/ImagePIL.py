from PIL import Image
import os

def calculate_transparency_ratio(image_path: str, include_semi: bool = False) -> float:
    """
    计算单张图片的透明度占比（百分比，保留2位小数）
    :param image_path: 图片文件全路径（支持PNG/WebP等带透明通道格式）
    :param include_semi: 是否统计半透明像素（A>0且A<255），默认False（仅统计A=0完全透明）
    :return: 透明度占比（0.0 ~ 100.0），文件不存在/非图片返回-1
    """
    # 校验文件是否存在
    if not os.path.exists(image_path):
        print(f"【错误】文件不存在：{image_path}")
        return -1.0
    # 校验是否为图片文件（简单后缀判断）
    valid_suffix = ('.png', '.webp', '.gif', '.tga')
    if not image_path.lower().endswith(valid_suffix):
        print(f"【警告】非支持的透明图片格式：{image_path}")
        return 0.0

    try:
        # 打开图片并避免自动加载缩略图
        with Image.open(image_path) as img:
            # 转换为RGBA模式（保留透明通道，非RGBA模式会自动补A=255）
            rgba_img = img.convert("RGBA")
            # 获取图片像素矩阵（(宽度, 高度)）和总像素数
            width, height = rgba_img.size
            total_pixels = width * height
            if total_pixels == 0:
                print(f"【错误】空图片：{image_path}")
                return -1.0

            # 提取所有像素的A通道值（透明度）
            # getdata()返回像素元组列表，每个元组为(R, G, B, A)
            a_channel = [pixel[3] for pixel in rgba_img.getdata()]

            # 统计透明像素数量
            if include_semi:
                # 统计：完全透明（A=0）+ 半透明（0<A<255）
                transparent_pixels = sum(1 for a in a_channel if a < 255)
            else:
                # 仅统计：完全透明（A=0）
                transparent_pixels = sum(1 for a in a_channel if a == 0)

            # 计算透明度占比（保留2位小数）
            ratio = (transparent_pixels / total_pixels) * 100
            return round(ratio, 2)

    except Exception as e:
        print(f"【错误】处理图片失败 {image_path}：{str(e)}")
        return -1.0

# ------------------- 调用示例 -------------------
if __name__ == "__main__":
    # 替换为你的图片路径（Windows用r''原始字符串）
    IMG_PATH = r"g:\b_SEED_dev_pre_2025-12-16\GameV2\Assets\_Game\Resource\ArtSource\UI\Icon\Item\FormulaBook_Part\FormulaBook.Part.Carpet_Square_M02C01.png"
    # 仅统计完全透明像素
    ratio1 = calculate_transparency_ratio(IMG_PATH)
    # 统计完全透明+半透明像素
    ratio2 = calculate_transparency_ratio(IMG_PATH, include_semi=True)
    
    if ratio1 >= 0:
        print(f"图片：{os.path.basename(IMG_PATH)}")
        print(f"仅完全透明占比：{ratio1}%")
        print(f"完全+半透明占比：{ratio2}%")