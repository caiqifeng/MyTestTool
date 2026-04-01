import Product from '../../src/models/Product';
import { ProductStatus } from '@shared/types';

describe('Product Model', () => {
  test('should be importable', () => {
    expect(Product).toBeDefined();
    expect(typeof Product).toBe('function');
  });

  test('should have static methods', () => {
    expect(Product.decreaseStock).toBeDefined();
    expect(Product.search).toBeDefined();
    expect(typeof Product.decreaseStock).toBe('function');
    expect(typeof Product.search).toBe('function');
  });

  test('should create product instance', () => {
    const product = new Product({
      name: 'Test Product',
      price: 10.99,
      categoryId: 'test_category',
      images: ['image1.jpg'],
      stock: 100,
      salesCount: 0,
      status: ProductStatus.ACTIVE,
      sortOrder: 0
    });

    expect(product).toBeDefined();
    expect(product.name).toBe('Test Product');
    expect(product.price).toBe(10.99);
    expect(product.categoryId).toBe('test_category');
    expect(product.images).toEqual(['image1.jpg']);
    expect(product.stock).toBe(100);
    expect(product.status).toBe(ProductStatus.ACTIVE);
  });
});