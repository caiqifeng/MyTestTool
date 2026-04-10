const fs = require('fs');
const path = require('path');
const axios = require('axios');

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

// URL to file mapping
const downloads = [
  // Banners (750x300)
  {
    url: 'https://source.unsplash.com/random/750x300/?bakery,interior,bread,store',
    fileName: 'banner-bakery-interior.jpg',
    directory: BANNERS_DIR,
    description: 'Bakery interior banner'
  },
  {
    url: 'https://source.unsplash.com/random/750x300/?cake,dessert,sweet,pastry',
    fileName: 'banner-cake-dessert.jpg',
    directory: BANNERS_DIR,
    description: 'Cake dessert banner'
  },
  {
    url: 'https://source.unsplash.com/random/750x300/?coffee,drink,bakery,breakfast',
    fileName: 'banner-coffee-breakfast.jpg',
    directory: BANNERS_DIR,
    description: 'Coffee breakfast banner'
  },
  // Product large (200x200)
  {
    url: 'https://source.unsplash.com/random/200x200/?croissant,french,pastry,bakery',
    fileName: 'product-croissant.jpg',
    directory: PRODUCTS_LARGE_DIR,
    description: 'Croissant product image'
  },
  {
    url: 'https://source.unsplash.com/random/200x200/?chocolate,cake,dessert,sweet',
    fileName: 'product-chocolate-cake.jpg',
    directory: PRODUCTS_LARGE_DIR,
    description: 'Chocolate cake product image'
  },
  {
    url: 'https://source.unsplash.com/random/200x200/?strawberry,mousse,dessert,berry',
    fileName: 'product-strawberry-mousse.jpg',
    directory: PRODUCTS_LARGE_DIR,
    description: 'Strawberry mousse product image'
  },
  // Product small (100x100)
  {
    url: 'https://source.unsplash.com/random/100x100/?bread,whole,wheat,healthy',
    fileName: 'product-bread.jpg',
    directory: PRODUCTS_SMALL_DIR,
    description: 'Bread product image'
  },
  {
    url: 'https://source.unsplash.com/random/100x100/?cheesecake,cheese,dessert,cake',
    fileName: 'product-cheesecake.jpg',
    directory: PRODUCTS_SMALL_DIR,
    description: 'Cheesecake product image'
  },
  {
    url: 'https://source.unsplash.com/random/100x100/?latte,coffee,drink,cafe',
    fileName: 'product-latte.jpg',
    directory: PRODUCTS_SMALL_DIR,
    description: 'Latte product image'
  },
  // Avatar (100x100)
  {
    url: 'https://source.unsplash.com/random/100x100/?portrait,avatar,user,profile',
    fileName: 'default-avatar.jpg',
    directory: AVATARS_DIR,
    description: 'Default user avatar'
  },
  // Product detail (750x500)
  {
    url: 'https://source.unsplash.com/featured/750x500/?bakery,bread,pastry',
    fileName: 'detail-bakery-display.jpg',
    directory: PRODUCT_DETAIL_DIR,
    description: 'Bakery display detail image'
  },
  // Product detail carousel (750x750)
  {
    url: 'https://source.unsplash.com/random/750x750/?croissant,french,pastry,bakery',
    fileName: 'carousel-croissant.jpg',
    directory: PRODUCT_DETAIL_DIR,
    description: 'Croissant carousel image'
  },
  {
    url: 'https://source.unsplash.com/random/750x750/?bread,bakery,food',
    fileName: 'carousel-bread.jpg',
    directory: PRODUCT_DETAIL_DIR,
    description: 'Bread carousel image'
  },
  {
    url: 'https://source.unsplash.com/random/750x750/?pastry,dessert,sweet',
    fileName: 'carousel-pastries.jpg',
    directory: PRODUCT_DETAIL_DIR,
    description: 'Pastries carousel image'
  },
  // Cart images (200x200) - reuse product large images
  // We'll copy later
];

// Function to download image
async function downloadImage(download) {
  console.log(`Downloading: ${download.description}...`);

  try {
    const response = await axios.get(download.url, {
      responseType: 'arraybuffer',
      timeout: 30000
    });

    const filePath = path.join(download.directory, download.fileName);
    fs.writeFileSync(filePath, response.data);
    console.log(`  Saved to: ${filePath} (${response.data.length} bytes)`);

    return { success: true, filePath };
  } catch (error) {
    console.error(`  Error downloading image: ${error.message}`);
    return { success: false, error: error.message };
  }
}

// Main function
async function main() {
  console.log('Starting Unsplash image download...\n');

  const results = [];
  for (const download of downloads) {
    const result = await downloadImage(download);
    results.push({ download, result });

    // Wait a bit to avoid rate limiting
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  console.log('\n--- Download Summary ---');
  const successful = results.filter(r => r.result.success).length;
  const failed = results.filter(r => !r.result.success).length;

  console.log(`Successful: ${successful}`);
  console.log(`Failed: ${failed}`);

  if (failed > 0) {
    console.log('\nFailed downloads:');
    results.filter(r => !r.result.success).forEach(({ download, result }) => {
      console.log(`  ${download.description}: ${result.error}`);
    });
  }

  // Copy product large images to cart (if needed)
  console.log('\nCopying product images for cart...');
  try {
    const copyPairs = [
      { src: 'product-croissant.jpg', dst: 'cart-croissant.jpg' },
      { src: 'product-chocolate-cake.jpg', dst: 'cart-chocolate-cake.jpg' }
    ];
    for (const pair of copyPairs) {
      const srcPath = path.join(PRODUCTS_LARGE_DIR, pair.src);
      const dstPath = path.join(PRODUCTS_LARGE_DIR, pair.dst);
      if (fs.existsSync(srcPath)) {
        fs.copyFileSync(srcPath, dstPath);
        console.log(`  Copied ${pair.src} -> ${pair.dst}`);
      } else {
        console.log(`  Source not found: ${srcPath}`);
      }
    }
  } catch (error) {
    console.error(`  Error copying: ${error.message}`);
  }

  console.log('\nDone.');
}

// Run main
main().catch(console.error);