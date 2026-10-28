'use client';

import React, { useState } from "react";
import {forget_password} from "@/service/api";
import {useRouter} from "next/navigation";
import Logo from "@/components/Logo";


export default function ForgetPasswordForm() {
  const [formData, setFormData] = useState({
    email: "",
  });
  const [errors, setErrors] = useState('');
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const router = useRouter();
  const [isButtonDisabled, setIsButtonDisabled] = useState(false);


  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      if (formData.email.trim() == '') {
          setErrors("Email field is required");
          return;
      }
      try {
          setIsButtonDisabled(true);
          await forget_password(formData.email);
          setShowModal(true);
      } catch (err) {
          setError((err as Error).message || "Invalid credentials. Please try again.");
          setIsButtonDisabled(false);
          return;
      }
      setIsButtonDisabled(false);
      setError('');
      setErrors('');
  };

  return (
      <>
          {showModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
              <div className="bg-white rounded-xl shadow-lg max-w-sm w-full p-8 text-center">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">Reset Link Sent</h2>
                <p className="text-gray-600 mb-6">
                  A password reset email has been sent to <strong>{formData.email}</strong>. Please check your inbox and follow the instructions to reset your password.
                </p>
                <button
                  onClick={() => router.push("/login")}
                  className="w-full mt-2 p-2 bg-[var(--button-theme)] text-white rounded-full hover:bg-[var(--button-theme)]/80"
                >
                  Go to Login
                </button>
              </div>
            </div>
          )}
          <div className="w-full lg:w-2/3 h-full flex justify-center bg-white flex-col px-6 sm:px-10 md:px-16 lg:pl-20 py-12">
              <div className="w-full max-w-lg space-y-6">
                  <div className="flex justify-center items-center">
                    <Logo className="w-50" />
              </div>
              <h2 className="text-2xl text-gray-900">
                Forget Password?
              </h2>
              <p className="text-gray-600">Enter your registered email address to receive password reset instructions</p>
              {error && <p className="text-red-500 text-sm mt-1">{error}</p>}

              <form onSubmit={handleSubmit}>
                <div>
                  <label className="block text-gray-700">Email</label>
                  <input
                    type="email"
                    className={`outline-[var(--button-theme)]/40 w-full p-2 mt-1 text-black border rounded-md focus:ring ${
                    errors ? "border-red-500 bg-red-100 focus:ring-red-300" : "border-gray-300 focus:ring-[var(--button-theme)]/30"
                    }`}
                    placeholder="Enter your email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                  />
                    {errors ? <p className="text-red-500 text-sm mt-1">{errors}</p> : <p className="invisible">Error</p>}
                </div>

                <button disabled={isButtonDisabled} className="w-full mt-8 p-2 bg-[var(--button-theme)] text-white rounded-full hover:bg-[var(--button-theme)]/80 cursor-pointer disabled:bg-gray-300 disabled:cursor-not-allowed">
                  Send Reset Instructions
                </button>
              </form>


              <p className="text-center text-gray-600">
                Don&apos;t have an account?<span> </span>
                <a href="/signup" className="text-[var(--button-theme)]">
                  Create Account
                </a>
              </p>
            </div>
          </div>
      </>
  );
}
