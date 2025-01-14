"use client";

import React, { useState, useEffect } from "react";
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
  Spinner,
} from "@nextui-org/react";
import { PieChartComponent, BarChartComponent } from "@/components/Diagrams";

export default function Visualizations() {
  const [operation, setOperation] = useState(() => {
    return "analyze";
  });
  const [selected, setSelected] = useState<string[]>([]);
  const [action, setAction] = useState<string | null>(null);
  const { collections, collection, handleCollections, handleCollectionSelect } =
    useCollections();

  const handleOnSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (operation === "analyze") {
      setAction("analyze");
    } else {
      setAction("visualize");
    }

    console.log(operation);
    console.log(collection);
    console.log(selected);
  };

  return (
    <div className="flex flex-col gap-5 px-auto">
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
            onClick={() => handleCollections("chunked")}
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
        <Button
          color="primary"
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
      </Form>
      <div>
        {action === "visualize" && (
          <div>
            <PieChartComponent />
            <BarChartComponent />
          </div>
        )}
      </div>
    </div>
  );
}
