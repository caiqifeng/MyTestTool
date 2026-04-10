import { Request, Response } from 'express';
import BannerModel from '../models/Banner';
import { asyncHandler } from '../middleware/error';
import config from '../config';

export class BannerController {
  /**
   * 获取轮播图列表
   */
  static getBanners = asyncHandler(async (req: Request, res: Response) => {
    const { activeOnly = 'true', limit = 10 } = req.query;
    const limitNum = parseInt(limit as string);

    try {
      let banners;

      if (activeOnly === 'true') {
        // 获取活跃的轮播图
        banners = await BannerModel.getActiveBanners();
      } else {
        // 获取所有轮播图（管理员）
        banners = await BannerModel.find()
          .sort({ sortOrder: 1, createdAt: -1 })
          .limit(limitNum);
      }

      res.json({
        success: true,
        data: {
          banners: banners.map((banner: any) => ({
            _id: banner._id,
            title: banner.title,
            description: banner.description,
            image: banner.image,
            linkType: banner.linkType,
            linkTarget: banner.linkTarget,
            sortOrder: banner.sortOrder,
            isActive: banner.isActive,
            isCurrentlyActive: banner.isCurrentlyActive,
            startDate: banner.startDate,
            endDate: banner.endDate,
            createdAt: banner.createdAt,
            updatedAt: banner.updatedAt
          }))
        }
      });
    } catch (error) {
      // 开发/测试环境下返回模拟数据
      if (config.env !== 'production') {
        console.warn('数据库连接失败，返回模拟轮播图数据');
        const mockBanners = [
          {
            _id: '1',
            title: '新鲜烘焙面包',
            description: '每日新鲜出炉，健康美味',
            image: '/static/banners/banner-bakery-interior.jpg',
            linkType: 'category',
            linkTarget: '2',
            sortOrder: 1,
            isActive: true,
            isCurrentlyActive: true,
            startDate: new Date('2023-01-01'),
            endDate: new Date('2023-12-31'),
            createdAt: new Date('2023-01-01'),
            updatedAt: new Date('2023-01-01')
          },
          {
            _id: '2',
            title: '精致蛋糕甜点',
            description: '生日庆祝，甜蜜时刻',
            image: '/static/banners/banner-cake-dessert.jpg',
            linkType: 'category',
            linkTarget: '3',
            sortOrder: 2,
            isActive: true,
            isCurrentlyActive: true,
            startDate: new Date('2023-01-01'),
            endDate: new Date('2023-12-31'),
            createdAt: new Date('2023-01-01'),
            updatedAt: new Date('2023-01-01')
          },
          {
            _id: '3',
            title: '咖啡饮品时光',
            description: '现磨咖啡，休闲时光',
            image: '/static/banners/banner-coffee-breakfast.jpg',
            linkType: 'category',
            linkTarget: '5',
            sortOrder: 3,
            isActive: true,
            isCurrentlyActive: true,
            startDate: new Date('2023-01-01'),
            endDate: new Date('2023-12-31'),
            createdAt: new Date('2023-01-01'),
            updatedAt: new Date('2023-01-01')
          }
        ];

        // 根据activeOnly过滤
        let filteredBanners = activeOnly === 'true'
          ? mockBanners.filter(b => b.isActive)
          : mockBanners;

        // 限制数量
        filteredBanners = filteredBanners.slice(0, limitNum);

        res.json({
          success: true,
          data: {
            banners: filteredBanners
          }
        });
      } else {
        throw error; // 生产环境抛出错误
      }
    }
  });

  /**
   * 获取轮播图详情
   */
  static getBannerById = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;

    const banner = await BannerModel.findById(id);

    if (!banner) {
      return res.status(404).json({
        success: false,
        message: '轮播图不存在'
      });
    }

