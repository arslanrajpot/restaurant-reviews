import { useState } from "react";
import { send_feedback } from "@/service/api";
import { FeedbackType } from "@/types/api";

export const useFeedback = () => {
  const [feedbackSent, setFeedbackSent] = useState<number | null>(null);
  const [sendingFeedback, setSendingFeedback] = useState(false);

  const sendFeedback = async (feedbackData: FeedbackType) => {
    if (sendingFeedback) return;
    
    setSendingFeedback(true);
    try {
      await send_feedback(feedbackData);
      setFeedbackSent(feedbackData.thumbs);
      return { success: true };
    } catch (error) {
      console.error('Error sending feedback:', error);
      return { success: false, error };
    } finally {
      setSendingFeedback(false);
    }
  };

  const resetFeedback = () => {
    setFeedbackSent(null);
    setSendingFeedback(false);
  };

  return {
    feedbackSent,
    sendingFeedback,
    sendFeedback,
    resetFeedback,
  };
}; 