import { useState } from "react";
import toast from "react-hot-toast";

type Status =
  | "PENDING"
  | "EXTRACTING"
  | "PREPROCESSING"
  | "CLASSIFYING"
  | "COMPLETED"
  | "ERROR";

export const useExtractor = () => {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<Status>("PENDING");
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<any>(null);

  const fetchFormData = async (
    context: string,
    keywords: string[],
    collection_name: string,
    is_existing_collection: boolean
  ) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_URL}/fetch`, {
        method: "POST",
        mode: "cors",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          context: context,
          keywords: keywords,
          collection_name: collection_name,
          is_existing_collection: is_existing_collection
        }),
      });
      const data = await response.json();
      console.log("Server response:", data);

      if (data.task_id) {
        // Check for task_id instead of response
        setTaskId(data.task_id);
        setStatus(data.status as Status);
        toast.success("Task started successfully");
      } else {
        toast.error("Received invalid response format from server");
      }
    } catch (error) {
      console.error("Submission error:", error);
      toast.error("Failed to get response from server");
    }
  };

  return {
    taskId,
    status,
    progress,
    result,
    setTaskId,
    setStatus,
    setProgress,
    setResult,
    fetchFormData,
  };
};
