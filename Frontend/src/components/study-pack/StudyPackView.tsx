"use client";

import React, { useState } from "react";
import { StudyPackOutput } from "@/types";
import { SummaryTab } from "./SummaryTab";
import { NotesTab } from "./NotesTab";
import { QuizTab } from "./QuizTab";
import { ShortAnswersTab } from "./ShortAnswersTab";
import { FlashcardsTab } from "./FlashcardsTab";
import { GlossaryTab } from "./GlossaryTab";
import { AITutorTab } from "./AITutorTab";
import { ResourcesTab } from "./ResourcesTab";
import {
  FileText,
  BookOpen,
  HelpCircle,
  FileQuestion,
  Layers,
  BookA,
  Bot,
  Calendar,
  Sparkles,
  BookMarked,
} from "lucide-react";
import { cn, formatDate } from "@/lib/utils";

interface StudyPackViewProps {
  pack: StudyPackOutput;
  initialTab?: string;
}

export function StudyPackView({ pack, initialTab = "summary" }: StudyPackViewProps) {
  const [activeTab, setActiveTab] = useState(initialTab);

  const tabs = [
    {
      id: "summary",
      label: "Summary",
      icon: FileText,
      count: undefined,
    },
    {
      id: "notes",
      label: "Core Notes",
      icon: BookOpen,
      count: pack.notes?.length,
    },
    {
      id: "quiz",
      label: "Adaptive Quiz",
      icon: HelpCircle,
      badge: "Easy · Medium · Tough",
      count: pack.mcqs?.length,
    },
    {
      id: "short_answers",
      label: "Short Answers",
      icon: FileQuestion,
      count: pack.short_answers?.length,
    },
    {
      id: "flashcards",
      label: "3D Flashcards",
      icon: Layers,
      count: pack.flashcards?.length,
    },
    {
      id: "glossary",
      label: "Glossary",
      icon: BookA,
      count: pack.glossary?.length,
    },
    {
      id: "tutor",
      label: "AI Tutor",
      icon: Bot,
      highlight: true,
    },
    {
      id: "resources",
      label: "Resources",
      icon: BookMarked,
    },
  ];

  return (
    <div className="max-w-6xl mx-auto px-6 py-8 space-y-8 animate-fade-in">
      {/* Pack Title Header Banner */}
      <div className="p-8 rounded-3xl bg-gradient-to-r from-neutral-900 via-[#101017] to-neutral-900 border border-neutral-800 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-1/4 w-72 h-72 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
                Verified Study Pack
              </span>
              <div className="flex items-center gap-1 text-xs text-neutral-400">
                <Calendar className="w-3.5 h-3.5" />
                <span>{formatDate(pack.created_at)}</span>
              </div>
            </div>

            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              {pack.title || "Study Guide & Knowledge Base"}
            </h1>

            {pack.source_file_name && (
              <p className="text-xs text-neutral-400 font-mono">
                Source: {pack.source_file_name}
              </p>
            )}
          </div>

          {/* Quick Metrics */}
          <div className="flex items-center gap-2.5 shrink-0">
            <div className="px-4 py-2.5 rounded-2xl bg-neutral-950/70 border border-neutral-800/80 text-center">
              <span className="text-base font-bold text-white block">
                {pack.mcqs?.length || 0}
              </span>
              <span className="text-[10px] text-neutral-400 uppercase tracking-wider">
                MCQs
              </span>
            </div>
            <div className="px-4 py-2.5 rounded-2xl bg-neutral-950/70 border border-neutral-800/80 text-center">
              <span className="text-base font-bold text-white block">
                {pack.flashcards?.length || 0}
              </span>
              <span className="text-[10px] text-neutral-400 uppercase tracking-wider">
                Cards
              </span>
            </div>
            <div className="px-4 py-2.5 rounded-2xl bg-neutral-950/70 border border-neutral-800/80 text-center">
              <span className="text-base font-bold text-white block">
                {pack.glossary?.length || 0}
              </span>
              <span className="text-[10px] text-neutral-400 uppercase tracking-wider">
                Terms
              </span>
            </div>
          </div>
        </div>

        {/* Minimal Navigation Bar (Tabs) */}
        <div className="flex items-center gap-1.5 overflow-x-auto pt-6 border-t border-neutral-800/80 mt-6 scrollbar-none">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all duration-150 border",
                  isActive
                    ? "bg-indigo-600/20 text-white border-indigo-500 shadow-md shadow-indigo-600/20"
                    : "bg-neutral-900/60 text-neutral-400 border-neutral-800/80 hover:text-neutral-200 hover:border-neutral-700"
                )}
              >
                <Icon
                  className={cn(
                    "w-3.5 h-3.5",
                    isActive ? "text-indigo-400" : "text-neutral-500"
                  )}
                />
                <span>{tab.label}</span>
                {tab.count !== undefined && (
                  <span
                    className={cn(
                      "px-1.5 py-0.2 rounded font-mono text-[10px]",
                      isActive
                        ? "bg-indigo-500/30 text-indigo-200"
                        : "bg-neutral-800 text-neutral-500"
                    )}
                  >
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content Panels */}
      <div className="pt-2">
        {activeTab === "summary" && (
          <SummaryTab pack={pack} onNavigateTab={(t) => setActiveTab(t)} />
        )}
        {activeTab === "notes" && <NotesTab pack={pack} />}
        {activeTab === "quiz" && <QuizTab pack={pack} />}
        {activeTab === "short_answers" && <ShortAnswersTab pack={pack} />}
        {activeTab === "flashcards" && <FlashcardsTab pack={pack} />}
        {activeTab === "glossary" && <GlossaryTab pack={pack} />}
        {activeTab === "tutor" && <AITutorTab pack={pack} />}
        {activeTab === "resources" && <ResourcesTab pack={pack} />}
      </div>
    </div>
  );
}
