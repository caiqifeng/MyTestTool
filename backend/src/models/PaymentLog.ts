import mongoose from 'mongoose';
import { PaymentStatus, PaymentMethod } from '../../../shared/src/types';

export interface IPaymentLog extends mongoose.Document {
  orderId: string;
  userId: string;
  transactionId?: string;
  paymentMethod: PaymentMethod;
  amount: number;
  status: PaymentStatus;
  requestData?: any;
  responseData?: any;
  errorMessage?: string;
  ipAddress?: string;
  userAgent?: string;
  createdAt: Date;
  updatedAt: Date;
}

const paymentLogSchema = new mongoose.Schema<IPaymentLog>(
  {
    orderId: {
      type: String,
      required: true,
      index: true
    },
    userId: {
      type: String,
      required: true,
      index: true
    },
    transactionId: {
      type: String,
      index: true
    },
    paymentMethod: {
      type: String,
      enum: Object.values(PaymentMethod),
      required: true,
      index: true
    },
    amount: {
      type: Number,
      required: true,
      min: 0
    },
    status: {
      type: String,
      enum: Object.values(PaymentStatus),
      required: true,
      index: true
    },
    requestData: {
      type: mongoose.Schema.Types.Mixed
    },
    responseData: {
      type: mongoose.Schema.Types.Mixed
    },
    errorMessage: {
      type: String,
      trim: true
    },
    ipAddress: {
      type: String,
      trim: true
    },
    userAgent: {
      type: String,
      trim: true
    }
  },
  {
    timestamps: true
  }
);

// 索引
paymentLogSchema.index({ createdAt: -1 });
paymentLogSchema.index({ orderId: 1, status: 1 });
paymentLogSchema.index({ userId: 1, createdAt: -1 });

const PaymentLog = mongoose.model<IPaymentLog>('PaymentLog', paymentLogSchema);

export default PaymentLog;