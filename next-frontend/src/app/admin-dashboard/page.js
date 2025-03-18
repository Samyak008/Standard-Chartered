"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import DashboardLayout from "@/components/dashboard/DashboardLayout";

export default function AdminDashboard() {
  const { data: session, status } = useSession();
  const router = useRouter();

  // Redirect if not authenticated or not admin
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/login");
    } else if (session?.user?.role !== "admin") {
      router.push("/user-dashboard");
    }
  }, [status, session, router]);

  // Show loading state while checking authentication
  if (status === "loading" || !session) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-purple-950 to-slate-900">
        <div className="backdrop-blur-lg bg-white/5 p-8 rounded-2xl border border-gray-700/30 shadow-lg flex items-center space-x-4">
          <div className="w-8 h-8 border-4 border-t-blue-500 border-r-transparent border-b-purple-500 border-l-transparent rounded-full animate-spin"></div>
          <p className="text-white font-medium">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center mb-8">
          <div className="bg-red-600/20 p-3 rounded-lg mr-4">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-8 w-8 text-red-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
              />
            </svg>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>
            <p className="text-gray-300">
              Manage users, applications and system settings
            </p>
          </div>
        </div>

        <div className="backdrop-blur-md bg-gray-800/50 p-8 rounded-xl border border-gray-700/50">
          <div className="text-center text-gray-400 py-12">
            <p className="text-lg mb-3">
              Admin dashboard functionality will be implemented later.
            </p>
            <p>You'll build this section yourself.</p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
