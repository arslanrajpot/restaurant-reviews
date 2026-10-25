"use client";

import ChatInput from "@/app/(sidebar)/review_agent/_component/ChatInput";
import Message from "@/app/(sidebar)/_components/message";
import ChildQuestions from "@/app/(sidebar)/review_agent/_component/ChildQuestions";
import {useEffect, useRef, useState} from "react";
import { get_user_data, review_agent } from "@/service/api";
import { UserDataType, FAQNode } from "@/types/api";
import { useRouter } from "next/navigation";

interface MessageType {
  userMessage: string;
  agentMessage: string;
  loading: boolean;
  children?: FAQNode[];
}

interface Props {
  message: MessageType[];
  setMessage: (p: (prev: MessageType[]) => MessageType[]) => void;
}

const ChatModal = ({ message, setMessage }: Props) => {
  const messageEndRef = useRef<HTMLDivElement | null>(null);
  const [userData, setUserData] = useState<UserDataType | null>(null);
  const [showLimitTooltip, setShowLimitTooltip] = useState(false);
  const [availableChildQuestions, setAvailableChildQuestions] = useState<FAQNode[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [clickedChildQuestions, setClickedChildQuestions] = useState<Set<number>>(new Set());
  const router = useRouter();

  useEffect(() => {
      if (messageEndRef.current !== null) {
        messageEndRef.current?.scrollIntoView({ behavior: "smooth" });
      }
  }, [message]);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await get_user_data();
        setUserData(response);
      } catch (err) {
        console.error("Error fetching user data:", err);
      }
    };
    fetchUserData();
  }, []);

  // Collect all child questions from messages
  useEffect(() => {
    const allChildQuestions: FAQNode[] = [];
    message.forEach(msg => {
      if (msg.children) {
        allChildQuestions.push(...msg.children);
      }
    });
    setAvailableChildQuestions(allChildQuestions);
  }, [message]);

  // Show tooltip and redirect if user is FREE and out of messages
  useEffect(() => {
    if (userData && userData.tier === "FREE" && userData.message_count === 0) {
      setShowLimitTooltip(true);
      const timer = setTimeout(() => {
        router.push("/subscription");
      }, 3000);
      return () => clearTimeout(timer);
    } else {
      setShowLimitTooltip(false);
    }
  }, [userData, router]);

  const handleChildQuestionClick = async (question: string, faqId: number) => {
    if (isProcessing) return;
    try {
      setIsProcessing(true);
      // Mark this question as clicked
      setClickedChildQuestions(prev => new Set([...prev, faqId]));
      
      // Add loading state
      setMessage(prev => [...prev, { userMessage: question, agentMessage: "", loading: true }]);
      
      // Use unified chat endpoint with FAQ params
      const response = await review_agent(question, true, faqId);
      
      // Update with response (child questions don't have their own children)
      setMessage(prev => {
        const newMessages = [...prev];
        const lastIndex = newMessages.length - 1;
        if (lastIndex >= 0) {
          newMessages[lastIndex] = {
            userMessage: question,
            agentMessage: response.response,
            loading: false
          };
        }
        return newMessages;
      });
    } catch (error) {
      console.error("Error asking child FAQ:", error);
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
      {showLimitTooltip && (
        <div className="fixed top-40 right-8 z-50 flex items-center gap-2 px-4 py-2 bg-red-100 border border-red-300 text-red-800 rounded-lg shadow-lg animate-fade-in">
          <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M21 12A9 9 0 1 1 3 12a9 9 0 0 1 18 0z" />
          </svg>
          <span className="font-medium">Limit reached, redirecting to subscription page</span>
        </div>
      )}
      <div className="relative flex flex-col justify-center items-center w-full h-[70vh] max-w-4xl mx-auto py-4">
        <div className="flex-grow p-4 w-full overflow-y-auto max-h-[70vh]">
          {message?.map((msg, index) => (
            <div key={index}>
              <Message sender="user" text={msg.userMessage} />
              <Message 
                sender="agent" 
                text={msg.agentMessage} 
                loading={msg.loading}
                question={msg.userMessage}
                userId={userData?.id}
              />
            </div>
          ))}
          <div ref={messageEndRef} />
        </div>
        {/* Child Questions - Fixed above input */}
        {availableChildQuestions.length > 0 && (
          <div className="w-full max-w-4xl px-4 mb-4">
            <ChildQuestions 
              items={availableChildQuestions.filter(child => !clickedChildQuestions.has(child.id))} 
              onChildQuestionClick={handleChildQuestionClick}
            />
          </div>
        )}
        <div className="mb-[-70px] w-full px-4 bg-white">
          <ChatInput setMessage={setMessage} message={message}/>
        </div>
      </div>
    </>
  );
};

export default ChatModal;
