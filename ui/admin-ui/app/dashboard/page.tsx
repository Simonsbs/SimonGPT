// src/app/dashboard/page.tsx

import DashboardLayout from "@/components/layouts/DashboardLayout";

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="flex min-h-screen flex-col items-center justify-center bg-gray-100 p-8">
        <h1 className="text-4xl font-bold mb-4">
          Welcome to the Admin Dashboard
        </h1>
        <p className="text-lg text-gray-700">
          This is your central hub for managing and monitoring the system.
        </p>
      </div>
    </DashboardLayout>
  );
}
