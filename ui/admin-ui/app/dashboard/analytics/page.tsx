// src/app/dashboard/analytics/page.tsx

import DashboardLayout from "@/components/layouts/DashboardLayout";

export default function AnalyticsPage() {
  return (
    <DashboardLayout>
      <div className="p-6">
        <h2 className="text-3xl font-bold mb-4">Analytics</h2>
        <p className="text-gray-700 mb-6">
          Overview of system performance and usage metrics.
        </p>

        {/* Placeholder for analytics charts and metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-4 rounded shadow">
            <h3 className="text-xl font-semibold mb-2">User Activity</h3>
            <p className="text-gray-600">
              Chart or data visualization goes here.
            </p>
          </div>
          <div className="bg-white p-4 rounded shadow">
            <h3 className="text-xl font-semibold mb-2">System Performance</h3>
            <p className="text-gray-600">
              Chart or data visualization goes here.
            </p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
