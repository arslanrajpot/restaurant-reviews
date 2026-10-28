"use client";

import DOMPurify from "dompurify";
import { marked } from "marked";
import FeedbackButtons from "./FeedbackButtons";

interface MessageProps {
  sender: "user" | "agent";
  text: string;
  loading?: boolean;
  question?: string; // The user's question for feedback
  userId?: string; // User ID for feedback
}

// Agent replies can contain text from scraped reviews, so the generated HTML must be sanitized
const renderAgentHtml = (markdown: string): string => {
  const html = marked.parse(markdown, { async: false });
  // DOMPurify needs a DOM; during server rendering fall back to an empty string
  return DOMPurify.isSupported ? DOMPurify.sanitize(html) : "";
};

const Message = ({ sender, text, loading, question, userId }: MessageProps) => {
  const cleanedText = text.replace(/\n{2,}/g, "\n").trim();

  return (
    <div className={`flex ${sender === "user" ? "justify-end" : "justify-start"} mb-4 break-words`}>
      <div className="flex flex-col max-w-xl space-y-2">
         <div
          className={`p-3 rounded-lg ${
            sender === "user" ? "bg-[var(--color-theme)] text-white" : "bg-gray-100 text-black"
          }`}
          style={{ whiteSpace: "pre-line" }}
        >
          {loading && sender === "agent" ? (
            <>
              <span className="dot-typing"></span>
              <span className="dot-typing"></span>
              <span className="dot-typing"></span>
            </>
          ) : sender === "user" ? (
            cleanedText
          ) : (
            <div dangerouslySetInnerHTML={{ __html: renderAgentHtml(cleanedText) }} />
          )}
        </div>
        
        {/* Feedback buttons for agent messages */}
        {sender === "agent" && !loading && question && userId && (
          <FeedbackButtons 
            question={question}
            answer={cleanedText}
            userId={userId}
          />
        )}
      </div>
    </div>
  );
};

export default Message;