import { mount } from '@vue/test-utils';
import ProductCard from './ProductCard.vue';
import { ProductStatus } from '@shared/types';

describe('ProductCard', () => {
  const mockProduct = {
    _id: '123',
    name: 'Test Bread',
    price: 15.99,
    originalPrice: 19.99,
    images: ['bread.jpg'],
    stock: 10,
    status: ProductStatus.ACTIVE,
  };

  test('renders product name', () => {
    const wrapper = mount(ProductCard, {
      props: { product: mockProduct },
    });
    expect(wrapper.text()).toContain('Test Bread');
  });

  test('renders product price', () => {
    const wrapper = mount(ProductCard, {
      props: { product: mockProduct },
    });
    expect(wrapper.text()).toContain('¥15.99');
  });

  test('shows original price when discounted', () => {
    const discountedProduct = { ...mockProduct, originalPrice: 19.99 };
    const wrapper = mount(ProductCard, {
      props: { product: discountedProduct },
    });
    expect(wrapper.text()).toContain('¥19.99');
  });

  test('shows out of stock badge when stock is zero', () => {
    const outOfStockProduct = { ...mockProduct, stock: 0, status: ProductStatus.OUT_OF_STOCK };
    const wrapper = mount(ProductCard, {
      props: { product: outOfStockProduct },
    });
    expect(wrapper.find('.out-of-stock-badge').exists()).toBe(true);
  });
});