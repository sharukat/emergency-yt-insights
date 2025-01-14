import React from "react";
import { Collection } from "@/lib/typings";
import { fetchCollections } from "@/lib/fetchData";

export default async function VideosPage() {
  const collections: Collection[] = await fetchCollections();
  return (
    <main className="flex flex-col items-center px-4">
      <div className="flex w-full flex-col items-center justify-center p-4">
        <div className="max-w-5xl">
          <h2 className="p-4 text-xl text-center sm:text-3xl pt-10">
            Watch Relevant Videos
          </h2>
          <p className="text-center text-base">
            Select a data collection related to a specific incident or topic,
            then type your search input to explore and watch the most relevant
            videos.
          </p>
        </div>
      </div>
    </main>
  );
}
