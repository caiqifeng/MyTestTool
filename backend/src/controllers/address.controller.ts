import { Request, Response } from 'express';
import AddressModel from '../models/Address';
import { asyncHandler } from '../middleware/error';

export class AddressController {
  /**
   * 添加地址
   */
  static createAddress = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const {
      contactName,
      contactPhone,
      province,
      city,
      district,
      detail,
      isDefault = false
    } = req.body;

    // 创建地址
    const address = new AddressModel({
      userId: req.user.userId,
      contactName,
      contactPhone,
      province,
      city,
      district,
      detail,
      isDefault
    });

    await address.save();

    res.status(201).json({
      success: true,
      data: {
        address: {
          _id: address._id,
          userId: address.userId,
          contactName: address.contactName,
          contactPhone: address.contactPhone,
          province: address.province,
          city: address.city,
          district: address.district,
          detail: address.detail,
          isDefault: address.isDefault,
          createdAt: address.createdAt,
          updatedAt: address.updatedAt
        }
      },
      message: '地址添加成功'
    });
  });

  /**
   * 获取地址列表
   */
  static getAddresses = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const addresses = await AddressModel.find({
      userId: req.user.userId
    }).sort({ isDefault: -1, updatedAt: -1 });

    res.json({
      success: true,
      data: {
        addresses: addresses.map(address => ({
          _id: address._id,
          userId: address.userId,
          contactName: address.contactName,
          contactPhone: address.contactPhone,
          province: address.province,
          city: address.city,
          district: address.district,
          detail: address.detail,
          isDefault: address.isDefault,
          createdAt: address.createdAt,
          updatedAt: address.updatedAt
        }))
      }
    });
  });

  /**
   * 获取地址详情
   */
  static getAddressById = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const { id } = req.params;

    const address = await AddressModel.findOne({
      _id: id,
      userId: req.user.userId
    });

    if (!address) {
      return res.status(404).json({
        success: false,
        message: '地址不存在'
      });
    }

    res.json({
      success: true,
      data: {
        address: {
          _id: address._id,
          userId: address.userId,
          contactName: address.contactName,
          contactPhone: address.contactPhone,
          province: address.province,
          city: address.city,
          district: address.district,
          detail: address.detail,
          isDefault: address.isDefault,
          createdAt: address.createdAt,
          updatedAt: address.updatedAt
        }
      }
    });
  });

  /**
   * 更新地址
   */
  static updateAddress = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const { id } = req.params;
    const updates = req.body;

    // 检查地址是否存在且属于当前用户
    const existingAddress = await AddressModel.findOne({
      _id: id,
      userId: req.user.userId
    });

    if (!existingAddress) {
      return res.status(404).json({
        success: false,
        message: '地址不存在'
      });
    }

    // 更新地址
    const address = await AddressModel.findByIdAndUpdate(
      id,
      { $set: updates },
      { new: true, runValidators: true }
    );

    if (!address) {
      return res.status(404).json({
        success: false,
        message: '地址更新失败'
      });
    }

    res.json({
      success: true,
      data: {
        address: {
          _id: address._id,
          userId: address.userId,
          contactName: address.contactName,
          contactPhone: address.contactPhone,
          province: address.province,
          city: address.city,
          district: address.district,
          detail: address.detail,
          isDefault: address.isDefault,
          createdAt: address.createdAt,
          updatedAt: address.updatedAt
        }
      },
      message: '地址更新成功'
    });
  });

  /**
   * 删除地址
   */
  static deleteAddress = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const { id } = req.params;

    // 检查地址是否存在且属于当前用户
    const address = await AddressModel.findOne({
      _id: id,
      userId: req.user.userId
    });

    if (!address) {
      return res.status(404).json({
        success: false,
        message: '地址不存在'
      });
    }

    // 如果是默认地址，需要检查是否有其他地址可以设置为默认
    if (address.isDefault) {
      const otherAddresses = await AddressModel.find({
        userId: req.user.userId,
        _id: { $ne: id }
      }).limit(1);

      if (otherAddresses.length > 0) {
        // 设置第一个其他地址为默认地址
        await AddressModel.findByIdAndUpdate(otherAddresses[0]._id, {
          $set: { isDefault: true }
        });
      }
    }

    // 删除地址
    await AddressModel.findByIdAndDelete(id);

    res.json({
      success: true,
      message: '地址删除成功'
    });
  });

  /**
   * 设置默认地址
   */
  static setDefaultAddress = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const { id } = req.params;

    // 检查地址是否存在且属于当前用户
    const address = await AddressModel.findOne({
      _id: id,
      userId: req.user.userId
    });

    if (!address) {
      return res.status(404).json({
        success: false,
        message: '地址不存在'
      });
    }

    // 如果已经是默认地址，直接返回
    if (address.isDefault) {
      return res.json({
        success: true,
        data: {
          address: {
            _id: address._id,
            isDefault: address.isDefault,
            updatedAt: address.updatedAt
          }
        },
        message: '地址已是默认地址'
      });
    }

    // 设置该地址为默认地址（pre-save hook会自动处理其他地址）
    address.isDefault = true;
    await address.save();

    res.json({
      success: true,
      data: {
        address: {
          _id: address._id,
          isDefault: address.isDefault,
          updatedAt: address.updatedAt
        }
      },
      message: '默认地址设置成功'
    });
  });

  /**
   * 获取默认地址
   */
  static getDefaultAddress = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const address = await AddressModel.findOne({
      userId: req.user.userId,
      isDefault: true
    });

    if (!address) {
      // 如果没有默认地址，返回第一个地址或空
      const firstAddress = await AddressModel.findOne({
        userId: req.user.userId
      }).sort({ createdAt: 1 });

      if (!firstAddress) {
        return res.json({
          success: true,
          data: {
            address: null
          }
        });
      }

      // 设置第一个地址为默认地址
      (firstAddress as any).isDefault = true;
      await firstAddress.save();

      return res.json({
        success: true,
        data: {
          address: {
            _id: firstAddress._id,
            userId: firstAddress.userId,
            contactName: firstAddress.contactName,
            contactPhone: firstAddress.contactPhone,
            province: firstAddress.province,
            city: firstAddress.city,
            district: firstAddress.district,
            detail: firstAddress.detail,
            isDefault: firstAddress.isDefault,
            createdAt: firstAddress.createdAt,
            updatedAt: firstAddress.updatedAt
          }
        }
      });
    }

    res.json({
      success: true,
      data: {
        address: {
          _id: address._id,
          userId: address.userId,
          contactName: address.contactName,
          contactPhone: address.contactPhone,
          province: address.province,
          city: address.city,
          district: address.district,
          detail: address.detail,
          isDefault: address.isDefault,
          createdAt: address.createdAt,
          updatedAt: address.updatedAt
        }
      }
    });
  });
}

export default AddressController;