import { useState } from "react";
import toast from "react-hot-toast";
import { Status } from "@/lib/typings";

export const useAnalysis = () => {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<Status>("Topic modeling in progress...");
  const [result, setResult] = useState<any>(null);

  const fetchFormData = async (
    collection_name: string,
    topics: string[],
    analysis_types: string[]
  ) => {
    try {
      const data_x = JSON.stringify({
        collection_name: collection_name,
        topics: topics,
        analysis_types: analysis_types
      })
      console.log(data_x)
      const response = await fetch(`${process.env.NEXT_PUBLIC_URL}/analyze`, {
        method: "POST",
        mode: "cors",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          collection_name: collection_name,
          topics: topics,
          analysis_types: analysis_types
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
