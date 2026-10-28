"use client";

import { useState, useEffect } from "react";
import { get_faqs } from "@/service/api";
import { FAQNode } from "@/types/api";

interface Props {
  onQuestionClick: (question: string, faqId: number) => void;
}

const FAQQuestions = ({ onQuestionClick }: Props) => {
  const [faqs, setFaqs] = useState<FAQNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    const fetchFAQs = async () => {
      try {
        setLoading(true);
        const data = await get_faqs();
        setFaqs(data);
        setError(null);
      } catch (err) {
        console.error("Error fetching FAQs:", err);
        setError("Failed to load FAQ questions");
      } finally {
        setLoading(false);
      }
    };

    fetchFAQs();
  }, []);

  const handleQuestionClick = async (faq: FAQNode) => {
    try {
      // For parent questions, we'll use the title as the question
      // and pass the FAQ ID for specific handling
      onQuestionClick(faq.title, faq.id);
    } catch (err) {
      console.error("Error handling FAQ question:", err);
    }
  };

  if (loading) {
    return (
      <div className="w-full max-w-4xl mt-6">
        <div className="text-center text-gray-500">Loading FAQ questions...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full max-w-4xl mt-6">
        <div className="text-center text-red-500">{error}</div>
      </div>
    );
  }

  if (faqs.length === 0) {
    return null;
  }

  const displayedFaqs = showAll ? faqs : faqs.slice(0, 9);
  const hasMoreQuestions = faqs.length > 9;

  return (
    <div className="w-full max-w-full mt-4 sm:mt-6 px-2 sm:px-0">
      <h3 className="text-md font-medium text-gray-700 mb-4">Popular Questions:</h3>
      <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 sm:gap-3 ${showAll && hasMoreQuestions ? 'max-h-96 overflow-y-auto' : ''}`}>
        {displayedFaqs.map((faq) => (
          <button
            key={faq.id}
            onClick={() => handleQuestionClick(faq)}
            className="group text-left p-1 sm:p-2 lg:p-3 bg-gray-50 hover:bg-gray-100 rounded-md sm:rounded-lg border border-gray-200 transition-colors duration-200 hover:border-gray-300 text-[11px] sm:text-xs lg:text-sm"
          >
            <div className="font-medium text-gray-800 group-hover:text-gray-1000 text-[11px] sm:text-xs lg:text-sm leading-snug">
              {faq.title}
            </div>
          </button>
        ))}
      </div>
      {hasMoreQuestions && !showAll && (
        <div className="mt-4 text-center">
          <button
            onClick={() => setShowAll(true)}
            className="text-gray-600 hover:text-[var(--button-theme)] text-sm font-medium underline"
          >
            Show more
          </button>
        </div>
      )}
    </div>
  );
};

export default FAQQuestions;
