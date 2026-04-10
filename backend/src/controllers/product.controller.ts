import { Request, Response } from 'express';
import ProductModel from '../models/Product';
import CategoryModel from '../models/Category';
import { ProductStatus } from '../../../shared/src/types';
import { asyncHandler } from '../middleware/error';
import config from '../config';

export class ProductController {
  /**
   * 获取商品列表
   */
  static getProducts = asyncHandler(async (req: Request, res: Response) => {
    console.warn('getProducts called');
    const {
      page = 1,
      limit = 10,
      categoryId,
      status,
      keyword,
      sortBy = 'sortOrder',
      sortOrder = 'desc'
    } = req.query;

    const pageNum = parseInt(page as string);
    const limitNum = parseInt(limit as string);
    const skip = (pageNum - 1) * limitNum;

    const query: any = {};

    // 状态过滤
    if (status) {
      if (status === 'active') {
        query.status = ProductStatus.ACTIVE;
      } else if (status === 'inactive') {
        query.status = ProductStatus.INACTIVE;
      } else if (status === 'out_of_stock') {
        query.status = ProductStatus.OUT_OF_STOCK;
      } else if (status === 'coming_soon') {
        query.status = ProductStatus.COMING_SOON;
      }
    } else {
      // 默认只显示活跃商品
      query.status = ProductStatus.ACTIVE;
    }

    // 分类过滤
    if (categoryId) {
      query.categoryId = categoryId;
    }

    // 关键词搜索
    if (keyword) {
      query.$or = [
        { name: { $regex: keyword, $options: 'i' } },
        { description: { $regex: keyword, $options: 'i' } }
      ];
    }

    // 排序
    const sortOptions: any = {};
    if (sortBy === 'price') {
      sortOptions.price = sortOrder === 'asc' ? 1 : -1;
    } else if (sortBy === 'sales') {
      sortOptions.salesCount = sortOrder === 'asc' ? 1 : -1;
    } else if (sortBy === 'createdAt') {
      sortOptions.createdAt = sortOrder === 'asc' ? 1 : -1;
    } else {
      // 默认按排序顺序
      sortOptions.sortOrder = sortOrder === 'asc' ? 1 : -1;
    }

    try {
      // 非生产环境直接返回模拟数据，避免数据库连接问题
      if (config.env !== 'production') {
        console.warn('config.env:', config.env);
        console.warn('非生产环境，返回模拟商品数据');
        throw new Error('Development mode - using mock data');
      }

      const [products, total] = await Promise.all([
        ProductModel.find(query)
          .populate('categoryId', 'name icon')
          .sort(sortOptions)
          .skip(skip)
          .limit(limitNum),
        ProductModel.countDocuments(query)
      ]);

      res.json({
        success: true,
        data: {
          products: products.map((product: any) => ({
            _id: product._id,
            name: product.name,
            description: product.description,
            price: product.price,
            originalPrice: product.originalPrice,
            categoryId: product.categoryId,
            images: product.images,
            stock: product.stock,
            salesCount: product.salesCount,
            status: product.status,
            specs: product.specs,
            sortOrder: product.sortOrder,
            createdAt: product.createdAt,
            updatedAt: product.updatedAt
          })),
          pagination: {
            page: pageNum,
            limit: limitNum,
            total,
            pages: Math.ceil(total / limitNum)
          }
        }
      });
    } catch (error) {
      // 如果数据库连接失败，返回模拟数据
      console.warn('数据库连接失败，返回模拟商品数据');

      const mockProducts = [
        {
          _id: '1',
          name: '奶油可颂',
          description: '新鲜烘焙的奶油可颂，外酥内软，奶香浓郁，早餐下午茶的不二选择。',
          price: 18,
          originalPrice: 22,
          categoryId: { _id: '1', name: '面包', icon: '🥖' },
          images: ['/static/product-detail/carousel-croissant.jpg'],
          stock: 100,
          salesCount: 152,
          status: ProductStatus.ACTIVE,
          specs: [
            { name: '尺寸', value: '中份' },
            { name: '口味', value: '原味' }
          ],
          sortOrder: 1,
          createdAt: new Date('2023-01-01'),
          updatedAt: new Date('2023-01-01')
        },
        {
          _id: '2',
          name: '巧克力蛋糕',
          description: '浓郁的巧克力蛋糕，口感丝滑，巧克力味十足。',
          price: 68,
          originalPrice: 88,
          categoryId: { _id: '3', name: '蛋糕', icon: '🍰' },
          images: ['/static/product-detail/carousel-croissant.jpg'],
          stock: 50,
          salesCount: 89,
          status: ProductStatus.ACTIVE,
          specs: [
            { name: '尺寸', value: '8寸' },
            { name: '口味', value: '巧克力' }
          ],
          sortOrder: 2,
          createdAt: new Date('2023-01-02'),
          updatedAt: new Date('2023-01-02')
        }
      ];

      // 应用简单的过滤（模拟）
      let filteredProducts = [...mockProducts];

      if (status) {
        filteredProducts = filteredProducts.filter(p => p.status === status);
      }

      if (categoryId) {
        filteredProducts = filteredProducts.filter(p => p.categoryId._id === categoryId);
      }

      if (keyword) {
        const lowerKeyword = String(keyword).toLowerCase();
        filteredProducts = filteredProducts.filter(p =>
          p.name.toLowerCase().includes(lowerKeyword) ||
          p.description.toLowerCase().includes(lowerKeyword)
        );
      }

      // 应用排序（模拟）
      if (sortBy === 'price') {
        filteredProducts.sort((a, b) => sortOrder === 'asc' ? a.price - b.price : b.price - a.price);
      } else if (sortBy === 'sales') {
        filteredProducts.sort((a, b) => sortOrder === 'asc' ? a.salesCount - b.salesCount : b.salesCount - a.salesCount);
      }

      // 分页
      const startIndex = skip;
      const endIndex = Math.min(startIndex + limitNum, filteredProducts.length);
      const paginatedProducts = filteredProducts.slice(startIndex, endIndex);

      res.json({
        success: true,
        data: {
          products: paginatedProducts,
          pagination: {
            page: pageNum,
            limit: limitNum,
            total: filteredProducts.length,
            pages: Math.ceil(filteredProducts.length / limitNum)
          }
        }
      });
    }
  });

