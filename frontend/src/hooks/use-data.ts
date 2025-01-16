import { useState, useCallback, useEffect } from "react";
import toast from "react-hot-toast";

export const useData = () => {
  const [bertTopics, setBertTopics] = useState<string[]>(() => {
    return [];
  });

  const getBertTopics = async (collection_name: string) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_URL}/topics/${collection_name}`,
        {
          method: "GET",
          mode: "cors",
          headers: { "Content-Type": "application/json" },
        }
      );
      const data = await response.json();
      if (data.response) {
        setBertTopics(data.response);
      } else {
        toast.error("Received invalid response format from server");
      }
    } catch (error) {
      console.error("Submission error:", error);
      toast.error("Failed to get response from server");
    }
  };

  return { bertTopics, getBertTopics }
};
