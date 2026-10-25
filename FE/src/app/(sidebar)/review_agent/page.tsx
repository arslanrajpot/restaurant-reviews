"use client";

import {useState} from "react";
import Welcome from "@/app/(sidebar)/_components/welcome";
import ChatModal from "@/app/(sidebar)/review_agent/_component/chatModal";
import { FAQNode } from "@/types/api";

const ReviewMunch = () => {
  const [messages, setMessages] = useState<{ userMessage: string, agentMessage: string, loading: boolean, children?: FAQNode[] }[]>([]);

  return (
    <div className="flex flex-col items-center mt-1 min-h-[70vh] px-4 md:px-6 lg:px-8">
      {
        messages.length === 0 ? (
          <Welcome
              setMessage={setMessages}
              title={"Craving some insights? I’m your food-savvy assistant!"}
              title_message={" Ask me about any UK restaurant and I’ll dish out what people are saying — from food quality and service to vibe and ambience.\n" +
                  " Want to compare places before making a reservation? I’ve got you.\n" +
                  " Just type the restaurant’s name or your food curiosity below, and I’ll serve the scoop!"}
          />
        ) : (
          <ChatModal message={messages} setMessage={setMessages}/>
        )
      }
    </div>
  );
};

export default ReviewMunch;
