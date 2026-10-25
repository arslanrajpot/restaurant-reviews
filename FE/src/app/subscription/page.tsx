"use client";

import React, { useState } from "react";
import Image from "next/image";
import loginImage from "@/assets/images/login_image.jpg";
import { createCheckoutSession, get_user_data } from "@/service/api";

const plans = [
  {
    name: "Pro",
    price: "£ 18",
    period: "/mo",
    features: [
      "All Pro features",
      "Advanced analytics dashboard",
      "Advanced analytics",
      "100 AI-powered review insights/month",
    ],
    id: "pro",
    popular: false,
    priceId: "price_1RoheuQPh3u6u99AxKoRNgVZ"
  },
  {
    name: "Premium",
    price: "£ 35",
    period: "/mo",
    features: [
      "All Premium features",
      "Advanced analytics dashboard",
      "Advanced analytics",
      "350 AI-powered review insights/month",
    ],
    id: "premium",
    popular: true,
    priceId: "price_1Rohn6QPh3u6u99AYY8A5SEg"
  }
];

const SubscriptionPage = () => {
  const [showSubscribedModal, setShowSubscribedModal] = useState(false);

  const handleSubscribe = async (plan: typeof plans[0]) => {
    try {
      const userData = await get_user_data() as { is_subscribed: boolean };
      if (userData.is_subscribed) {
        setShowSubscribedModal(true);
        return;
      }
      const currentUrl = window.location.origin;
      const successUrl = `${currentUrl}/subscription/success`;
      const cancelUrl = `${currentUrl}/subscription`;
      const response = await createCheckoutSession(
        plan.priceId,
        successUrl,
        cancelUrl
      );
      if (response?.url) {
        window.location.href = response.url;
      } else {
        alert("Failed to create checkout session. Please try again.");
      }
    } catch {
      alert("Failed to create checkout session. Please try again.");
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left: Image */}
      <div className="hidden md:block md:w-1/2 h-screen relative">
        <Image
          src={loginImage}
          alt="Login Visual"
          fill
          style={{ objectFit: "cover" }}
          className="rounded-r-1xl"
          priority
        />
      </div>
      {/* Right: Subscription Cards */}
      <div className="flex-1 flex flex-col justify-center items-center bg-white">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Choose Your Plan</h1>
          <p className="text-gray-600">
            Unlock the full potential of our AI-powered restaurant review assistant
          </p>
        </div>
        <div className="flex flex-col md:flex-row gap-10">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`relative bg-white rounded-2xl shadow-xl border transition-all duration-300 flex flex-col max-w-xs w-full p-8 ${
                plan.popular ? 'border-[var(--button-theme)] ring-2 ring-[var(--button-theme)]/30' : 'border-gray-200'
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-5 left-1/2 transform -translate-x-1/2">
                  <span className="bg-[var(--button-theme)] text-white px-4 py-1 rounded-full text-sm font-semibold shadow">
                    Most Popular
                  </span>
                </div>
              )}
              <div className="text-center mb-6 mt-2">
                <h2 className="text-xl font-bold text-gray-900 mb-2">{plan.name}</h2>
                <div className="flex items-baseline justify-center">
                  <span className="text-3xl font-bold text-gray-900">{plan.price}</span>
                  <span className="text-gray-600 ml-1">{plan.period}</span>
                </div>
              </div>
              <div className="flex-grow mb-6">
                <ul className="space-y-2">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-center text-gray-700 text-sm">
                      <svg className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
              <button
                onClick={() => handleSubscribe(plan)}
                className="bg-[var(--button-theme)] hover:bg-[var(--button-theme)]/80 text-white font-bold py-3 px-4 rounded-lg shadow transition-colors duration-200 mt-auto"
              >
                Subscribe Now
              </button>
            </div>
          ))}
        </div>
        {/* Modal for already subscribed */}
        {showSubscribedModal && (
          <div className="fixed inset-0 flex items-center justify-center bg-opacity-40 backdrop-blur-sm z-50">
            <div className="bg-white p-8 rounded-lg shadow-lg text-center">
              <h2 className="text-xl font-bold mb-4">Already Subscribed</h2>
              <p className="mb-4">You already have an active subscription.</p>
              <button
                className="bg-[var(--button-theme)] hover:bg-[var(--button-theme)]/80 text-white font-bold py-2 px-6 rounded-lg shadow transition-colors duration-200"
                onClick={() => setShowSubscribedModal(false)}
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SubscriptionPage; 