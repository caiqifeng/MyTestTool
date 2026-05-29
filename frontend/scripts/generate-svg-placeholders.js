const fs = require('fs');
const path = require('path');

// Directory paths
const STATIC_DIR = path.join(__dirname, '..', 'static');
const BANNERS_DIR = path.join(STATIC_DIR, 'banners');
const PRODUCTS_LARGE_DIR = path.join(STATIC_DIR, 'products', 'large');
const PRODUCTS_SMALL_DIR = path.join(STATIC_DIR, 'products', 'small');
const AVATARS_DIR = path.join(STATIC_DIR, 'avatars');
const PRODUCT_DETAIL_DIR = path.join(STATIC_DIR, 'product-detail');

// Ensure directories exist
[ BANNERS_DIR, PRODUCTS_LARGE_DIR, PRODUCTS_SMALL_DIR, AVATARS_DIR, PRODUCT_DETAIL_DIR ].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

// Color palette for different categories
const colors = {
  banner: { bg: '#FFE4CC', text: '#8B4513' }, // warm beige
  productLarge: { bg: '#E6F7FF', text: '#0066CC' }, // light blue
  productSmall: { bg: '#F0FFF0', text: '#228B22' }, // light green
  avatar: { bg: '#F0E6FF', text: '#6A0DAD' }, // light purple
  detail: { bg: '#FFF0F5', text: '#C71585' }, // light pink
  carousel: { bg: '#FFFACD', text: '#DAA520' } // light yellow
};

