"use client";

import ChatInput from "@/app/(sidebar)/review_agent/_component/ChatInput";
import Message from "@/app/(sidebar)/_components/message";
import ChildQuestions from "@/app/(sidebar)/review_agent/_component/ChildQuestions";
import LimitReachedBanner from "@/app/(sidebar)/review_agent/_component/LimitReachedBanner";
import {useEffect, useRef, useState} from "react";
import { get_user_data, review_agent } from "@/service/api";
import { UserDataType, FAQNode } from "@/types/api";

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
  const [dailyLimitMessage, setDailyLimitMessage] = useState<string | null>(null);
  const [availableChildQuestions, setAvailableChildQuestions] = useState<FAQNode[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [clickedChildQuestions, setClickedChildQuestions] = useState<Set<number>>(new Set());

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

  // Surface the free-tier daily limit as soon as we know about it (e.g. right after
  // loading the chat), not just after the user's next message fails.
  useEffect(() => {
    if (userData && userData.tier === "FREE" && userData.daily_messages_remaining === 0) {
      setDailyLimitMessage(
        "You've reached today's free message limit. Subscribe for unlimited access, or come back tomorrow when your free messages reset."
      );
    }
  }, [userData]);

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
      const { status, message: errorMessage } = (error as { status?: number; message?: string }) || {};
      const isLimitReached = status === 403 && typeof errorMessage === "string";
      // Update with error message
      setMessage(prev => {
        const newMessages = [...prev];
        const lastIndex = newMessages.length - 1;
        if (lastIndex >= 0) {
          newMessages[lastIndex] = {
            userMessage: question,
            agentMessage: isLimitReached ? errorMessage! : "Sorry, I couldn't process that question. Please try again.",
            loading: false
          };
        }
        return newMessages;
      });
      if (isLimitReached) {
        setDailyLimitMessage(errorMessage!);
      }
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <>
      {dailyLimitMessage && (
        <LimitReachedBanner message={dailyLimitMessage} onClose={() => setDailyLimitMessage(null)} />
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
          <ChatInput setMessage={setMessage} message={message} onLimitReached={setDailyLimitMessage}/>
        </div>
      </div>
    </>
  );
};

export default ChatModal;
