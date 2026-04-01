import mongoose from 'mongoose';

export interface IBanner extends mongoose.Document {
  title: string;
  description?: string;
  image: string;
  linkType: 'product' | 'category' | 'url';
  linkTarget?: string;
  sortOrder: number;
  isActive: boolean;
  startDate?: Date;
  endDate?: Date;
  createdAt: Date;
  updatedAt: Date;

  // Virtual properties
  isCurrentlyActive: boolean;
}

const bannerSchema = new mongoose.Schema<IBanner>(
  {
    title: {
      type: String,
      required: true,
      trim: true,
      maxlength: 50
    },
    description: {
      type: String,
      trim: true,
      maxlength: 200
    },
    image: {
      type: String,
      required: true,
      trim: true
    },
    linkType: {
      type: String,
      enum: ['product', 'category', 'url'],
      required: true,
      index: true
    },
    linkTarget: {
      type: String,
      trim: true
    },
    sortOrder: {
      type: Number,
      default: 0,
      index: true
    },
    isActive: {
      type: Boolean,
      default: true,
      index: true
    },
    startDate: {
      type: Date
    },
    endDate: {
      type: Date
    }
  },
  {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
  }
);

// Indexes
bannerSchema.index({ createdAt: -1 });
bannerSchema.index({ updatedAt: -1 });
bannerSchema.index({ sortOrder: 1, createdAt: -1 });
bannerSchema.index({ isActive: 1, startDate: 1, endDate: 1 });

// Virtual for checking if banner is currently active
bannerSchema.virtual('isCurrentlyActive').get(function() {
  const now = new Date();

  if (!this.isActive) {
    return false;
  }

  if (this.startDate && now < this.startDate) {
    return false;
  }

  if (this.endDate && now > this.endDate) {
    return false;
  }

  return true;
});

// Static method to get active banners
bannerSchema.statics.getActiveBanners = async function(): Promise<IBanner[]> {
  const now = new Date();

  const query: any = {
    isActive: true
  };

  // Add date range conditions
  const dateConditions = [];

  // Banners with no date restrictions
  dateConditions.push({
    $and: [
      { startDate: { $exists: false } },
      { endDate: { $exists: false } }
    ]
  });

  // Banners with only start date
  dateConditions.push({
    $and: [
      { startDate: { $lte: now } },
      { endDate: { $exists: false } }
    ]
  });

  // Banners with only end date
  dateConditions.push({
    $and: [
      { startDate: { $exists: false } },
      { endDate: { $gte: now } }
    ]
  });

  // Banners with both start and end dates
  dateConditions.push({
    $and: [
      { startDate: { $lte: now } },
      { endDate: { $gte: now } }
    ]
  });

  query.$or = dateConditions;

  return this.find(query)
    .sort({ sortOrder: 1, createdAt: -1 })
    .limit(10);
};

interface IBannerModel extends mongoose.Model<IBanner> {
  getActiveBanners(): Promise<IBanner[]>;
}

const Banner = mongoose.model<IBanner, IBannerModel>('Banner', bannerSchema);

export default Banner;