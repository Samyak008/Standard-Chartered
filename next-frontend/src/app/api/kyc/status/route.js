import { NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";
import { connectToDB } from "@/lib/db";
import KYC from "@/models/KYC";
import User from "@/models/User";

export async function GET(request) {
  try {
    // Verify authentication
    const session = await getServerSession(authOptions);
    if (!session) {
      return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    await connectToDB();

    // Find the user
    const user = await User.findOne({ email: session.user.email });
    if (!user) {
      return NextResponse.json({ message: "User not found" }, { status: 404 });
    }

    // Find KYC record
    const kycRecord = await KYC.findOne({ userId: user._id });

    if (!kycRecord) {
      return NextResponse.json({
        success: true,
        data: {
          kycStatus: "Not Started",
          faceVerified: false,
          isComplete: false,
          name: user.name,
        },
      });
    }

    // Check if KYC is complete based on status and face verification
    const isComplete =
      kycRecord.kycStatus === "Verified" && kycRecord.faceVerified === true;

    console.log("KYC status API response:", {
      kycStatus: kycRecord.kycStatus,
      faceVerified: kycRecord.faceVerified,
      isComplete: isComplete,
      lastUpdated: kycRecord.updatedAt || kycRecord.verificationDate,
      name: kycRecord.name,
    });

    return NextResponse.json({
      success: true,
      data: {
        kycStatus: kycRecord.kycStatus,
        faceVerified: kycRecord.faceVerified,
        isComplete: isComplete,
        lastUpdated: kycRecord.updatedAt || kycRecord.verificationDate,
        name: kycRecord.name,
      },
    });
  } catch (error) {
    console.error("Error fetching KYC status:", error);
    return NextResponse.json(
      {
        success: false,
        message: error.message || "Failed to fetch KYC status",
      },
      { status: 500 }
    );
  }
}
