import mongoose from "mongoose";

const KYCSchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
      required: true,
      unique: true,
    },
    name: { type: String, required: true },
    email: { type: String, required: true },
    dateOfBirth: { type: Date },
    age: { type: Number, min: 18 },
    gender: { type: String, enum: ["Male", "Female", "Other"] },
    marital_status: {
      type: String,
      enum: ["Single", "Married", "Divorced", "Widowed"],
    },
    education_level: {
      type: String,
      enum: ["High School", "Bachelor's", "Master's", "PhD", "Other"],
    },
    employment_status: {
      type: String,
      enum: ["Employed", "Self-Employed", "Unemployed", "Retired"],
    },
    income: { type: Number, min: 0 },
    address: { type: String },
    city: { type: String },
    postalCode: { type: String },
    country: { type: String },
    aadhaarNumber: { type: String },
    panNumber: { type: String },
    kycStatus: {
      type: String,
      enum: ["Not Started", "In Progress", "Verified", "Rejected"],
      default: "In Progress",
    },
    verificationDate: { type: Date, default: Date.now },
    documents: {
      aadhaarCard: { type: String },
      panCard: { type: String },
      photo: { type: String },
      signature: { type: String },
    },
    faceVerified: { type: Boolean, default: false },
    notes: { type: String },
    reviewedBy: { type: mongoose.Schema.Types.ObjectId, ref: "User" },
  },
  { timestamps: true }
);

export default mongoose.models.KYC || mongoose.model("KYC", KYCSchema);
