import { NextResponse } from "next/server";
import { connectToDB } from "@/lib/db";
import LoanSuggestion from "@/models/vapi";
import mongoose from "mongoose";

export async function POST(request) {
  try {
    // Parse request body
    const {
      age,
      gender,
      maritalStatus,
      educationLevel,
      employmentStatus,
      incomeType,
      additionalIncome,
      existingLoan,
      monthlyIncome,
      userid,
    } = await request.json();

    // Log received request data
    console.log("Received request with data:", {
      age,
      gender,
      maritalStatus,
      educationLevel,
      employmentStatus,
      incomeType,
      additionalIncome: additionalIncome || false,
      existingLoan: existingLoan || false,
      monthlyIncome,
      userid,
    });

    // Validate required fields
    const requiredFields = {
      age,
      gender,
      maritalStatus,
      educationLevel,
      employmentStatus,
      incomeType,
      monthlyIncome,
      userid,
    };

    const missingFields = Object.keys(requiredFields).filter(
      (key) => !requiredFields[key] && requiredFields[key] !== 0
    );

    if (missingFields.length > 0) {
      return NextResponse.json(
        {
          success: false,
          error: `Missing required fields: ${missingFields.join(", ")}`,
        },
        { status: 400 }
      );
    }

    // Connect to database
    await connectToDB();

    // Import AI SDK dynamically
    const { generateText } = await import("ai");
    const { google } = await import("@ai-sdk/google");

    const prompt = `You are Loanly's AI financial advisor. Based on the following client profile, suggest the most suitable loan types from the available options. Provide reasoning for your suggestions.

User Profile:
- Age: ${age}
- Gender: ${gender}
- Marital Status: ${maritalStatus}
- Education Level: ${educationLevel}
- Employment Status: ${employmentStatus}
- Income Type: ${incomeType}
- Monthly Income: ${monthlyIncome}
- Has Additional Income: ${additionalIncome ? "Yes" : "No"}
- Has Existing Loans: ${existingLoan ? "Yes" : "No"}

Available Loan Types:
- Home Loan
- Car Loan
- Education Loan
- Medical Loan
- Business Loan
- Premium Loan
- Agriculture Loan
- Startup Loan
- Gold Loan
- Loan Against Property

Please return your response in the following JSON format without any additional text:
{
  "suggestedLoans": ["Loan Type 1", "Loan Type 2", "Loan Type 3"],
  "riskAssessment": "Low/Medium/High",
  "affordabilityScore": 85,
  "reasoningExplanation": "Brief explanation of your loan suggestions and risk assessment"
}
`;

    // Generate loan suggestions using AI SDK
    const { text: resultJson } = await generateText({
      model: google("gemini-1.5-pro"),
      prompt: prompt,
      temperature: 0.4,
      maxTokens: 1024,
    });

    // Parse the JSON response
    let loanData;
    try {
      // Find JSON in the response
      const jsonMatch = resultJson.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        loanData = JSON.parse(jsonMatch[0]);
      } else {
        throw new Error("Could not extract JSON from AI response");
      }
    } catch (parseError) {
      console.error("Error parsing AI response:", parseError, resultJson);
      return NextResponse.json(
        {
          success: false,
          error: "Failed to parse AI response",
          rawResponse: resultJson,
        },
        { status: 500 }
      );
    }

    // Create user ObjectId
    let userObjectId;
    try {
      userObjectId = new mongoose.Types.ObjectId(userid);
    } catch (error) {
      return NextResponse.json(
        {
          success: false,
          error: "Invalid user ID format",
        },
        { status: 400 }
      );
    }

    // Create loan suggestion document
    const loanSuggestion = new LoanSuggestion({
      userId: userObjectId,
      age,
      gender,
      maritalStatus,
      educationLevel,
      employmentStatus,
      incomeType,
      additionalIncome: additionalIncome || false,
      existingLoan: existingLoan || false,
      monthlyIncome,
      suggestedLoans: loanData.suggestedLoans,
      riskAssessment: loanData.riskAssessment,
      affordabilityScore: loanData.affordabilityScore,
      reasoningExplanation: loanData.reasoningExplanation,
    });

    // Log about to save loan suggestion
    console.log("About to save loan suggestion:", loanSuggestion);

    // Save to database
    await loanSuggestion.save();

    // Log successfully saved loan suggestion
    console.log(
      "Successfully saved loan suggestion with ID:",
      loanSuggestion._id
    );

    return NextResponse.json(
      {
        success: true,
        data: {
          id: loanSuggestion._id,
          suggestedLoans: loanData.suggestedLoans,
          riskAssessment: loanData.riskAssessment,
          affordabilityScore: loanData.affordabilityScore,
          reasoningExplanation: loanData.reasoningExplanation,
        },
      },
      { status: 200 }
    );
  } catch (error) {
    console.error("Error generating loan suggestions:", error);
    return NextResponse.json(
      {
        success: false,
        error: error.message || "Failed to generate loan suggestions",
      },
      { status: 500 }
    );
  }
}

// Handle GET requests for testing the API endpoint
export async function GET() {
  return NextResponse.json({
    success: true,
    data: "Loan suggestion API is online. Send a POST request to generate loan suggestions.",
    exampleRequest: {
      age: 35,
      gender: "Male",
      maritalStatus: "Married",
      educationLevel: "Bachelor's",
      employmentStatus: "Employed",
      incomeType: "Fixed",
      additionalIncome: false,
      existingLoan: false,
      monthlyIncome: 50000,
      userid: "valid-mongodb-user-id",
    },
  });
}
