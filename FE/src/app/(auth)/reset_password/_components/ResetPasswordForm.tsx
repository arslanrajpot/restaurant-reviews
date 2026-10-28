"use client";

import React, { useState } from "react";
import { IoEyeOff, IoEye } from "react-icons/io5";
import {useRouter, useSearchParams} from "next/navigation";
import {reset_password} from "@/service/api";
import Logo from "@/components/Logo";

export default function ResetPasswordForm() {
  const [formData, setFormData] = useState({
    password: "",
    confirmed_password: "",
  });
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [errors, setErrors] = useState({
    password: "",
    confirmed_password: "",
  });
  const [error, setError] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmedPassword, setShowConfirmedPassword] = useState(false);

  const passwordLengthValid = formData.password.length >= 6 && formData.password.length <= 20;
  const passwordUppercaseValid = /[A-Z]/.test(formData.password);
  const passwordLowercaseValid = /[a-z]/.test(formData.password);
  const [isButtonDisabled, setIsButtonDisabled] = useState(false);
  const passwordNumberValid = /\d/.test(formData.password);
  const passwordSpecialCharValid = /[@$!%*?&]/.test(formData.password);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    setErrors((prev) => ({
      ...prev,
      [name]: "",
    }));
  };
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const newErrors = {password: "", confirmed_password: ""};

    if (!formData.password.trim()) {
      newErrors.password = "This field is required";
    } else if (
        !passwordLengthValid ||
        !passwordUppercaseValid ||
        !passwordLowercaseValid ||
        !passwordNumberValid ||
        !passwordSpecialCharValid
    ) {
      return
    }

    if (!formData.confirmed_password.trim()) {
      newErrors.confirmed_password = "This field is required";
    } else if (formData.password !== formData.confirmed_password) {
      newErrors.confirmed_password = "Passwords do not match";
    }

    if (newErrors.password || newErrors.confirmed_password) {
      setErrors(newErrors);
      return;
    }
    try {
      setIsButtonDisabled(true);
      await reset_password(token || "", formData.password);
      router.push('/login');
    } catch (err) {
      setError((err as Error).message || "Invalid credentials. Please try again.");
      setIsButtonDisabled(false);
      return;
    }
    setIsButtonDisabled(false);
    setError('');
    setErrors({password: "", confirmed_password: ""});
  };

  return (
    <div className="w-full lg:w-2/3 h-full flex justify-center bg-white flex-col px-6 sm:px-10 md:px-16 lg:pl-20 py-12">
      <div className="w-full max-w-lg space-y-6">
        <div className="flex justify-center items-center">
            <Logo className="w-50" />
        </div>
        <h2 className="text-2xl text-gray-900">Reset your password</h2>
        <p className="text-gray-600">Enter a new password to reset your account.</p>
        {error && <p className="text-red-500 text-sm mt-1">{error}</p>}

        <form onSubmit={handleSubmit}>
          <div>
            <label className="block text-gray-700">Password</label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                className={`outline-[var(--button-theme)]/40 w-full p-2 mt-1 text-black border rounded-md focus:ring pr-10 ${
                  errors.password ? "border-red-500 bg-red-100 focus:ring-red-300" : "border-gray-300 focus:ring-[var(--button-theme)]/30"
                }`}
                placeholder="Enter your password"
                value={formData.password}
                onChange={handleChange}
              />
              <button
                type="button"
                className="absolute top-3 right-2 text-gray-500 cursor-pointer"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <IoEyeOff className="text-2xl" /> : <IoEye className="text-2xl" />}
              </button>
            </div>
            {errors.password ? <p className="text-red-500 text-sm mt-1">{errors.password}</p> : <p className="invisible">Error</p>}
          </div>
          {formData.password && (
            <ul className="list-disc ml-5 mb-4 mt-[-10px] text-sm">
              <li className={`${passwordLengthValid ? "text-green-500" : "text-red-500"}`}>
                Password should be 6 to 20 characters long.
              </li>
              <li className={`${passwordUppercaseValid && passwordLowercaseValid && passwordNumberValid ? "text-green-500" : "text-red-500"}`}>
                At least one digit, uppercase & lowercase letter.
              </li>
              <li className={`${passwordSpecialCharValid ? "text-green-500" : "text-red-500"}`}>
                At least one special character (@, $, !, %, *, ?, &).
              </li>
            </ul>
          )}


          <div>
            <label className="block text-gray-700 mt-2">Confirm Password</label>
            <div className="relative">
              <input
                type={showConfirmedPassword ? "text" : "password"}
                name="confirmed_password"
                className={`outline-[var(--button-theme)]/40 w-full p-2 mt-1 text-black border rounded-md focus:ring pr-10 ${
                  errors.confirmed_password ? "border-red-500 bg-red-100 focus:ring-red-300" : "border-gray-300 focus:ring-[var(--button-theme)]/30"
                }`}
                placeholder="Confirm your password"
                value={formData.confirmed_password}
                onChange={handleChange}
              />
              <button
                type="button"
                className="absolute top-3 right-2 text-gray-500 cursor-pointer"
                onClick={() => setShowConfirmedPassword(!showConfirmedPassword)}
              >
                {showConfirmedPassword ? <IoEyeOff className="text-2xl" /> : <IoEye className="text-2xl" />}
              </button>
            </div>
            {errors.confirmed_password ? <p className="text-red-500 text-sm mt-1">{errors.confirmed_password}</p> : <p className="invisible">Error</p>}
          </div>

          {/* Reset Button */}
          <button
              className={`w-full mt-10 p-2 rounded-full mt-10 ${
                !token || isButtonDisabled
                  ? "bg-gray-300 text-gray-400 cursor-not-allowed"
                  : "bg-[var(--button-theme)] text-white hover:bg-[var(--button-theme)]/80"
              }`}
              disabled={!token || isButtonDisabled}
          >
            Reset Password
          </button>
        </form>

        {/* Signup Link */}
        <p className="text-center text-gray-600">
          Don&apos;t have an account? <span> </span>
          <a href="/signup" className="text-[var(--button-theme)]">Sign Up</a>
        </p>
      </div>
    </div>
  );
}
