import { connectToDB } from "@/lib/db";
import User from "@/models/User";
import KYC from "@/models/KYC";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";

export async function GET(req) {
  try {
    // Check authentication
    const session = await getServerSession(authOptions);
    if (!session) {
      return new Response(JSON.stringify({ message: "Unauthorized" }), {
        status: 401,
      });
    }

    await connectToDB();

    // Find the user
    const user = await User.findOne({ email: session.user.email });

    if (!user) {
      return new Response(JSON.stringify({ message: "User not found" }), {
        status: 404,
      });
    }

    // Find KYC data for the user
    const kycData = await KYC.findOne({ userId: user._id });

    // Prepare user data with KYC information if available
    const userData = {
      id: user._id,
      name: user.name,
      email: user.email,
      role: user.role,
      createdAt: user.createdAt,
    };

    // If KYC data exists, add it to the response
    if (kycData) {
      userData.dateOfBirth = kycData.dateOfBirth;
      userData.age = kycData.age;
      userData.gender = kycData.gender;
      userData.marital_status = kycData.marital_status;
      userData.education_level = kycData.education_level;
      userData.employment_status = kycData.employment_status;
      userData.income = kycData.income;
      userData.address = kycData.address;
      userData.city = kycData.city;
      userData.postalCode = kycData.postalCode;
      userData.country = kycData.country;
      userData.aadhaarNumber = kycData.aadhaarNumber;
      userData.panNumber = kycData.panNumber;
      userData.kycStatus = kycData.kycStatus || "Not Started";
      userData.kycVerificationDate = kycData.verificationDate;
      userData.faceVerified = kycData.faceVerified;
    } else {
      userData.kycStatus = "Not Started";
    }

    return new Response(
      JSON.stringify({
        user: userData,
      }),
      { status: 200 }
    );
  } catch (error) {
    console.error("Error fetching user profile:", error);
    return new Response(JSON.stringify({ message: "Server error" }), {
      status: 500,
    });
  }
}
