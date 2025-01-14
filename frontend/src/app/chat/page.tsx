import React from "react";
import ChatInput from "@/components/Chat";
import { Collection } from "@/lib/typings";
import { fetchCollections } from "@/lib/fetchData";
import { useCollections } from "@/hooks/use_collections";

export default async function AIChatPage() {
  // const { collections, getCollections } = useCollections();
  // const collections: Collection[] = await fetchCollections();
  return (
    <main className="flex flex-col items-center px-4">
      <div className="flex w-full flex-col items-center justify-center p-4">
        <div className="max-w-5xl">
          <h2 className="p-4 text-xl text-center sm:text-3xl pt-10">
            Ask Me Questions
          </h2>
          <p className="text-center text-base">
            Select a data collection related to a specific incident or topic and
            ask questions to gain valuable insights. Our tool utilizes
            Retrieval-Augmented Generation (RAG) to generate responses grounded
            in real-world data extracted from YouTube.
          </p>
        </div>
        <ChatInput />
      </div>
    </main>
  );
}
