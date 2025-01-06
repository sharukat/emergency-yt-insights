"use client";

import React from "react";
import {
  Form,
  Input,
  Button,
  Switch,
  Select,
  SelectItem,
} from "@nextui-org/react";

export const animals = [
  { key: "plane-crash", label: "plane-crash" },
  { key: "drink-driving", label: "drink-driving" },
  {
    key: "disaster-emergency-management",
    label: "disaster-emergency-management",
  },
  { key: "health-safety-environment", label: "health-safety-environment" },
];

export default function ExtractForm() {
  const [action, setAction] = React.useState(() => {
    return "";
  });
  const [isSelected, setIsSelected] = React.useState(false);

  return (
    <Form
      className="w-full max-w-xs flex flex-col gap-4"
      validationBehavior="native"
      onReset={() => setAction("reset")}
      onSubmit={(e) => {
        e.preventDefault();
        let data = Object.fromEntries(new FormData(e.currentTarget));

        setAction(`submit ${JSON.stringify(data)}`);
      }}
    >
      <Input
        isRequired
        errorMessage="Please the context of the search query"
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

      {isSelected && (
        <Select
          isRequired
          className="max-w-xs"
          defaultSelectedKeys={["plane-crash"]}
          label="Collection"
          placeholder="Select an existing collection"
        >
          {animals.map((collection) => (
            <SelectItem key={collection.key}>{collection.label}</SelectItem>
          ))}
        </Select>
      )}

      <div className="flex gap-2">
        <Button color="primary" type="submit">
          Fetch Data
        </Button>
        <Button type="reset" variant="flat">
          Reset
        </Button>
      </div>
      {action && (
        <div className="text-small text-default-500">
          Action: <code>{action}</code>
        </div>
      )}
    </Form>
  );
}
