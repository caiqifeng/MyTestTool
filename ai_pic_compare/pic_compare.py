"""
现代图片相似度对比工具
支持多种算法：SSIM(结构相似性)、MSE、感知哈希等
"""

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from PIL import Image
import imagehash
import argparse
from pathlib import Path


def extract_content_bbox(img):
    """
    提取图片中非透明内容的边界框
    
    Args:
        img: 输入图片（可能包含 alpha 通道）
    
    Returns:
        tuple: (x, y, w, h, content_img, has_alpha)
               边界框坐标和尺寸，裁剪后的内容图片，是否有alpha通道
    """
    has_alpha = False
    
    if len(img.shape) == 3 and img.shape[2] == 4:  # 有 alpha 通道
        has_alpha = True
        alpha = img[:, :, 3]
        # 找到非透明像素（alpha > 10）
        mask = alpha > 10
    else:
        # 没有 alpha 通道，创建全部为True的掩码
        mask = np.ones(img.shape[:2], dtype=bool)
    
    # 找到所有非透明像素的坐标
    coords = np.argwhere(mask)
    
    if len(coords) == 0:
        # 完全透明的图片，返回整个图片
        return 0, 0, img.shape[1], img.shape[0], img, has_alpha
    
    # 计算边界框
    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0)
    
    # 裁剪内容区域
    content = img[y_min:y_max+1, x_min:x_max+1]
    
    return x_min, y_min, x_max - x_min + 1, y_max - y_min + 1, content, has_alpha


def resize_content_to_same_size(img1_content, img2_content, target_size=None):
    """
    将两张内容图片缩放到相同尺寸
    
    Args:
        img1_content: 第一张内容图片
        img2_content: 第二张内容图片
        target_size: 目标尺寸 (width, height)，如果为None则使用较小图片的尺寸
    
    Returns:
        tuple: (resized_img1, resized_img2)
    """
    h1, w1 = img1_content.shape[:2]
    h2, w2 = img2_content.shape[:2]
    
    if target_size is None:
        # 使用较小的尺寸作为目标
        if h1 * w1 <= h2 * w2:
            target_size = (w1, h1)
        else:
            target_size = (w2, h2)
    
    # 缩放两张图片
    if (w1, h1) != target_size:
        resized1 = cv2.resize(img1_content, target_size, interpolation=cv2.INTER_LANCZOS4)
    else:
        resized1 = img1_content
    
    if (w2, h2) != target_size:
        resized2 = cv2.resize(img2_content, target_size, interpolation=cv2.INTER_LANCZOS4)
    else:
        resized2 = img2_content
    
    return resized1, resized2


def convert_to_white_bg(img, has_alpha):
    """
    将带alpha通道的图片转换为白色背景的BGR图片
    
    Args:
        img: 输入图片
        has_alpha: 是否有alpha通道
    
    Returns:
        BGR图片
    """
    if has_alpha and len(img.shape) == 3 and img.shape[2] == 4:
        bgr = img[:, :, :3]
        alpha = img[:, :, 3]
        
        # 创建白色背景
        white_bg = np.ones_like(bgr, dtype=np.uint8) * 255
        
        # alpha混合
        alpha_float = alpha.astype(float) / 255.0
        alpha_3channel = np.stack([alpha_float] * 3, axis=2)
        
        result = (bgr * alpha_3channel + white_bg * (1 - alpha_3channel)).astype(np.uint8)
        return result
    elif len(img.shape) == 3 and img.shape[2] >= 3:
        return img[:, :, :3]
    else:
        return img


