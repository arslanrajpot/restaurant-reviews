"use client";

import { useRouter } from "next/navigation";

export default function Setting() {
  const router = useRouter();

  return (
    <div className="flex flex-col bg-white rounded-lg shadow-lg p-4 min-w-[250px]">
      <button
        onClick={() => router.push("/setting/change_password")}
        className="text-left hover:bg-gray-100 px-3 py-2 rounded-md font-medium"
      >
        Change Password
      </button>
      <button
        onClick={() => router.push("/setting/billing_details")}
        className="text-left hover:bg-gray-100 px-3 py-2 rounded-md font-medium"
      >
        Billing Details
      </button>
    </div>
  );
}
