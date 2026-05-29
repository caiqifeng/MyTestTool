import request from 'supertest';
import App from '../../src/app';

describe('Basic API Integration Tests', () => {
  let appInstance: any;

  beforeAll(() => {
    appInstance = new App();
  });

  afterAll(() => {
    // 清理资源
    if (appInstance && appInstance.close) {
      appInstance.close();
    }
  });

  describe('Health Check', () => {
    it('should return server health status', async () => {
      const response = await request(appInstance.app).get('/health');
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.message).toContain('healthy');
    });
  });

  describe('Product API', () => {
    it('should return product list', async () => {
      const response = await request(appInstance.app).get('/api/products-test');
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.products).toBeInstanceOf(Array);
      if (response.body.data.products.length > 0) {
        expect(response.body.data.products[0]).toHaveProperty('_id');
        expect(response.body.data.products[0]).toHaveProperty('name');
        expect(response.body.data.products[0]).toHaveProperty('price');
      }
    });
  });

  describe('Category API', () => {
    it('should return category list', async () => {
      const response = await request(appInstance.app).get('/api/categories');
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.categories).toBeInstanceOf(Array);
      expect(response.body.data.categories.length).toBeGreaterThan(0);
    });
  });

  describe.skip('Banner API', () => {
    it('should return banner list', async () => {
      const response = await request(appInstance.app).get('/api/banners');
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.banners).toBeInstanceOf(Array);
    });
  });

  describe('Static File Serving', () => {
    it('should serve static images', async () => {
      const response = await request(appInstance.app).get('/static/product-detail/carousel-croissant.jpg');
      expect(response.status).toBe(200);
      expect(response.headers['content-type']).toContain('image/');
    });
  });
});