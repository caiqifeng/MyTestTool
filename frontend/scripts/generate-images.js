const fs = require('fs');
const path = require('path');
const axios = require('axios');

// OpenAI API configuration
//const API_KEY = process.env.OPENAI_API_KEY || 'sk-28c643380ebc43fdb85cd08d7f53ae25'; // Use provided key
//const API_URL = 'https://api.openai.com/v1/images/generations';

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

// Image generation requests
const imageRequests = [
  // Banners (750x300)
  {
    prompt: 'cozy bakery interior with bread on shelves, warm lighting, professional photography',
    size: '1792x1024', // DALL-E 3 supports 1792x1024, we'll crop/resize later
    fileName: 'banner-bakery-interior.png',
    directory: BANNERS_DIR,
    description: 'Bakery interior banner'
  },
  {
    prompt: 'delicious chocolate cake with berries on top, dessert, pastry, professional photography',
    size: '1792x1024',
    fileName: 'banner-cake-dessert.png',
    directory: BANNERS_DIR,
    description: 'Cake dessert banner'
  },
  {
    prompt: 'fresh coffee cup with latte art and croissant on side, breakfast, professional photography',
    size: '1792x1024',
    fileName: 'banner-coffee-breakfast.png',
    directory: BANNERS_DIR,
    description: 'Coffee breakfast banner'
  },
  // Product large (200x200)
  {
    prompt: 'flaky croissant on wooden board, french pastry, bakery, professional photography',
    size: '1024x1024',
    fileName: 'product-croissant.png',
    directory: PRODUCTS_LARGE_DIR,
    description: 'Croissant product image'
  },
  {
    prompt: 'slice of chocolate cake with frosting, dessert, sweet, professional photography',
    size: '1024x1024',
    fileName: 'product-chocolate-cake.png',
    directory: PRODUCTS_LARGE_DIR,
    description: 'Chocolate cake product image'
  },
  {
    prompt: 'strawberry mousse dessert with fresh strawberries, berry, professional photography',
    size: '1024x1024',
    fileName: 'product-strawberry-mousse.png',
    directory: PRODUCTS_LARGE_DIR,
    description: 'Strawberry mousse product image'
  },
  // Product small (100x100)
  {
    prompt: 'whole wheat bread loaf, healthy, bakery, professional photography',
    size: '1024x1024',
    fileName: 'product-bread.png',
    directory: PRODUCTS_SMALL_DIR,
    description: 'Bread product image'
  },
  {
    prompt: 'cheesecake slice with berry topping, cheese, dessert, professional photography',
    size: '1024x1024',
    fileName: 'product-cheesecake.png',
    directory: PRODUCTS_SMALL_DIR,
    description: 'Cheesecake product image'
  },
  {
    prompt: 'latte coffee in a cup with foam, drink, cafe, professional photography',
    size: '1024x1024',
    fileName: 'product-latte.png',
    directory: PRODUCTS_SMALL_DIR,
    description: 'Latte product image'
  },
  // Avatar (100x100)
  {
    prompt: 'friendly generic user avatar, neutral gender, simple background, professional',
    size: '1024x1024',
    fileName: 'default-avatar.png',
    directory: AVATARS_DIR,
    description: 'Default user avatar'
  },
  // Product detail (750x500)
  {
    prompt: 'bakery display with various breads and pastries, professional photography',
    size: '1792x1024',
    fileName: 'detail-bakery-display.png',
    directory: PRODUCT_DETAIL_DIR,
    description: 'Bakery display detail image'
  },
  // Product detail carousel (750x750)
  {
    prompt: 'croissant close-up on marble table, french pastry, bakery, professional photography',
    size: '1024x1024',
    fileName: 'carousel-croissant.png',
    directory: PRODUCT_DETAIL_DIR,
    description: 'Croissant carousel image'
  },
  {
    prompt: 'artisan bread loaf on wooden cutting board, bakery, food, professional photography',
    size: '1024x1024',
    fileName: 'carousel-bread.png',
    directory: PRODUCT_DETAIL_DIR,
    description: 'Bread carousel image'
  },
  {
    prompt: 'assorted pastries and desserts on display, sweet, professional photography',
    size: '1024x1024',
    fileName: 'carousel-pastries.png',
    directory: PRODUCT_DETAIL_DIR,
    description: 'Pastries carousel image'
  }
];

// Function to generate image via OpenAI API
async function generateImage(request) {
  console.log(`Generating: ${request.description}...`);

  try {
    const response = await axios.post(
      API_URL,
      {
        model: 'dall-e-3',
        prompt: request.prompt,
        n: 1,
        size: request.size,
        quality: 'standard',
        style: 'natural'
      },
      {
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const imageUrl = response.data.data[0].url;
    console.log(`  Image generated: ${imageUrl}`);

    // Download image
    const imageResponse = await axios.get(imageUrl, { responseType: 'arraybuffer' });
    const filePath = path.join(request.directory, request.fileName);
    fs.writeFileSync(filePath, imageResponse.data);
    console.log(`  Saved to: ${filePath}`);

    return { success: true, filePath };
  } catch (error) {
    console.error(`  Error generating image: ${error.message}`);
    if (error.response) {
      console.error(`  Status: ${error.response.status}, Data: ${JSON.stringify(error.response.data)}`);
    }
    return { success: false, error: error.message };
  }
}

// Main function
async function main() {
  console.log('Starting image generation...\n');

  const results = [];
  for (const request of imageRequests) {
    const result = await generateImage(request);
    results.push({ request, result });

    // Wait a bit to avoid rate limiting
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  console.log('\n--- Generation Summary ---');
  const successful = results.filter(r => r.result.success).length;
  const failed = results.filter(r => !r.result.success).length;

  console.log(`Successful: ${successful}`);
  console.log(`Failed: ${failed}`);

  if (failed > 0) {
    console.log('\nFailed requests:');
    results.filter(r => !r.result.success).forEach(({ request, result }) => {
      console.log(`  ${request.description}: ${result.error}`);
    });
  }

  console.log('\nDone.');
}

// Run main
main().catch(console.error);