"""
批量对比 UI 目录下的大图标和小图标，生成带图片的 Excel 表格
使用项目配置文件来匹配图标对
"""

import os
import re
import io
import subprocess
from pathlib import Path
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from pic_compare import compare_images
from PIL import Image
from datetime import datetime
from typing import Optional


fWrite_Log = None

def write_log(msg):
    print(msg)
    fWrite_Log.write(msg + "\n")
    fWrite_Log.flush()

def create_log_file(log_fullPath):
    global fWrite_Log    
    fWrite_Log = open(log_fullPath, "a", encoding="utf-8")
    

def get_image_info(dir_path):
    if not os.path.exists(dir_path):
        return "不存在"

    try:
        with Image.open(dir_path) as img:
            image_info = str(img.width) + "x" + str(img.height)
            return image_info

    except Exception as e:
        #write_log(f"错误: {e}")
        return "获取异常"

def parse_config_file(config_file_path):
    """
    解析项目配置文件，提取UIBigIcon和UIIcon的路径对
    
    Args:
        config_file_path: 配置文件路径（UIIcon.txt）
    
    Returns:
        list: [(icon_name, bigicon_path, icon_path), ...]
    """
    matches = []
    
    with open(config_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 正则匹配UIBigIcon和UIIcon的路径
    # 匹配两种格式：
    # 1. "Assets/_Game/Resource/ArtSource/UI/..."
    # 2. "ArtSource://UI/..."
    #pattern = r'"UIBigIcon":\s*"([^"]+)"\s*,\s*[\r\n]+\s*[^\r\n]*"UIIcon":\s*"([^"]+)"'
    #pattern = r'"ID":\s*"([^"]+)".*?$|^.*?"UIBigIcon":\s*"([^"]+)".*?$|^.*?"UIIcon":\s*"([^"]+)".*?$'

    pattern = r'"ID":\s*"([^"]*)".*?"UIBigIcon":\s*"([^"]*)".*?"UIIcon":\s*"([^"]*)"'
    found_pairs = re.findall(pattern, content, re.DOTALL)
    print(f"共匹配到 {len(found_pairs)} 组数据：\n")

    for idx,(id_raw, big_icon_raw, icon_raw) in enumerate(found_pairs, 1):
        # 跳过空路径
        if not big_icon_raw:
            big_icon_raw = "大图为空"

        if not icon_raw:
            big_icon_raw = "小图为空"
        
        # 清理路径前缀
        def clean_path(path):
            # 移除 "Assets/_Game/Resource/ArtSource/UI/"
            path = re.sub(r'^Assets/_Game/Resource/ArtSource/UI/', '', path)
            # 移除 "ArtSource://UI/"
            path = re.sub(r'^ArtSource://UI/', '', path)
            return path       
        
        big_icon_path = big_icon_raw #clean_path(big_icon_raw)
        icon_path = icon_raw #clean_path(icon_raw)
        id_name = id_raw
        
        # 提取图标名称（使用文件名不含扩展名）
        icon_name = Path(icon_path).stem
        
        matches.append((id_name, icon_name, big_icon_path, icon_path))
    
    return matches

def index_png_files(directory):
    """
    递归索引目录下所有的 PNG 文件
    
    Args:
        directory: 要索引的目录路径
    
    Returns:
        dict: {文件名: 完整路径} 的字典
    """
    png_files = {}
    directory_path = Path(directory)
    
    if not directory_path.exists():
        write_log(f"警告: 目录不存在 - {directory}")
        return png_files
    
    # 递归查找所有 .png 文件
    for png_file in directory_path.rglob("*.png"):
        filename = png_file.name
        # 如果有重名文件，保存相对路径作为key
        if filename in png_files:
            # 使用相对于根目录的路径作为key
            rel_path = png_file.relative_to(directory_path)
            key = str(rel_path).replace("\\", "/")
        else:
            key = filename
        
        png_files[key] = str(png_file)
    
    return png_files

def match_icons(bigicon_files, icon_files):
    """
    根据文件名匹配大图标和小图标
    
    Args:
        bigicon_files: 大图标文件字典
        icon_files: 小图标文件字典
    
    Returns:
        list: [(图标名称, 大图路径, 小图路径), ...]
    """
    matches = []
    
    # 为小图标创建一个快速查找字典（支持文件名和相对路径）
    icon_lookup = {}
    for key, path in icon_files.items():
        # 同时用文件名和相对路径作为key
        filename = Path(key).name
        icon_lookup[filename] = path
        icon_lookup[key] = path
    
    # 遍历大图标，查找对应的小图标
    for big_key, big_path in bigicon_files.items():
        big_filename = Path(big_key).name
        
        # 尝试多种匹配方式
        small_path = None
        
        # 1. 先尝试完全匹配文件名
        if big_filename in icon_lookup:
            small_path = icon_lookup[big_filename]
        
        # 2. 尝试匹配相对路径（去掉 BigIcon 前缀）
        elif big_key in icon_lookup:
            small_path = icon_lookup[big_key]
        
        # 3. 尝试匹配去掉 "BigIcon/" 后的路径
        if not small_path and isinstance(big_key, str):
            # 从相对路径中提取子路径
            big_path_obj = Path(big_path)
            # 找到 BigIcon 后面的路径部分
            parts = big_path_obj.parts
            try:
                bigicon_idx = parts.index("BigIcon")
                sub_path = Path(*parts[bigicon_idx + 1:])
                sub_path_str = str(sub_path).replace("\\", "/")
                
                # 在 Icon 目录下查找相同的子路径
                if sub_path_str in icon_lookup:
                    small_path = icon_lookup[sub_path_str]
                elif sub_path.name in icon_lookup:
                    small_path = icon_lookup[sub_path.name]
            except (ValueError, IndexError):
                pass
        
        if small_path:
            # 提取图标名称（不含扩展名）
            icon_name = Path(big_filename).stem
            matches.append((icon_name, big_path, small_path))
        else:
            write_log(f"未找到匹配: {big_filename}")
    
    return matches

def resize_image_for_excel(image_path, max_width=100, max_height=100):
    """
    调整图片大小以适应 Excel 单元格
    
    Args:
        image_path: 图片路径
        max_width: 最大宽度（像素）
        max_height: 最大高度（像素）
    
    Returns:
        BytesIO: 调整后的图片数据流
    """
    try:
        img = Image.open(image_path)
        
        # 保持纵横比调整大小
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # 转换为 RGB（如果是 RGBA）
        if img.mode == 'RGBA':
            # 创建白色背景
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # 使用 alpha 通道作为蒙版
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 保存到内存
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return img_buffer
    except Exception as e:
        write_log(f"  警告: 无法处理图片 {image_path}: {e}")
        return None

def custom_protocol_to_abs_path(root_path, protocol_path: str) -> Optional[str]:
    """
    将ArtSource:///ArtBase://自定义协议路径转换为绝对路径
    :param protocol_path: 带自定义协议的路径（如ArtSource://UI/BigIcon/xxx.png）
    :return: 拼接后的绝对路径，协议不支持/路径为空则返回None
    """
    # 项目固定根路径（根据你的实际路径修改，无需末尾反斜杠）
    # ROOT_PATH = r"G:\b_SEED_dev_pre_2025-12-16\GameV2\Assets\_Game\Resource"

    # 自定义协议与对应子目录的映射（扩展其他协议只需在此添加键值对）
    PROTOCOL_MAP = {
        "ArtSource://": "ArtSource",
        "ArtBase://": "ArtBase"
    }

    # 前置校验：路径为空直接返回None
    if not isinstance(protocol_path, str) or len(protocol_path.strip()) == 0:
        print(f"【错误】无效路径：路径为空或非字符串类型")
        return protocol_path

    # 遍历协议映射，匹配并处理路径
    for protocol_prefix, sub_dir in PROTOCOL_MAP.items():
        if protocol_path.startswith(protocol_prefix):
            # 提取协议后的相对路径（移除协议前缀）
            relative_path = protocol_path[len(protocol_prefix):]
            # 前置校验：移除前缀后无有效路径
            if not relative_path.strip():
                print(f"【错误】无效路径：{protocol_path}，协议后无实际路径")
                return protocol_path
            # 拼接完整绝对路径：根路径 + 协议对应子目录 + 相对路径
            # os.path.join自动适配系统分隔符，兼容/和\
            #print(f"===========:{sub_dir}")
            abs_path = os.path.join(root_path, sub_dir, relative_path).replace('\\','/')
            
            return abs_path

     # 场景2：处理以Assets/_Game/Resource/开头的相对根路径
     # 相对根路径的固定前缀
    RELATIVE_ROOT_PREFIX = "Assets/_Game/Resource/"
    if protocol_path.startswith(RELATIVE_ROOT_PREFIX):
        protocol_path = protocol_path.replace(RELATIVE_ROOT_PREFIX,'')
        # 直接拼接项目根路径与相对根路径，生成绝对路径
        abs_path = os.path.join(root_path, protocol_path).replace('\\','/')
        return abs_path
    
    # 未匹配到支持的自定义协议
    print(f"【错误】不支持的协议：{protocol_path}，仅支持{list(PROTOCOL_MAP.keys())}")
    return protocol_path

def compare_all_icons_to_excel(ui_directory, config_file, output_file="comparison_results.xlsx"):
    """
    根据配置文件对比所有匹配的图标并生成带图片的 Excel 报告
    
    Args:
        ui_directory: UI 根目录路径
        config_file: 配置文件路径（UIIcon.txt）
        output_file: 输出 Excel 文件名
    """
    #ui_path = Path(ui_directory)
    
    write_log("正在解析配置文件...")

    matches = parse_config_file(config_file)
    write_log(f"从配置文件中找到 {len(matches)} 对图标配置\n")
    
    if not matches:
        write_log("配置文件中没有找到有效的图标对，程序退出")
        return
    
    # 创建 Excel 工作簿
    wb = Workbook()
    ws = wb.active
    ws.title = "图标相似度对比"
    
    # 设置表头
    headers = ['ID', '图片名', '大图路径', '小图路径', '大图图片', '小图图片', '感知相似度', 'SSIM', '像素相似度', '大图Size', '小图Size', '大图透明度', '小图透明度']
    ws.append(headers)
    
    # 设置表头样式
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    
    for col_num in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # 设置列宽
    ws.column_dimensions['A'].width = 30  # ID
    ws.column_dimensions['B'].width = 30  # 图片名
    ws.column_dimensions['C'].width = 40  # 大图路径
    ws.column_dimensions['D'].width = 40  # 小图路径
    ws.column_dimensions['E'].width = 15  # 大图图片
    ws.column_dimensions['F'].width = 15  # 小图图片
    ws.column_dimensions['G'].width = 12  # 感知相似度
    ws.column_dimensions['H'].width = 15  # SSIM
    ws.column_dimensions['I'].width = 15  # 像素相似度
    ws.column_dimensions['J'].width = 15  # 大图Size
    ws.column_dimensions['K'].width = 15  # 小图Size
    ws.column_dimensions['L'].width = 15  # 大图透明度
    ws.column_dimensions['M'].width = 15  # 小图透明度
    
    # 设置行高（标准行高适合 100px 的图片）
    ws.row_dimensions[1].height = 30  # 表头
    
    total = len(matches)
    write_log("="*80)
    write_log(f"开始对比 {total} 对图标并生成 Excel...")
    write_log("="*80 + "\n")
    
    current_row = 2
    success_count = 0
    error_count = 0
    skip_count = 0
    
    for idx, (id_name, icon_name, big_rel_path, small_rel_path) in enumerate(matches, 1):
        # 构建完整路径
        print(f"========================111:{big_rel_path}")
        big_path = custom_protocol_to_abs_path(ui_directory, big_rel_path)
        print(f"========================:{big_path},{big_rel_path}")
        small_path = custom_protocol_to_abs_path(ui_directory, small_rel_path)
        print(f"========================:{small_path},{small_rel_path}")
        
        big_image_info = get_image_info(big_path)
        small_image_info = get_image_info(small_path)
        # big_image_ratio = calculate_transparency_ratio(big_path, include_semi=True)
        # small_image_ratio = calculate_transparency_ratio(small_path, include_semi=True)
        big_image_ratio = calculate_transparency_ratio(big_path)
        small_image_ratio = calculate_transparency_ratio(small_path)

        write_log(f"[{idx}/{total}] 处理: {icon_name}")
        write_log(f"  大图: {big_rel_path} \t {big_image_info} \t {big_image_ratio}")
        write_log(f"  小图: {small_rel_path} \t {small_image_info} \t {small_image_ratio}")
                
        nSkill_Check = False

        # 检查文件是否存在
        if not os.path.exists(big_path):
            write_log(f"  警告: 大图不存在，跳过")
            #big_rel_path = "大图不存在"
            skip_count += 1
            nSkill_Check = True
            write_log(f"\n")
        
        if not os.path.exists(small_path):
            write_log(f"  警告: 小图不存在，跳过")
            #small_rel_path = "小图不存在"
            skip_count += 1
            nSkill_Check = True
            write_log(f"\n")
                
        try:
            # 计算相似度
            if not nSkill_Check:
                comparison = compare_images(str(big_path), str(small_path), show_details=False)
                perc_sim = comparison['Perceptual_Similarity']
                ssim_score = comparison['SSIM']
                pixel_sim = comparison['Pixel_Similarity']
            else:
                comparison = 0
            
            print("=====================================1")
            # 写入文本数据
            ws.cell(row=current_row, column=1, value=id_name)
            ws.cell(row=current_row, column=2, value=icon_name)
            ws.cell(row=current_row, column=3, value=big_rel_path)
            ws.cell(row=current_row, column=4, value=small_rel_path)
            ws.cell(row=current_row, column=7, value=f"{perc_sim:.4f}")
            ws.cell(row=current_row, column=8, value=f"{ssim_score:.4f}")
            ws.cell(row=current_row, column=9, value=f"{pixel_sim:.4f}")
                        
            print("=====================================2")
            # 设置文本对齐
            for col_num in range(1, 11):
                cell = ws.cell(row=current_row, column=col_num)
                cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
            
            # 相似度列居中
            for col_num in [5, 6, 7, 8, 9, 10, 11, 12, 13]:
                ws.cell(row=current_row, column=col_num).alignment = Alignment(horizontal='center', vertical='center')
            print("=====================================3")
            # 插入大图
            if os.path.exists(big_path):
                big_img_buffer = resize_image_for_excel(str(big_path), max_width=100, max_height=100)
                if big_img_buffer:
                    xl_big_img = XLImage(big_img_buffer)
                    # 设置图片大小
                    xl_big_img.width = 100
                    xl_big_img.height = 100
                    # 将图片锚定到单元格 E (列4)
                    ws.add_image(xl_big_img, f'E{current_row}')
            
            # 插入小图
            if os.path.exists(small_path):
                small_img_buffer = resize_image_for_excel(str(small_path), max_width=100, max_height=100)
                if small_img_buffer:
                    xl_small_img = XLImage(small_img_buffer)
                    # 设置图片大小
                    xl_small_img.width = 100
                    xl_small_img.height = 100
                    # 将图片锚定到单元格 F (列5)
                    ws.add_image(xl_small_img, f'F{current_row}')
            print("=====================================4")
            # 设置行高以容纳图片（约 100px + 边距）
            ws.row_dimensions[current_row].height = 80
            write_log(f"  感知相似度: {perc_sim:.4f}, SSIM: {ssim_score:.4f} ✓")

            ws.cell(row=current_row, column=10, value=big_image_info)
            ws.cell(row=current_row, column=11, value=small_image_info)
            ws.cell(row=current_row, column=12, value=big_image_ratio)
            ws.cell(row=current_row, column=13, value=small_image_ratio)
            print("=====================================5")            
            current_row += 1
            success_count += 1
            
        except Exception as e:
            write_log(f"  错误: {e}")
            # 即使出错也记录
            ws.cell(row=current_row, column=1, value=icon_name)
            ws.cell(row=current_row, column=2, value=big_rel_path)
            ws.cell(row=current_row, column=3, value=small_rel_path)
            ws.cell(row=current_row, column=6, value="ERROR")
            ws.cell(row=current_row, column=7, value="ERROR")
            ws.cell(row=current_row, column=8, value="ERROR")
            ws.row_dimensions[current_row].height = 20
            current_row += 1
            error_count += 1
        
        write_log(f"\n")
    
    # 保存 Excel 文件
    output_path = Path(output_file)
    write_log("="*80)
    write_log(f"保存结果到: {output_path.absolute()}")
    wb.save(output_path)
    write_log("="*80 + "\n")
    
    write_log(f"✓ 成功保存 Excel 文件")
    write_log(f"  成功: {success_count}")
    write_log(f"  失败: {error_count}")
    write_log(f"  跳过: {skip_count}")
    write_log(f"  总计: {len(matches)}")
    write_log("="*80)

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
        return -999.0
    # 校验是否为图片文件（简单后缀判断）
    valid_suffix = ('.png', '.webp', '.gif', '.tga')
    # if not image_path.lower().endswith(valid_suffix):
    #     print(f"【警告】非支持的透明图片格式：{image_path}")
    #     return -999.0
    if Path(str(image_path)).suffix not in valid_suffix:
        print(f"【警告】非支持的透明图片格式：{image_path}")
        return -999.0

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
                return -999.0

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
        return -999.0

def search_json_files(root_dir, save_txt_path):
    """
    递归遍历根目录下所有.json文件，提取指定行内容并保存到TXT文件
    :param root_dir: 要搜索的根目录（JSON文件所在文件夹）
    :param save_txt_path: 结果TXT文件的保存全路径
    """
    # 编译正则：匹配包含"ID":/"UIBigIcon":/"UIIcon":的行，兼容JSON缩进/行尾逗号
    pattern = re.compile(r'^\s*("ID":|"UIBigIcon":|"UIIcon":)\s*.+,?$', re.MULTILINE)
    # 打开TXT文件（w模式：覆盖原有内容；a模式：追加内容，根据需求选择）
    with open(save_txt_path, 'w', encoding='utf-8') as txt_f:
        # 递归遍历所有目录和文件
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                # 仅处理.json后缀文件（忽略大小写，兼容.JSON/.Json）
                if filename.lower().endswith('.json'):
                    file_full_path = os.path.join(dirpath, filename)
                    match_lines = []  # 存储当前文件匹配到的目标行
                    try:
                        # 读取JSON文件（utf-8编码，兼容中文/特殊字符）
                        with open(file_full_path, 'r', encoding='utf-8') as json_f:
                            content = json_f.read()
                            # 逐行匹配，提取符合条件的行并保留原始缩进
                            for line in content.splitlines():
                                if pattern.search(line):
                                    match_lines.append(line.rstrip())  # 去除行尾多余空白
                        # 仅当同时匹配到3行（ID/UIBigIcon/UIIcon）时写入TXT
                        if len(match_lines) == 3:
                            # 按格式写入：2个空格+文件全路径
                            txt_f.write(f"  {file_full_path}\n")
                            # 每个目标行前加1个制表符\t，逐行写入
                            for line in match_lines:
                                txt_f.write(f"\t{line}\n")
                            # 不同文件间空一行，与示例格式一致
                            txt_f.write("\n")
                    except Exception as e:
                        # 捕获异常（编码/权限/文件损坏等），写入错误信息便于排查
                        error_info = f"【读取失败】{file_full_path} - 原因：{str(e)}\n\n"
                        txt_f.write(error_info)
                        print(error_info.strip())  # 控制台也打印错误，提醒用户
    print(f"提取完成！结果已保存至：{save_txt_path}")

def svn_update_dir(target_dir: str, ignore_error: bool = False) -> bool:
    """
    对指定目录执行svn update操作
    :param target_dir: 要执行svn update的目录全路径（必填）
    :param ignore_error: 是否忽略执行错误（False=报错时抛出异常/打印详情，True=仅返回False不中断程序）
    :return: 执行成功返回True，失败返回False
    """
    # 校验目标目录是否存在
    if not os.path.exists(target_dir):
        print(f"【错误】目标目录不存在：{target_dir}")
        return False
    if not os.path.isdir(target_dir):
        print(f"【错误】指定路径不是目录：{target_dir}")
        return False

    # 构建svn update命令（--non-interactive 非交互模式，避免终端弹框阻塞）
    # 核心命令：svn update 目标目录 --non-interactive
    cmd = ["svn", "update", target_dir, "--non-interactive"]
    print(f"【开始执行】SVN Update 目录：{target_dir}")
    print(f"【执行命令】{' '.join(cmd)}")

    try:
        # 执行命令，捕获输出和错误（stdout/stderr合并，统一编码）
        # shell=False：跨平台兼容，cmd以列表形式传入更安全
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=False,
            encoding="utf-8",
            errors="ignore",
            cwd=target_dir  # 切换到目标目录执行，避免路径问题
        )

        # 打印SVN执行输出日志
        if result.stdout:
            print(f"【SVN输出日志】\n{result.stdout.strip()}")

        # 判断执行结果：returncode=0表示成功，非0表示失败
        if result.returncode == 0:
            print(f"【执行成功】目录SVN Update完成：{target_dir}\n")
            return True
        else:
            error_info = f"【执行失败】目录SVN Update出错，返回码：{result.returncode}"
            if ignore_error:
                print(f"{error_info}，已忽略错误\n")
                return False
            else:
                raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"【SVN命令错误】{e}\n")
        return False
    except Exception as e:
        print(f"【系统执行错误】目录{target_dir}执行SVN Update失败，原因：{str(e)}\n")
        return False

