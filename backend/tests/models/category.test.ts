import Category from '../../src/models/Category';

describe('Category Model', () => {
  test('should be importable', () => {
    expect(Category).toBeDefined();
    expect(typeof Category).toBe('function');
  });

  test('should have static methods', () => {
    expect(Category.getCategoryTree).toBeDefined();
    expect(typeof Category.getCategoryTree).toBe('function');
  });

  test('should create category instance', () => {
    const category = new Category({
      name: 'Test Category',
      description: 'Test Description',
      icon: 'test-icon',
      sortOrder: 0
    });

    expect(category).toBeDefined();
    expect(category.name).toBe('Test Category');
    expect(category.description).toBe('Test Description');
    expect(category.icon).toBe('test-icon');
    expect(category.sortOrder).toBe(0);
  });
});