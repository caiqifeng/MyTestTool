"""
冥想小程序 - 音频上传到腾讯云 COS 并生成配置
使用方法：
  1. pip install cos-python-sdk-v5
  2. 填写下方 COS_CONFIG 中的配置信息
  3. python upload_audio_to_cos.py
  4. 脚本自动上传并打印可直接粘贴到 session.js 的 AUDIO_CDN 配置

也可以不用脚本，直接在 COS 控制台手动上传，然后复制链接填到 session.js
"""

import os
import sys

# ============================================================
# 🔧 填写你的腾讯云 COS 配置
# ============================================================
COS_CONFIG = {
    'secret_id':  'YOUR_SECRET_ID',    # 腾讯云 API SecretId
    'secret_key': 'YOUR_SECRET_KEY',   # 腾讯云 API SecretKey
    'region':     'ap-guangzhou',      # Bucket 所在地区
    'bucket':     'YOUR_BUCKET_NAME',  # Bucket 名称，例: meditation-audio-1234567890
    'prefix':     'meditation/audio/', # COS 中的目录前缀
}
# ============================================================

AUDIO_DIR = os.path.join(os.path.dirname(__file__), 'audioPackage', 'audio')
AUDIO_DIR2 = os.path.join(os.path.dirname(__file__), 'audioPackage2', 'audio')

AUDIO_FILES = {
    'rain_forest':   os.path.join(AUDIO_DIR, 'rain_forest.mp3'),
    'ocean_waves':   os.path.join(AUDIO_DIR, 'ocean_waves.mp3'),
    'morning_birds': os.path.join(AUDIO_DIR, 'morning_birds.mp3'),
    'deep_rumble':   os.path.join(AUDIO_DIR, 'deep_rumble.mp3'),
    'night_ambient': os.path.join(AUDIO_DIR2, 'night_ambient.mp3'),
    'singing_bowl':  os.path.join(AUDIO_DIR2, 'singing_bowl.mp3'),
}


def upload_all():
    try:
        from qcloud_cos import CosConfig, CosS3Client
    except ImportError:
        print('请先安装：pip install cos-python-sdk-v5')
        sys.exit(1)

    cfg = COS_CONFIG
    if 'YOUR_' in cfg['secret_id']:
        print('❌ 请先填写 COS_CONFIG 中的配置信息')
        sys.exit(1)

    config = CosConfig(
        Region=cfg['region'],
        SecretId=cfg['secret_id'],
        SecretKey=cfg['secret_key'],
    )
    client = CosS3Client(config)
    bucket = cfg['bucket']
    prefix = cfg['prefix']
    base_url = f"https://{bucket}.cos.{cfg['region']}.myqcloud.com/{prefix}"

    cdn_map = {}
    for key, filepath in AUDIO_FILES.items():
        if not os.path.exists(filepath):
            print(f'⚠️  文件不存在，跳过: {filepath}')
            continue
        cos_key = prefix + os.path.basename(filepath)
        print(f'上传 {os.path.basename(filepath)} ...', end=' ')
        with open(filepath, 'rb') as f:
            client.put_object(
                Bucket=bucket,
                Body=f,
                Key=cos_key,
                ContentType='audio/mpeg',
            )
        url = base_url + os.path.basename(filepath)
        cdn_map[key] = url
        print(f'✓  {url}')

    print('\n\n✅ 上传完成！将以下代码替换 session.js 中的 AUDIO_CDN：\n')
    print('var AUDIO_CDN = {')
    for key, url in cdn_map.items():
        print(f"  {key}: '{url}',")
    print('}\n')


if __name__ == '__main__':
    upload_all()
