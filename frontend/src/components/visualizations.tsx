"use client";

import React, { useState, useEffect } from "react";
import { PressEvent } from "@react-types/shared";
import { useCollections } from "@/hooks/use_collections";
import {
  Form,
  Input,
  Button,
  Switch,
  Select,
  SelectItem,
  CheckboxGroup,
  Checkbox,
  RadioGroup,
  Radio,
  Accordion,
  AccordionItem,
} from "@nextui-org/react";
import { PieChartComponent, BarChartComponent } from "@/components/Diagrams";
import { useAnalysis } from "@/hooks/use-analysis";
import toast from "react-hot-toast";
import { Status } from "@/lib/typings";
import { useData } from "@/hooks/use-data";

export default function Visualizations() {
  const [operation, setOperation] = useState(() => {
    return "analyze";
  });
  const [selected, setSelected] = useState<string[]>([]);
  const [topic, setTopic] = useState(() => {
    return "";
  });
  const [topics, setTopics] = useState<string[]>([]);
  const [action, setAction] = useState<string | null>(null);
  const { collections, collection, handleCollections, handleCollectionSelect } =
    useCollections();
  const {
    taskId,
    status,
    result,
    setTaskId,
    setStatus,
    setResult,
    fetchFormData,
  } = useAnalysis();
  const { bertTopics, getBertTopics } = useData();

  useEffect(() => {
    if (!taskId) return;

    const eventSource = new EventSource(
      `${process.env.NEXT_PUBLIC_URL}/status/analysis/${taskId}`
    );

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.status) {
          setStatus(data.status as Status);

          switch (data.status) {
            case "Completed":
              setResult(data.result);
              console.log("Operation completed successfully");
              eventSource.close();
              setAction(null);
              break;
            case "Error":
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

  const handleClick = () => {
    // If operation is 'analyze', pass 'topics', otherwise pass 'chunked'
    const db_name = operation === "analyze" ? "chunked" : "topics";
    handleCollections(db_name);
  };

  const handleOnSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (operation === "analyze") {
      setAction("analyze");
      let data = Object.fromEntries(new FormData(e.currentTarget));
      await fetchFormData(String(data.collection), topics, selected);
    } else {
      setAction("visualize");
      await getBertTopics(collection);
    }

    console.log(operation);
    console.log(collection);
    console.log(selected);
    console.log(topics);
  };

  const handleTopicSubmit = async (e: PressEvent) => {
    if (topic.trim()) {
      setTopics((prevTopics) => [...prevTopics, topic.trim()]);
      setTopic(""); // Clear input
    }
  };

  return (
    <div className="flex flex-col items-center justify-center gap-5 px-auto">
      <Form
        className="w-full max-w-5xl flex flex-col gap-5 mt-10"
        validationBehavior="native"
        //   onReset={handleReset}
        onSubmit={handleOnSubmit}
      >
        <div className="flex w-full flex-wrap md:flex-nowrap gap-8">
          <RadioGroup
            label="Operation Type:"
            orientation="horizontal"
            name="operation"
            defaultValue="analyze"
            value={operation}
            onValueChange={setOperation}
          >
            <Radio value="analyze">Analyze</Radio>
            <Radio value="visualize">Visualize</Radio>
          </RadioGroup>

          <Select
            isRequired
            className="max-w-sm"
            label="Collection Name"
            name="collection"
            labelPlacement="outside"
            placeholder="Select an existing collection"
            onClick={handleClick}
            onChange={handleCollectionSelect}
            value={collection}
          >
            {collections.map((collection) => (
              <SelectItem key={collection} value={collection}>
                {collection}
              </SelectItem>
            ))}
          </Select>
          <CheckboxGroup
            isRequired
            color="primary"
            name="analysis"
            label="Analysis Types:"
            value={selected}
            onValueChange={setSelected}
            orientation="horizontal"
          >
            <Checkbox value="topic-model">Topic Modeling</Checkbox>
            <Checkbox value="sentiments">Sentiment Analysis</Checkbox>
          </CheckboxGroup>
          {/* <p className="text-default-500 text-small">
            Selected: {selected.join(", ")}
          </p> */}
        </div>
        {selected.includes("topic-model") && operation === "analyze" && (
          <div className="flex flex-col gap-5 border rounded-2xl p-10">
            <h1 className="text-center text-lg">
              Add few topics you expect to find within this data collection
            </h1>
            <p className="text-gray-300 text-center">
              Zero-shot Topic Modeling identifies predefined topics in large
              document collections while dynamically uncovering new topics for
              unmatched documents. This approach combines targeted analysis with
              discovery, offering deeper insights into your data.
            </p>
            <div className="flex w-full flex-nowrap gap-8">
              <Input
                labelPlacement="outside"
                name="topic"
                placeholder="Enter a sample topic for few-shot topic modeling"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              />
              <Button variant="flat" onPress={handleTopicSubmit}>
                Add to the List
              </Button>
            </div>
            {topics && (
              <ul className="list-disc">
                {topics.map((topic, index) => (
                  <li key={index}>{topic}</li>
                ))}
              </ul>
            )}
          </div>
        )}

        <div className="flex w-full flex-wrap md:flex-nowrap gap-8">
          <Button
            isLoading={action === "analyze"}
            color="success"
            type="submit"
            variant="ghost"
            isDisabled={action === "analyze"}
          >
            {operation === "visualize"
              ? "Visualize Data"
              : action === "analyze"
              ? "Processing"
              : "Analyze Data"}
          </Button>
          {action === "analyze" && <p>{status}</p>}
        </div>
      </Form>

      <div>
        {action === "visualize" && operation === "visualize" && (
          <div className="flex flex-col gap-5 w-full w-[64rem] border rounded-2xl p-5">
            <Accordion variant="splitted" className="w-full">
              <AccordionItem
                key="1"
                aria-label="Accordion 1"
                title="Topic Modeling Results"
              >
                <ul className="list-disc p-5">
                  {bertTopics.map((topic, index) => (
                    <li key={index} className="text-gray-400 py-1">{topic}</li>
                  ))}
                </ul>
              </AccordionItem>
            </Accordion>
          </div>
        )}
      </div>
    </div>
  );
}
