"use client";

import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { useSession, signOut } from "next-auth/react";

export default function DashboardLayout({ children }) {
  const { data: session } = useSession();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const pathname = usePathname();

  // Close mobile menu when route changes
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [pathname]);

  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-purple-950 to-slate-900">
      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <button
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="p-2 rounded-lg bg-gray-800/70 backdrop-blur-sm border border-gray-700/50 text-white"
        >
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
              d={
                isMobileMenuOpen
                  ? "M6 18L18 6M6 6l12 12"
                  : "M4 6h16M4 12h16M4 18h16"
              }
            />
          </svg>
        </button>
      </div>

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 transform ${
          isMobileMenuOpen ? "translate-x-0" : "-translate-x-full"
        } lg:translate-x-0 transition duration-300 ease-in-out z-40 w-64 bg-gray-900/80 backdrop-blur-xl border-r border-gray-800/50 flex flex-col`}
      >
        {/* Logo */}
        <div className="p-6 border-b border-gray-800/50">
          <div className="flex items-center">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-blue-500 to-purple-600 flex items-center justify-center shadow-lg mr-3">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6 text-white"
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
            <h1 className="text-xl font-bold text-white">Standard Chartered</h1>
          </div>
        </div>

        {/* User profile summary */}
        <div className="p-6 border-b border-gray-800/50">
          <div className="flex items-center mb-4">
            <div className="w-10 h-10 rounded-full bg-blue-600/30 flex items-center justify-center text-blue-300 font-semibold mr-3">
              {session?.user?.name?.charAt(0) || "U"}
            </div>
            <div>
              <p className="text-white font-medium">
                {session?.user?.name || "User"}
              </p>
              <p className="text-gray-400 text-sm">
                {session?.user?.email || ""}
              </p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          <Link
            href="/user-dashboard"
            className={`flex items-center px-4 py-3 rounded-lg transition-all ${
              pathname === "/user-dashboard"
                ? "bg-blue-600/20 text-blue-300 border-l-4 border-blue-500"
                : "text-gray-300 hover:bg-gray-800/70"
            }`}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 mr-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
              />
            </svg>
            Dashboard
          </Link>

          <Link
            href="/user-dashboard/kyc"
            className={`flex items-center px-4 py-3 rounded-lg transition-all ${
              pathname === "/user-dashboard/kyc"
                ? "bg-blue-600/20 text-blue-300 border-l-4 border-blue-500"
                : "text-gray-300 hover:bg-gray-800/70"
            }`}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 mr-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2"
              />
            </svg>
            KYC Verification
          </Link>

          <Link
            href="/user-dashboard/loan"
            className={`flex items-center px-4 py-3 rounded-lg transition-all ${
              pathname === "/user-dashboard/loan"
                ? "bg-blue-600/20 text-blue-300 border-l-4 border-blue-500"
                : "text-gray-300 hover:bg-gray-800/70"
            }`}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 mr-3"
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
            Loan Eligibility
          </Link>

          <div className="pt-4 mt-4 border-t border-gray-800/50">
            <button
              onClick={() => signOut({ callbackUrl: "/auth/login" })}
              className="flex w-full items-center px-4 py-3 rounded-lg text-gray-300 hover:bg-red-900/20 hover:text-red-300 transition-all"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 mr-3"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
              Sign Out
            </button>
          </div>
        </nav>
      </div>

      {/* Main content */}
      <div className="lg:ml-64 min-h-screen">
        <div className="p-6 md:p-10">{children}</div>
      </div>
    </div>
  );
}
