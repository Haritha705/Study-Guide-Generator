"use client";

import React, { useState } from "react";
import { StudyPackOutput } from "@/types";
import {
  FileQuestion,
  Eye,
  EyeOff,
  CheckCircle2,
  Sparkles,
  Award,
} from "lucide-react";
import { cn } from "@/lib/utils";

export function ShortAnswersTab({ pack }: { pack: StudyPackOutput }) {
  const saqs = pack.short_answers || [];
  // Default to showing answers so user can immediately view model answers
  const [revealedAnswers, setRevealedAnswers] = useState<Record<number, boolean>>({});
  const [practiceMode, setPracticeMode] = useState(false);
  const [userDrafts, setUserDrafts] = useState<Record<number, string>>({});

  const toggleReveal = (id: number) => {
    setRevealedAnswers((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const handleDraftChange = (id: number, text: string) => {
    setUserDrafts((prev) => ({
      ...prev,
      [id]: text,
    }));
  };

  if (!saqs || saqs.length === 0) {
    return (
      <div className="p-10 text-center rounded-2xl bg-neutral-900 border border-neutral-800 text-neutral-400">
        No short-answer questions available in this pack.
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">
            Short-Answer Conceptual Questions & Model Answers
          </h2>
          <p className="text-xs text-neutral-400">
            Authoritative model answers and analytical grading rubrics
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setPracticeMode(!practiceMode)}
            className={cn(
              "px-3.5 py-1.5 rounded-xl text-xs font-semibold border transition-all",
              practiceMode
                ? "bg-indigo-600/20 text-indigo-300 border-indigo-500/40"
                : "bg-neutral-900 text-neutral-400 border-neutral-800 hover:text-white"
            )}
          >
            {practiceMode ? "Practice Mode Active (Answers Hidden)" : "Toggle Self-Test Mode"}
          </button>
          <span className="text-xs font-mono text-neutral-400 bg-neutral-900 px-3 py-1.5 rounded-lg border border-neutral-800">
            {saqs.length} Questions
          </span>
        </div>
      </div>

      <div className="space-y-6">
        {saqs.map((saq: any, idx: number) => {
          const saqKey = saq.id !== undefined ? saq.id : idx;
          // In normal mode answers are shown; in practice mode they are hidden unless toggled
          const isRevealed = practiceMode ? !!revealedAnswers[saqKey] : true;
          const draft = userDrafts[saqKey] || "";
          
          const modelAnswer =
            saq.model_answer ||
            saq.sample_answer ||
            saq.answer ||
            saq.explanation ||
            "Model answer not provided.";

          const rubrics: string[] = Array.isArray(saq.rubric)
            ? saq.rubric
            : typeof saq.rubric === "string"
            ? [saq.rubric]
            : [];

          return (
            <div
              key={saqKey}
              className="p-6 rounded-2xl bg-neutral-900/80 border border-neutral-800 space-y-4 shadow-lg"
            >
              {/* Question Header */}
              <div className="flex items-start gap-3">
                <span className="w-7 h-7 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 font-mono text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                  Q{idx + 1}
                </span>
                <div className="flex-1 space-y-1.5">
                  <div className="flex items-center gap-2">
                    {saq.difficulty && (
                      <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                        {saq.difficulty}
                      </span>
                    )}
                    {saq.topic && (
                      <span className="text-[10px] font-mono text-neutral-400 bg-neutral-800 px-2 py-0.5 rounded border border-neutral-700/50">
                        {saq.topic}
                      </span>
                    )}
                  </div>
                  <h3 className="text-base font-semibold text-white leading-relaxed">
                    {saq.question}
                  </h3>
                </div>
              </div>

              {/* Practice Drafting Box (Shown in self-test mode) */}
              {practiceMode && (
                <div className="space-y-2 pt-1">
                  <textarea
                    rows={3}
                    value={draft}
                    onChange={(e) => handleDraftChange(saqKey, e.target.value)}
                    placeholder="Draft your solution here before viewing the model answer..."
                    className="w-full p-3.5 bg-neutral-950/80 border border-neutral-800 rounded-xl text-xs text-white placeholder:text-neutral-600 focus:outline-none focus:border-indigo-500 transition-colors leading-relaxed"
                  />
                  <div className="flex justify-end">
                    <button
                      type="button"
                      onClick={() => toggleReveal(saqKey)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-neutral-300 bg-neutral-800 hover:bg-neutral-700 border border-neutral-700 transition-colors"
                    >
                      {isRevealed ? (
                        <>
                          <EyeOff className="w-3.5 h-3.5" />
                          <span>Hide Model Answer</span>
                        </>
                      ) : (
                        <>
                          <Eye className="w-3.5 h-3.5" />
                          <span>Check Model Answer</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}

              {/* Model Answer Card (Prominently displayed) */}
              {isRevealed && (
                <div className="p-5 rounded-2xl bg-indigo-950/20 border border-indigo-500/30 space-y-3 animate-fade-in">
                  <div className="flex items-center gap-2 text-xs font-bold text-indigo-300 uppercase tracking-wider">
                    <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Official Model Answer</span>
                  </div>
                  <p className="text-sm text-neutral-200 leading-relaxed font-normal bg-neutral-900/80 p-4 rounded-xl border border-neutral-800/80">
                    {modelAnswer}
                  </p>

                  {/* Rubric Checklist if available */}
                  {rubrics.length > 0 && (
                    <div className="space-y-2 pt-2 border-t border-indigo-500/20">
                      <span className="text-[11px] font-bold text-neutral-300 uppercase tracking-wider">
                        Grading Rubric Criteria:
                      </span>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {rubrics.map((item, rIdx) => (
                          <div
                            key={rIdx}
                            className="flex items-start gap-2 p-2.5 rounded-lg bg-neutral-900/60 border border-neutral-800 text-xs text-neutral-300"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
                            <span>{item}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
