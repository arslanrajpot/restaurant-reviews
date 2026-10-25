"use client";

import { useState } from "react";
import { IoEyeOff, IoEye } from "react-icons/io5";
import { change_password } from "@/service/api";

export default function ChangePasswordPage() {
  const [formData, setFormData] = useState({
    old_password: "",
    new_password: "",
  });
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  const [showOld, setShowOld] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [isButtonDisabled, setIsButtonDisabled] = useState<boolean>(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const isFormValid = Object.entries(formData).every(([, val]) => val.trim() !== "");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSave = async () => {
    if (!isFormValid || !confirmPassword) return;

    if (formData.old_password === formData.new_password) {
      setError("New password and old password should not match");
      return;
    }

    if (formData.new_password !== confirmPassword) {
      setError("New password and confirm password do not match");
      return;
    }

    try {
      setIsButtonDisabled(true);
      await change_password(formData);
      alert("Password updated successfully!");
      setFormData({ old_password: "", new_password: "" });
      setConfirmPassword("");
      setError("");
      setIsButtonDisabled(false);
    } catch (err) {
      setError((err as Error).message || "An unexpected error occurred");
      setIsButtonDisabled(false);
    }
  };

  return (
    <div className="w-full h-[77vh] mx-auto p-6 pt-1 overflow-scroll flex flex-col items-center justify-center">
      <div className="mb-6 shadow-lg p-6 pt-0 w-full max-w-xl">
        <h3 className="text-lg font-semibold text-black mb-3 text-center">Change Password</h3>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded mb-4">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        <div className="space-y-6">
          {/* Old Password */}
          <div className="flex flex-col relative">
            <label className="block text-gray-700 text-left mb-1">Old Password</label>
            <input
              type={showOld ? "text" : "password"}
              name="old_password"
              value={formData.old_password}
              onChange={handleChange}
              className="w-full p-3 border text-black/70 border-gray-300 rounded-md outline-[#A57C00]/40 pr-10"
            />
            <button
              type="button"
              className="absolute right-3 top-11 text-gray-500"
              onClick={() => setShowOld(!showOld)}
            >
              {showOld ? <IoEyeOff className="text-xl" /> : <IoEye className="text-xl" />}
            </button>
          </div>

          {/* New Password */}
          <div className="flex flex-col relative">
            <label className="block text-gray-700 text-left mb-1">New Password</label>
            <input
              type={showNew ? "text" : "password"}
              name="new_password"
              value={formData.new_password}
              onChange={handleChange}
              className="w-full p-3 border text-black/70 border-gray-300 rounded-md outline-[#A57C00]/40 pr-10"
            />
            <button
              type="button"
              className="absolute right-3 top-11 text-gray-500"
              onClick={() => setShowNew(!showNew)}
            >
              {showNew ? <IoEyeOff className="text-xl" /> : <IoEye className="text-xl" />}
            </button>
          </div>

          {/* Confirm Password */}
          <div className="flex flex-col relative">
            <label className="block text-gray-700 text-left mb-1">Confirm New Password</label>
            <input
              type={showConfirm ? "text" : "password"}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full p-3 border text-black/70 border-gray-300 rounded-md outline-[#A57C00]/40 pr-10"
            />
            <button
              type="button"
              className="absolute right-3 top-11 text-gray-500"
              onClick={() => setShowConfirm(!showConfirm)}
            >
              {showConfirm ? <IoEyeOff className="text-xl" /> : <IoEye className="text-xl" />}
            </button>
          </div>
        </div>
      </div>

      <div className="flex justify-end gap-3 mt-4">
        <button
          onClick={handleSave}
          className={`px-6 py-3 rounded-md font-semibold text-white transition ${
            (isFormValid && confirmPassword) || !isButtonDisabled
              ? "bg-[#A57C00] hover:bg-[#A57C00]/70"
              : "bg-gray-400 cursor-not-allowed"
          }`}
          disabled={!isFormValid || !confirmPassword || isButtonDisabled}
        >
          Submit
        </button>
      </div>
    </div>
  );
}
