// src/components/layouts/DashboardLayout.tsx

"use client";

import { ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = async () => {
    try {
      const response = await fetch("/api/logout", {
        method: "GET",
      });

      if (response.redirected) {
        router.push(response.url);
      } else {
        router.push("/login");
      }
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-800 text-white flex-shrink-0">
        <div className="h-16 flex items-center justify-center border-b border-gray-700">
          <span className="text-xl font-bold">SimonGPT Admin</span>
        </div>
        <nav className="flex flex-col p-4 space-y-2">
          <Link
            href="/dashboard"
            className={`px-4 py-2 rounded hover:bg-gray-700 ${
              pathname === "/dashboard" ? "bg-gray-700" : ""
            }`}
          >
            Dashboard
          </Link>
          <Link
            href="/dashboard/analytics"
            className={`px-4 py-2 rounded hover:bg-gray-700 ${
              pathname === "/dashboard/analytics" ? "bg-gray-700" : ""
            }`}
          >
            Analytics
          </Link>
          <Link
            href="/dashboard/settings"
            className={`px-4 py-2 rounded hover:bg-gray-700 ${
              pathname === "/dashboard/settings" ? "bg-gray-700" : ""
            }`}
          >
            Settings
          </Link>
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 shadow">
          <h1 className="text-2xl font-semibold">Dashboard</h1>
          <button
            onClick={handleLogout}
            className="py-2 px-4 bg-red-600 text-white rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
          >
            Logout
          </button>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6 bg-gray-100">
          {children}
        </main>
      </div>
    </div>
  );
}
