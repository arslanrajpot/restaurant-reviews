"use client";

import { FaPaperPlane } from "react-icons/fa";
import React, { useState } from "react";
import {review_agent} from "@/service/api";

interface MessageType {
  userMessage: string;
  agentMessage: string;
  loading: boolean;
}

interface Props {
  setMessage: (p: (prev: MessageType[]) => MessageType[]) => void;
  message?: MessageType[];
}

const ChatInput = ({ setMessage, message }: Props) => {
  const [inputValue, setInputValue] = useState(""); // State to hold the input value
  const [height, setHeight] = useState(56); // Dynamic height for the textarea
  const [isProgress, setIsProgress] = useState(false); // Track if a message is processing

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);

    const scrollHeight = e.target.scrollHeight;
    if (scrollHeight <= 100) {
      setHeight(scrollHeight);
    }
  };
  // const generateRandomString = (length: number) => {
  //   const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  //   let result = '';
  //   for (let i = 0; i < length; i++) {
  //       const randomIdx = Math.floor(Math.random() * chars.length);
  //       result += chars[randomIdx];
  //   }
  //   return result;
  // }

  const sendMessage = async () => {
    if (!inputValue.trim()) return;
    const hasLoadingMessage = message?.some(msg => msg.loading);
    if (hasLoadingMessage) return;
    setMessage(prev => [...prev, { userMessage: inputValue, agentMessage: "", loading: true }]);
    const input_data = inputValue;
    setInputValue("");

    setIsProgress(true); // ✅ Disable send button while processing

    try {
      // let sessionId = sessionStorage.getItem("session_id");
      // if (is_first_message) {
      //    sessionId = generateRandomString(12);
      //    sessionStorage.setItem("session_id", sessionId);
      // }
      const response = await review_agent(input_data);

      setMessage(prev => {
        const updatedMessages = [...prev];
        updatedMessages[updatedMessages.length - 1] = {
          ...updatedMessages[updatedMessages.length - 1],
          agentMessage: response.response,
          loading: false,
        };
        return updatedMessages;
      });

    } catch (error) {
      console.error("Error fetching response:", error);
      setMessage(prev => {
        const updatedMessages = [...prev];
        updatedMessages[updatedMessages.length - 1] = {
          ...updatedMessages[updatedMessages.length - 1],
          agentMessage: "i am sorry, but i am not able to answer your question. please try again later.",
          loading: false,
        };
        return updatedMessages;
      });
    } finally {
      setIsProgress(false);
    }
  };

  // Handle Enter key for sending message
  const handleKeyDown = async (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (isProgress) return;
      await sendMessage();
    }
  };

  return (
    <div className="relative w-full max-w-4xl">
      <textarea
        placeholder="Ask anything"
        value={inputValue}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        className="w-full p-4 pl-5 rounded-lg border border-gray-300 focus:outline-none text-black focus:ring-2 focus:ring-[var(--button-theme)]/40 resize-none"
        style={{
          height: height,
          overflowY: "auto",
        }}
        rows={1}
      />
      <FaPaperPlane
        onClick={sendMessage}
        className={`absolute right-3 top-1/2 transform -translate-y-1/2 ${
          isProgress ? "text-gray-300 cursor-pointer" : "text-gray-500 cursor-pointer hover:text-[var(--button-theme)]"
        }`}
      />
    </div>
  );
};

export default ChatInput;