def batch_svn_update(root_dir: str, ignore_error: bool = False) -> None:
    """
    递归遍历根目录，对所有包含.svn文件夹的目录执行svn update（仅更新SVN受控目录）
    :param root_dir: 根目录全路径
    :param ignore_error: 是否忽略单个目录的执行错误
    """
    if not os.path.exists(root_dir) or not os.path.isdir(root_dir):
        print(f"【错误】根目录无效：{root_dir}")
        return

    print(f"【开始批量更新】递归检测{root_dir}下的所有SVN受控目录...\n")
    success_count = 0
    fail_count = 0

    # 递归遍历所有子目录
    for dirpath, _, _ in os.walk(root_dir):
        # 仅对包含.svn文件夹的目录执行update（SVN受控目录标识）
        svn_meta_dir = os.path.join(dirpath, ".svn")
        if os.path.exists(svn_meta_dir) and os.path.isdir(svn_meta_dir):
            if svn_update_dir(dirpath, ignore_error):
                success_count += 1
            else:
                fail_count += 1

    print(f"【批量更新完成】总计检测到{success_count + fail_count}个SVN受控目录，成功{success_count}个，失败{fail_count}个")

def get_branch(root_dir: str):
    if r"b_SEED_sandbox_dev_2022-06-24" in root_dir:
        return "main"
    elif r"b_SEED_dev_pre_2025-12-16" in root_dir:
        return "pre"
    else:
        return "nil"

