import mongoose from "mongoose";

const LoanSuggestionSchema = new mongoose.Schema(
  {
    // User demographics
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
      required: true,
    },
    age: {
      type: Number,
      required: true,
    },
    gender: {
      type: String,
      required: true,
      enum: ["Male", "Female", "Other"],
    },
    maritalStatus: {
      type: String,
      required: true,
      enum: ["Single", "Married", "Divorced", "Widowed"],
    },
    educationLevel: {
      type: String,
      required: true,
      enum: [
        "Primary",
        "Secondary",
        "Bachelor's",
        "Master's",
        "Doctorate",
        "Other",
      ],
    },
    employmentStatus: {
      type: String,
      required: true,
      enum: [
        "Employed",
        "Self-employed",
        "Business Owner",
        "Student",
        "Retired",
        "Unemployed",
      ],
    },
    incomeType: {
      type: String,
      required: true,
      enum: ["Fixed", "Variable", "Mixed", "None"],
    },
    additionalIncome: {
      type: Boolean,
      default: false,
    },
    existingLoan: {
      type: Boolean,
      default: false,
    },

    // Income information
    monthlyIncome: {
      type: Number,
      required: true,
    },

    // Loan suggestions
    suggestedLoans: {
      type: [String],
      required: true,
    },

    // AI analysis
    riskAssessment: {
      type: String,
      enum: ["Low", "Medium", "High"],
    },
    affordabilityScore: {
      type: Number, // 1-100 score
    },
    reasoningExplanation: {
      type: String,
    },

    // Creation timestamps
    createdAt: {
      type: Date,
      default: Date.now,
    },
  },
  { timestamps: true }
);

export default mongoose.models.LoanSuggestion ||
  mongoose.model("LoanSuggestion", LoanSuggestionSchema);
