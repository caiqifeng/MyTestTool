import subprocess
import os
from typing import Optional

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

# ------------------- 主程序执行 -------------------
if __name__ == "__main__":
    # ************************* 需修改的配置 *************************
    # 配置1：要执行SVN Update的目标目录（Windows用r''原始字符串，Linux/macOS用普通路径）
    TARGET_DIR = r"G:\b_SEED_sandbox_dev_2025_12\GameV2"
    TARGET_PATH = [
        r"Assets\_Game\Resource\Config\Item\Item",
        r"Assets\_Game\Resource\ArtSource\UI\BigIcon",
        r"Assets\_Game\Resource\ArtSource\UI\Icon"
        ]
    
    # 配置2：执行模式（True=批量更新根目录下所有SVN子目录，False=仅更新指定单个目录）
    BATCH_UPDATE = False
    # 配置3：是否忽略错误（True=单个目录失败不影响后续执行，False=失败即终止）
    IGNORE_ERROR = False
    # *****************************************************************

    if BATCH_UPDATE:
        # 模式1：批量更新根目录下所有SVN受控子目录
        for temp_path in TARGET_PATH:
            full_path = os.path.join(TARGET_DIR, temp_path)
            batch_svn_update(full_path, IGNORE_ERROR)
    else:
        # 模式2：仅更新指定的单个目录
        for temp_path in TARGET_PATH:
            full_path = os.path.join(TARGET_DIR, temp_path)
            svn_update_dir(full_path, IGNORE_ERROR)
            #svn_update_dir(TARGET_DIR, IGNORE_ERROR)