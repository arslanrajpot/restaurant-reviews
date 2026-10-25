"use client";

import { marked } from "marked";
import FeedbackButtons from "./FeedbackButtons";

interface MessageProps {
  sender: "user" | "agent";
  text: string;
  loading?: boolean;
  question?: string; // The user's question for feedback
  userId?: string; // User ID for feedback
}

const Message = ({ sender, text, loading, question, userId }: MessageProps) => {
  const cleanedText = text.replace(/\n{2,}/g, "\n").trim();

  return (
    <div className={`flex ${sender === "user" ? "justify-end" : "justify-start"} mb-4 break-words`}>
      <div className="flex flex-col max-w-xl space-y-2">
         <div
          className={`p-3 rounded-lg ${
            sender === "user" ? "bg-black text-white" : "bg-[#F1F5FF] text-black"
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
            <div dangerouslySetInnerHTML={{ __html: marked(cleanedText) }} />
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