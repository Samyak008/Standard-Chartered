"use client";

import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";

export default function VerificationComplete({ formData }) {
  const router = useRouter();
  const { data: session } = useSession();
  const [kycData, setKycData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch updated KYC data
  useEffect(() => {
    const fetchKycData = async () => {
      if (!session) return;

      try {
        const response = await fetch("/api/kyc/status");
        if (!response.ok) {
          throw new Error("Failed to fetch KYC data");
        }

        const data = await response.json();
        setKycData(data.data);
      } catch (error) {
        console.error("Error fetching KYC data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchKycData();
  }, [session]);

  return (
    <div className="flex flex-col items-center text-center py-6">
      <div className="w-20 h-20 mb-6 rounded-full bg-green-600/20 flex items-center justify-center">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-10 w-10 text-green-500"
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
      </div>

      <h3 className="text-2xl font-bold text-white mb-3">
        Verification Successful!
      </h3>
      <p className="text-gray-300 mb-8">
        Your identity has been successfully verified.
      </p>

      <div className="w-full max-w-md p-6 bg-gray-800/70 border border-gray-700 rounded-xl mb-8">
        <h4 className="text-lg font-medium text-white mb-4">
          Verification Summary
        </h4>
        <div className="space-y-3">
          <div className="flex justify-between pb-2 border-b border-gray-700">
            <span className="text-gray-400">Name</span>
            <span className="text-white font-medium">
              {kycData?.name || formData?.personal?.name || "N/A"}
            </span>
          </div>
          <div className="flex justify-between pb-2 border-b border-gray-700">
            <span className="text-gray-400">Email</span>
            <span className="text-white font-medium">
              {session?.user?.email || formData?.personal?.email || "N/A"}
            </span>
          </div>
          <div className="flex justify-between pb-2 border-b border-gray-700">
            <span className="text-gray-400">Documents</span>
            <span className="text-green-500 font-medium">Verified</span>
          </div>
          <div className="flex justify-between pb-2 border-b border-gray-700">
            <span className="text-gray-400">Face Verification</span>
            <span className="text-green-500 font-medium">Verified</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Verification Date</span>
            <span className="text-white font-medium">
              {kycData?.lastUpdated
                ? new Date(kycData.lastUpdated).toLocaleDateString()
                : new Date().toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>

      <div className="flex flex-col md:flex-row space-y-3 md:space-y-0 md:space-x-4">
        <button
          onClick={() => router.push("/user-dashboard")}
          className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium rounded-lg transition-all duration-300 shadow-md shadow-blue-900/20 flex items-center justify-center"
        >
          <span>Go to Dashboard</span>
        </button>
        <button
          onClick={() => router.push("/user-dashboard/account-services")}
          className="px-6 py-3 border border-gray-600 text-gray-300 font-medium rounded-lg hover:bg-gray-800 transition-all duration-300 flex items-center justify-center"
        >
          <span>Explore Account Services</span>
        </button>
      </div>
    </div>
  );
}
