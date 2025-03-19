import { connectToDB } from "@/lib/db";
import User from "@/models/User";
import KYC from "@/models/KYC";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";
import mongoose from "mongoose";

export async function POST(req) {
  try {
    // Check authentication
    const session = await getServerSession(authOptions);
    if (!session) {
      return new Response(JSON.stringify({ message: "Unauthorized" }), {
        status: 401,
      });
    }

    const { userId, kycData } = await req.json();

    console.log("Updating KYC for:", session.user.email);
    console.log("KYC Data received:", JSON.stringify(kycData, null, 2));

    await connectToDB();

    // Find the user
    const user = await User.findOne({ email: session.user.email });

    if (!user) {
      console.error(`User not found with email: ${session.user.email}`);
      return new Response(
        JSON.stringify({
          message: "User not found. Please check your account.",
        }),
        { status: 404 }
      );
    }

    console.log("Found user:", user.email);

    // Check if user already has KYC record
    let kycRecord = await KYC.findOne({ userId: user._id });

    if (kycRecord) {
      // Update existing KYC record
      console.log("Updating existing KYC record");

      kycRecord.name = kycData.name || kycRecord.name;
      kycRecord.dateOfBirth = kycData.dateOfBirth || kycRecord.dateOfBirth;
      kycRecord.age = kycData.age || kycRecord.age;
      kycRecord.gender = kycData.gender || kycRecord.gender;
      kycRecord.marital_status =
        kycData.marital_status || kycRecord.marital_status;
      kycRecord.education_level =
        kycData.education_level || kycRecord.education_level;
      kycRecord.employment_status =
        kycData.employment_status || kycRecord.employment_status;
      kycRecord.income = kycData.income || kycRecord.income;
      kycRecord.address = kycData.address || kycRecord.address;
      kycRecord.city = kycData.city || kycRecord.city;
      kycRecord.postalCode = kycData.postalCode || kycRecord.postalCode;
      kycRecord.country = kycData.country || kycRecord.country;
      kycRecord.aadhaarNumber =
        kycData.aadhaarNumber || kycRecord.aadhaarNumber;
      kycRecord.panNumber = kycData.panNumber || kycRecord.panNumber;
      kycRecord.kycStatus = "In Progress";
      kycRecord.verificationDate = new Date();

      await kycRecord.save();
    } else {
      // Create new KYC record
      console.log("Creating new KYC record");

      kycRecord = new KYC({
        userId: user._id,
        name: kycData.name || user.name,
        email: user.email,
        dateOfBirth: kycData.dateOfBirth,
        age: kycData.age,
        gender: kycData.gender,
        marital_status: kycData.marital_status,
        education_level: kycData.education_level,
        employment_status: kycData.employment_status,
        income: kycData.income,
        address: kycData.address,
        city: kycData.city,
        postalCode: kycData.postalCode,
        country: kycData.country,
        aadhaarNumber: kycData.aadhaarNumber,
        panNumber: kycData.panNumber,
        kycStatus: "In Progress",
        verificationDate: new Date(),
      });

      await kycRecord.save();
    }

    console.log("KYC record saved:", kycRecord);

    return new Response(
      JSON.stringify({
        message: "KYC details updated successfully",
        kyc: {
          id: kycRecord._id,
          name: kycRecord.name,
          email: kycRecord.email,
          kycStatus: kycRecord.kycStatus,
        },
      }),
      { status: 200 }
    );
  } catch (error) {
    console.error("Error updating KYC details:", error);
    return new Response(
      JSON.stringify({ message: error.message || "Server error" }),
      {
        status: 500,
      }
    );
  }
}
