"use client";

import React, { useState } from "react";
import { IoEyeOff, IoEye } from "react-icons/io5";
import { useRouter } from "next/navigation";
import {login} from "@/service/api";
import Logo from "@/components/Logo";

export default function LoginForm() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [errors, setErrors] = useState({
    email: "",
    password: "",
    both: "",
  });
  const [isButtonDisabled, setIsButtonDisabled] = useState(false);


  const [showPassword, setShowPassword] = useState(false);

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
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const newErrors = {email: "", password: "", both: ""};

    if (!formData.email.trim()) {
      newErrors.email = "Email field is required";
    }
    if (!formData.password.trim()) {
      newErrors.password = "Password field is required";
    }

    if (newErrors.email || newErrors.password) {
      setErrors(newErrors);
      return;
    }
    try {
      setIsButtonDisabled(true);
      await login(formData.email, formData.password);
      router.push("/review_agent")

    } catch (err) {
      newErrors.both = (err as Error).message || "Invalid credentials. Please try again.";
      setErrors(newErrors);
      setIsButtonDisabled(false);
      return;
    }
    setIsButtonDisabled(false);

  };

  return (
    <div className="w-full lg:w-2/3 h-full flex justify-center bg-white flex-col px-6 sm:px-10 md:px-16 lg:pl-20 py-12">
  <div className="w-full max-w-lg space-y-6 mx-auto lg:mx-0">
    <div className="flex justify-center items-center">
      <Logo className="w-50" />
    </div>
    <h2 className="text-2xl text-gray-900">Login</h2>
    <p className="text-gray-600">Enter your credentials to login.</p>
    {errors.both && <p className="text-red-500 text-sm mt-1">{errors.both}</p>}
        <form onSubmit={handleSubmit}>
          <div>
            <label className="block text-gray-700">Email</label>
            <input
              type="email"
              className={`outline-[var(--button-theme)]/40 w-full p-2 mt-1 text-black border rounded-md focus:ring ${
                errors.email ? "border-red-500 bg-red-100 focus:ring-red-300" : "border-gray-300 focus:ring-blue-300"
              }`}
              placeholder="Enter your email"
              name="email"
              value={formData.email}
              onChange={handleChange}
            />
            {errors.email ? <p className="text-red-500 text-sm mt-1">{errors.email}</p> : <p className="invisible">Error</p>}
          </div>

          <div className="mt-1">
            <label className="block text-gray-700">Password</label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                className={`outline-[var(--button-theme)]/40 w-full p-2 mt-1 text-black border rounded-md focus:ring pr-10 ${
                  errors.password ? "border-red-500 bg-red-100 focus:ring-red-300" : "border-gray-300 focus:ring-blue-300"
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

          <div className="text-right text-[var(--button-theme)] mt-[-15px]">
            <a href="/forget_password" className="text-sm">
              Forgot password?
            </a>
          </div>

          <button
              className="w-full p-2 mt-10 bg-[var(--button-theme)] text-white rounded-full hover:bg-[var(--button-theme)]/80 cursor-pointer disabled:bg-gray-300 disabled:cursor-not-allowed"
              disabled={isButtonDisabled}
          >
            Login
          </button>
        </form>

        <p className="text-center text-gray-600">
          Don&apos;t have an account?<span> </span>
          <a href="/signup" className="text-[var(--button-theme)]">Sign Up</a>
        </p>
      </div>
    </div>
  );
}
