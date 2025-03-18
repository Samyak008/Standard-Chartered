"use client";

import { useState } from "react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";

export default function AuthForm({ type }) {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    role: "user",
  });
  const [error, setError] = useState(null);
  const router = useRouter();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (type === "register") {
      // Registration logic
      const res = await fetch("/api/auth/register", {
        method: "POST",
        body: JSON.stringify(formData),
        headers: { "Content-Type": "application/json" },
      });

      if (!res.ok) {
        setError((await res.json()).message);
        return;
      }
    }

    // Login logic
    const result = await signIn("credentials", {
      email: formData.email,
      password: formData.password,
      redirect: false,
    });

    if (result.error) {
      setError(result.error);
      return;
    }

    router.push("/dashboard");
  };

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">
        {type === "login" ? "Login" : "Register"}
      </h2>
      {error && <p className="text-red-500">{error}</p>}
      <form onSubmit={handleSubmit} className="flex flex-col space-y-4">
        {type === "register" && (
          <input
            type="text"
            name="name"
            placeholder="Full Name"
            required
            onChange={handleChange}
            className="p-2 border rounded"
          />
        )}
        <input
          type="email"
          name="email"
          placeholder="Email"
          required
          onChange={handleChange}
          className="p-2 border rounded"
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          required
          onChange={handleChange}
          className="p-2 border rounded"
        />
        {type === "register" && (
          <select
            name="role"
            onChange={handleChange}
            className="p-2 border rounded"
          >
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
        )}
        <button type="submit" className="bg-blue-500 text-white p-2 rounded">
          {type === "login" ? "Login" : "Register"}
        </button>
      </form>
    </div>
  );
}
