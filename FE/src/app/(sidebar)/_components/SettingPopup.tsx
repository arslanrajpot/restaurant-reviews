"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function SettingPopup({ anchorRef, onClose }: { anchorRef: React.RefObject<HTMLElement | null>; onClose: () => void }) {
  const router = useRouter();
  const [position, setPosition] = useState({ top: 0, left: 0 });

  useEffect(() => {
    if (anchorRef.current) {
      const rect = anchorRef.current.getBoundingClientRect();
      setPosition({
        top: rect.top + window.scrollY,
        left: rect.right + 10,
      });
    }

    const handleClickOutside = (e: MouseEvent) => {
      if (!anchorRef.current?.contains(e.target as Node)) {
        onClose();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [anchorRef, onClose]);

  return (
    <div
      className="absolute z-50 bg-white border rounded-md shadow-lg p-4 w-64"
      style={{ top: position.top, left: position.left }}
    >
      <div className="flex flex-col gap-3">
        <button
          onClick={() => router.push("/setting/change_password")}
          className="flex items-center gap-2 px-3 py-2 hover:bg-gray-200 rounded-lg transition text-left"
        >
          Change Password
        </button>
        <button
          onClick={() => router.push("/setting/billing_details")}
          className="flex items-center gap-2 px-3 py-2 hover:bg-gray-200 rounded-lg transition text-left"
        >
          Billing Details
        </button>
      </div>
    </div>
  );
}
