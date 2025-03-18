"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import LogoutButton from "@/components/LogoutButton";

export default function AdminDashboard() {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === "loading") return;
    if (!session) {
      router.push("/login");
    } else if (session.user.role !== "admin") {
      router.push("/user-dashboard"); // Redirect non-admin users
    }
  }, [session, status, router]);

  if (!session || session.user.role !== "admin") return null;

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Admin Dashboard</h2>
      <p>Welcome, {session.user.name}!</p>
      <LogoutButton />
    </div>
  );
}
