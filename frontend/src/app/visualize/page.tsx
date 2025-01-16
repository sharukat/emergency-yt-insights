import React from "react";
import Visualizations from "@/components/visualizations";

export default async function VisualizationPage() {
  return (
    <main className="flex flex-col items-center px-4">
      <div className="flex w-full flex-col items-center justify-center p-4">
        <div className="max-w-5xl">
          <h2 className="p-4 text-xl text-center sm:text-3xl pt-10">
            Analyze and Visualize Data Insights
          </h2>
          <p className="text-center text-base">
            Choose data collection related to a specific incident or topic to
            explore and analyze. Perform advanced data analyses, including
            sentiment analysis and topic modeling, and visualize the results.
          </p>
          <div className="flex flex-col gap-6 mt-10">
            <Visualizations />
          </div>
        </div>
      </div>
    </main>
  );
}
