"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import DashboardLayout from "@/components/dashboard/DashboardLayout";

export default function LoanEligibilityPage() {
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
          <p className="text-white font-medium">Loading loan eligibility...</p>
        </div>
      </div>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center mb-8">
          <div className="bg-purple-600/20 p-3 rounded-lg mr-4">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-8 w-8 text-purple-400"
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
          <div>
            <h1 className="text-3xl font-bold text-white">Loan Eligibility</h1>
            <p className="text-gray-300">
              Check your eligibility and apply for loans
            </p>
          </div>
        </div>

        {/* Loan Status Card */}
        <div className="backdrop-blur-md bg-gray-800/50 p-6 rounded-xl border border-gray-700/50 mb-8">
          <div className="flex items-center">
            <div className="h-16 w-16 rounded-full bg-indigo-600/20 flex items-center justify-center text-indigo-500 mr-6">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-8 w-8"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-white">
                Eligibility Check
              </h3>
              <p className="text-gray-300 mt-1">
                Complete the form below to check your loan eligibility.
              </p>
            </div>
          </div>
        </div>

        {/* Loan Eligibility Form will go here - you'll implement this part */}
        <div className="backdrop-blur-md bg-gray-800/50 p-6 rounded-xl border border-gray-700/50">
          <h3 className="text-xl font-semibold text-white mb-6">
            Loan Application
          </h3>

          {/* You'll implement the form here */}
          <div className="p-8 text-center text-gray-400">
            <p>Loan eligibility form will be implemented here.</p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
