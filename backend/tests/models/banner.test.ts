import Banner from '../../src/models/Banner';

describe('Banner Model', () => {
  test('should be importable', () => {
    expect(Banner).toBeDefined();
    expect(typeof Banner).toBe('function');
  });

  test('should have static methods', () => {
    expect(Banner.getActiveBanners).toBeDefined();
    expect(typeof Banner.getActiveBanners).toBe('function');
  });

  test('should create banner instance', () => {
    const banner = new Banner({
      title: 'Test Banner',
      description: 'Test banner description',
      image: 'banner.jpg',
      linkType: 'product',
      linkTarget: 'product123',
      sortOrder: 0,
      isActive: true
    });

    expect(banner).toBeDefined();
    expect(banner.title).toBe('Test Banner');
    expect(banner.image).toBe('banner.jpg');
    expect(banner.linkType).toBe('product');
    expect(banner.linkTarget).toBe('product123');
    expect(banner.isActive).toBe(true);
  });
});