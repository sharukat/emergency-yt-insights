import React from "react";
import ExtractForm from "@/components/extract-form";
import { Toaster } from "react-hot-toast";

export default function ExtractPage() {
  return (
    <div className="flex w-full flex-col items-center justify-center p-4">
      <Toaster position="bottom-right" reverseOrder={false} />
      <div className="max-w-5xl">
        <h2 className="p-4 text-xl text-center sm:text-3xl pt-10">
          Extract Insights from YouTube
        </h2>
        <p className="text-center text-base">
          Search and extract YouTube transcripts and comments related to
          specific incidents or topics.
        </p>
      </div>
      <ExtractForm />
    </div>
  );
}