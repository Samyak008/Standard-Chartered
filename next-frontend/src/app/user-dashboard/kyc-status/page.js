"use client";

import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";

export default function KycStatusPage() {
  const { data: session } = useSession();
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchUserData = async () => {
      if (!session?.user?.email) return;

      try {
        const response = await fetch("/api/user/profile");
        const data = await response.json();

        if (response.ok) {
          setUserData(data.user);
        } else {
          setError(data.message || "Failed to fetch user data");
        }
      } catch (error) {
        setError("An error occurred while fetching user data");
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [session]);

  if (loading)
    return (
      <div className="flex justify-center items-center min-h-screen bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );

  if (error)
    return (
      <div className="text-center p-8 bg-gray-900 min-h-screen">
        <div className="p-4 bg-red-900/30 border border-red-700/50 text-red-400 rounded-lg mb-6">
          {error}
        </div>
      </div>
    );

  return (
    <div className="p-6 bg-gray-900 min-h-screen">
      <h1 className="text-2xl font-bold text-white mb-6">KYC Information</h1>

      {userData ? (
        <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-xl font-medium text-white mb-4">
                Personal Details
              </h3>
              <dl className="space-y-3">
                <div className="flex flex-col">
                  <dt className="text-gray-400 text-sm">Name</dt>
                  <dd className="text-white">
                    {userData.name || "Not provided"}
                  </dd>
                </div>
                <div className="flex flex-col">
                  <dt className="text-gray-400 text-sm">Email</dt>
                  <dd className="text-white">
                    {userData.email || "Not provided"}
                  </dd>
                </div>
                <div className="flex flex-col">
                  <dt className="text-gray-400 text-sm">Gender</dt>
                  <dd className="text-white">
                    {userData.gender || "Not provided"}
                  </dd>
                </div>
                <div className="flex flex-col">
                  <dt className="text-gray-400 text-sm">Date of Birth</dt>
                  <dd className="text-white">
                    {userData.dateOfBirth
                      ? new Date(userData.dateOfBirth).toLocaleDateString()
                      : "Not provided"}
                  </dd>
                </div>
                <div className="flex flex-col">
                  <dt className="text-gray-400 text-sm">Age</dt>
                  <dd className="text-white">
                    {userData.age || "Not provided"}
                  </dd>
                </div>
                <div className="flex flex-col">
                  <dt className="text-gray-400 text-sm">Marital Status</dt>
                  <dd className="text-white">
                    {userData.marital_status || "Not provided"}
                  </dd>
                </div>
              </dl>
            </div>

            <div>
              <h3 className="text-xl font-medium text-white mb-4">
                Professional Details
              </h3>
              <dl className="space-y-3">
                <div className="flex flex-col">
                  <dt className="text-gray-400 text-sm">Education Level</dt>
                  <dd className="text-white">
                    {userData.education_level || "Not provided"}
                  </dd>
                </div>
                <div className="flex flex-col">
                  <dt className="text-gray-400 text-sm">Employment Status</dt>
                  <dd className="text-white">
                    {userData.employment_status || "Not provided"}
                  </dd>
                </div>
                <div className="flex flex-col">
                  <dt className="text-gray-400 text-sm">Annual Income</dt>
                  <dd className="text-white">
                    {userData.income
                      ? `₹${parseInt(userData.income).toLocaleString()}`
                      : "Not provided"}
                  </dd>
                </div>
              </dl>
            </div>
          </div>

          <div className="mt-8 border-t border-gray-700 pt-6">
            <h3 className="text-xl font-medium text-white mb-4">
              Address Information
            </h3>
            <dl className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex flex-col">
                <dt className="text-gray-400 text-sm">Address</dt>
                <dd className="text-white">
                  {userData.address || "Not provided"}
                </dd>
              </div>
              <div className="flex flex-col">
                <dt className="text-gray-400 text-sm">City</dt>
                <dd className="text-white">
                  {userData.city || "Not provided"}
                </dd>
              </div>
              <div className="flex flex-col">
                <dt className="text-gray-400 text-sm">Postal Code</dt>
                <dd className="text-white">
                  {userData.postalCode || "Not provided"}
                </dd>
              </div>
              <div className="flex flex-col">
                <dt className="text-gray-400 text-sm">Country</dt>
                <dd className="text-white">
                  {userData.country || "Not provided"}
                </dd>
              </div>
            </dl>
          </div>

          <div className="mt-8 border-t border-gray-700 pt-6">
            <h3 className="text-xl font-medium text-white mb-4">KYC Status</h3>
            <div className="flex items-center space-x-4">
              <div
                className={`h-10 w-10 rounded-full flex items-center justify-center ${
                  userData.kycStatus === "Verified"
                    ? "bg-green-600/20 text-green-500"
                    : userData.kycStatus === "In Progress"
                    ? "bg-yellow-600/20 text-yellow-500"
                    : userData.kycStatus === "Rejected"
                    ? "bg-red-600/20 text-red-500"
                    : "bg-gray-600/20 text-gray-500"
                }`}
              >
                {userData.kycStatus === "Verified" ? (
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
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                ) : userData.kycStatus === "In Progress" ? (
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
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                ) : userData.kycStatus === "Rejected" ? (
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
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                ) : (
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
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                )}
              </div>
              <div>
                <p className="text-white text-lg font-medium">
                  {userData.kycStatus || "Not Started"}
                </p>
                <p className="text-gray-400 text-sm">
                  {userData.kycVerificationDate
                    ? `Last updated: ${new Date(
                        userData.kycVerificationDate
                      ).toLocaleDateString()}`
                    : "Not yet submitted"}
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center text-gray-400">
          No KYC information found
        </div>
      )}
    </div>
  );
}
