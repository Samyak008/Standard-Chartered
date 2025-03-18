"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Link from "next/link";

export default function HomePage() {
  const { data: session } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (session) {
      if (session.user.role === "admin") {
        router.push("/admin-dashboard");
      } else {
        router.push("/user-dashboard");
      }
    }
  }, [session, router]);

  if (session) return null;

  return (
    <div className="flex flex-col items-center justify-center h-screen text-center">
      <h1 className="text-4xl font-bold">Welcome to Loanly</h1>
      <p className="mt-2 text-gray-600">Your personalized loan companion</p>
      <div className="mt-6 space-x-4">
        <Link
          href="/auth/login"
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Login
        </Link>
        <Link
          href="/auth/register"
          className="bg-green-500 text-white px-4 py-2 rounded"
        >
          Register
        </Link>
      </div>
    </div>
  );
}
