"use client";

import React, { useState } from "react";
import { StudyPackOutput } from "@/types";
import {
  BookOpen,
  Clock,
  ListOrdered,
  Copy,
  Check,
  Sparkles,
  ArrowRight,
} from "lucide-react";

export function SummaryTab({
  pack,
  onNavigateTab,
}: {
  pack: StudyPackOutput;
  onNavigateTab?: (tab: string) => void;
}) {
  const [copied, setCopied] = useState(false);

  const wordCount = pack.summary.split(/\s+/).length;
  const readingTime = Math.max(1, Math.round(wordCount / 200));

  const handleCopy = () => {
    navigator.clipboard.writeText(pack.summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-8 animate-fade-in max-w-4xl">
      {/* Executive Summary Card */}
      <div className="p-8 rounded-2xl bg-neutral-900/70 border border-neutral-800/80 shadow-xl space-y-5 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-600/5 rounded-full blur-3xl pointer-events-none" />

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-white">Executive Summary</h2>
              <p className="text-xs text-neutral-400">AI-synthesized high-level conceptual core</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-xs text-neutral-400 bg-neutral-800/60 px-3 py-1.5 rounded-lg border border-neutral-700/40">
              <Clock className="w-3.5 h-3.5 text-neutral-400" />
              <span>{readingTime} min read</span>
            </div>

            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-neutral-300 bg-neutral-800/60 hover:bg-neutral-800 hover:text-white border border-neutral-700/40 transition-colors"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy</span>
                </>
              )}
            </button>
          </div>
        </div>

        <div className="text-sm md:text-base leading-relaxed text-neutral-300 font-normal space-y-4 pt-1">
          {pack.summary.split("\n\n").map((para, i) => (
            <p key={i} className="tracking-normal">
              {para}
            </p>
          ))}
        </div>
      </div>

      {/* Recommended Study Sequence */}
      {pack.recommended_study_order && pack.recommended_study_order.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-neutral-200">
            <ListOrdered className="w-4 h-4 text-indigo-400" />
            <span>Optimal Study Order (Cognitive Progression)</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {pack.recommended_study_order.map((step, idx) => (
              <div
                key={idx}
                className="flex items-start gap-3 p-4 rounded-xl bg-neutral-900/50 border border-neutral-800 hover:border-neutral-700 transition-colors group"
              >
                <span className="w-6 h-6 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center font-mono text-xs font-semibold shrink-0 mt-0.5">
                  0{idx + 1}
                </span>
                <p className="text-xs text-neutral-300 leading-relaxed font-medium">
                  {step}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Launchpad to Quiz or Flashcards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
        <div
          onClick={() => onNavigateTab && onNavigateTab("quiz")}
          className="p-5 rounded-xl bg-gradient-to-br from-indigo-950/40 to-neutral-900 border border-indigo-500/30 hover:border-indigo-500/60 cursor-pointer transition-all group"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold uppercase text-indigo-400 tracking-wider">
              Test Retention
            </span>
            <ArrowRight className="w-4 h-4 text-indigo-400 group-hover:translate-x-1 transition-transform" />
          </div>
          <h3 className="text-base font-semibold text-white">Adaptive Quiz Challenge</h3>
          <p className="text-xs text-neutral-400 mt-1">
            {pack.mcqs?.length || 0} Questions across Easy, Medium, and Tough tiers with instant feedback.
          </p>
        </div>

        <div
          onClick={() => onNavigateTab && onNavigateTab("flashcards")}
          className="p-5 rounded-xl bg-gradient-to-br from-purple-950/40 to-neutral-900 border border-purple-500/30 hover:border-purple-500/60 cursor-pointer transition-all group"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold uppercase text-purple-400 tracking-wider">
              Active Recall
            </span>
            <ArrowRight className="w-4 h-4 text-purple-400 group-hover:translate-x-1 transition-transform" />
          </div>
          <h3 className="text-base font-semibold text-white">3D Interactive Flashcards</h3>
          <p className="text-xs text-neutral-400 mt-1">
            {pack.flashcards?.length || 0} Flashcards to master definitions and core principles.
          </p>
        </div>
      </div>
    </div>
  );
}
