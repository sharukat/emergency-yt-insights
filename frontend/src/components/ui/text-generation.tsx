"use client";

import React, { useEffect } from "react";
import { motion, stagger, useAnimate } from "framer-motion";

export const TextGenerateEffect = ({
  words,
  className = "",
  filter = true,
  duration = 0.1, 
  staggerDelay = 0.015,
  onAnimationComplete,
}: {
  words: string;
  className?: string;
  filter?: boolean;
  duration?: number;
  staggerDelay?: number;
  onAnimationComplete?: () => void;
}) => {
  const [scope, animate] = useAnimate();

  // Split text into blocks (paragraphs)
  const blocks = words.split("\n\n").filter(block => block.trim());

  useEffect(() => {
    // Perform animation
    const animationSequence = async () => {
      await animate(
        "span",
        {
          opacity: 1,
          filter: filter ? "blur(0px)" : "none",
        },
        {
          duration: duration ? duration : 0.1,
          delay: stagger(staggerDelay),
        }
      );

      // Call onAnimationComplete after animation is done
      if (onAnimationComplete) {
        onAnimationComplete();
      }
    };

    animationSequence();
  }, [words, scope.current, onAnimationComplete]);

  const renderWords = (text: string) => {
    // Split text into segments based on bold markers
    const segments = text.split(/(\*\*.*?\*\*)/g);
    
    return segments.map((segment, segmentIndex) => {
      // Check if this segment is bold (wrapped in **)
      const isBold = /^\*\*(.*)\*\*$/.test(segment);
      
      // Remove ** from bold segments
      const cleanSegment = isBold ? segment.slice(2, -2) : segment;
      
      // Split segment into words
      const words = cleanSegment.split(" ").filter(word => word);
      
      return words.map((word, wordIndex) => (
        <motion.span
          key={`${segmentIndex}-${wordIndex}`}
          className={`opacity-0 ${isBold ? "font-bold" : ""}`}
          style={{
            filter: filter ? "blur(10px)" : "none",
          }}
        >
          {word}{" "}
        </motion.span>
      ));
    });
  };

  const renderBlock = (block: string, index: number) => {
    // Check if the block starts with a number followed by a dot (numbered list)
    const isNumberedList = /^\d+\.\s/.test(block);
    // Check if the block starts with an asterisk (bullet point)
    const isBulletPoint = block.startsWith("*");

    let blockClassName = "mb-4"; // Default margin bottom for paragraphs

    if (isNumberedList) {
      blockClassName += " pl-8"; // Add padding for numbered lists
    } else if (isBulletPoint) {
      blockClassName += " pl-8"; // Add padding for bullet points
    }

    return (
      <div key={index} className={blockClassName}>
        {renderWords(block)}
      </div>
    );
  };

  return (
    <div className="mt-10">
      <div className="mt-4">
        <motion.div
          ref={scope}
          className="dark:text-gray-400 text-gray-800"
        >
          {blocks.map((block, index) => renderBlock(block, index))}
        </motion.div>
      </div>
    </div>
  );
};

export default TextGenerateEffect;