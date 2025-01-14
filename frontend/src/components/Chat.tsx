"use client";

import { LLMInput } from "./ui/user-input";
import React, { useState, useCallback, useMemo } from "react";
import { Tabs, Tab } from "@nextui-org/tabs";
import { TextGenerateEffect } from "./ui/text-generation";
import {
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
  Button,
  Spinner,
  Select,
  SelectItem,
} from "@nextui-org/react";
import { Questions, SelectedQuestion, Collection } from "@/lib/typings";
import { Toaster } from "react-hot-toast";
import { useAnswerGeneration } from "@/hooks/use-generate";
import { useCollections } from "@/hooks/use_collections";

interface Question {
  category: string;
  questions: string[];
}

interface SelectedQuestionState {
  categoryIndex: number | null;
  questionIndex: number | null;
}

// Constants
const collectionQuestions = {
  "plane-crash": [
    {
      category: "Investigation",
      questions: [
        "What are the common causes of plane crashes?",
        "How are plane crash investigations conducted?",
        "What role does AI play in preventing aviation accidents?",
      ],
    },
    {
      category: "Prevention",
      questions: [
        "What safety measures are implemented to prevent plane crashes?",
        "How is weather monitoring used to prevent aviation accidents?",
        "What technological advancements help prevent plane crashes?",
      ],
    },
  ],
  "drink-driving": [
    {
      category: "Prevention",
      questions: [
        "What are effective measures to prevent drink driving?",
        "How do breathalyzers work?",
        "What are the legal limits for blood alcohol content?",
      ],
    },
    {
      category: "Impact",
      questions: [
        "What are the consequences of drink driving?",
        "How does alcohol affect driving ability?",
        "What are the statistics on drink driving accidents?",
      ],
    },
  ],
  "disaster-emergency-management": [
    {
      category: "Planning",
      questions: [
        "How are emergency response plans developed?",
        "What role does AI play in disaster prediction?",
        "How are resources allocated during emergencies?",
      ],
    },
    {
      category: "Response",
      questions: [
        "What are the key components of emergency response?",
        "How is communication managed during disasters?",
        "What technologies are used in emergency management?",
      ],
    },
  ],
  "health-safety-environment": [
    {
      category: "Workplace Safety",
      questions: [
        "What are common workplace hazards?",
        "How are risk assessments conducted?",
        "What are essential safety protocols?",
      ],
    },
    {
      category: "Environmental Impact",
      questions: [
        "How are environmental impacts assessed?",
        "What are sustainable workplace practices?",
        "How is waste management handled?",
      ],
    },
  ],
};

type Props = {
  collections: Collection[];
};

