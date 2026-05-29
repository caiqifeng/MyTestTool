import mongoose from 'mongoose';

export interface ICategory extends mongoose.Document {
  name: string;
  description?: string;
  icon?: string;
  sortOrder: number;
  parentId?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ICategoryModel extends mongoose.Model<ICategory> {
  // Static methods
  getCategoryTree(): Promise<Array<ICategory & { children: ICategory[] }>>;
}

const categorySchema = new mongoose.Schema<ICategory, ICategoryModel>(
  {
    name: {
      type: String,
      required: true,
      trim: true,
      maxlength: 50,
      index: true
    },
    description: {
      type: String,
      trim: true,
      maxlength: 200
    },
    icon: {
      type: String,
      trim: true
    },
    sortOrder: {
      type: Number,
      default: 0,
      index: true
    },
    parentId: {
      type: String,
      index: true,
      default: null
    }
  },
  {
    timestamps: true
  }
);

// Indexes
categorySchema.index({ createdAt: -1 });
categorySchema.index({ updatedAt: -1 });

// Static methods
categorySchema.statics.getCategoryTree = async function(): Promise<Array<ICategory & { children: ICategory[] }>> {
  const categories = await this.find().sort({ sortOrder: 1, name: 1 });

  // Build tree structure
  const categoryMap = new Map<string, ICategory & { children: ICategory[] }>();
  const rootCategories: Array<ICategory & { children: ICategory[] }> = [];

  // First pass: create map with empty children arrays
  categories.forEach(category => {
    const categoryWithChildren = category.toObject() as ICategory & { children: ICategory[] };
    categoryWithChildren.children = [];
    categoryMap.set(category._id.toString(), categoryWithChildren);
  });

  // Second pass: build tree
  categories.forEach(category => {
    const categoryWithChildren = categoryMap.get(category._id.toString())!;

    if (category.parentId && categoryMap.has(category.parentId)) {
      // Add as child to parent
      const parent = categoryMap.get(category.parentId)!;
      parent.children.push(categoryWithChildren);
    } else {
      // Root category
      rootCategories.push(categoryWithChildren);
    }
  });

  return rootCategories;
};

const Category = mongoose.model<ICategory, ICategoryModel>('Category', categorySchema);

export default Category;