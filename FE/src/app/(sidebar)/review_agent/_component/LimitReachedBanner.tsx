"use client";

import { useRouter } from "next/navigation";

interface Props {
  message: string;
  onClose: () => void;
}

const LimitReachedBanner = ({ message, onClose }: Props) => {
  const router = useRouter();

  return (
    <div className="fixed top-40 right-8 z-50 flex flex-col gap-3 px-4 py-3 bg-red-100 border border-red-300 text-red-800 rounded-lg shadow-lg max-w-sm animate-fade-in">
      <div className="flex items-start gap-2">
        <svg className="w-5 h-5 text-red-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M21 12A9 9 0 1 1 3 12a9 9 0 0 1 18 0z" />
        </svg>
        <span className="font-medium text-sm">{message}</span>
      </div>
      <div className="flex gap-2 justify-end">
        <button
          onClick={onClose}
          className="text-xs px-3 py-1.5 rounded-md text-red-700 hover:bg-red-200"
        >
          Dismiss
        </button>
        <button
          onClick={() => router.push("/subscription")}
          className="text-xs px-3 py-1.5 rounded-md bg-[var(--button-theme)] text-white hover:bg-[var(--button-theme)]/80"
        >
          Subscribe
        </button>
      </div>
    </div>
  );
};

export default LimitReachedBanner;