export default function ChatInput(): JSX.Element {
  const [selectedTab, setSelectedTab] = useState(() => {
    return "english";
  });
  const [userInput, setUserInput] = useState<string>("");
  const [isTextAnimationComplete, setIsTextAnimationComplete] =
    useState<boolean>(false);
  const [selectedCategory, setSelectedCategory] =
    useState<SelectedQuestionState>({
      categoryIndex: null,
      questionIndex: null,
    });
  const { collections, getCollections } = useCollections();
  const [selectedCollection, setSelectedCollection] = useState<string | number>("");

  const handleCollections = () => {
    if (!collections || collections.length === 0) {
      getCollections("extract");
    }
  };

  const handleCollectionSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
    console.log(e.target.value)
    setSelectedCollection(e.target.value);
  };

  // const handleCollectionChange = useCallback((collection: CollectionKey) => {
  //   setSelectedCollection(collection);
  //   setUserInput("");
  //   setSelectedCategory({ categoryIndex: null, questionIndex: null });
  // }, []);

  // const handleDropdownSelection = useCallback(
  //   (categoryIndex: number, questionIndex: number) => {
  //     setSelectedCategory((prev) => {
  //       if (
  //         prev.categoryIndex === categoryIndex &&
  //         prev.questionIndex === questionIndex
  //       ) {
  //         setUserInput("");
  //         return { categoryIndex: null, questionIndex: null };
  //       }

  //       const selectedQuestion = selectedCollection
  //         ? collectionQuestions[selectedCollection][categoryIndex].questions[questionIndex]
  //         : "";
  //       setUserInput(selectedQuestion);
  //       return { categoryIndex, questionIndex };
  //     });
  //   },
  //   [selectedCollection]
  // );

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedCategory({ categoryIndex: null, questionIndex: null });
    setUserInput(e.target.value);
  }, []);

  const handleTabChange = (key: React.Key) => {
    console.log("Selected Tab:", String(key));
    setSelectedTab(String(key));
  };

  const handleTextAnimationComplete = useCallback(() => {
    setIsTextAnimationComplete(true);
  }, []);

  const { words, metaData, isLoading, generateText, setAnswerStates } =
    useAnswerGeneration(userInput, selectedTab);

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setAnswerStates();
    setIsTextAnimationComplete(false);
    generateText();
  };

  // const memoizedDropdowns = useMemo(() => {
  //   if (!selectedCollection) return null;

  //   return collectionQuestions[selectedCollection]?.map((sample, categoryIndex) => (
  //     <Dropdown
  //       key={categoryIndex}
  //       backdrop="blur"
  //       size="sm"
  //       classNames={{
  //         base: "min-w-[280px]",
  //         content: "min-w-[280px] max-h-[400px] overflow-y-auto",
  //       }}
  //     >
  //       <DropdownTrigger>
  //         <Button
  //           variant="flat"
  //           radius="full"
  //           className="min-w-[200px] px-auto"
  //         >
  //           {sample.category}
  //         </Button>
  //       </DropdownTrigger>
  //       <DropdownMenu
  //         variant="faded"
  //         aria-label="Sample Questions"
  //         selectionMode="single"
  //         selectedKeys={
  //           selectedCategory.categoryIndex === categoryIndex
  //             ? new Set([String(selectedCategory.questionIndex)])
  //             : new Set()
  //         }
  //         onSelectionChange={(keys) => {
  //           const selectedKey = Array.from(keys)[0];
  //           if (selectedKey) {
  //             handleDropdownSelection(categoryIndex, Number(selectedKey));
  //           }
  //         }}
  //         className="max-h-lg overflow-y-auto border border-transparent"
  //       >
  //         {sample.questions.map((question, questionIndex) => (
  //           <DropdownItem
  //             key={questionIndex}
  //             className="text-sm py-2 hover:bg-neutral-100 dark:hover:bg-neutral-800"
  //           >
  //             {question}
  //           </DropdownItem>
  //         ))}
  //       </DropdownMenu>
  //     </Dropdown>
  //   ));
  // }, [
  //   selectedCollection,
  //   selectedCategory.categoryIndex,
  //   selectedCategory.questionIndex,
  //   handleDropdownSelection,
  // ]);

  return (
    <section className="w-full flex flex-col items-center justify-center">
      <Toaster position="bottom-right" reverseOrder={false} />
      <div className="w-[80%] max-w-5xl flex flex-col justify-center items-center overflow-hidden">
        <div className="px-4 w-full flex flex-col gap-4 my-10 items-center justify-center">
          <div className="flex w-full flex-wrap items-center justify-between md:flex-nowrap gap-8">
            <Select
              isRequired
              className="max-w-lg"
              label="Collection Name"
              labelPlacement="outside"
              placeholder="Select an existing collection"
              onClick={handleCollections}
              onChange={handleCollectionSelect}
              value={selectedCollection}
            >
              {collections.map((collection) => (
                <SelectItem key={collection} value={collection}>
                  {collection}
                </SelectItem>
              ))}
            </Select>

            <div className="flex flex-col">
              <p className="mb-2">Choose Your Preferred Response Language:</p>
              <Tabs
                radius="full"
                color="primary"
                aria-label="Language selection tabs"
                defaultSelectedKey={"english"}
                variant="bordered"
                onSelectionChange={handleTabChange}
                isDisabled={!selectedCollection}
              >
                <Tab key="english" title="English" />
                <Tab key="french" title="French" />
                <Tab key="spanish" title="Spanish" />
                <Tab key="german" title="German" />
                <Tab key="italian" title="Italian" />
              </Tabs>
            </div>
          </div>

          <LLMInput
            externalInput={userInput}
            placeholders={[
              "Select a collection to view sample questions",
              "Or type your own question after selecting a collection",
            ]}
            onChange={handleChange}
            onSubmit={onSubmit}
          />

          {/* <div className="flex flex-row flex-wrap items-center justify-center gap-4">
            {memoizedDropdowns}
          </div> */}
        </div>

        {(isLoading || words) && (
          <div className="flex flex-col gap-4 p-4">
            {isLoading ? (
              <div className="flex justify-center items-center">
                <Spinner label="Generation in Progress.." size="lg" />
              </div>
            ) : (
              <TextGenerateEffect
                words={words}
                onAnimationComplete={handleTextAnimationComplete}
              />
            )}
          </div>
        )}
      </div>
    </section>
  );
}
