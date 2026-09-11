"use client";

import React, { useState, useEffect, useMemo } from "react";
import { StudyPackOutput, FlashcardItem } from "@/types";
import {
  Rotate3D,
  ChevronLeft,
  ChevronRight,
  Check,
  RotateCcw,
  Sparkles,
  Layers,
  HelpCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";

export function FlashcardsTab({ pack }: { pack: StudyPackOutput }) {
  // If pack.flashcards is empty, seamlessly use glossary items as flashcards
  const flashcards: FlashcardItem[] = useMemo(() => {
    if (pack.flashcards && pack.flashcards.length > 0) {
      return pack.flashcards;
    }
    if (pack.glossary && pack.glossary.length > 0) {
      return pack.glossary.map((g, idx) => ({
        id: idx + 1,
        front: g.term,
        back: g.definition,
        term: g.term,
        definition: g.definition,
        topic: "Glossary Concept",
      }));
    }
    return [];
  }, [pack.flashcards, pack.glossary]);

  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [masteredIds, setMasteredIds] = useState<Record<number, boolean>>({});

  const currentCard: FlashcardItem | undefined = flashcards[currentIndex];
  const frontText =
    currentCard?.front ||
    currentCard?.term ||
    (currentCard as any)?.question ||
    "Core Concept";
  const backText =
    currentCard?.back ||
    currentCard?.definition ||
    (currentCard as any)?.answer ||
    (currentCard as any)?.explanation ||
    "Detailed Explanation";
  const cardKey = currentCard?.id ?? currentIndex;

  useEffect(() => {
    setIsFlipped(false);
  }, [currentIndex]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === "Space") {
        e.preventDefault();
        setIsFlipped((prev) => !prev);
      } else if (e.code === "ArrowRight") {
        if (currentIndex < flashcards.length - 1) {
          setCurrentIndex((prev) => prev + 1);
        }
      } else if (e.code === "ArrowLeft") {
        if (currentIndex > 0) {
          setCurrentIndex((prev) => prev - 1);
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [currentIndex, flashcards.length]);

  const toggleMastered = (id: number) => {
    setMasteredIds((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  if (flashcards.length === 0) {
    return (
      <div className="p-10 text-center rounded-2xl bg-neutral-900 border border-neutral-800 text-neutral-400">
        No flashcards available in this pack.
      </div>
    );
  }

  const masteredCount = Object.values(masteredIds).filter(Boolean).length;

  return (
    <div className="space-y-6 max-w-2xl mx-auto animate-fade-in select-none">
      {/* Top Controls & Status */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">
            3D Active Recall Flashcards
          </h2>
          <p className="text-xs text-neutral-400">
            Click card or press <kbd className="px-1 py-0.5 rounded bg-neutral-800 border border-neutral-700 font-mono text-[10px]">Space</kbd> to flip
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-emerald-400 bg-emerald-950/30 px-2.5 py-1 rounded-lg border border-emerald-800/40">
            {masteredCount} of {flashcards.length} Mastered
          </span>
        </div>
      </div>

      {/* 3D Flip Card Container */}
      <div
        className="w-full h-80 perspective-1000 cursor-pointer"
        onClick={() => setIsFlipped(!isFlipped)}
      >
        <div
          className={cn(
            "relative w-full h-full duration-500 transform-style-3d transition-transform rounded-3xl shadow-2xl border",
            isFlipped ? "rotate-y-180" : "",
            masteredIds[cardKey]
              ? "border-emerald-500/40"
              : "border-neutral-800 hover:border-neutral-700"
          )}
        >
          {/* FRONT FACE */}
          <div className="absolute inset-0 w-full h-full backface-hidden rounded-3xl bg-gradient-to-br from-neutral-900 via-neutral-900 to-[#121218] p-8 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-medium px-2.5 py-1 rounded-md bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                {currentCard?.topic || "Concept"}
              </span>
              <span className="text-xs font-mono text-neutral-500">
                {currentIndex + 1} / {flashcards.length}
              </span>
            </div>

            <div className="flex-1 flex items-center justify-center text-center px-4">
              <p className="text-lg md:text-xl font-medium text-white leading-relaxed">
                {frontText}
              </p>
            </div>

            <div className="flex items-center justify-center gap-2 text-xs text-neutral-500">
              <Rotate3D className="w-3.5 h-3.5" />
              <span>Click or Spacebar to reveal answer</span>
            </div>
          </div>

          {/* BACK FACE */}
          <div className="absolute inset-0 w-full h-full backface-hidden rotate-y-180 rounded-3xl bg-gradient-to-br from-[#121020] via-neutral-900 to-neutral-950 p-8 flex flex-col justify-between border border-indigo-500/30">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-medium px-2.5 py-1 rounded-md bg-purple-500/10 text-purple-400 border border-purple-500/20">
                Definition & Solution
              </span>
              <span className="text-xs font-mono text-neutral-500">
                {currentIndex + 1} / {flashcards.length}
              </span>
            </div>

            <div className="flex-1 flex items-center justify-center text-center px-4">
              <p className="text-base md:text-lg font-medium text-indigo-100 leading-relaxed">
                {backText}
              </p>
            </div>

            <div className="flex items-center justify-center gap-2 text-xs text-indigo-400/70">
              <Rotate3D className="w-3.5 h-3.5" />
              <span>Click or Spacebar to flip back</span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation & Mastery Controls */}
      <div className="flex items-center justify-between pt-2">
        <button
          type="button"
          onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
          disabled={currentIndex === 0}
          className="p-3 rounded-xl bg-neutral-900 border border-neutral-800 text-neutral-300 hover:text-white disabled:opacity-40 transition-colors"
          title="Previous Card (Left Arrow)"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => toggleMastered(cardKey)}
            className={cn(
              "flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold transition-all border",
              masteredIds[cardKey]
                ? "bg-emerald-950/50 text-emerald-300 border-emerald-800 shadow-md shadow-emerald-950/50"
                : "bg-neutral-900 text-neutral-300 hover:text-white border-neutral-800 hover:border-neutral-700"
            )}
          >
            <Check className="w-4 h-4 text-emerald-400" />
            <span>
              {masteredIds[cardKey] ? "Marked as Mastered" : "Mark as Mastered"}
            </span>
          </button>
        </div>

        <button
          type="button"
          onClick={() =>
            setCurrentIndex((prev) => Math.min(flashcards.length - 1, prev + 1))
          }
          disabled={currentIndex === flashcards.length - 1}
          className="p-3 rounded-xl bg-neutral-900 border border-neutral-800 text-neutral-300 hover:text-white disabled:opacity-40 transition-colors"
          title="Next Card (Right Arrow)"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
