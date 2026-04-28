"""Further compress MP3 files to 24kbps for strict size limits."""
import os, subprocess

FFMPEG = r'C:\Users\admin\.workbuddy\binaries\node\workspace\node_modules\ffmpeg-static\ffmpeg.exe'
AUDIO_DIR = r'C:\Users\admin\WorkBuddy\Claw\meditation-miniapp\audioPackage\audio'

print('Re-compressing to 24kbps mono 16000Hz...')
print('=' * 60)

total_before = 0
total_after = 0

for fname in sorted(os.listdir(AUDIO_DIR)):
    if not fname.endswith('.mp3'):
        continue

    src = os.path.join(AUDIO_DIR, fname)
    tmp = src + '_tmp.mp3'
    size_before = os.path.getsize(src)
    total_before += size_before

    # 24kbps mono 16000Hz - still acceptable for ambient nature sounds
    cmd = [
        FFMPEG, '-y', '-i', src, '-vn',
        '-acodec', 'libmp3lame',
        '-b:a', '24k',
        '-ac', '1',
        '-ar', '16000',
        tmp
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        size_after = os.path.getsize(tmp)
        total_after += size_after
        ratio = (1 - size_after / size_before) * 100
        print(f'{fname:25s}  {size_before/1024:.0f}KB -> {size_after/1024:.0f}KB  (-{ratio:.0f}%)')
        os.replace(tmp, src)
    else:
        print(f'FAILED: {fname}')
        if os.path.exists(tmp):
            os.remove(tmp)

print('=' * 60)
if total_before > 0:
    total_mb_after = total_after/1024/1024
    print(f'Total:  {total_before/1024:.0f}KB -> {total_after/1024:.0f}KB ({total_mb_after:.2f}MB)  (-{(1-total_after/total_before)*100:.0f}%)')
    if total_mb_after > 2.0:
        print(f'WARNING: still over 2MB limit! Need to split into 2 subpackages or lower bitrate.')
    else:
        print(f'OK: within 2MB limit.')
print('Done!')
