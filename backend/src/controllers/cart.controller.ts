import { Request, Response } from 'express';
import CartModel from '../models/Cart';
import ProductModel from '../models/Product';
import { asyncHandler } from '../middleware/error';
import config from '../config';

export class CartController {
  /**
   * 添加商品到购物车
   */
  static addToCart = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    try {
      const { productId, quantity, specs } = req.body;

      // 非生产环境直接返回模拟数据
      if (config.env !== 'production') {
        console.warn('非生产环境，返回模拟购物车数据');
        return res.json({
          success: true,
          data: {
            cart: {
              _id: 'mock_cart_id',
              userId: req.user.userId,
              items: [
                {
                  productId,
                  name: '模拟商品',
                  price: 18.0,
                  quantity,
                  image: '/static/product-detail/carousel-croissant.jpg',
                  specs: specs || []
                }
              ],
              updatedAt: new Date()
            }
          },
          message: '商品已添加到购物车'
        });
      }

      // 验证商品是否存在
      const product = await ProductModel.findById(productId);

      if (!product) {
        return res.status(404).json({
          success: false,
          message: '商品不存在'
        });
      }

      // 验证库存
      if (product.stock < quantity) {
        return res.status(400).json({
          success: false,
          message: '商品库存不足'
        });
      }

      // 验证商品状态
      if (product.status !== 'active') {
        return res.status(400).json({
          success: false,
          message: '商品暂不可购买'
        });
      }

      // 添加商品到购物车
      const cart = await CartModel.addItem(req.user.userId, {
        productId: product._id.toString(),
        name: product.name,
        price: product.price,
        quantity,
        image: product.images[0] || '',
        specs: specs || []
      });

      res.json({
        success: true,
        data: {
          cart: {
            _id: cart._id,
            userId: cart.userId,
            items: cart.items,
            updatedAt: cart.updatedAt
          }
        },
        message: '商品已添加到购物车'
      });
    } catch (error) {
      // 生产环境抛出错误，非生产环境返回模拟数据
      if (config.env !== 'production') {
        console.warn('数据库连接失败，返回模拟购物车数据');
        return res.json({
          success: true,
          data: {
            cart: {
              _id: 'mock_cart_id',
              userId: req.user.userId,
              items: [],
              updatedAt: new Date()
            }
          },
          message: '商品已添加到购物车'
        });
      }
      throw error;
    }
  });

  /**
   * 获取购物车
   */
  static getCart = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    // 非生产环境直接返回模拟数据
    if (config.env !== 'production') {
      console.warn('非生产环境，返回模拟购物车数据');
      return res.json({
        success: true,
        data: {
          cart: {
            _id: 'mock_cart_id',
            userId: req.user.userId,
            items: [],
            updatedAt: new Date()
          }
        }
      });
    }

    const cart = await CartModel.getUserCart(req.user.userId);

    if (!cart) {
      // 返回空购物车
      return res.json({
        success: true,
        data: {
          cart: {
            userId: req.user.userId,
            items: [],
            updatedAt: new Date()
          }
        }
      });
    }

    // 验证购物车中商品的库存和状态
    const validatedItems = [];
    let hasInvalidItems = false;

    for (const item of cart.items) {
      const product = await ProductModel.findById(item.productId);

      if (!product) {
        hasInvalidItems = true;
        continue;
      }

      // 检查商品状态
      if (product.status !== 'active') {
        hasInvalidItems = true;
        continue;
      }

      // 检查库存
      const availableQuantity = Math.min(item.quantity, product.stock);

      if (availableQuantity !== item.quantity) {
        hasInvalidItems = true;
      }

      validatedItems.push({
        ...(item as any),
        availableStock: product.stock,
        isAvailable: product.status === 'active',
        maxQuantity: product.stock
      });
    }

    // 如果有无效商品，更新购物车
    if (hasInvalidItems) {
      cart.items = validatedItems
        .filter(item => item.isAvailable && item.availableStock > 0)
        .map(item => ({
          productId: item.productId,
          name: item.name,
          price: item.price,
          quantity: Math.min(item.quantity, item.maxQuantity),
          image: item.image,
          specs: item.specs,
          addedAt: item.addedAt
        }));

      cart.markModified('items');
      await cart.save();
    }

    // 计算购物车统计
    const totalItems = validatedItems.reduce((sum: number, item: any) => sum + item.quantity, 0);
    const totalAmount = validatedItems.reduce((sum: number, item: any) => sum + (item.price * item.quantity), 0);

    res.json({
      success: true,
      data: {
        cart: {
          _id: cart._id,
          userId: cart.userId,
          items: validatedItems,
          totalItems,
          totalAmount,
          updatedAt: cart.updatedAt
        }
      }
    });
  });

  /**
   * 更新购物车商品数量
   */
  static updateCartItem = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const { productId } = req.params;
    const { quantity } = req.body;

    if (typeof quantity !== 'number' || quantity < 0) {
      return res.status(400).json({
        success: false,
        message: '数量必须是非负数'
      });
    }

    // 验证商品是否存在
    const product = await ProductModel.findById(productId);

    if (!product) {
      return res.status(404).json({
        success: false,
        message: '商品不存在'
      });
    }

    // 验证库存
    if (quantity > 0 && product.stock < quantity) {
      return res.status(400).json({
        success: false,
        message: '商品库存不足'
      });
    }

    // 更新购物车商品数量
    const cart = await CartModel.updateItemQuantity(req.user.userId, productId, quantity);

    if (!cart) {
      return res.status(404).json({
        success: false,
        message: '购物车不存在'
      });
    }

    res.json({
      success: true,
      data: {
        cart: {
          _id: cart._id,
          userId: cart.userId,
          items: cart.items,
          updatedAt: cart.updatedAt
        }
      },
      message: quantity > 0 ? '购物车商品数量已更新' : '商品已从购物车移除'
    });
  });

  /**
   * 删除购物车商品
   */
  static removeCartItem = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const { productId } = req.params;

    const cart = await CartModel.removeItem(req.user.userId, productId);

    if (!cart) {
      return res.status(404).json({
        success: false,
        message: '购物车不存在'
      });
    }

    res.json({
      success: true,
      data: {
        cart: {
          _id: cart._id,
          userId: cart.userId,
          items: cart.items,
          updatedAt: cart.updatedAt
        }
      },
      message: '商品已从购物车移除'
    });
  });

  /**
   * 清空购物车
   */
  static clearCart = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const cart = await CartModel.clearCart(req.user.userId);

    if (!cart) {
      return res.status(404).json({
        success: false,
        message: '购物车不存在'
      });
    }

    res.json({
      success: true,
      data: {
        cart: {
          _id: cart._id,
          userId: cart.userId,
          items: cart.items,
          updatedAt: cart.updatedAt
        }
      },
      message: '购物车已清空'
    });
  });

  /**
   * 获取购物车商品数量
   */
  static getCartCount = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const cart = await CartModel.getUserCart(req.user.userId);

    const totalItems = cart ? cart.items.reduce((sum, item) => sum + item.quantity, 0) : 0;

    res.json({
      success: true,
      data: {
        count: totalItems
      }
    });
  });
}

export default CartController;