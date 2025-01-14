"use client";

import React, { useState, useEffect } from "react";
import {
  Form,
  Input,
  Button,
  Switch,
  Select,
  SelectItem,
  Spinner,
} from "@nextui-org/react";
import { useCollections } from "@/hooks/use_collections";
import { useExtractor } from "@/hooks/use-extactor";
import toast from "react-hot-toast";
import { Status } from "@/lib/typings";

export default function ExtractForm() {
  const [action, setAction] = useState<string | null>(null);
  const [isSelected, setIsSelected] = useState(false);
  const [isCommentsSelected, setIsCommentsSelected] = useState(false);
  const { collections, getCollections } = useCollections();
  const {
    taskId,
    status,
    result,
    setTaskId,
    setStatus,
    setResult,
    fetchFormData,
  } = useExtractor();

  useEffect(() => {
    if (isSelected && (!collections || collections.length === 0)) {
      getCollections("extract");
    }
  }, [isSelected, collections]);

  useEffect(() => {
    if (!taskId) return;

    const eventSource = new EventSource(
      `${process.env.NEXT_PUBLIC_URL}/status/${taskId}`
    );

    eventSource.onmessage = (event) => {
      console.log("Raw SSE event data:", event.data);
      try {
        const data = JSON.parse(event.data);
        console.log("SSE update:", data);

        if (data.status) {
          setStatus(data.status as Status);

          switch (data.status) {
            case "EXTRACTING":
              console.log("Starting data extraction");
              break;
            case "PREPROCESSING":
              console.log("Data extracted, preprocessing started");
              break;
            case "SAVING": // Changed from "DATABASE" to "SAVING"
              console.log("Saving data to database");
              break;
            case "COMPLETED":
              setResult(data.result);
              console.log("Operation completed successfully");
              eventSource.close();
              setAction(null);
              break;
            case "ERROR":
              console.error(`Error: ${data.error}`);
              toast.error(data.error || "An error occurred during processing");
              eventSource.close();
              setAction(null);
              break;
          }
        }
      } catch (error) {
        console.error("Error parsing SSE data:", error);
        toast.error("Error processing server response");
        eventSource.close();
        setAction(null);
      }
    };

    eventSource.onerror = (error) => {
      console.error("EventSource error:", error);
      toast.error("Lost connection to server");
      eventSource.close();
      setAction(null);
    };

    return () => {
      eventSource.close();
    };
  }, [taskId]);

  const handleOnSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setAction("fetch");
    setStatus("Extracting...");

    let data = Object.fromEntries(new FormData(e.currentTarget));
    let keywords: string[] = (data.keywords as string)
      .split(",")
      .map((item) => item.trim());

    await fetchFormData(
      String(data.context),
      keywords,
      String(data.collection),
      isSelected,
      isCommentsSelected
    );
  };

  const handleReset = () => {
    setAction(null);
    setStatus("Extracting...");
    setTaskId(null);
    setResult(null);
  };

  return (
    <Form
      className="w-full max-w-5xl flex flex-col gap-10 mt-10"
      validationBehavior="native"
      onReset={handleReset}
      onSubmit={handleOnSubmit}
    >
      <div className="flex w-full flex-wrap md:flex-nowrap gap-8">
        <Input
          isRequired
          errorMessage="Please enter the context of the search query"
          label="Context"
          labelPlacement="outside"
          name="context"
          placeholder="Enter the context (e.g.: Plane crash)"
          type="text"
        />
        <Input
          isRequired
          errorMessage="Please enter the keywords"
          label="Keywords"
          labelPlacement="outside"
          name="keywords"
          placeholder="Enter the keywords (e.g.: korean flight, jeju)"
          type="text"
        />
      </div>

      <div className="flex w-full flex-wrap md:flex-nowrap gap-8">
        <div className="flex flex-col gap-2">
          <Switch isSelected={isSelected} onValueChange={setIsSelected}>
            Existing collection
          </Switch>
          <p className="text-small text-default-500">
            Selected:{" "}
            {isSelected
              ? "Using an existing collection"
              : "Creating a new collection"}
          </p>
        </div>

        <div className="flex flex-col gap-2">
          <Switch isSelected={isCommentsSelected} onValueChange={setIsCommentsSelected}>
            Extract comments
          </Switch>
          <p className="text-small text-default-500">
            Selected:{" "}
            {isCommentsSelected
              ? "Extracting transcripts and comments"
              : "Extracting transcripts only"}
          </p>
        </div>
      </div>

      {isSelected && (
        <Select
          isRequired
          className="max-w-lg"
          label="Collection Name"
          name="collection"
          labelPlacement="outside"
          placeholder="Select an existing collection"
        >
          {collections.map((collection) => (
            <SelectItem key={collection} value={collection}>
              {collection}
            </SelectItem>
          ))}
        </Select>
      )}
      {!isSelected && (
        <Input
          isRequired
          className="max-w-lg"
          errorMessage="Please enter a collection name"
          label="Collection Name"
          labelPlacement="outside"
          name="collection"
          placeholder="Enter a collection name (e.g.: plane-crash)"
          type="text"
        />
      )}

      {action === "fetch" && status !== "Completed" && (
        <Spinner color="default" label={status} labelColor="foreground" />
      )}

      <div className="flex gap-2">
        <Button color="primary" type="submit" isDisabled={action === "fetch"}>
          {action === "fetch" ? "Processing..." : "Fetch Data"}
        </Button>
        <Button type="reset" variant="flat" isDisabled={action === "fetch"}>
          Reset
        </Button>
      </div>
    </Form>
  );
}
