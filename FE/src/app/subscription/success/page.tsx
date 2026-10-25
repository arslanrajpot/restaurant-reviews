"use client";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import Loader from "@/shared/loader";
import { BASE_API_URL } from "@/service/api";
import { useRouter } from "next/navigation";
import { Suspense } from "react";

type PaymentDetails = {
  success: boolean;
  subscription_status?: string;
  payment_method?: string;
  amount?: number;
  payment_status?: string;
  error?: string;
};

export default function SuccessPage() {
  return (
    <Suspense fallback={<Loader />}>
      <SuccessPageContent />
    </Suspense>
  );
}

function SuccessPageContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session_id");
  const [details, setDetails] = useState<PaymentDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    if (!sessionId) {
      setLoading(false);
      return;
    }
    if (sessionId) {
      fetch(`${BASE_API_URL}stripe/success?session_id=${encodeURIComponent(sessionId)}`)
        .then(res => res.json())
        .then(data => {
          setDetails(data);
          setLoading(false);
        })
        .catch(() => {
          setDetails({ success: false, error: "Failed to fetch payment details." });
          setLoading(false);
        });
    }
  }, [sessionId]);

  useEffect(() => {
    if (details && details.success) {
      const timer = setTimeout(() => {
        router.push("/login");
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [details, router]);

  if (loading) return <Loader />;

  if (!details) return <div className="flex flex-col items-center justify-center h-[70vh]"><p className="text-red-500">No payment details found.</p></div>;

  if (!details.success) {
    return (
      <div className="flex flex-col items-center justify-center h-[70vh]">
        <div className="bg-white shadow-lg rounded-lg p-8 text-center">
          <h1 className="text-3xl font-bold text-red-600 mb-4">Payment Failed</h1>
          <p className="text-lg mb-2">{details.error || "Your payment could not be verified."}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center h-[80vh] bg-gradient-to-br">
      <div className="bg-white shadow-2xl rounded-2xl p-10 max-w-md w-full text-center animate-fade-in">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-green-600 text-3xl">✓</span>
        </div>
        <h1 className="text-3xl font-extrabold mb-2" style={{ color: 'var(--button-theme)' }}>Payment Successful!</h1>
        <p className="mb-4 text-gray-700">Thank you for your payment.</p>
        <ul className="text-lg text-left mx-auto inline-block mb-4">
          <li className="mb-1"><span className="font-semibold text-gray-800">Subscription Status:</span> <span style={{ color: 'var(--button-theme)' }}>{details.subscription_status}</span></li>
          <li className="mb-1"><span className="font-semibold text-gray-800">Payment Method:</span> {details.payment_method}</li>
          <li className="mb-1"><span className="font-semibold text-gray-800">Amount:</span> {details.amount ? (details.amount / 100).toFixed(2) : "N/A"} {details.amount ? "£" : ""}</li>
          <li><span className="font-semibold text-gray-800">Payment Status:</span> <span style={{ color: 'var(--button-theme)' }}>{details.payment_status}</span></li>
        </ul>
        <div className="mt-4">
          <a href="/dashboard" className="inline-block bg-[var(--button-theme)] hover:bg-[var(--button-theme)]/80 text-white font-bold py-2 px-6 rounded-lg shadow transition-colors duration-200">Go to Dashboard</a>
        </div>
      </div>
    </div>
  );
}