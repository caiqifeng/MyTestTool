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

const addressSchema = new mongoose.Schema<IAddress>(
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
    const AddressModel = this.constructor as mongoose.Model<IAddress>;
    await AddressModel.updateMany(
      { userId: this.userId, _id: { $ne: this._id } },
      { $set: { isDefault: false } }
    );
  }
  next();
});

const Address = mongoose.model<IAddress>('Address', addressSchema);

export default Address;