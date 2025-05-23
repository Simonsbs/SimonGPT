// src/app/dashboard/settings/page.tsx

"use client";

import { useForm } from "react-hook-form";
import DashboardLayout from "@/components/layouts/DashboardLayout";

type SettingsFormData = {
  siteTitle: string;
  enableLogging: boolean;
  maxUsers: number;
};

export default function SettingsPage() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SettingsFormData>({
    defaultValues: {
      siteTitle: "SimonGPT",
      enableLogging: true,
      maxUsers: 100,
    },
  });

  const onSubmit = (data: SettingsFormData) => {
    // Handle form submission, e.g., send data to an API
    console.log("Settings updated:", data);
  };

  return (
    <DashboardLayout>
      <div className="p-6">
        <h2 className="text-3xl font-bold mb-4">Settings</h2>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 max-w-xl">
          {/* Site Title */}
          <div>
            <label
              htmlFor="siteTitle"
              className="block text-sm font-medium text-gray-700"
            >
              Site Title
            </label>
            <input
              id="siteTitle"
              type="text"
              {...register("siteTitle", { required: "Site title is required" })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
            {errors.siteTitle && (
              <p className="mt-1 text-sm text-red-600">
                {errors.siteTitle.message}
              </p>
            )}
          </div>

          {/* Enable Logging */}
          <div className="flex items-center">
            <input
              id="enableLogging"
              type="checkbox"
              {...register("enableLogging")}
              className="h-4 w-4 text-indigo-600 border-gray-300 rounded"
            />
            <label
              htmlFor="enableLogging"
              className="ml-2 block text-sm text-gray-700"
            >
              Enable Logging
            </label>
          </div>

          {/* Max Users */}
          <div>
            <label
              htmlFor="maxUsers"
              className="block text-sm font-medium text-gray-700"
            >
              Max Users
            </label>
            <input
              id="maxUsers"
              type="number"
              {...register("maxUsers", {
                required: "Max users is required",
                min: { value: 1, message: "Must be at least 1" },
              })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
            {errors.maxUsers && (
              <p className="mt-1 text-sm text-red-600">
                {errors.maxUsers.message}
              </p>
            )}
          </div>

          {/* Submit Button */}
          <div>
            <button
              type="submit"
              className="inline-flex items-center px-4 py-2 bg-indigo-600 border border-transparent rounded-md font-semibold text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              Save Settings
            </button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  );
}