    res.json({
      success: true,
      data: {
        banner: {
          _id: banner._id,
          title: banner.title,
          description: banner.description,
          image: banner.image,
          linkType: banner.linkType,
          linkTarget: banner.linkTarget,
          sortOrder: banner.sortOrder,
          isActive: banner.isActive,
          isCurrentlyActive: banner.isCurrentlyActive,
          startDate: banner.startDate,
          endDate: banner.endDate,
          createdAt: banner.createdAt,
          updatedAt: banner.updatedAt
        }
      }
    });
  });

  /**
   * 创建轮播图（管理员）
   */
  static createBanner = asyncHandler(async (req: Request, res: Response) => {
    const {
      title,
      description,
      image,
      linkType,
      linkTarget,
      sortOrder,
      isActive,
      startDate,
      endDate
    } = req.body;

    // 验证链接类型和链接目标
    if (linkType !== 'url' && !linkTarget) {
      return res.status(400).json({
        success: false,
        message: `${linkType === 'product' ? '商品' : '分类'}ID不能为空`
      });
    }

    // 验证日期
    if (startDate && endDate) {
      const start = new Date(startDate);
      const end = new Date(endDate);
      if (start >= end) {
        return res.status(400).json({
          success: false,
          message: '结束日期必须晚于开始日期'
        });
      }
    }

    const banner = new BannerModel({
      title,
      description,
      image,
      linkType,
      linkTarget,
      sortOrder: sortOrder || 0,
      isActive: isActive !== undefined ? isActive : true,
      startDate: startDate ? new Date(startDate) : undefined,
      endDate: endDate ? new Date(endDate) : undefined
    });

    await banner.save();

    res.status(201).json({
      success: true,
      data: {
        banner: {
          _id: banner._id,
          title: banner.title,
          description: banner.description,
          image: banner.image,
          linkType: banner.linkType,
          linkTarget: banner.linkTarget,
          sortOrder: banner.sortOrder,
          isActive: banner.isActive,
          isCurrentlyActive: banner.isCurrentlyActive,
          startDate: banner.startDate,
          endDate: banner.endDate,
          createdAt: banner.createdAt,
          updatedAt: banner.updatedAt
        }
      },
      message: '轮播图创建成功'
    });
  });

  /**
   * 更新轮播图（管理员）
   */
  static updateBanner = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const updates = req.body;

    // 检查轮播图是否存在
    const existingBanner = await BannerModel.findById(id);
    if (!existingBanner) {
      return res.status(404).json({
        success: false,
        message: '轮播图不存在'
      });
    }

    // 验证链接类型和链接目标
    if (updates.linkType && updates.linkType !== 'url' && !updates.linkTarget) {
      return res.status(400).json({
        success: false,
        message: `${updates.linkType === 'product' ? '商品' : '分类'}ID不能为空`
      });
    }

    // 验证日期
    if (updates.startDate && updates.endDate) {
      const start = new Date(updates.startDate);
      const end = new Date(updates.endDate);
      if (start >= end) {
        return res.status(400).json({
          success: false,
          message: '结束日期必须晚于开始日期'
        });
      }
    }

    // 更新轮播图
    const banner = await BannerModel.findByIdAndUpdate(
      id,
      { $set: updates },
      { new: true, runValidators: true }
    );

    if (!banner) {
      return res.status(404).json({
        success: false,
        message: '轮播图更新失败'
      });
    }

    res.json({
      success: true,
      data: {
        banner: {
          _id: banner._id,
          title: banner.title,
          description: banner.description,
          image: banner.image,
          linkType: banner.linkType,
          linkTarget: banner.linkTarget,
          sortOrder: banner.sortOrder,
          isActive: banner.isActive,
          isCurrentlyActive: banner.isCurrentlyActive,
          startDate: banner.startDate,
          endDate: banner.endDate,
          createdAt: banner.createdAt,
          updatedAt: banner.updatedAt
        }
      },
      message: '轮播图更新成功'
    });
  });

  /**
   * 删除轮播图（管理员）
   */
  static deleteBanner = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;

    const banner = await BannerModel.findByIdAndDelete(id);

    if (!banner) {
      return res.status(404).json({
        success: false,
        message: '轮播图不存在'
      });
    }

    res.json({
      success: true,
      message: '轮播图删除成功'
    });
  });

  /**
   * 更新轮播图排序（管理员）
   */
  static updateBannerOrder = asyncHandler(async (req: Request, res: Response) => {
    const { orders } = req.body;

    if (!Array.isArray(orders) || orders.length === 0) {
      return res.status(400).json({
        success: false,
        message: '排序数据无效'
      });
    }

    // 批量更新排序
    const updatePromises = orders.map(({ id, sortOrder }) =>
      BannerModel.findByIdAndUpdate(id, { $set: { sortOrder } }, { new: true })
    );

    const updatedBanners = await Promise.all(updatePromises);

    // 过滤掉未找到的轮播图
    const validBanners = updatedBanners.filter((banner: any) => banner !== null);

    res.json({
      success: true,
      data: {
        banners: validBanners.map((banner: any) => ({
          _id: banner!._id,
          title: banner!.title,
          sortOrder: banner!.sortOrder,
          updatedAt: banner!.updatedAt
        }))
      },
      message: '轮播图排序更新成功'
    });
  });

  /**
   * 批量更新轮播图状态（管理员）
   */
  static batchUpdateBannerStatus = asyncHandler(async (req: Request, res: Response) => {
    const { ids, isActive } = req.body;

    if (!Array.isArray(ids) || ids.length === 0 || typeof isActive !== 'boolean') {
      return res.status(400).json({
        success: false,
        message: '请求参数无效'
      });
    }

    // 批量更新状态
    const result = await BannerModel.updateMany(
      { _id: { $in: ids } },
      { $set: { isActive } }
    );

    res.json({
      success: true,
      data: {
        matchedCount: result.matchedCount,
        modifiedCount: result.modifiedCount
      },
      message: `已${isActive ? '启用' : '禁用'} ${result.modifiedCount} 个轮播图`
    });
  });
}

export default BannerController;