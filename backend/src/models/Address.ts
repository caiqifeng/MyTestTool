import mongoose from 'mongoose';

export interface IAddress extends mongoose.Document {
  userId: string;
  contactName: string;
  contactPhone: string;
  province: string;
  city: string;
  district: string;
  detail: string;
  isDefault: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface IAddressModel extends mongoose.Model<IAddress> {}

const addressSchema = new mongoose.Schema<IAddress, IAddressModel>(
  {
    userId: {
      type: String,
      required: true,
      index: true
    },
    contactName: {
      type: String,
      required: true,
      trim: true,
      maxlength: 20
    },
    contactPhone: {
      type: String,
      required: true,
      trim: true,
      match: [/^1[3-9]\d{9}$/, '请输入有效的手机号码']
    },
    province: {
      type: String,
      required: true,
      trim: true
    },
    city: {
      type: String,
      required: true,
      trim: true
    },
    district: {
      type: String,
      required: true,
      trim: true
    },
    detail: {
      type: String,
      required: true,
      trim: true,
      maxlength: 200
    },
    isDefault: {
      type: Boolean,
      default: false,
      index: true
    }
  },
  {
    timestamps: true
  }
);

// Indexes
addressSchema.index({ userId: 1, isDefault: 1 });
addressSchema.index({ createdAt: -1 });
addressSchema.index({ updatedAt: -1 });

// Pre-save hook to ensure only one default address per user
addressSchema.pre('save', async function(next) {
  if (this.isDefault) {
    try {
      const AddressModel = this.constructor as mongoose.Model<IAddress>;
      // Use updateMany to set all other addresses to non-default
      await AddressModel.updateMany(
        { userId: this.userId, _id: { $ne: this._id } },
        { $set: { isDefault: false } }
      );
      next();
    } catch (error) {
      next(error as Error);
    }
  } else {
    next();
  }
});

// Post-save hook to validate that only one address is default per user
addressSchema.post('save', async function() {
  const AddressModel = this.constructor as mongoose.Model<IAddress>;
  const defaultAddresses = await AddressModel.find({
    userId: this.userId,
    isDefault: true
  });

  if (defaultAddresses.length > 1) {
    // If somehow we have multiple default addresses, fix it
    // Keep the most recently updated one as default
    const addressesToUpdate = defaultAddresses
      .sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime())
      .slice(1)
      .map(addr => addr._id);

    if (addressesToUpdate.length > 0) {
      await AddressModel.updateMany(
        { _id: { $in: addressesToUpdate } },
        { $set: { isDefault: false } }
      );
    }
  }
});

const Address = mongoose.model<IAddress, IAddressModel>('Address', addressSchema);

export default Address;