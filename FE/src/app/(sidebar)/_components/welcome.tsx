"use client";

import ChatInput from "@/app/(sidebar)/review_agent/_component/ChatInput";
import FAQQuestions from "@/app/(sidebar)/review_agent/_component/FAQQuestions";
import {useEffect, useState} from "react";
import {chat_start, review_agent} from "@/service/api";
import { FAQNode } from "@/types/api";

interface Props {
  setMessage: React.Dispatch<React.SetStateAction<{ userMessage: string; agentMessage: string, loading: boolean, children?: FAQNode[] }[]>>;
  title: string;
  title_message: string;
}

const Welcome = ({ setMessage, title, title_message }: Props) => {
  const [isProcessing, setIsProcessing] = useState(false);
  useEffect(() => {
      const startChat = async () => {
      try {
        await chat_start();
      } catch (error) {
        console.error("Error fetching restaurants:", error);
      }
    };

    startChat();
  }, []);

  const handleFAQQuestionClick = async (question: string, faqId: number) => {
    if (isProcessing) return;
    try {
      setIsProcessing(true);
      // Add loading state
      setMessage(prev => [...prev, { userMessage: question, agentMessage: "", loading: true }]);
      
      // Use unified chat endpoint with FAQ params
      const response = await review_agent(question, true, faqId);
      
      // Update with response and children
      setMessage(prev => {
        const newMessages = [...prev];
        const lastIndex = newMessages.length - 1;
        if (lastIndex >= 0) {
          newMessages[lastIndex] = {
            userMessage: question,
            agentMessage: response.response,
            loading: false,
            children: response.children
          };
        }
        return newMessages;
      });
    } catch (error) {
      console.error("Error asking FAQ:", error);
      // Update with error message
      setMessage(prev => {
        const newMessages = [...prev];
        const lastIndex = newMessages.length - 1;
        if (lastIndex >= 0) {
          newMessages[lastIndex] = {
            userMessage: question,
            agentMessage: "Sorry, I couldn't process that question. Please try again.",
            loading: false
          };
        }
        return newMessages;
      });
    } finally {
      setIsProcessing(false);
    }
  };


  return (
    <>
      <h1 className="text-lg font-semibold mb-2 text-black">{title}</h1>
      <p className={'text-gray-600 flex w-[600px] mb-5'}>{title_message}</p>
      <div className="relative w-full max-w-4xl bg-white">
        <ChatInput setMessage={setMessage}/>
      </div>
      <FAQQuestions onQuestionClick={handleFAQQuestionClick} />
    </>
  );
};

export default Welcome;
