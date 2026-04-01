import { Request, Response } from 'express';
import { ProductModel } from '../models/Product';
import { CategoryModel } from '../models/Category';
import { ProductStatus } from '../../../shared/src/types';
import { asyncHandler } from '../middleware/error';

export class ProductController {
  /**
   * 获取商品列表
   */
  static getProducts = asyncHandler(async (req: Request, res: Response) => {
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
        products: products.map(product => ({
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

  /**
   * 获取商品详情
   */
  static getProductById = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;

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
  });

  /**
   * 创建商品（管理员）
   */
  static createProduct = asyncHandler(async (req: Request, res: Response) => {
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
        $set: { stock },
        // 根据库存更新状态
        $set: {
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
        products: products.map(product => ({
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
        products: products.map(product => ({
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