import { Request, Response } from 'express';
import CategoryModel from '../models/Category';
import { asyncHandler } from '../middleware/error';

export class CategoryController {
  /**
   * 创建分类
   */
  static createCategory = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const {
      name,
      description,
      icon,
      sortOrder = 0,
      parentId
    } = req.body;

    // 检查分类名称是否已存在
    const existingCategory = await CategoryModel.findOne({ name });
    if (existingCategory) {
      return res.status(409).json({
        success: false,
        message: '分类名称已存在'
      });
    }

    // 如果指定了父分类，检查父分类是否存在
    if (parentId) {
      const parentCategory = await CategoryModel.findById(parentId);
      if (!parentCategory) {
        return res.status(404).json({
          success: false,
          message: '父分类不存在'
        });
      }
    }

    // 创建分类
    const category = new CategoryModel({
      name,
      description,
      icon,
      sortOrder,
      parentId: parentId || null
    });

    await category.save();

    res.status(201).json({
      success: true,
      data: {
        category: {
          _id: category._id,
          name: category.name,
          description: category.description,
          icon: category.icon,
          sortOrder: category.sortOrder,
          parentId: category.parentId,
          createdAt: category.createdAt,
          updatedAt: category.updatedAt
        }
      },
      message: '分类创建成功'
    });
  });

  /**
   * 获取分类列表
   */
  static getCategories = asyncHandler(async (req: Request, res: Response) => {
    const categories = await CategoryModel.find()
      .sort({ sortOrder: 1, name: 1 });

    res.json({
      success: true,
      data: {
        categories: categories.map(category => ({
          _id: category._id,
          name: category.name,
          description: category.description,
          icon: category.icon,
          sortOrder: category.sortOrder,
          parentId: category.parentId,
          createdAt: category.createdAt,
          updatedAt: category.updatedAt
        }))
      }
    });
  });

  /**
   * 获取分类详情
   */
  static getCategoryById = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;

    const category = await CategoryModel.findById(id);

    if (!category) {
      return res.status(404).json({
        success: false,
        message: '分类不存在'
      });
    }

    res.json({
      success: true,
      data: {
        category: {
          _id: category._id,
          name: category.name,
          description: category.description,
          icon: category.icon,
          sortOrder: category.sortOrder,
          parentId: category.parentId,
          createdAt: category.createdAt,
          updatedAt: category.updatedAt
        }
      }
    });
  });

  /**
   * 更新分类
   */
  static updateCategory = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const { id } = req.params;
    const updates = req.body;

    // 检查分类是否存在
    const existingCategory = await CategoryModel.findById(id);
    if (!existingCategory) {
      return res.status(404).json({
        success: false,
        message: '分类不存在'
      });
    }

    // 如果更新名称，检查名称是否与其他分类冲突
    if (updates.name && updates.name !== existingCategory.name) {
      const duplicateCategory = await CategoryModel.findOne({
        name: updates.name,
        _id: { $ne: id }
      });
      if (duplicateCategory) {
        return res.status(409).json({
          success: false,
          message: '分类名称已存在'
        });
      }
    }

    // 如果更新父分类，检查是否形成循环引用
    if (updates.parentId) {
      if (updates.parentId === id) {
        return res.status(400).json({
          success: false,
          message: '不能将分类设置为自己的父分类'
        });
      }

      const parentCategory = await CategoryModel.findById(updates.parentId);
      if (!parentCategory) {
        return res.status(404).json({
          success: false,
          message: '父分类不存在'
        });
      }

      // 检查循环引用（简单检查）
      let currentParentId = parentCategory.parentId;
      while (currentParentId) {
        if (currentParentId === id) {
          return res.status(400).json({
            success: false,
            message: '不能形成循环引用'
          });
        }
        const currentParent = await CategoryModel.findById(currentParentId);
        currentParentId = currentParent?.parentId;
      }
    }

    // 更新分类
    const category = await CategoryModel.findByIdAndUpdate(
      id,
      { $set: updates },
      { new: true, runValidators: true }
    );

    if (!category) {
      return res.status(404).json({
        success: false,
        message: '分类更新失败'
      });
    }

    res.json({
      success: true,
      data: {
        category: {
          _id: category._id,
          name: category.name,
          description: category.description,
          icon: category.icon,
          sortOrder: category.sortOrder,
          parentId: category.parentId,
          createdAt: category.createdAt,
          updatedAt: category.updatedAt
        }
      },
      message: '分类更新成功'
    });
  });

  /**
   * 删除分类
   */
  static deleteCategory = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const { id } = req.params;

    // 检查分类是否存在
    const category = await CategoryModel.findById(id);
    if (!category) {
      return res.status(404).json({
        success: false,
        message: '分类不存在'
      });
    }

    // 检查是否有子分类
    const childCategories = await CategoryModel.find({ parentId: id });
    if (childCategories.length > 0) {
      return res.status(400).json({
        success: false,
        message: '请先删除所有子分类'
      });
    }

    // TODO: 检查是否有商品属于该分类

    // 删除分类
    await CategoryModel.findByIdAndDelete(id);

    res.json({
      success: true,
      message: '分类删除成功'
    });
  });

  /**
   * 获取分类树
   */
  static getCategoryTree = asyncHandler(async (req: Request, res: Response) => {
    const categoryTree = await CategoryModel.getCategoryTree();

    res.json({
      success: true,
      data: {
        categories: categoryTree
      }
    });
  });
}

export default CategoryController;