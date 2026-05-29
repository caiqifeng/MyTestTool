"""
Fix failed images using verified Pexels photo IDs.
Also compress the large avatar PNG.
"""

import urllib.request
import ssl
import os
from io import BytesIO
from PIL import Image

STATIC = r'F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app\frontend\static'
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

# (local_path, target_size, pexels_id)
FIXES = [
    # Failed images - using verified Pexels IDs
    ('products/large/product-croissant.jpg', (600, 600), 4828339),
    ('products/large/cart-croissant.jpg', (600, 600), 6537669),
    ('products/large/cart-chocolate-cake.jpg', (600, 600), 12927134),
    ('products/small/product-cheesecake.jpg', (300, 300), 10964755),
    ('product-detail/carousel-bread.jpg', (400, 300), 18319033),

    # Also replace some existing ones with better quality photos
    ('product-detail/carousel-croissant.jpg', (400, 300), 15533810),
    ('product-detail/carousel-pastries.jpg', (400, 300), 29349521),
    ('product-detail/detail-bakery-display.jpg', (400, 300), 29380152),
    ('banners/banner-bakery-interior.jpg', (800, 400), 30666847),
    ('banners/banner-cake-dessert.jpg', (800, 400), 30884565),
    ('banners/banner-coffee-breakfast.jpg', (800, 400), 16773426),

    # Better product shots
    ('products/large/product-chocolate-cake.jpg', (600, 600), 33327470),
    ('products/large/product-strawberry-mousse.jpg', (600, 600), 33327466),
    ('products/small/product-bread.jpg', (300, 300), 14160612),
    ('products/small/product-latte.jpg', (300, 300), 19859289),

    # Fresh avatar
    ('avatars/default-avatar.png', (400, 400), 19499005),
]

def download(photo_id, w, h):
    url = f'https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg?auto=compress&cs=tinysrgb&w={w}&h={h}&dpr=1&fit=crop'
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
        return resp.read()

def smart_crop(img, target):
    tw, th = target
    iw, ih = img.size
    if iw == tw and ih == th:
        return img
    ratio = tw / th
    img_ratio = iw / ih
    if img_ratio > ratio:
        new_w = int(ih * ratio)
        left = (iw - new_w) // 2
        img = img.crop((left, 0, left + new_w, ih))
    else:
        new_h = int(iw / ratio)
        top = (ih - new_h) // 2
        img = img.crop((0, top, iw, top + new_h))
    return img.resize(target, Image.LANCZOS)

def process(rel_path, target_size, photo_id):
    target = os.path.join(STATIC, rel_path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    is_png = rel_path.endswith('.png')
    max_dim = max(target_size) * 2

    try:
        data = download(photo_id, max_dim, max_dim)
        img = Image.open(BytesIO(data))
        img = img.convert('RGBA' if is_png else 'RGB')
        img = smart_crop(img, target_size)

        if is_png:
            img.save(target, 'PNG', optimize=True)
        else:
            img.save(target, 'JPEG', quality=85, optimize=True)

        sz = os.path.getsize(target)
        print(f'  OK: {rel_path} ({target_size[0]}x{target_size[1]}) {sz//1024}KB  [ID:{photo_id}]')
        return True
    except Exception as e:
        print(f'  FAIL: {rel_path} - {e}')
        return False

print('Fixing failed images and upgrading quality...\n')
ok = fail = 0
for rel_path, size, pid in FIXES:
    if process(rel_path, size, pid):
        ok += 1
    else:
        fail += 1

print(f'\nDone! Success: {ok}, Failed: {fail}')