// SVG generator function
function createSVG(width, height, bgColor, textColor, text) {
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="${width}" height="${height}" fill="${bgColor}" />
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="${textColor}" font-family="Arial, sans-serif" font-size="${Math.min(width, height) * 0.1}">${text}</text>
</svg>`;
}

// Image definitions
const images = [
  // Banners (750x300)
  {
    width: 750,
    height: 300,
    bgColor: colors.banner.bg,
    textColor: colors.banner.text,
    text: 'Bakery Interior',
    fileName: 'banner-bakery-interior.svg',
    directory: BANNERS_DIR,
    description: 'Bakery interior banner'
  },
  {
    width: 750,
    height: 300,
    bgColor: colors.banner.bg,
    textColor: colors.banner.text,
    text: 'Cake Dessert',
    fileName: 'banner-cake-dessert.svg',
    directory: BANNERS_DIR,
    description: 'Cake dessert banner'
  },
  {
    width: 750,
    height: 300,
    bgColor: colors.banner.bg,
    textColor: colors.banner.text,
    text: 'Coffee Breakfast',
    fileName: 'banner-coffee-breakfast.svg',
    directory: BANNERS_DIR,
    description: 'Coffee breakfast banner'
  },
  // Product large (200x200)
  {
    width: 200,
    height: 200,
    bgColor: colors.productLarge.bg,
    textColor: colors.productLarge.text,
    text: 'Croissant',
    fileName: 'product-croissant.svg',
    directory: PRODUCTS_LARGE_DIR,
    description: 'Croissant product image'
  },
  {
    width: 200,
    height: 200,
    bgColor: colors.productLarge.bg,
    textColor: colors.productLarge.text,
    text: 'Chocolate Cake',
    fileName: 'product-chocolate-cake.svg',
    directory: PRODUCTS_LARGE_DIR,
    description: 'Chocolate cake product image'
  },
  {
    width: 200,
    height: 200,
    bgColor: colors.productLarge.bg,
    textColor: colors.productLarge.text,
    text: 'Strawberry Mousse',
    fileName: 'product-strawberry-mousse.svg',
    directory: PRODUCTS_LARGE_DIR,
    description: 'Strawberry mousse product image'
  },
  // Product small (100x100)
  {
    width: 100,
    height: 100,
    bgColor: colors.productSmall.bg,
    textColor: colors.productSmall.text,
    text: 'Bread',
    fileName: 'product-bread.svg',
    directory: PRODUCTS_SMALL_DIR,
    description: 'Bread product image'
  },
  {
    width: 100,
    height: 100,
    bgColor: colors.productSmall.bg,
    textColor: colors.productSmall.text,
    text: 'Cheesecake',
    fileName: 'product-cheesecake.svg',
    directory: PRODUCTS_SMALL_DIR,
    description: 'Cheesecake product image'
  },
  {
    width: 100,
    height: 100,
    bgColor: colors.productSmall.bg,
    textColor: colors.productSmall.text,
    text: 'Latte',
    fileName: 'product-latte.svg',
    directory: PRODUCTS_SMALL_DIR,
    description: 'Latte product image'
  },
  // Avatar (100x100) - circular
  {
    width: 100,
    height: 100,
    bgColor: colors.avatar.bg,
    textColor: colors.avatar.text,
    text: 'Avatar',
    fileName: 'default-avatar.svg',
    directory: AVATARS_DIR,
    description: 'Default user avatar',
    circular: true
  },
  // Product detail (750x500)
  {
    width: 750,
    height: 500,
    bgColor: colors.detail.bg,
    textColor: colors.detail.text,
    text: 'Bakery Display',
    fileName: 'detail-bakery-display.svg',
    directory: PRODUCT_DETAIL_DIR,
    description: 'Bakery display detail image'
  },
  // Product detail carousel (750x750)
  {
    width: 750,
    height: 750,
    bgColor: colors.carousel.bg,
    textColor: colors.carousel.text,
    text: 'Croissant Close-up',
    fileName: 'carousel-croissant.svg',
    directory: PRODUCT_DETAIL_DIR,
    description: 'Croissant carousel image'
  },
  {
    width: 750,
    height: 750,
    bgColor: colors.carousel.bg,
    textColor: colors.carousel.text,
    text: 'Artisan Bread',
    fileName: 'carousel-bread.svg',
    directory: PRODUCT_DETAIL_DIR,
    description: 'Bread carousel image'
  },
  {
    width: 750,
    height: 750,
    bgColor: colors.carousel.bg,
    textColor: colors.carousel.text,
    text: 'Pastries Dessert',
    fileName: 'carousel-pastries.svg',
    directory: PRODUCT_DETAIL_DIR,
    description: 'Pastries carousel image'
  },
  // Cart images (200x200) - same as product large but different names
  {
    width: 200,
    height: 200,
    bgColor: colors.productLarge.bg,
    textColor: colors.productLarge.text,
    text: 'Croissant',
    fileName: 'cart-croissant.svg',
    directory: PRODUCTS_LARGE_DIR,
    description: 'Croissant cart image'
  },
  {
    width: 200,
    height: 200,
    bgColor: colors.productLarge.bg,
    textColor: colors.productLarge.text,
    text: 'Chocolate Cake',
    fileName: 'cart-chocolate-cake.svg',
    directory: PRODUCTS_LARGE_DIR,
    description: 'Chocolate cake cart image'
  }
];

// Generate SVG images
console.log('Generating SVG placeholder images...\n');
images.forEach(image => {
  let svgContent;
  if (image.circular) {
    // Create circular SVG
    svgContent = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="${image.width}" height="${image.height}" viewBox="0 0 ${image.width} ${image.height}" xmlns="http://www.w3.org/2000/svg">
  <circle cx="${image.width / 2}" cy="${image.height / 2}" r="${Math.min(image.width, image.height) / 2}" fill="${image.bgColor}" />
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="${image.textColor}" font-family="Arial, sans-serif" font-size="${Math.min(image.width, image.height) * 0.2}">${image.text}</text>
</svg>`;
  } else {
    svgContent = createSVG(image.width, image.height, image.bgColor, image.textColor, image.text);
  }

  const filePath = path.join(image.directory, image.fileName);
  fs.writeFileSync(filePath, svgContent);
  console.log(`✓ ${image.description}: ${filePath}`);
});

console.log('\nAll SVG placeholder images generated.');

// Also generate PNG versions using a simple method? We'll keep SVG for now.
// If PNG needed, we could use a library like sharp, but skip for simplicity.