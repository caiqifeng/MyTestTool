"""
Download bakery product images from Pexels (free commercial use).
Downloads, resizes, and compresses all images in one pass.
"""

import urllib.request
import ssl
import os
import json
from io import BytesIO

try:
    from PIL import Image
except ImportError:
    os.system(f'"{os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python", "Python313", "python.exe")}" -m pip install Pillow -q')
    from PIL import Image

STATIC = r'F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app\frontend\static'
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

# Pexels photo IDs - hand-curated bakery/food photos
# Format: (local_path, target_size, pexels_id, search_desc)
IMAGES = [
    # === Product Large (600x600) ===
    ('products/large/product-croissant.jpg', (600, 600), '6214515', 'croissant'),
    ('products/large/product-chocolate-cake.jpg', (600, 600), '1126359', 'chocolate cake'),
    ('products/large/product-strawberry-mousse.jpg', (600, 600), '6580636', 'strawberry dessert'),

    # === Cart Large (600x600) - different angle/similar item ===
    ('products/large/cart-croissant.jpg', (600, 600), '1092825', 'pastry'),
    ('products/large/cart-chocolate-cake.jpg', (600, 600), '3774498', 'cake slice'),

    # === Product Small (300x300) ===
    ('products/small/product-bread.jpg', (300, 300), '8256741', 'bread loaf'),
    ('products/small/product-cheesecake.jpg', (300, 300), '2183465', 'cheesecake'),
    ('products/small/product-latte.jpg', (300, 300), '324028', 'latte coffee'),

    # === Banners (800x400) ===
    ('banners/banner-bakery-interior.jpg', (800, 400), '3184291', 'bakery interior'),
    ('banners/banner-cake-dessert.jpg', (800, 400), '4587966', 'cake display'),
    ('banners/banner-coffee-breakfast.jpg', (800, 400), '3774598', 'coffee breakfast'),

    # === Product Detail Carousel (400x300) ===
    ('product-detail/carousel-croissant.jpg', (400, 300), '6270807', 'croissant close'),
    ('product-detail/carousel-bread.jpg', (400, 300), '2303946', 'artisan bread'),
    ('product-detail/carousel-pastries.jpg', (400, 300), '2099641', 'pastries display'),
    ('product-detail/detail-bakery-display.jpg', (400, 300), '326512', 'bakery showcase'),

    # === Avatar (400x400) ===
    ('avatars/default-avatar.png', (400, 400), '220453', 'person avatar'),
]


def download_pexels_photo(photo_id: str, width: int, height: int) -> bytes:
    """Download a Pexels photo at the specified size."""
    # Pexels CDN direct link
    url = f'https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg?auto=compress&cs=tinysrgb&w={width}&h={height}&dpr=1&fit=crop'
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
        return resp.read()


def smart_crop(img: Image.Image, target_size: tuple) -> Image.Image:
    """Smart crop to target size, center-focused."""
    tw, th = target_size
    iw, ih = img.size

    # If already exact size, return as-is
    if iw == tw and ih == th:
        return img

    # Calculate crop box (center crop)
    target_ratio = tw / th
    img_ratio = iw / ih

    if img_ratio > target_ratio:
        # Image is wider - crop sides
        new_w = int(ih * target_ratio)
        left = (iw - new_w) // 2
        img = img.crop((left, 0, left + new_w, ih))
    else:
        # Image is taller - crop top/bottom
        new_h = int(iw / target_ratio)
        top = (ih - new_h) // 2
        img = img.crop((0, top, iw, top + new_h))

    return img.resize(target_size, Image.LANCZOS)


def process_image(rel_path: str, target_size: tuple, photo_id: str, desc: str) -> bool:
    """Download, resize, compress and save an image."""
    target = os.path.join(STATIC, rel_path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    is_png = rel_path.endswith('.png')

    try:
        # Download at a larger size for quality
        max_dim = max(target_size) * 2
        data = download_pexels_photo(photo_id, max_dim, max_dim)

        # Verify image
        img = Image.open(BytesIO(data))
        img = img.convert('RGB' if not is_png else 'RGBA')

        # Smart crop/resize
        img = smart_crop(img, target_size)

        # Save with compression
        if is_png:
            img.save(target, 'PNG', optimize=True)
        else:
            img.save(target, 'JPEG', quality=85, optimize=True)

        sz = os.path.getsize(target)
        print(f'  OK: {rel_path} ({target_size[0]}x{target_size[1]}) {sz//1024}KB  [{desc}]')
        return True

    except Exception as e:
        print(f'  FAIL: {rel_path} - {e}')
        return False


def main():
    print(f'Static dir: {STATIC}')
    print(f'Downloading {len(IMAGES)} images from Pexels...\n')

    ok = 0
    fail = 0
    for rel_path, target_size, photo_id, desc in IMAGES:
        if process_image(rel_path, target_size, photo_id, desc):
            ok += 1
        else:
            fail += 1

    print(f'\nDone! Success: {ok}, Failed: {fail}, Total: {len(IMAGES)}')


if __name__ == '__main__':
    main()