def main():
    """
    主函数
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='批量对比 UI 目录下的大图标和小图标，生成带图片的 Excel 表格',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python batch_compare_excel.py UI UIIcon.txt
  python batch_compare_excel.py UI UIIcon.txt -o my_results.xlsx
        """
    )
    
    parser.add_argument('ui_directory', 
                       help='UI 根目录路径')
    # parser.add_argument('config_file', 
    #                    help='配置文件路径 (UIIcon.txt)')
    # parser.add_argument('-o', '--output', default='icon_comparison.xlsx',
    #                    help='输出 Excel 文件名 (默认: icon_comparison.xlsx)')
    
    args = parser.parse_args()

    # 涉及的目录
    PROJECT_PATH = [
        r"Assets\_Game\Resource\Config\Item\Item",
        r"Assets\_Game\Resource\ArtSource\UI\BigIcon",
        r"Assets\_Game\Resource\ArtSource\UI\Icon",
        r"Assets\_Game\Resource\ArtBase\UI"
        ]
        
    # 工程根目录
    remove_suffix = r"\Assets\_Game\Resource" #r"\Assets\_Game\Resource\ArtSource\UI"
    TARGET_DIR = args.ui_directory.replace(remove_suffix, "")
    
    # Item目录
    ITEM_ROOT = os.path.join(TARGET_DIR, PROJECT_PATH[0])
       
    time_str = datetime.now().strftime("%m%d_%H%M")

    # 分支/主干
    BRANCH = get_branch(args.ui_directory)

    LOG_FULL_PATH = f"{BRANCH}_{time_str}_Log_.txt"
    create_log_file(LOG_FULL_PATH)

    # JSON内容读取结果
    JSON_CONTENT_TXT = f"{BRANCH}_{time_str}_json_content.txt"
    
    # 完整结果
    RESULT_XLSX = f"{BRANCH}_{time_str}_icon_comparison.xlsx"

    try:
        # 更新SVN
        IGNORE_ERROR = False
        for temp_path in PROJECT_PATH:
            full_path = os.path.join(TARGET_DIR, temp_path)
            # 配置3：是否忽略错误（True=单个目录失败不影响后续执行，False=失败即终止）    
            svn_update_dir(full_path, IGNORE_ERROR)

        # 读取Item/Item目录下的json内容
        search_json_files(ITEM_ROOT, JSON_CONTENT_TXT)

        compare_all_icons_to_excel(args.ui_directory, JSON_CONTENT_TXT, RESULT_XLSX)
        return 0
    except Exception as e:
        write_log(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
