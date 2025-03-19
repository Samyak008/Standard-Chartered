import { NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";
import { connectToDB } from "@/lib/db";
import KYC from "@/models/KYC";
import User from "@/models/User";

export async function POST(request) {
  try {
    // Verify authentication
    const session = await getServerSession(authOptions);
    if (!session) {
      return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { kycStatus, faceVerified } = body;

    await connectToDB();

    // Find the user
    const user = await User.findOne({ email: session.user.email });
    if (!user) {
      return NextResponse.json({ message: "User not found" }, { status: 404 });
    }

    // Find or create a KYC record
    let kycRecord = await KYC.findOne({ userId: user._id });

    if (kycRecord) {
      // Update existing record
      if (kycStatus !== undefined) kycRecord.kycStatus = kycStatus;
      if (faceVerified !== undefined) kycRecord.faceVerified = faceVerified;

      // Update verification date if status is changing to "Verified"
      if (kycStatus === "Verified") {
        kycRecord.verificationDate = new Date();
      }

      await kycRecord.save();
    } else {
      // Create a new KYC record
      kycRecord = new KYC({
        userId: user._id,
        name: user.name,
        email: user.email,
        kycStatus: kycStatus || "In Progress",
        faceVerified: faceVerified || false,
        verificationDate: kycStatus === "Verified" ? new Date() : null,
      });

      await kycRecord.save();
    }

    return NextResponse.json({
      success: true,
      message: "KYC status updated successfully",
      data: {
        kycStatus: kycRecord.kycStatus,
        faceVerified: kycRecord.faceVerified,
      },
    });
  } catch (error) {
    console.error("Error updating KYC status:", error);
    return NextResponse.json(
      {
        success: false,
        message: error.message || "Failed to update KYC status",
      },
      { status: 500 }
    );
  }
}
