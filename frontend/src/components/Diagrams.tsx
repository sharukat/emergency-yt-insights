"use client";

import * as React from "react";
import { TrendingUp } from "lucide-react";
import {
  Label,
  Pie,
  PieChart,
  Bar,
  BarChart,
  CartesianGrid,
  XAxis,
} from "recharts";

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

// Pie chart - Sentiments
const pieChartData = [
  { sentiment: "negative", count: 656, fill: "var(--color-negative)" },
  { sentiment: "neutral", count: 543, fill: "var(--color-neutral)" },
  { sentiment: "positive", count: 5, fill: "var(--color-positive)" },
];

const pieChartConfig = {
  count: {
    label: "Count",
  },
  negative: {
    label: "Negative",
    color: "hsl(var(--chart-1))",
  },
  neutral: {
    label: "Neutral",
    color: "hsl(var(--chart-2))",
  },
  positive: {
    label: "Positive",
    color: "hsl(var(--chart-3))",
  },
} satisfies ChartConfig;

export function PieChartComponent() {
  const totalCount = React.useMemo(() => {
    return pieChartData.reduce((acc, curr) => acc + curr.count, 0);
  }, []);

  return (
    <Card className="flex flex-col">
      <CardHeader className="items-center pb-0">
        <CardTitle>Sentiments of Drink</CardTitle>
        <CardTitle>Driving Videos</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 pb-0">
        <ChartContainer
          config={pieChartConfig}
          className="mx-auto aspect-square max-h-[250px]"
        >
          <PieChart>
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent hideLabel />}
            />
            <Pie
              data={pieChartData}
              dataKey="count"
              nameKey="sentiment"
              innerRadius={60}
              strokeWidth={5}
            >
              <Label
                content={({ viewBox }) => {
                  if (viewBox && "cx" in viewBox && "cy" in viewBox) {
                    return (
                      <text
                        x={viewBox.cx}
                        y={viewBox.cy}
                        textAnchor="middle"
                        dominantBaseline="middle"
                        fill="currentColor"
                        className="text-black dark:text-white"
                      >
                        <tspan
                          x={viewBox.cx}
                          y={viewBox.cy}
                          className="text-3xl font-bold fill-current"
                        >
                          {totalCount.toLocaleString()}
                        </tspan>
                        <tspan
                          x={viewBox.cx}
                          y={(viewBox.cy || 0) + 24}
                          className="text-gray-600 dark:text-gray-300"
                        >
                          Count
                        </tspan>
                      </text>
                    );
                  }
                }}
              />
            </Pie>
          </PieChart>
        </ChartContainer>
      </CardContent>
      <CardFooter className="flex-col gap-2 text-sm">
        <div className="flex items-center gap-2 font-medium leading-none">
          Negative sentiment videos exceed
        </div>
        <div className="flex items-center gap-2 font-medium leading-none">
          positive ones by 54%.
        </div>
      </CardFooter>
    </Card>
  );
}

// Grouped bar chart

const barChartData = [
  { language: "English", negative: 186, neutral: 80, positive: 80 },
  { language: "French", negative: 305, neutral: 200, positive: 80 },
  { language: "German", negative: 237, neutral: 120, positive: 80 },
  { language: "Italian", negative: 73, neutral: 190, positive: 80 },
  { language: "Spanish", negative: 209, neutral: 130, positive: 80 },
];

const barChartConfig = {
  negative: {
    label: "Negative",
    color: "hsl(var(--chart-1))",
  },
  neutral: {
    label: "Neutral",
    color: "hsl(var(--chart-2))",
  },
  positive: {
    label: "Positive",
    color: "hsl(var(--chart-3))",
  },
} satisfies ChartConfig;

export function BarChartComponent() {
  return (
    <Card>
      <CardHeader className="items-center pb-4">
        <CardTitle>Sentiment of Drink Driving</CardTitle>
        <CardTitle>Videos by Language</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={barChartConfig}>
          <BarChart accessibilityLayer data={barChartData}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="language"
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              tickFormatter={(value) => value.slice(0, 10)}
            />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="dashed" />}
            />
            <Bar dataKey="negative" fill="var(--color-negative)" radius={4} />
            <Bar dataKey="neutral" fill="var(--color-neutral)" radius={4} />
            <Bar dataKey="positive" fill="var(--color-positive)" radius={4} />
          </BarChart>
        </ChartContainer>
      </CardContent>
      <CardFooter className="flex-col items-start gap-2 text-sm">
        <div className="flex items-center gap-2 font-medium leading-none">
          The majority of sentiments across languages
        </div>
        <div className="flex items-center gap-2 font-medium leading-none">
          are either negative or neutral.
        </div>
      </CardFooter>
    </Card>
  );
}
