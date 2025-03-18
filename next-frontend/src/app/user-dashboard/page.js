"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Link from "next/link";
import DashboardLayout from "@/components/dashboard/DashboardLayout";

export default function UserDashboard() {
  const { data: session, status } = useSession();
  const router = useRouter();

  // Redirect if not authenticated
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/login");
    }
  }, [status, router]);

  // Show loading state while checking authentication
  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-purple-950 to-slate-900">
        <div className="backdrop-blur-lg bg-white/5 p-8 rounded-2xl border border-gray-700/30 shadow-lg flex items-center space-x-4">
          <div className="w-8 h-8 border-4 border-t-blue-500 border-r-transparent border-b-purple-500 border-l-transparent rounded-full animate-spin"></div>
          <p className="text-white font-medium">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  // Check for session before rendering content
  if (!session) {
    return null;
  }

  return (
    <DashboardLayout>
      <h2 className="text-2xl font-bold mb-6 text-white">Dashboard Overview</h2>

      {/* Dashboard cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {/* KYC Status Card */}
        <div className="backdrop-blur-md bg-blue-600/10 p-6 rounded-xl border border-blue-500/20 hover:border-blue-500/40 transition-all duration-300 shadow-lg">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                KYC Status
              </h3>
              <p className="text-sm text-gray-300 mb-4">
                Complete your verification process
              </p>
              <div className="inline-block text-sm bg-yellow-600/20 text-yellow-400 px-3 py-1 rounded-full">
                Pending
              </div>
            </div>
            <div className="bg-blue-600/20 p-3 rounded-lg">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-7 w-7 text-blue-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                />
              </svg>
            </div>
          </div>
          <Link href="/user-dashboard/kyc">
            <div className="mt-4 text-blue-400 hover:text-blue-300 transition-colors flex items-center text-sm">
              Complete verification
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4 ml-1"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
          </Link>
        </div>

        {/* Loan Eligibility Card */}
        <div className="backdrop-blur-md bg-purple-600/10 p-6 rounded-xl border border-purple-500/20 hover:border-purple-500/40 transition-all duration-300 shadow-lg">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Loan Eligibility
              </h3>
              <p className="text-sm text-gray-300 mb-4">
                Check your loan status
              </p>
              <div className="inline-block text-sm bg-gray-700/40 text-gray-300 px-3 py-1 rounded-full">
                Not Checked
              </div>
            </div>
            <div className="bg-purple-600/20 p-3 rounded-lg">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-7 w-7 text-purple-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
          </div>
          <Link href="/user-dashboard/loan">
            <div className="mt-4 text-purple-400 hover:text-purple-300 transition-colors flex items-center text-sm">
              Check eligibility
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4 ml-1"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
          </Link>
        </div>

        {/* Account Summary Card */}
        <div className="backdrop-blur-md bg-indigo-600/10 p-6 rounded-xl border border-indigo-500/20 hover:border-indigo-500/40 transition-all duration-300 shadow-lg">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Account Summary
              </h3>
              <p className="text-sm text-gray-300 mb-4">
                Your financial overview
              </p>
              <div className="inline-block text-sm bg-indigo-600/20 text-indigo-400 px-3 py-1 rounded-full">
                Active
              </div>
            </div>
            <div className="bg-indigo-600/20 p-3 rounded-lg">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-7 w-7 text-indigo-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
          </div>
          <div className="mt-4 text-indigo-400 hover:text-indigo-300 transition-colors flex items-center text-sm">
            View details
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4 ml-1"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Welcome message */}
      <div className="mb-8 bg-gray-800/30 p-6 rounded-xl border border-gray-700/50">
        <h3 className="text-xl font-semibold mb-2 text-white">
          Welcome, {session.user?.name || "User"}!
        </h3>
        <p className="text-gray-300">
          Your Standard Chartered banking dashboard provides quick access to all
          your financial needs. Complete your KYC verification to unlock full
          banking features.
        </p>
      </div>
    </DashboardLayout>
  );
}
