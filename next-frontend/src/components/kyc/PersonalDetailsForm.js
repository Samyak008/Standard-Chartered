"use client";

import { useState } from "react";
import { useSession } from "next-auth/react";

export default function PersonalDetailsForm({ onNextStep, updateFormData }) {
  const { data: session } = useSession();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState({ type: "", message: "" });

  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    phoneNumber: "",
    dob: "",
    address: "",
    city: "",
    postalCode: "",
    country: "",
    aadhaarNumber: "",
    panNumber: "",
    gender: "",
    marital_status: "",
    education_level: "",
    employment_status: "",
    income: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const calculateAge = (dateString) => {
    const today = new Date();
    const birthDate = new Date(dateString);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();

    if (
      monthDiff < 0 ||
      (monthDiff === 0 && today.getDate() < birthDate.getDate())
    ) {
      age--;
    }
    return age;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setStatusMessage({ type: "", message: "" });

    try {
      if (!session) {
        throw new Error("You must be signed in to complete KYC");
      }

      // Log the session data to debug
      console.log("Session data:", session);

      if (!session.user?.email) {
        throw new Error("User email not found in session");
      }

      // Calculate age from DOB
      const age = calculateAge(formData.dob);

      // Prepare the data to be sent to the server
      const kycData = {
        name: formData.fullName || session.user.name,
        email: session.user.email, // Use the email from session to ensure consistency
        dateOfBirth: formData.dob,
        age: age,
        gender: formData.gender,
        marital_status: formData.marital_status,
        education_level: formData.education_level,
        employment_status: formData.employment_status,
        income: parseInt(formData.income) || 0,
        address: formData.address,
        city: formData.city,
        postalCode: formData.postalCode,
        country: formData.country,
        aadhaarNumber: formData.aadhaarNumber,
        panNumber: formData.panNumber,
        kycStatus: "In Progress",
      };

      // Send data to the server to update MongoDB
      const response = await fetch("/api/kyc/update-personal-details", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userId: session.user.id,
          kycData: kycData,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || "Failed to update KYC details");
      }

      if (response.ok) {
        console.log("KYC update successful:", result);

        // If using the updateFormData function from props
        if (typeof updateFormData === "function") {
          updateFormData({
            ...kycData,
            kycId: result.kyc?.id,
          });
        }

        setStatusMessage({
          type: "success",
          message: "Personal details saved successfully!",
        });

        // Move to next step after a short delay to show the success message
        setTimeout(() => {
          onNextStep();
        }, 1000);
      }
    } catch (error) {
      console.error("Error updating KYC details:", error);
      setStatusMessage({
        type: "error",
        message: error.message || "Something went wrong. Please try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Status message */}
      {statusMessage.message && (
        <div
          className={`p-4 mb-6 rounded-lg ${
            statusMessage.type === "success"
              ? "bg-green-900/30 border border-green-700/50 text-green-400"
              : "bg-red-900/30 border border-red-700/50 text-red-400"
          }`}
        >
          {statusMessage.message}
        </div>
      )}

      {/* Personal Information */}
      <div className="space-y-6 mb-8">
        <h4 className="text-lg font-medium text-white">Personal Information</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label
              htmlFor="fullName"
              className="block text-gray-300 text-sm font-medium mb-1"
            >
              Full Name
            </label>
            <input
              type="text"
              id="fullName"
              name="fullName"
              value={formData.fullName}
              onChange={handleChange}
              className="w-full bg-gray-800/80 border border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your full name"
              required
            />
          </div>

          <div>
            <label
              htmlFor="email"
              className="block text-gray-300 text-sm font-medium mb-1"
            >
              Email Address
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full bg-gray-800/80 border border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your email address"
              required
            />
          </div>

          <div>
            <label
              htmlFor="phoneNumber"
              className="block text-gray-300 text-sm font-medium mb-1"
            >
              Phone Number
            </label>
            <input
              type="tel"
              id="phoneNumber"
              name="phoneNumber"
              value={formData.phoneNumber}
              onChange={handleChange}
              className="w-full bg-gray-800/80 border border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your phone number"
              required
            />
          </div>

          <div>
            <label
              htmlFor="dob"
              className="block text-gray-300 text-sm font-medium mb-1"
            >
              Date of Birth
            </label>
            <input
              type="date"
              id="dob"
              name="dob"
              value={formData.dob}
              onChange={handleChange}
              className="w-full bg-gray-800/80 border border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label
              htmlFor="gender"
              className="block text-gray-300 text-sm font-medium mb-1"
            >
              Gender
            </label>
            <select
              id="gender"
              name="gender"
              value={formData.gender}
              onChange={handleChange}
              className="w-full bg-gray-800/80 border border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
              <option value="">Select gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div>
            <label
              htmlFor="marital_status"
              className="block text-gray-300 text-sm font-medium mb-1"
            >
              Marital Status
            </label>
            <select
              id="marital_status"
              name="marital_status"
              value={formData.marital_status}
              onChange={handleChange}
              className="w-full bg-gray-800/80 border border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
              <option value="">Select marital status</option>
              <option value="Single">Single</option>
              <option value="Married">Married</option>
              <option value="Divorced">Divorced</option>
              <option value="Widowed">Widowed</option>
            </select>
          </div>
        </div>
      </div>

      {/* Education & Employment */}
      <div className="space-y-6 mb-8">
        <h4 className="text-lg font-medium text-white">
          Education & Employment
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label
              htmlFor="education_level"
              className="block text-gray-300 text-sm font-medium mb-1"
            >
              Education Level
            </label>
            <select
              id="education_level"
              name="education_level"
              value={formData.education_level}
              onChange={handleChange}
              className="w-full bg-gray-800/80 border border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
              <option value="">Select education level</option>
              <option value="High School">High School</option>
              <option value="Bachelor's">Bachelor's</option>
              <option value="Master's">Master's</option>
              <option value="PhD">PhD</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div>
            <label
              htmlFor="employment_status"
              className="block text-gray-300 text-sm font-medium mb-1"
            >
              Employment Status
            </label>
            <select
              id="employment_status"
              name="employment_status"
              value={formData.employment_status}
              onChange={handleChange}
              className="w-full bg-gray-800/80 border border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
              <option value="">Select employment status</option>
              <option value="Employed">Employed</option>
              <option value="Self-Employed">Self-Employed</option>
              <option value="Unemployed">Unemployed</option>
              <option value="Retired">Retired</option>
            </select>
          </div>

          <div>
            <label
              htmlFor="income"
              className="block text-gray-300 text-sm font-medium mb-1"
            >
              Annual Income (in ₹)
            </label>
            <select
              id="income"
              name="income"
              value={formData.income}
              onChange={handleChange}
              className="w-full bg-gray-800/80 border border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
              <option value="">Select income range</option>
              <option value="100000">Less than 1,00,000</option>
              <option value="250000">1,00,000 - 2,50,000</option>
              <option value="500000">2,50,000 - 5,00,000</option>
              <option value="1000000">5,00,000 - 10,00,000</option>
              <option value="2000000">10,00,000 - 20,00,000</option>
              <option value="3000000">More than 20,00,000</option>
            </select>
          </div>
        </div>
      </div>

      {/* Rest of your form follows the same pattern... */}

      {/* KYC Status Information */}
      <div className="p-4 bg-gray-800/30 border border-gray-700/50 rounded-lg mb-8 space-y-3">
        <div className="flex items-center">
          <div className="h-10 w-10 rounded-full bg-blue-600/20 flex items-center justify-center text-blue-500 mr-4">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div>
            <h5 className="text-white font-medium">KYC Verification</h5>
            <p className="text-gray-400 text-sm">
              Your information will be used for KYC verification. Status will be
              updated to In Progress after submission.
            </p>
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isSubmitting}
          className={`px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium rounded-lg transition-all duration-300 shadow-md shadow-blue-900/20 flex items-center ${
            isSubmitting ? "opacity-70 cursor-not-allowed" : ""
          }`}
        >
          {isSubmitting ? (
            <>
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              <span>Processing...</span>
            </>
          ) : (
            <>
              <span>Next Step</span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 ml-2"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            </>
          )}
        </button>
      </div>
    </form>
  );
}
