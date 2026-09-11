"use client";

import React from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { AITutorTab } from "@/components/study-pack/AITutorTab";
import { useStudyStore } from "@/stores/useStudyStore";
import Link from "next/link";
import { Bot, PlusCircle } from "lucide-react";

export default function TutorPage() {
  const { activePack } = useStudyStore();

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto px-6 py-8 space-y-6 animate-fade-in">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 text-purple-400 text-xs font-semibold uppercase tracking-wider">
            <Bot className="w-3.5 h-3.5" />
            AI Course Tutor
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Interactive AI Study Tutor
          </h1>
          <p className="text-xs text-neutral-400">
            {activePack
              ? `Grounding context: ${activePack.title}`
              : "Ask questions, explore derivations, and get step-by-step guidance."}
          </p>
        </div>

        {activePack ? (
          <AITutorTab pack={activePack} />
        ) : (
          <div className="p-12 text-center rounded-2xl bg-neutral-900 border border-neutral-800 space-y-4">
            <Bot className="w-12 h-12 text-neutral-600 mx-auto" />
            <h3 className="text-base font-semibold text-white">No Active Study Pack Selected</h3>
            <p className="text-xs text-neutral-400 max-w-sm mx-auto">
              Please generate or choose a study pack to initialize the grounded AI tutor.
            </p>
            <Link
              href="/create"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 text-white hover:bg-indigo-500 transition-colors"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Create Study Pack</span>
            </Link>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
