"use client";

import { useRef, useState } from "react";
import SettingPopup from "./SettingPopup";

export default function Sidebar() {
  const [showPopup, setShowPopup] = useState(false);
  const settingsRef = useRef<HTMLButtonElement | null>(null);

  return (
    <div className="relative h-full bg-gray-100 p-4 space-y-4">
      <button
        ref={settingsRef}
        onClick={() => setShowPopup((prev) => !prev)}
        className="flex items-center gap-2 px-3 py-2 hover:bg-gray-200 rounded-lg transition"
      >
        <span className="material-icons">settings</span>
        <span>Settings</span>
      </button>
      {showPopup && (
        <SettingPopup anchorRef={settingsRef as React.RefObject<HTMLElement>} onClose={() => setShowPopup(false)} />
      )}
    </div>
  );
}
