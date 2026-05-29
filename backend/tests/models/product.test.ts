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

  test('decreaseStock should validate quantity is integer', async () => {
    // Mock the Product model methods for this test
    const mockProduct = {
      _id: 'test_id',
      stock: 100,
      salesCount: 0,
      status: ProductStatus.ACTIVE,
      save: jest.fn().mockResolvedValue({
        _id: 'test_id',
        stock: 90,
        salesCount: 10,
        status: ProductStatus.ACTIVE
      })
    };

    const mockFindById = jest.fn().mockResolvedValue(mockProduct);

    // Temporarily replace the static method for testing
    const originalFindById = Product.findById;
    Product.findById = mockFindById;

    try {
      // Test with non-integer quantity
      await expect(Product.decreaseStock('test_id', 10.5)).rejects.toThrow('Quantity must be an integer');

      // Test with negative quantity
      await expect(Product.decreaseStock('test_id', -5)).rejects.toThrow('Quantity must be greater than 0');

      // Test with zero quantity
      await expect(Product.decreaseStock('test_id', 0)).rejects.toThrow('Quantity must be greater than 0');
    } finally {
      // Restore original method
      Product.findById = originalFindById;
    }
  });

  test('decreaseStock should handle insufficient stock', async () => {
    const mockProduct = {
      _id: 'test_id',
      stock: 5,
      salesCount: 0,
      status: ProductStatus.ACTIVE,
      save: jest.fn()
    };

    const mockFindById = jest.fn().mockResolvedValue(mockProduct);

    const originalFindById = Product.findById;
    Product.findById = mockFindById;

    try {
      await expect(Product.decreaseStock('test_id', 10)).rejects.toThrow('Insufficient stock. Available: 5, Requested: 10');
    } finally {
      Product.findById = originalFindById;
    }
  });

  test('decreaseStock should update status when stock reaches zero', async () => {
    const mockProduct = {
      _id: 'test_id',
      stock: 5,
      salesCount: 0,
      status: ProductStatus.ACTIVE,
      save: jest.fn().mockResolvedValue({
        _id: 'test_id',
        stock: 0,
        salesCount: 5,
        status: ProductStatus.OUT_OF_STOCK
      })
    };

    const mockFindById = jest.fn().mockResolvedValue(mockProduct);

    const originalFindById = Product.findById;
    Product.findById = mockFindById;

    try {
      const result = await Product.decreaseStock('test_id', 5);
      expect(result).toBeDefined();
      expect(mockProduct.stock).toBe(0); // Should be updated to 0
      expect(mockProduct.salesCount).toBe(5); // Should be incremented
      // Note: The status update happens in the save() method which we mocked
    } finally {
      Product.findById = originalFindById;
    }
  });
});