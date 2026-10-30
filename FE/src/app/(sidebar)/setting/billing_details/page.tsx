"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { get_billing_details, cancel_subscription, get_subscription_status } from "@/service/api";
import Loader from "@/shared/loader";

interface LatestPaidInvoice {
  invoice_number?: string;
  amount_paid: number;
  currency: string;
  status: string;
  description?: string;
  payment_method?: string;
  paid_at?: number | null;
  next_billing_date?: number;
}

function formatDate(ts?: number | null) {
  if (!ts) return "-";
  
  const date = new Date(ts * 1000);
  const day = date.getDate();
  const month = date.toLocaleString('en-US', { month: 'long' });
  const year = date.getFullYear();
  const time = date.toLocaleString('en-US', { 
    hour: 'numeric', 
    minute: '2-digit',
    hour12: true 
  });
  
  return `${day} ${month} ${year}, ${time}`;
}

export default function BillingDetailsPage() {
  const router = useRouter();
  const [invoice, setInvoice] = useState<LatestPaidInvoice | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [noSubscription, setNoSubscription] = useState(false);
  const [cancelLoading, setCancelLoading] = useState(false);
  const [showPopup, setShowPopup] = useState(false);
  const [popupMessage, setPopupMessage] = useState<string | null>(null);
  const [popupType, setPopupType] = useState<"success" | "error" | null>(null);
  const [alreadyCancelled, setAlreadyCancelled] = useState(false);
  const [cancelStatusLoading, setCancelStatusLoading] = useState(true);

  useEffect(() => {
    get_billing_details()
      .then((data) => setInvoice(data.latest_paid_invoice))
      .catch((err) => {
        if (err?.status === 404) {
          setNoSubscription(true);
        } else {
          setError(err.message || err);
        }
      })
      .finally(() => setLoading(false));
    // Use the new status endpoint
    get_subscription_status()
      .then((res) => {
        if (res.status === "cancelled") {
          setAlreadyCancelled(true);
        }
      })
      .catch(() => {})
      .finally(() => setCancelStatusLoading(false));
  }, []);

  useEffect(() => {
    if (showPopup) {
      const timer = setTimeout(() => setShowPopup(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [showPopup]);

  const handleCancel = async () => {
    setCancelLoading(true);
    try {
      const res = await cancel_subscription();
      setPopupMessage(res.message || "Subscription cancellation requested.");
      setPopupType("success");
      setShowPopup(true);
    } catch (err: unknown) {
      let message = "Failed to cancel subscription.";
      if (
        err &&
        typeof err === "object" &&
        "message" in err &&
        typeof (err as { message?: unknown }).message === "string"
      ) {
        message = (err as { message: string }).message;
      }
      setPopupMessage(message);
      setPopupType("error");
      setShowPopup(true);
    } finally {
      setCancelLoading(false);
    }
  };

  if (loading || cancelStatusLoading) {
    return (
      <div className="absolute inset-0 bg-white/80 backdrop-blur-sm rounded-lg flex items-center justify-center z-10">
        <div className="flex flex-col items-center">
          <Loader />
          <p className="text-sm text-gray-500 mt-1">
            Please wait while we fetch your billing information
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full px-20 py-12">
      {showPopup && popupMessage && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
          <div className="relative w-full max-w-lg bg-white rounded-2xl shadow-2xl p-8 flex flex-col items-center">
            <button
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-700 text-2xl"
              onClick={() => setShowPopup(false)}
              aria-label="Close"
            >
              &times;
            </button>
            <div className="mb-4">
              {popupType === "success" ? (
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="text-green-600 text-3xl">✓</span>
                </div>
              ) : (
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                  <span className="text-red-600 text-3xl">✕</span>
                </div>
              )}
            </div>
            <div className="text-center text-lg font-medium text-gray-800">
              {popupMessage}
            </div>
          </div>
        </div>
      )}
    
      {noSubscription && (
        <div className="flex justify-center">
          <div className="w-full max-w-lg bg-white rounded-xl shadow-md p-10 text-center">
            <h1 className="text-2xl font-bold mb-3">You&apos;re on the Free plan</h1>
            <p className="text-gray-600 mb-8">
              There&apos;s no billing history to show yet. Upgrade to a paid plan to unlock more features.
            </p>
            <button
              onClick={() => router.push("/subscription")}
              className="px-6 py-2 bg-[var(--button-theme)] text-white font-medium rounded-full hover:bg-[var(--button-theme)]/80"
            >
              View Plans
            </button>
          </div>
        </div>
      )}
      {error && !noSubscription && <div className="text-red-500">Error: {error}</div>}
      {!loading && !error && !noSubscription && invoice && (
        <>
          <div className="flex justify-center">
            <div className="w-full max-w-4xl bg-white rounded-xl shadow-md p-10">
              <h1 className="text-3xl font-bold mb-8 text-center">
                Billing Details
              </h1>

              <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-12 gap-y-6 text-gray-700">
                <div>
                  <dt className="font-semibold">Invoice Number:</dt>
                  <dd>{invoice.invoice_number || "-"}</dd>
                </div>
                <div>
                  <dt className="font-semibold">Amount Paid:</dt>
                  <dd>
                    {(invoice.amount_paid / 100).toFixed(2)}{" "}
                    {invoice.currency.toUpperCase()}
                  </dd>
                </div>

                <div>
                  <dt className="font-semibold">Status:</dt>
                  <dd
                    className={
                      invoice.status === "paid"
                        ? "text-yellow-700"
                        : "text-red-600"
                    }
                  >
                    {invoice.status}
                  </dd>
                </div>
                <div>
                  <dt className="font-semibold">Description:</dt>
                  <dd>{invoice.description || "-"}</dd>
                </div>

                <div>
                  <dt className="font-semibold">Payment Method:</dt>
                  <dd>{invoice.payment_method || "-"}</dd>
                </div>
                <div>
                  <dt className="font-semibold">Paid At:</dt>
                  <dd>{formatDate(invoice.paid_at)}</dd>
                </div>

                <div>
                  <dt className="font-semibold">Next Billing Date:</dt>
                  <dd>{formatDate(invoice.next_billing_date)}</dd>
                </div>
              </dl>

              {invoice.status === "paid" && (
                <div className="mt-10 flex justify-center">
                  <button
                    onClick={handleCancel}
                    disabled={cancelLoading || alreadyCancelled}
                    className="px-6 py-2 bg-[var(--button-theme)] text-white font-medium rounded-full hover:bg-[var(--button-theme)]/80 disabled:bg-gray-300 disabled:cursor-not-allowed"
                  >
                    {cancelLoading ? "Cancelling..." : "Cancel Subscription"}
                  </button>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
