"use client";

import { useState } from "react";
import { FAQNode } from "@/types/api";

interface Props {
  items: FAQNode[];
  onChildQuestionClick: (question: string, faqId: number) => void;
}

const ChildQuestions = ({ items, onChildQuestionClick }: Props) => {
  const [showAll, setShowAll] = useState(false);

  if (!items || items.length === 0) {
    return null;
  }

  const displayedChildren = showAll ? items : items.slice(0, 3);
  const hasMoreQuestions = items.length > 3;

  const truncateWords = (text: string, count: number) => {
    const words = text.trim().split(/\s+/);
    if (words.length <= count) return text;
    return words.slice(0, count).join(" ") + "...";
  };

  return (
    <div className="mt-4 p-4 rounded-lg border" style={{ backgroundColor: '#F4F8F9', borderColor: '#D8E6E8' }}>

      {/* Row with arrow aligned to the right */}
      <div className="flex items-center">
        <div
          className={`${showAll ? 'overflow-x-auto pb-4 pt-1' : 'overflow-x-hidden'} flex-1 flex gap-3 whitespace-nowrap`}
        >
          {displayedChildren.map((child) => (
            <button
              key={child.id}
              onClick={() => onChildQuestionClick(child.title, child.id)}
              className={`${showAll ? 'min-w-[280px]' : 'flex-1'} inline-flex items-center text-left p-3 rounded-md border transition-colors duration-200 text-sm bg-white`}
              style={{ borderColor: '#D8E6E8', color: '#111827' }}
              onMouseOver={(e) => { (e.currentTarget.style.backgroundColor = '#EAF2F3'); }}
              onMouseOut={(e) => { (e.currentTarget.style.backgroundColor = 'white'); }}
            >
              <div className="font-medium">
                {truncateWords(child.title, 4)}
              </div>
            </button>
          ))}
        </div>

        {hasMoreQuestions && !showAll && (
          <button
            onClick={() => setShowAll(true)}
            className="ml-2 p-1"
            style={{ color: 'var(--color-theme)' }}
            aria-label="Show more related questions"
            title="Show more"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

export default ChildQuestions;
