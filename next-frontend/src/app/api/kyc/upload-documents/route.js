import { NextResponse } from "next/server";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";
import { connectToDB } from "@/lib/db";
import KYC from "@/models/KYC";
import User from "@/models/User";
import { writeFile } from "fs/promises";
import path from "path";
import { v4 as uuidv4 } from "uuid";

export async function POST(request) {
  try {
    // Check authentication
    const session = await getServerSession(authOptions);
    if (!session) {
      return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    // Parse form data with files
    const formData = await request.formData();
    const userId = formData.get("userId");

    // Ensure the user is only uploading their own documents
    if (userId !== session.user.id) {
      return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    // Get extracted data if available
    const extractedName = formData.get("extractedName");
    const extractedAadhaarNumber = formData.get("extractedAadhaarNumber");

    // Get the files
    const aadhaarFile = formData.get("aadhaar");
    const panFile = formData.get("pan");
    const photoFile = formData.get("photo");
    const signatureFile = formData.get("signature");

    if (!aadhaarFile || !panFile) {
      return NextResponse.json(
        { message: "Aadhaar and PAN documents are required" },
        { status: 400 }
      );
    }

    await connectToDB();

    // Find user
    const user = await User.findOne({ email: session.user.email });
    if (!user) {
      return NextResponse.json({ message: "User not found" }, { status: 404 });
    }

    // Find KYC record or create if doesn't exist
    let kyc = await KYC.findOne({ userId: user._id });
    if (!kyc) {
      kyc = new KYC({
        userId: user._id,
        email: user.email,
        name: user.name,
        kycStatus: "In Progress",
      });
    }

    // Create uploads directory if it doesn't exist
    const uploadDir = path.join(process.cwd(), "public", "uploads");
    try {
      await fs.mkdir(uploadDir, { recursive: true });
    } catch (error) {
      console.error("Error creating upload directory:", error);
    }

    // Function to save a file and return its path
    async function saveFile(file, prefix) {
      if (!file) return null;

      const bytes = await file.arrayBuffer();
      const buffer = Buffer.from(bytes);

      // Get file extension
      const fileExt = file.name.split(".").pop().toLowerCase();

      // Generate unique filename
      const fileName = `${prefix}_${uuidv4()}.${fileExt}`;
      const filePath = path.join(uploadDir, fileName);

      // Save the file
      await writeFile(filePath, buffer);

      // Return the relative URL path
      return `/uploads/${fileName}`;
    }

    // Save documents and store their paths
    const documents = {};

    documents.aadhaarCard = await saveFile(aadhaarFile, "aadhaar");
    documents.panCard = await saveFile(panFile, "pan");

    if (photoFile) {
      documents.photo = await saveFile(photoFile, "photo");
    }

    if (signatureFile) {
      documents.signature = await saveFile(signatureFile, "signature");
    }

    // Update KYC record with document info and extracted data
    kyc.documents = documents;

    if (extractedAadhaarNumber) {
      kyc.aadhaarNumber = extractedAadhaarNumber;
    }

    if (extractedName && !kyc.name) {
      kyc.name = extractedName;
    }

    // Update KYC status
    kyc.kycStatus = "In Progress";
    kyc.verificationDate = new Date();
    kyc.documentsUploaded = true;

    await kyc.save();

    return NextResponse.json(
      {
        message: "Documents uploaded successfully",
        documentUrls: documents,
        success: true,
      },
      { status: 200 }
    );
  } catch (error) {
    console.error("Error uploading documents:", error);
    return NextResponse.json(
      {
        message: error.message || "Error uploading documents",
      },
      { status: 500 }
    );
  }
}
