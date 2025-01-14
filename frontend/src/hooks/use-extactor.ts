import { useState } from "react";
import toast from "react-hot-toast";
import { Status } from "@/lib/typings";

export const useExtractor = () => {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<Status>("Extracting...");
  const [result, setResult] = useState<any>(null);

  const fetchFormData = async (
    context: string,
    keywords: string[],
    collection_name: string,
    is_existing_collection: boolean,
    comments_required: boolean
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
          is_existing_collection: is_existing_collection,
          comments_required: comments_required
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
    result,
    setTaskId,
    setStatus,
    setResult,
    fetchFormData,
  };
};
