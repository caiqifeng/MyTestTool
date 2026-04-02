import Cart from '../../src/models/Cart';

describe('Cart Model', () => {
  test('should be importable', () => {
    expect(Cart).toBeDefined();
    expect(typeof Cart).toBe('function');
  });

  test('should create cart instance', () => {
    const cart = new Cart({
      userId: 'test_user_id',
      items: [
        {
          productId: 'product_1',
          name: 'Test Product',
          price: 25.99,
          quantity: 2,
          image: 'test.jpg',
          specs: [
            { name: 'Size', value: 'Medium' },
            { name: 'Color', value: 'Red' }
          ],
          addedAt: new Date()
        }
      ]
    });

    expect(cart).toBeDefined();
    expect(cart.userId).toBe('test_user_id');
    expect(cart.items).toHaveLength(1);
    expect(cart.items[0].productId).toBe('product_1');
    expect(cart.items[0].name).toBe('Test Product');
    expect(cart.items[0].price).toBe(25.99);
    expect(cart.items[0].quantity).toBe(2);
    expect(cart.items[0].image).toBe('test.jpg');
    expect(cart.items[0].specs).toHaveLength(2);
    expect(cart.items[0].specs![0].name).toBe('Size');
    expect(cart.items[0].specs![0].value).toBe('Medium');
  });

  test('should have static methods', () => {
    expect(Cart.getUserCart).toBeDefined();
    expect(typeof Cart.getUserCart).toBe('function');

    expect(Cart.addItem).toBeDefined();
    expect(typeof Cart.addItem).toBe('function');

    expect(Cart.updateItemQuantity).toBeDefined();
    expect(typeof Cart.updateItemQuantity).toBe('function');

    expect(Cart.removeItem).toBeDefined();
    expect(typeof Cart.removeItem).toBe('function');

    expect(Cart.clearCart).toBeDefined();
    expect(typeof Cart.clearCart).toBe('function');
  });

  describe('static method getUserCart', () => {
    beforeEach(() => {
      jest.clearAllMocks();
    });

    test('should call findOne with userId', async () => {
      const mockCart = {
        userId: 'test_user',
        items: []
      };
      const findOneSpy = jest.spyOn(Cart, 'findOne').mockResolvedValue(mockCart as any);

      const result = await Cart.getUserCart('test_user');

      expect(findOneSpy).toHaveBeenCalledWith({ userId: 'test_user' });
      expect(result).toEqual(mockCart);
    });
  });

  describe('static method addItem', () => {
    beforeEach(() => {
      jest.clearAllMocks();
    });

    test('should create new cart when user has no cart', async () => {
      const mockSave = jest.fn().mockResolvedValue({
        userId: 'test_user',
        items: [{
          productId: 'product_1',
          name: 'Test Product',
          price: 25.99,
          quantity: 1,
          addedAt: new Date()
        }]
      });
      jest.spyOn(Cart, 'findOne').mockResolvedValue(null);
      jest.spyOn(Cart.prototype, 'save').mockImplementation(mockSave);

      const result = await Cart.addItem('test_user', {
        productId: 'product_1',
        name: 'Test Product',
        price: 25.99,
        quantity: 1
      });

      expect(mockSave).toHaveBeenCalled();
      expect(result.userId).toBe('test_user');
      expect(result.items).toHaveLength(1);
    });

    test('should update existing item quantity when item already in cart', async () => {
      const existingCart = {
        userId: 'test_user',
        items: [{
          productId: 'product_1',
          name: 'Test Product',
          price: 25.99,
          quantity: 1,
          addedAt: new Date()
        }],
        markModified: jest.fn(),
        save: jest.fn().mockResolvedValue({
          userId: 'test_user',
          items: [{
            productId: 'product_1',
            name: 'Test Product',
            price: 25.99,
            quantity: 3, // original 1 + new 2
            addedAt: new Date()
          }]
        })
      };
      jest.spyOn(Cart, 'findOne').mockResolvedValue(existingCart as any);

      const result = await Cart.addItem('test_user', {
        productId: 'product_1',
        name: 'Test Product',
        price: 25.99,
        quantity: 2
      });

      expect(existingCart.markModified).toHaveBeenCalledWith('items');
      expect(existingCart.save).toHaveBeenCalled();
      expect(result.items[0].quantity).toBe(3);
    });

    test('should add new item when item not in cart', async () => {
      const existingCart = {
        userId: 'test_user',
        items: [{
          productId: 'product_1',
          name: 'Existing Product',
          price: 15.99,
          quantity: 1,
          addedAt: new Date()
        }],
        markModified: jest.fn(),
        save: jest.fn().mockResolvedValue({
          userId: 'test_user',
          items: [
            {
              productId: 'product_1',
              name: 'Existing Product',
              price: 15.99,
              quantity: 1,
              addedAt: new Date()
            },
            {
              productId: 'product_2',
              name: 'New Product',
              price: 25.99,
              quantity: 2,
              addedAt: new Date()
            }
          ]
        })
      };
      jest.spyOn(Cart, 'findOne').mockResolvedValue(existingCart as any);

      const result = await Cart.addItem('test_user', {
        productId: 'product_2',
        name: 'New Product',
        price: 25.99,
        quantity: 2
      });

      expect(existingCart.markModified).toHaveBeenCalledWith('items');
      expect(existingCart.save).toHaveBeenCalled();
      expect(result.items).toHaveLength(2);
    });
  });

  describe('static method updateItemQuantity', () => {
    beforeEach(() => {
      jest.clearAllMocks();
    });

    test('should remove item when quantity is less than 1', async () => {
      const removeItemSpy = jest.spyOn(Cart, 'removeItem').mockResolvedValue({
        userId: 'test_user',
        items: []
      } as any);

      await Cart.updateItemQuantity('test_user', 'product_1', 0);

      expect(removeItemSpy).toHaveBeenCalledWith('test_user', 'product_1');
    });

    test('should update quantity when item exists', async () => {
      const existingCart = {
        userId: 'test_user',
        items: [{
          productId: 'product_1',
          name: 'Test Product',
          price: 25.99,
          quantity: 1,
          addedAt: new Date()
        }],
        markModified: jest.fn(),
        save: jest.fn().mockResolvedValue({
          userId: 'test_user',
          items: [{
            productId: 'product_1',
            name: 'Test Product',
            price: 25.99,
            quantity: 3,
            addedAt: new Date()
          }]
        })
      };
      jest.spyOn(Cart, 'findOne').mockResolvedValue(existingCart as any);

      const result = await Cart.updateItemQuantity('test_user', 'product_1', 3);

      expect(existingCart.markModified).toHaveBeenCalledWith('items');
      expect(existingCart.save).toHaveBeenCalled();
      expect(result!.items[0].quantity).toBe(3);
    });

    test('should return existing cart when item not found', async () => {
      const existingCart = {
        userId: 'test_user',
        items: [{
          productId: 'product_1',
          name: 'Test Product',
          price: 25.99,
          quantity: 1,
          addedAt: new Date()
        }],
        save: jest.fn()
      };
      jest.spyOn(Cart, 'findOne').mockResolvedValue(existingCart as any);

      const result = await Cart.updateItemQuantity('test_user', 'product_2', 3);

      expect(existingCart.save).not.toHaveBeenCalled();
      expect(result).toEqual(existingCart);
    });
  });

  describe('static method removeItem', () => {
    beforeEach(() => {
      jest.clearAllMocks();
    });

    test.skip('should remove item from cart', async () => {
      const existingCart = {
        userId: 'test_user',
        items: [
          {
            productId: 'product_1',
            name: 'Product 1',
            price: 25.99,
            quantity: 1,
            addedAt: new Date()
          },
          {
            productId: 'product_2',
            name: 'Product 2',
            price: 15.99,
            quantity: 2,
            addedAt: new Date()
          }
        ],
        markModified: jest.fn(),
        save: jest.fn().mockResolvedValue({
          userId: 'test_user',
          items: [{
            productId: 'product_2',
            name: 'Product 2',
            price: 15.99,
            quantity: 2,
            addedAt: new Date()
          }]
        })
      };
      jest.spyOn(Cart, 'findOne').mockResolvedValue(existingCart as any);

      const result = await Cart.removeItem('test_user', 'product_1');

      // expect(existingCart.markModified).toHaveBeenCalledWith('items');
      expect(existingCart.save).toHaveBeenCalled();
      expect(result!.items).toHaveLength(1);
      expect(result!.items[0].productId).toBe('product_2');
    });

    test.skip('should return null when cart not found', async () => {
      jest.spyOn(Cart, 'findOne').mockResolvedValue(null);

      const result = await Cart.removeItem('test_user', 'product_1');

      expect(result).toBeNull();
    });
  });

  describe('static method clearCart', () => {
    beforeEach(() => {
      jest.clearAllMocks();
    });

    test('should clear all items from cart', async () => {
      const existingCart = {
        userId: 'test_user',
        items: [
          {
            productId: 'product_1',
            name: 'Product 1',
            price: 25.99,
            quantity: 1,
            addedAt: new Date()
          }
        ],
        markModified: jest.fn(),
        save: jest.fn().mockResolvedValue({
          userId: 'test_user',
          items: []
        })
      };
      jest.spyOn(Cart, 'findOne').mockResolvedValue(existingCart as any);

      const result = await Cart.clearCart('test_user');

      expect(existingCart.markModified).toHaveBeenCalledWith('items');
      expect(existingCart.save).toHaveBeenCalled();
      expect(result!.items).toHaveLength(0);
    });

    test.skip('should return null when cart not found', async () => {
      jest.spyOn(Cart, 'findOne').mockResolvedValue(null);

      const result = await Cart.clearCart('test_user');

      expect(result).toBeNull();
    });
  });
});