  /**
   * 获取商品详情
   */
  static getProductById = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;

    try {
      const product = await ProductModel.findById(id).populate('categoryId', 'name icon description');

      if (!product) {
        return res.status(404).json({
          success: false,
          message: '商品不存在'
        });
      }

      // 如果是非活跃状态且不是管理员，返回404
      if (product.status !== ProductStatus.ACTIVE && !req.user?.role.includes('admin')) {
        return res.status(404).json({
          success: false,
          message: '商品不存在'
        });
      }

      res.json({
        success: true,
        data: {
          product: {
            _id: product._id,
            name: product.name,
            description: product.description,
            price: product.price,
            originalPrice: product.originalPrice,
            categoryId: product.categoryId,
            images: product.images,
            stock: product.stock,
            salesCount: product.salesCount,
            status: product.status,
            specs: product.specs,
            sortOrder: product.sortOrder,
            createdAt: product.createdAt,
            updatedAt: product.updatedAt
          }
        }
      });
    } catch (error) {
      // 如果数据库连接失败，返回模拟数据
      console.warn('数据库连接失败，返回模拟商品详情数据');

      // 模拟数据
      const mockProducts = [
        {
          _id: '1',
          name: '奶油可颂',
          description: '新鲜烘焙的奶油可颂，外酥内软，奶香浓郁，早餐下午茶的不二选择。',
          price: 18,
          originalPrice: 22,
          categoryId: { _id: '1', name: '面包', icon: '🥖' },
          images: ['/static/product-detail/carousel-croissant.jpg'],
          stock: 100,
          salesCount: 152,
          status: ProductStatus.ACTIVE,
          specs: [
            { name: '尺寸', value: '中份' },
            { name: '口味', value: '原味' }
          ],
          sortOrder: 1,
          createdAt: new Date('2023-01-01'),
          updatedAt: new Date('2023-01-01')
        },
        {
          _id: '2',
          name: '巧克力蛋糕',
          description: '浓郁的巧克力蛋糕，口感丝滑，巧克力味十足。',
          price: 68,
          originalPrice: 88,
          categoryId: { _id: '3', name: '蛋糕', icon: '🍰' },
          images: ['/static/product-detail/carousel-croissant.jpg'],
          stock: 50,
          salesCount: 89,
          status: ProductStatus.ACTIVE,
          specs: [
            { name: '尺寸', value: '8寸' },
            { name: '口味', value: '巧克力' }
          ],
          sortOrder: 2,
          createdAt: new Date('2023-01-02'),
          updatedAt: new Date('2023-01-02')
        }
      ];

      // 查找匹配的产品
      const product = mockProducts.find(p => p._id === id);

      if (!product) {
        return res.status(404).json({
          success: false,
          message: '商品不存在'
        });
      }

      res.json({
        success: true,
        data: {
          product: {
            _id: product._id,
            name: product.name,
            description: product.description,
            price: product.price,
            originalPrice: product.originalPrice,
            categoryId: product.categoryId,
            images: product.images,
            stock: product.stock,
            salesCount: product.salesCount,
            status: product.status,
            specs: product.specs,
            sortOrder: product.sortOrder,
            createdAt: product.createdAt,
            updatedAt: product.updatedAt
          }
        }
      });
    }
  });

  /**
   * 创建商品（管理员）
   */
  static createProduct = asyncHandler(async (req: Request, res: Response) => {
    // 开发环境返回模拟数据
    if (config.env === 'development') {
      console.warn('开发环境，返回模拟创建商品响应');
      const mockProduct = {
        _id: Date.now().toString(),
        name: req.body.name || '测试商品',
        description: req.body.description || '测试描述',
        price: req.body.price || 0,
        originalPrice: req.body.originalPrice || req.body.price || 0,
        categoryId: req.body.categoryId || '1',
        images: req.body.images || [],
        stock: req.body.stock || 0,
        salesCount: 0,
        status: req.body.status || 'active',
        specs: req.body.specs || [],
        sortOrder: req.body.sortOrder || 0,
        createdAt: new Date(),
        updatedAt: new Date()
      };
      return res.status(201).json({
        success: true,
        data: {
          product: mockProduct
        }
      });
    }

    const {
      name,
      description,
      price,
      originalPrice,
      categoryId,
      images,
      stock,
      specs,
      sortOrder,
      status
    } = req.body;

    // 验证分类是否存在
    const category = await CategoryModel.findById(categoryId);
    if (!category) {
      return res.status(400).json({
        success: false,
        message: '分类不存在'
      });
    }

    const product = new ProductModel({
      name,
      description,
      price,
      originalPrice,
      categoryId,
      images: images || [],
      stock: stock || 0,
      salesCount: 0,
      status: status || ProductStatus.ACTIVE,
      specs: specs || [],
      sortOrder: sortOrder || 0
    });

    await product.save();

    res.status(201).json({
      success: true,
      data: {
        product: {
          _id: product._id,
          name: product.name,
          description: product.description,
          price: product.price,
          originalPrice: product.originalPrice,
          categoryId: product.categoryId,
          images: product.images,
          stock: product.stock,
          salesCount: product.salesCount,
          status: product.status,
          specs: product.specs,
          sortOrder: product.sortOrder,
          createdAt: product.createdAt,
          updatedAt: product.updatedAt
        }
      }
    });
  });

  /**
   * 更新商品（管理员）
   */
  static updateProduct = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const updates = req.body;

    // 如果更新分类，验证分类是否存在
    if (updates.categoryId) {
      const category = await CategoryModel.findById(updates.categoryId);
      if (!category) {
        return res.status(400).json({
          success: false,
          message: '分类不存在'
        });
      }
    }

    const product = await ProductModel.findByIdAndUpdate(
      id,
      { $set: updates },
      { new: true, runValidators: true }
    ).populate('categoryId', 'name icon');

    if (!product) {
      return res.status(404).json({
        success: false,
        message: '商品不存在'
      });
    }

    res.json({
      success: true,
      data: {
        product: {
          _id: product._id,
          name: product.name,
          description: product.description,
          price: product.price,
          originalPrice: product.originalPrice,
          categoryId: product.categoryId,
          images: product.images,
          stock: product.stock,
          salesCount: product.salesCount,
          status: product.status,
          specs: product.specs,
          sortOrder: product.sortOrder,
          createdAt: product.createdAt,
          updatedAt: product.updatedAt
        }
      }
    });
  });

  /**
   * 删除商品（管理员）
   */
  static deleteProduct = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;

    const product = await ProductModel.findByIdAndDelete(id);

    if (!product) {
      return res.status(404).json({
        success: false,
        message: '商品不存在'
      });
    }

    res.json({
      success: true,
      message: '商品删除成功'
    });
  });

  /**
   * 更新商品库存（管理员）
   */
  static updateStock = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const { stock } = req.body;

    if (typeof stock !== 'number' || stock < 0) {
      return res.status(400).json({
        success: false,
        message: '库存必须是非负数'
      });
    }

    const product = await ProductModel.findByIdAndUpdate(
      id,
      {
        $set: {
          stock,
          // 根据库存更新状态
          status: stock <= 0 ? ProductStatus.OUT_OF_STOCK : ProductStatus.ACTIVE
        }
      },
      { new: true, runValidators: true }
    );

    if (!product) {
      return res.status(404).json({
        success: false,
        message: '商品不存在'
      });
    }

    res.json({
      success: true,
      data: {
        product: {
          _id: product._id,
          name: product.name,
          stock: product.stock,
          status: product.status,
          updatedAt: product.updatedAt
        }
      }
    });
  });

  /**
   * 获取热门商品
   */
  static getPopularProducts = asyncHandler(async (req: Request, res: Response) => {
    const { limit = 10 } = req.query;
    const limitNum = parseInt(limit as string);

    const products = await ProductModel.find({ status: ProductStatus.ACTIVE })
      .sort({ salesCount: -1, sortOrder: -1 })
      .limit(limitNum)
      .populate('categoryId', 'name icon');

    res.json({
      success: true,
      data: {
        products: products.map((product: any) => ({
          _id: product._id,
          name: product.name,
          description: product.description,
          price: product.price,
          originalPrice: product.originalPrice,
          categoryId: product.categoryId,
          images: product.images,
          stock: product.stock,
          salesCount: product.salesCount,
          status: product.status,
          specs: product.specs,
          sortOrder: product.sortOrder,
          createdAt: product.createdAt,
          updatedAt: product.updatedAt
        }))
      }
    });
  });

  /**
   * 获取分类下的商品
   */
  static getProductsByCategory = asyncHandler(async (req: Request, res: Response) => {
    const { categoryId } = req.params;
    const { page = 1, limit = 10 } = req.query;
    const pageNum = parseInt(page as string);
    const limitNum = parseInt(limit as string);
    const skip = (pageNum - 1) * limitNum;

    // 验证分类是否存在
    const category = await CategoryModel.findById(categoryId);
    if (!category) {
      return res.status(404).json({
        success: false,
        message: '分类不存在'
      });
    }

    const [products, total] = await Promise.all([
      ProductModel.find({
        categoryId,
        status: ProductStatus.ACTIVE
      })
        .sort({ sortOrder: -1, createdAt: -1 })
        .skip(skip)
        .limit(limitNum)
        .populate('categoryId', 'name icon'),
      ProductModel.countDocuments({
        categoryId,
        status: ProductStatus.ACTIVE
      })
    ]);

    res.json({
      success: true,
      data: {
        category: {
          _id: category._id,
          name: category.name,
          description: category.description,
          icon: category.icon
        },
        products: products.map((product: any) => ({
          _id: product._id,
          name: product.name,
          description: product.description,
          price: product.price,
          originalPrice: product.originalPrice,
          categoryId: product.categoryId,
          images: product.images,
          stock: product.stock,
          salesCount: product.salesCount,
          status: product.status,
          specs: product.specs,
          sortOrder: product.sortOrder,
          createdAt: product.createdAt,
          updatedAt: product.updatedAt
        })),
        pagination: {
          page: pageNum,
          limit: limitNum,
          total,
          pages: Math.ceil(total / limitNum)
        }
      }
    });
  });
}

export default ProductController;