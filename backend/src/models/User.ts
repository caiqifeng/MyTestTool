import mongoose from 'mongoose';
import { UserRole } from '@shared/types';

export interface IUser extends mongoose.Document {
  openid: string;
  nickname: string;
  avatar?: string;
  phone?: string;
  email?: string;
  role: UserRole;
  createdAt: Date;
  updatedAt: Date;

  // Instance methods
  hasRole(role: UserRole): boolean;
  isAdmin(): boolean;
}

export interface IUserModel extends mongoose.Model<IUser> {
  // Static methods
  findByOpenid(openid: string): Promise<IUser | null>;
  createOrUpdate(userData: Partial<IUser>): Promise<IUser>;
}

const userSchema = new mongoose.Schema<IUser, IUserModel>(
  {
    openid: {
      type: String,
      required: true,
      unique: true,
      index: true,
      trim: true
    },
    nickname: {
      type: String,
      required: true,
      trim: true,
      maxlength: 50
    },
    avatar: {
      type: String,
      trim: true
    },
    phone: {
      type: String,
      trim: true,
      match: [/^1[3-9]\d{9}$/, '请输入有效的手机号码']
    },
    email: {
      type: String,
      trim: true,
      lowercase: true,
      match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, '请输入有效的邮箱地址']
    },
    role: {
      type: String,
      enum: Object.values(UserRole),
      default: UserRole.CUSTOMER,
      index: true
    }
  },
  {
    timestamps: true
  }
);

// Indexes
userSchema.index({ createdAt: -1 });
userSchema.index({ updatedAt: -1 });

// Static methods
userSchema.statics.findByOpenid = async function(openid: string): Promise<IUser | null> {
  return this.findOne({ openid });
};

userSchema.statics.createOrUpdate = async function(userData: Partial<IUser>): Promise<IUser> {
  if (!userData.openid) {
    throw new Error('openid is required');
  }

  const existingUser = await this.findOne({ openid: userData.openid });

  if (existingUser) {
    // Update existing user
    Object.assign(existingUser, userData);
    return await existingUser.save();
  } else {
    // Create new user
    const user = new this(userData);
    return await user.save();
  }
};

// Instance methods
userSchema.methods.hasRole = function(role: UserRole): boolean {
  return this.role === role;
};

userSchema.methods.isAdmin = function(): boolean {
  return this.role === UserRole.ADMIN;
};

const User = mongoose.model<IUser, IUserModel>('User', userSchema);

export default User;