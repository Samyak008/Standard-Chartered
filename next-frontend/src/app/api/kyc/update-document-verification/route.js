import { NextResponse } from "next/server";
import { connectToDB } from "@/lib/db";
import User from "@/models/User";
import KYC from "@/models/KYC";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";

export async function POST(request) {
  try {
    // Check authentication
    const session = await getServerSession(authOptions);
    if (!session) {
      return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { userId, aadhaarNumber, name, documentsUploaded } = body;

    // Verify that the user is updating their own record
    if (userId !== session.user.id) {
      return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    await connectToDB();

    // Find the user
    const user = await User.findOne({ email: session.user.email });

    if (!user) {
      return NextResponse.json({ message: "User not found" }, { status: 404 });
    }

    // Find or create KYC record
    let kycRecord = await KYC.findOne({ userId: user._id });

    if (kycRecord) {
      // Update existing KYC record with document verification details
      kycRecord.aadhaarNumber = aadhaarNumber || kycRecord.aadhaarNumber;

      // Update name if extracted and different from current
      if (name && (!kycRecord.name || kycRecord.name !== name)) {
        kycRecord.name = name;
      }

      kycRecord.documentsUploaded =
        documentsUploaded || kycRecord.documentsUploaded;
      kycRecord.documentVerificationDate = new Date();

      await kycRecord.save();
    } else {
      // Create new KYC record with document verification details
      kycRecord = new KYC({
        userId: user._id,
        name: name || user.name,
        email: user.email,
        aadhaarNumber: aadhaarNumber || "",
        documentsUploaded: documentsUploaded || false,
        documentVerificationDate: new Date(),
        kycStatus: "In Progress",
      });

      await kycRecord.save();
    }

    return NextResponse.json(
      {
        success: true,
        message: "Document verification details updated",
        kyc: {
          id: kycRecord._id,
          aadhaarNumber: kycRecord.aadhaarNumber,
          documentsUploaded: kycRecord.documentsUploaded,
        },
      },
      { status: 200 }
    );
  } catch (error) {
    console.error("Error updating document verification:", error);
    return NextResponse.json(
      {
        success: false,
        message: error.message || "Failed to update document verification",
      },
      { status: 500 }
    );
  }
}