def calculate_aligned_similarity(img1_content, img2_content, has_alpha1, has_alpha2):
    """
    计算对齐后的图片相似度
    
    Args:
        img1_content: 第一张内容图片
        img2_content: 第二张内容图片
        has_alpha1: 第一张图片是否有alpha
        has_alpha2: 第二张图片是否有alpha
    
    Returns:
        dict: 相似度指标
    """
    # 转换为白色背景的BGR图片
    bgr1 = convert_to_white_bg(img1_content, has_alpha1)
    bgr2 = convert_to_white_bg(img2_content, has_alpha2)
    
    # 缩放到相同尺寸
    aligned1, aligned2 = resize_content_to_same_size(bgr1, bgr2)
    
    h, w = aligned1.shape[:2]
    total_pixels = h * w
    
    # 1. 像素级MSE
    mse = np.mean((aligned1.astype(float) - aligned2.astype(float)) ** 2)
    max_mse = 255 * 255 * 3
    pixel_similarity = 1 - (mse / max_mse)
    
    # 2. 结构相似性 SSIM
    gray1 = cv2.cvtColor(aligned1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(aligned2, cv2.COLOR_BGR2GRAY)
    ssim_score, _ = ssim(gray1, gray2, full=True)
    
    # 3. 颜色直方图相似度
    hist_similarities = []
    for ch in range(3):
        hist1 = cv2.calcHist([aligned1], [ch], None, [256], [0, 256])
        hist2 = cv2.calcHist([aligned2], [ch], None, [256], [0, 256])
        cv2.normalize(hist1, hist1)
        cv2.normalize(hist2, hist2)
        corr = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        hist_similarities.append(max(0, corr))
    
    avg_hist_similarity = np.mean(hist_similarities)
    
    # 4. 感知相似度（综合指标）
    # 权重：SSIM 50%, 像素相似度 30%, 直方图 20%
    perceptual_similarity = (
        ssim_score * 0.5 + 
        pixel_similarity * 0.3 + 
        avg_hist_similarity * 0.2
    )
    
    return {
        'pixel_similarity': pixel_similarity,
        'ssim': ssim_score,
        'histogram_similarity': avg_hist_similarity,
        'perceptual_similarity': perceptual_similarity,
        'mse': mse,
        'aligned_size': (w, h),
        'total_pixels': total_pixels
    }


def extract_non_transparent_pixels(img):
    """
    提取图片中非透明的像素
    
    Args:
        img: 输入图片（可能包含 alpha 通道）
    
    Returns:
        tuple: (非透明像素的BGR值数组, alpha掩码, BGR图像)
    """
    if len(img.shape) == 3 and img.shape[2] == 4:  # 有 alpha 通道
        bgr = img[:, :, :3]
        alpha = img[:, :, 3]
        # 非透明像素的掩码（alpha > 10，避免完全透明或接近透明的像素）
        mask = alpha > 10
        non_transparent_pixels = bgr[mask]
        return non_transparent_pixels, mask, bgr
    else:
        # 没有 alpha 通道，所有像素都是非透明的
        h, w = img.shape[:2]
        mask = np.ones((h, w), dtype=bool)
        return img.reshape(-1, 3), mask, img


def sample_pixels_intelligently(large_pixels, small_pixel_count, method='uniform'):
    """
    从大图的像素中智能采样，使其数量接近小图
    
    Args:
        large_pixels: 大图的像素数组 (N, 3)
        small_pixel_count: 目标采样数量
        method: 采样方法 ('uniform' 均匀采样, 'random' 随机采样)
    
    Returns:
        采样后的像素数组
    """
    large_count = len(large_pixels)
    
    if large_count <= small_pixel_count:
        # 大图像素数不比小图多，直接返回
        return large_pixels
    
    if method == 'uniform':
        # 均匀采样：每隔固定间隔取一个像素
        step = large_count / small_pixel_count
        indices = np.arange(0, large_count, step).astype(int)[:small_pixel_count]
        return large_pixels[indices]
    elif method == 'random':
        # 随机采样
        indices = np.random.choice(large_count, small_pixel_count, replace=False)
        return large_pixels[indices]
    else:
        raise ValueError(f"未知的采样方法: {method}")


def calculate_pixel_similarity(pixels1, pixels2):
    """
    基于像素值计算相似度
    
    Args:
        pixels1: 第一组像素 (N, 3)
        pixels2: 第二组像素 (M, 3)
    
    Returns:
        dict: 包含多种相似度指标
    """
    # 确保两组像素数量相同
    min_count = min(len(pixels1), len(pixels2))
    if len(pixels1) > min_count:
        pixels1 = sample_pixels_intelligently(pixels1, min_count, method='uniform')
    if len(pixels2) > min_count:
        pixels2 = sample_pixels_intelligently(pixels2, min_count, method='uniform')
    
    # 1. 颜色直方图相似度
    def calc_hist_similarity(p1, p2):
        hist1 = np.histogram(p1.flatten(), bins=256, range=(0, 256))[0]
        hist2 = np.histogram(p2.flatten(), bins=256, range=(0, 256))[0]
        hist1 = hist1.astype(float) / (hist1.sum() + 1e-7)
        hist2 = hist2.astype(float) / (hist2.sum() + 1e-7)
        # 计算直方图相关性
        correlation = np.corrcoef(hist1, hist2)[0, 1]
        return max(0, correlation)  # 确保非负
    
    # 2. 均方误差
    mse = np.mean((pixels1.astype(float) - pixels2.astype(float)) ** 2)
    
    # 3. 归一化相似度 (基于MSE)
    max_mse = 255 * 255 * 3  # 最大可能的MSE
    normalized_similarity = 1 - (mse / max_mse)
    
    # 4. 颜色分布相似度（按通道）
    channel_similarities = []
    for ch in range(3):
        ch_sim = calc_hist_similarity(pixels1[:, ch:ch+1], pixels2[:, ch:ch+1])
        channel_similarities.append(ch_sim)
    
    avg_channel_similarity = np.mean(channel_similarities)
    
    return {
        'pixel_mse': mse,
        'pixel_similarity': normalized_similarity,
        'histogram_similarity': avg_channel_similarity,
        'channel_similarities': channel_similarities
    }


def resize_to_match(img1, img2):
    """
    将较大的图片调整为较小图片的尺寸
    
    Args:
        img1: 第一张图片
        img2: 第二张图片
    
    Returns:
        调整后的两张图片
    """
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    
    # 确定较小的尺寸
    if h1 * w1 > h2 * w2:
        # img1 是大图，调整为 img2 的尺寸
        target_size = (w2, h2)
        img1_resized = cv2.resize(img1, target_size, interpolation=cv2.INTER_LANCZOS4)
        img2_resized = img2
        print(f"已将大图 ({w1}x{h1}) 调整为小图尺寸 ({w2}x{h2})")
    elif h2 * w2 > h1 * w1:
        # img2 是大图，调整为 img1 的尺寸
        target_size = (w1, h1)
        img1_resized = img1
        img2_resized = cv2.resize(img2, target_size, interpolation=cv2.INTER_LANCZOS4)
        print(f"已将大图 ({w2}x{h2}) 调整为小图尺寸 ({w1}x{h1})")
    else:
        # 尺寸相同
        img1_resized = img1
        img2_resized = img2
        print(f"两张图片尺寸相同 ({w1}x{h1})")
    
    return img1_resized, img2_resized


def calculate_ssim(img1, img2):
    """
    使用 SSIM (结构相似性指数) 计算相似度
    SSIM 是最现代和准确的图片相似度算法之一
    
    Returns:
        float: 相似度分数 (0-1, 1 表示完全相同)
    """
    # 转换为灰度图
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # 计算 SSIM
    score, diff = ssim(gray1, gray2, full=True)
    return score


def calculate_mse(img1, img2):
    """
    计算均方误差 (MSE)
    
    Returns:
        float: MSE 值 (0 表示完全相同，值越大差异越大)
    """
    err = np.sum((img1.astype("float") - img2.astype("float")) ** 2)
    err /= float(img1.shape[0] * img1.shape[1])
    return err


def calculate_phash(img1_path, img2_path):
    """
    使用感知哈希 (Perceptual Hash) 计算相似度
    适合检测轻微修改过的图片
    
    Returns:
        int: 汉明距离 (0 表示完全相同，值越小越相似)
    """
    hash1 = imagehash.phash(Image.open(img1_path))
    hash2 = imagehash.phash(Image.open(img2_path))
    return hash1 - hash2


def calculate_dhash(img1_path, img2_path):
    """
    使用差异哈希 (Difference Hash) 计算相似度
    
    Returns:
        int: 汉明距离 (0 表示完全相同，值越小越相似)
    """
    hash1 = imagehash.dhash(Image.open(img1_path))
    hash2 = imagehash.dhash(Image.open(img2_path))
    return hash1 - hash2


def calculate_histogram_similarity(img1, img2):
    """
    使用直方图相关性计算相似度
    
    Returns:
        float: 相关系数 (0-1, 1 表示完全相同)
    """
    # 计算每个通道的直方图
    hist1_b = cv2.calcHist([img1], [0], None, [256], [0, 256])
    hist1_g = cv2.calcHist([img1], [1], None, [256], [0, 256])
    hist1_r = cv2.calcHist([img1], [2], None, [256], [0, 256])
    
    hist2_b = cv2.calcHist([img2], [0], None, [256], [0, 256])
    hist2_g = cv2.calcHist([img2], [1], None, [256], [0, 256])
    hist2_r = cv2.calcHist([img2], [2], None, [256], [0, 256])
    
    # 归一化
    cv2.normalize(hist1_b, hist1_b)
    cv2.normalize(hist1_g, hist1_g)
    cv2.normalize(hist1_r, hist1_r)
    cv2.normalize(hist2_b, hist2_b)
    cv2.normalize(hist2_g, hist2_g)
    cv2.normalize(hist2_r, hist2_r)
    
    # 计算相关性
    corr_b = cv2.compareHist(hist1_b, hist2_b, cv2.HISTCMP_CORREL)
    corr_g = cv2.compareHist(hist1_g, hist2_g, cv2.HISTCMP_CORREL)
    corr_r = cv2.compareHist(hist1_r, hist2_r, cv2.HISTCMP_CORREL)
    
    # 平均相关性
    return (corr_b + corr_g + corr_r) / 3.0


def compare_images(img1_path, img2_path, show_details=True):
    """
    对比两张图片的相似度，使用内容对齐的算法
    自动提取非透明区域的边界框，对齐后再对比
    
    Args:
        img1_path: 第一张图片路径
        img2_path: 第二张图片路径
        show_details: 是否显示详细信息
    
    Returns:
        dict: 包含各种相似度指标的字典
    """
    # 检查文件是否存在
    if not Path(img1_path).exists():
        raise FileNotFoundError(f"图片不存在: {img1_path}")
    if not Path(img2_path).exists():
        raise FileNotFoundError(f"图片不存在: {img2_path}")
    
    # 读取图片（包含 alpha 通道）
    img1 = cv2.imread(img1_path, cv2.IMREAD_UNCHANGED)
    img2 = cv2.imread(img2_path, cv2.IMREAD_UNCHANGED)
    
    if img1 is None:
        raise ValueError(f"无法读取图片: {img1_path}")
    if img2 is None:
        raise ValueError(f"无法读取图片: {img2_path}")
    
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    
    # 提取内容边界框
    x1, y1, w1_content, h1_content, content1, has_alpha1 = extract_content_bbox(img1)
    x2, y2, w2_content, h2_content, content2, has_alpha2 = extract_content_bbox(img2)
    
    if show_details:
        print(f"图片1: {w1}x{h1}, 内容区域: {w1_content}x{h1_content}, 锚点: ({x1}, {y1})")
        print(f"图片2: {w2}x{h2}, 内容区域: {w2_content}x{h2_content}, 锚点: ({x2}, {y2})")
    
    # 计算对齐后的相似度
    aligned_sim = calculate_aligned_similarity(content1, content2, has_alpha1, has_alpha2)
    
    # 计算感知哈希（用于快速判断）
    phash_dist = calculate_phash(img1_path, img2_path)
    dhash_dist = calculate_dhash(img1_path, img2_path)
    
    # 组合结果
    results = {
        'Perceptual_Similarity': aligned_sim['perceptual_similarity'],
        'Pixel_Similarity': aligned_sim['pixel_similarity'],
        'SSIM': aligned_sim['ssim'],
        'Histogram_Similarity': aligned_sim['histogram_similarity'],
        'MSE': aligned_sim['mse'],
        'pHash_distance': phash_dist,
        'dHash_distance': dhash_dist,
        'aligned_size': aligned_sim['aligned_size'],
        'content1_size': (w1_content, h1_content),
        'content2_size': (w2_content, h2_content),
    }
    
    if show_details:
        print("\n" + "="*70)
        print("图片相似度对比结果（基于内容对齐算法）")
        print("="*70)
        print(f"图片1: {img1_path}")
        print(f"图片2: {img2_path}")
        print("-"*70)
        
        print(f"【感知相似度（推荐）】: {results['Perceptual_Similarity']:.4f}")
        print(f"  说明: 综合评分（SSIM 50% + 像素 30% + 直方图 20%）")
        print(f"  评估: ", end="")
        if results['Perceptual_Similarity'] > 0.95:
            print("✓✓✓ 图片几乎完全相同")
        elif results['Perceptual_Similarity'] > 0.90:
            print("✓✓ 图片高度相似")
        elif results['Perceptual_Similarity'] > 0.80:
            print("✓ 图片较为相似")
        elif results['Perceptual_Similarity'] > 0.70:
            print("○ 图片有一定相似性")
        else:
            print("✗ 图片差异较大")
        
        print(f"\n【SSIM - 结构相似性】: {results['SSIM']:.4f}")
        print(f"  说明: 考虑亮度、对比度和结构的综合指标")
        
        print(f"\n【像素相似度】: {results['Pixel_Similarity']:.4f}")
        print(f"  说明: 基于像素值的直接对比")
        
        print(f"\n【直方图相似度】: {results['Histogram_Similarity']:.4f}")
        print(f"  说明: 基于颜色分布的相似性")
        
        print(f"\n【像素MSE】: {results['MSE']:.2f}")
        print(f"  说明: 均方误差，越小越相似")
        
        print(f"\n【pHash距离】: {results['pHash_distance']}")
        print(f"  说明: 感知哈希，<10为高度相似")
        
        print(f"\n【dHash距离】: {results['dHash_distance']}")
        print(f"  说明: 差异哈希，<10为高度相似")
        
        print(f"\n【对齐尺寸】: {results['aligned_size'][0]}x{results['aligned_size'][1]}")
        print(f"  内容1: {results['content1_size'][0]}x{results['content1_size'][1]}")
        print(f"  内容2: {results['content2_size'][0]}x{results['content2_size'][1]}")
        
        print("="*70)
        print("\n综合评估:")
        perc_sim = results['Perceptual_Similarity']
        phash = results['pHash_distance']
        
        if perc_sim > 0.95 and phash < 5:
            print("✓✓✓ 两张图片内容几乎完全相同")
        elif perc_sim > 0.90 and phash < 10:
            print("✓✓ 两张图片内容高度相似")
        elif perc_sim > 0.80:
            print("✓ 两张图片内容较为相似")
        elif perc_sim > 0.70:
            print("○ 两张图片有一定相似性")
        else:
            print("✗ 两张图片差异较大")
        
        print("="*70 + "\n")
    
    return results


def main():
    """
    主函数 - 命令行接口
    """
    parser = argparse.ArgumentParser(
        description='现代图片相似度对比工具 - 基于内容对齐算法',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python pic_compare.py image1.jpg image2.jpg
  python pic_compare.py large_image.png small_image.png --quiet
        """
    )
    
    parser.add_argument('image1', help='第一张图片路径')
    parser.add_argument('image2', help='第二张图片路径')
    parser.add_argument('-q', '--quiet', action='store_true', 
                       help='安静模式，只显示感知相似度分数')
    
    args = parser.parse_args()
    
    try:
        results = compare_images(args.image1, args.image2, show_details=not args.quiet)
        
        if args.quiet:
            print(f"{results['Perceptual_Similarity']:.4f}")
        
        return 0
    
    except Exception as e:
        print(f"错误: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
