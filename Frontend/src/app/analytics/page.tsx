"use client";

import React from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { useStudyStore } from "@/stores/useStudyStore";
import {
  BarChart3,
  TrendingUp,
  Award,
  CheckCircle2,
  Zap,
  ShieldCheck,
  Flame,
  Clock,
  Target,
} from "lucide-react";

export default function AnalyticsPage() {
  const { studyPacks, activePack } = useStudyStore();

  const totalMCQs = studyPacks.reduce((acc, p) => acc + (p.mcqs?.length || 0), 0);
  const totalCards = studyPacks.reduce((acc, p) => acc + (p.flashcards?.length || 0), 0);

  return (
    <AppLayout>
      <div className="max-w-5xl mx-auto px-6 py-8 space-y-8 animate-fade-in">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold uppercase tracking-wider">
            <BarChart3 className="w-3.5 h-3.5" />
            Performance & Mastery
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Learning Analytics & Adaptive Trajectory
          </h1>
          <p className="text-xs text-neutral-400">
            Real-time breakdown of comprehension across performance tiers
          </p>
        </div>

        {/* Big Performance Dial Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl bg-neutral-900/80 border border-neutral-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                Overall Accuracy
              </span>
              <Target className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-white">84%</span>
              <span className="text-xs text-emerald-400 font-semibold">+6% vs last week</span>
            </div>
            <div className="w-full h-2 bg-neutral-800 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 w-[84%]" />
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-neutral-900/80 border border-neutral-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                Questions Attempted
              </span>
              <Award className="w-4 h-4 text-purple-400" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-white">{totalMCQs}</span>
              <span className="text-xs text-neutral-400">across {studyPacks.length} packs</span>
            </div>
            <p className="text-[11px] text-neutral-500">
              Covers Easy, Medium, and Tough difficulty levels
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-neutral-900/80 border border-neutral-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                Active Recall Retention
              </span>
              <Clock className="w-4 h-4 text-amber-400" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-white">92%</span>
              <span className="text-xs text-emerald-400 font-semibold">High Stability</span>
            </div>
            <p className="text-[11px] text-neutral-500">
              {totalCards} 3D flashcards engaged in spaced intervals
            </p>
          </div>
        </div>

        {/* Tier Progression Breakdown */}
        <div className="p-6 rounded-3xl bg-neutral-900/80 border border-neutral-800 space-y-5">
          <h2 className="text-base font-semibold text-white">
            Difficulty Tier Progression
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-2xl bg-neutral-950/70 border border-neutral-800/80 space-y-2">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-xs font-semibold text-neutral-200">
                  <Zap className="w-3.5 h-3.5 text-indigo-400" />
                  Easy Tier (Recall)
                </span>
                <span className="text-xs font-mono font-bold text-emerald-400">95%</span>
              </div>
              <div className="w-full h-1.5 bg-neutral-800 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-400 w-[95%]" />
              </div>
              <p className="text-[10px] text-neutral-500">Direct facts and definitions</p>
            </div>

            <div className="p-4 rounded-2xl bg-neutral-950/70 border border-neutral-800/80 space-y-2">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-xs font-semibold text-neutral-200">
                  <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
                  Medium Tier (Application)
                </span>
                <span className="text-xs font-mono font-bold text-indigo-400">82%</span>
              </div>
              <div className="w-full h-1.5 bg-neutral-800 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-400 w-[82%]" />
              </div>
              <p className="text-[10px] text-neutral-500">Conceptual mechanics and problem solving</p>
            </div>

            <div className="p-4 rounded-2xl bg-neutral-950/70 border border-neutral-800/80 space-y-2">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-xs font-semibold text-neutral-200">
                  <Flame className="w-3.5 h-3.5 text-amber-400" />
                  Tough Tier (Synthesis)
                </span>
                <span className="text-xs font-mono font-bold text-amber-400">74%</span>
              </div>
              <div className="w-full h-1.5 bg-neutral-800 rounded-full overflow-hidden">
                <div className="h-full bg-amber-400 w-[74%]" />
              </div>
              <p className="text-[10px] text-neutral-500">Complex proofs, tradeoffs & deep analysis</p>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
