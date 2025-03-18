"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import LogoutButton from "@/components/LogoutButton";

export default function UserDashboard() {
  const { data: session, status } = useSession();
  const router = useRouter();

  // Redirect if not authenticated
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  // Show loading state while checking authentication
  if (status === "loading") {
    return (
      <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
        <p>Loading...</p>
      </div>
    );
  }

  // Check for session before rendering content
  if (!session) {
    return null;
  }

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">User Dashboard</h2>
      <p>Welcome, {session.user?.name || "User"}!</p>
      <LogoutButton />
    </div>
  );
}
