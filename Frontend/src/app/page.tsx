"use client";

import React, { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { AppLayout } from "@/components/layout/AppLayout";
import { useStudyStore } from "@/stores/useStudyStore";
import {
  Sparkles,
  ArrowRight,
  BookOpen,
  HelpCircle,
  Layers,
  Bot,
  Zap,
  ShieldCheck,
  Flame,
  FileText,
  UploadCloud,
  CheckCircle2,
  TrendingUp,
  Cpu,
  GraduationCap,
  Play,
  Rotate3D,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Show, UserButton, SignInButton, SignUpButton } from "@clerk/nextjs";

export default function HomePage() {
  const { studyPacks, activePack, setActivePack } = useStudyStore();
  const [activePreviewTab, setActivePreviewTab] = useState<"summary" | "quiz" | "flashcards" | "tutor">("quiz");

  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto px-6 py-10 space-y-16">
        {/* HERO SECTION */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="relative rounded-3xl bg-gradient-to-b from-[#11111a] via-[#0d0d14] to-[#09090d] border border-white/[0.08] p-8 md:p-14 overflow-hidden shadow-2xl premium-glass"
        >
          {/* Subtle Ambient Light Glows */}
          <motion.div 
            animate={{ scale: [1, 1.1, 1], opacity: [0.15, 0.3, 0.15] }}
            transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
            className="absolute -top-24 -left-24 w-96 h-96 bg-indigo-600 rounded-full blur-[100px] pointer-events-none" 
          />
          <motion.div 
            animate={{ scale: [1, 1.2, 1], opacity: [0.15, 0.25, 0.15] }}
            transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 1 }}
            className="absolute top-1/2 -right-24 w-96 h-96 bg-purple-600 rounded-full blur-[100px] pointer-events-none" 
          />

          <div className="relative z-10 max-w-3xl space-y-6">
            {/* Top Pill */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-semibold tracking-wide">
              <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
              <span>StudyPack AI · Dual Engine (Gemini + Mistral)</span>
            </div>

            {/* Headline */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-white tracking-tight leading-[1.1]">
              The Intelligent Study Guide &{" "}
              <span className="bg-gradient-to-r from-indigo-400 via-purple-300 to-indigo-200 bg-clip-text text-transparent">
                Adaptive Assessment
              </span>{" "}
              Studio
            </h1>

            {/* Subtitle */}
            <p className="text-sm md:text-base text-neutral-300 leading-relaxed font-normal max-w-2xl">
              Turn lecture notes, syllabus chapters, and PDFs into verified executive summaries,
              performance-tiered MCQs (<strong className="text-white">Easy</strong>, <strong className="text-white">Medium</strong>, <strong className="text-white">Tough</strong>),
              3D interactive flashcards, model answers with rubrics, and a grounded AI course tutor.
            </p>

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center gap-4 pt-2">
              <Link
                href="/create"
                className="flex items-center gap-2.5 px-6 py-3.5 rounded-xl font-semibold text-sm text-white bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:opacity-95 shadow-xl shadow-indigo-600/30 transition-all group"
              >
                <UploadCloud className="w-4 h-4" />
                <span>Upload PDF & Synthesize</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>

              <Show when="signed-in">
                <Link
                  href="/dashboard"
                  className="flex items-center gap-2 px-5 py-3.5 rounded-xl font-semibold text-sm text-neutral-200 bg-neutral-900/90 hover:bg-neutral-800 border border-neutral-700/80 transition-colors"
                >
                  <span>Go to Dashboard</span>
                  <ArrowRight className="w-4 h-4 text-indigo-400" />
                </Link>
              </Show>

              <Show when="signed-out">
                <Link
                  href="/sign-in"
                  className="flex items-center gap-2 px-5 py-3.5 rounded-xl font-semibold text-sm text-neutral-200 bg-neutral-900/90 hover:bg-neutral-800 border border-neutral-700/80 transition-colors"
                >
                  <span>Sign In</span>
                </Link>
                <Link
                  href="/sign-up"
                  className="flex items-center gap-2 px-5 py-3.5 rounded-xl font-semibold text-sm text-indigo-300 bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/30 transition-colors"
                >
                  <span>Sign Up Free</span>
                </Link>
              </Show>
            </div>
          </div>

          {/* Quick Metrics Bar */}
          <div className="mt-12 pt-8 border-t border-white/[0.08] grid grid-cols-2 sm:grid-cols-4 gap-6">
            <div>
              <span className="text-xl md:text-2xl font-bold text-white block">Easy · Medium · Tough</span>
              <span className="text-xs text-neutral-400 mt-0.5 block">Adaptive MCQ Tiers</span>
            </div>
            <div>
              <span className="text-xl md:text-2xl font-bold text-white block">3D Spatial</span>
              <span className="text-xs text-neutral-400 mt-0.5 block">Active Recall Flashcards</span>
            </div>
            <div>
              <span className="text-xl md:text-2xl font-bold text-white block">Model + Rubric</span>
              <span className="text-xs text-neutral-400 mt-0.5 block">Short Answer Grading</span>
            </div>
            <div>
              <span className="text-xl md:text-2xl font-bold text-white block">RAG Grounded</span>
              <span className="text-xs text-neutral-400 mt-0.5 block">Context-Aware AI Tutor</span>
            </div>
          </div>
        </motion.div>

        {/* DYNAMIC INTERACTIVE FEATURE PREVIEW */}
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.7 }}
          className="space-y-6"
        >
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">
                Interactive Capability Sandbox
              </span>
              <h2 className="text-2xl font-bold text-white tracking-tight">
                Preview What StudyPack AI Synthesizes
              </h2>
            </div>

            {/* Preview Tabs */}
            <div className="flex items-center gap-1.5 p-1 bg-neutral-900 border border-neutral-800 rounded-xl overflow-x-auto scrollbar-none">
              {(
                [
                  { id: "quiz", label: "Adaptive MCQs", icon: HelpCircle },
                  { id: "summary", label: "Executive Summary", icon: FileText },
                  { id: "flashcards", label: "3D Flashcards", icon: Layers },
                  { id: "tutor", label: "AI Course Tutor", icon: Bot },
                ] as const
              ).map((tab) => {
                const Icon = tab.icon;
                const isActive = activePreviewTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActivePreviewTab(tab.id)}
                    className={cn(
                      "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all",
                      isActive
                        ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30 font-semibold"
                        : "text-neutral-400 hover:text-white"
                    )}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Dynamic Preview Container */}
          <div className="p-8 rounded-3xl bg-neutral-900/80 border border-neutral-800 shadow-xl min-h-[320px] flex items-center justify-center relative overflow-hidden">
            {activePreviewTab === "quiz" && (
              <div className="w-full max-w-2xl space-y-4 animate-fade-in">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-0.5 rounded-md text-[10px] font-bold uppercase bg-amber-500/15 text-amber-300 border border-amber-500/30 flex items-center gap-1">
                      <Flame className="w-3 h-3" /> Tough Tier
                    </span>
                    <span className="text-xs text-neutral-400">Deep Reasoning & Synthesis</span>
                  </div>
                  <span className="text-xs font-mono text-neutral-500">Question 3 of 10</span>
                </div>
                <h4 className="text-base font-semibold text-white">
                  Why do residual skip connections enable training in networks with hundreds of layers?
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
                  <div className="p-3 rounded-xl bg-neutral-950/80 border border-neutral-800 text-xs text-neutral-300">
                    A. They eliminate backpropagation matrix operations
                  </div>
                  <div className="p-3 rounded-xl bg-indigo-500/15 border border-indigo-500/50 text-xs text-indigo-200 font-medium flex items-center justify-between">
                    <span>B. Additive identity ensures non-vanishing gradient</span>
                    <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                  </div>
                  <div className="p-3 rounded-xl bg-neutral-950/80 border border-neutral-800 text-xs text-neutral-300">
                    C. They convert non-convex loss into quadratic form
                  </div>
                  <div className="p-3 rounded-xl bg-neutral-950/80 border border-neutral-800 text-xs text-neutral-300">
                    D. They constrain all weight eigenvalues strictly to 1.0
                  </div>
                </div>
              </div>
            )}

            {activePreviewTab === "summary" && (
              <div className="w-full max-w-2xl space-y-3 animate-fade-in">
                <div className="flex items-center gap-2 text-xs text-neutral-400">
                  <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                  <span>AI Synthesized Core Extraction</span>
                </div>
                <h4 className="text-base font-semibold text-white">
                  Neural Networks, Backpropagation & Optimization Dynamics
                </h4>
                <p className="text-xs md:text-sm text-neutral-300 leading-relaxed">
                  Artificial neural networks approximate complex non-linear mappings by composing affine transformations with non-linear activation functions. Optimization occurs via gradient descent where error derivatives are systematically propagated backward using the differential chain rule, while adaptive optimizers dynamically calibrate per-parameter learning steps.
                </p>
                <div className="flex items-center gap-2 pt-2">
                  <span className="px-2 py-0.5 rounded bg-neutral-800 text-neutral-400 text-[10px] font-mono">
                    3 min read
                  </span>
                  <span className="px-2 py-0.5 rounded bg-neutral-800 text-neutral-400 text-[10px] font-mono">
                    7 Step Study Order
                  </span>
                </div>
              </div>
            )}

            {activePreviewTab === "flashcards" && (
              <div className="w-full max-w-md animate-fade-in">
                <div className="p-6 rounded-2xl bg-gradient-to-br from-[#13121d] via-neutral-900 to-[#101017] border border-indigo-500/30 text-center space-y-4 shadow-xl">
                  <span className="text-[10px] font-mono uppercase text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                    Concept Prompt
                  </span>
                  <p className="text-base font-semibold text-white leading-relaxed">
                    What mathematical principle underpins the backpropagation algorithm?
                  </p>
                  <div className="pt-2 border-t border-neutral-800 flex items-center justify-between text-xs text-neutral-400">
                    <span className="flex items-center gap-1 text-indigo-300">
                      <Rotate3D className="w-3.5 h-3.5" /> 3D Flip Enabled
                    </span>
                    <span className="font-mono text-emerald-400 text-[11px]">Answer: Differential Chain Rule</span>
                  </div>
                </div>
              </div>
            )}

            {activePreviewTab === "tutor" && (
              <div className="w-full max-w-xl space-y-3 animate-fade-in">
                <div className="p-3 rounded-xl bg-indigo-600 text-white text-xs max-w-md ml-auto">
                  Can you give an intuition for why Sigmoid causes vanishing gradients?
                </div>
                <div className="p-4 rounded-xl bg-neutral-950 border border-neutral-800 text-neutral-200 text-xs leading-relaxed max-w-lg mr-auto space-y-2">
                  <p>
                    Think of Sigmoid as compressing an infinite number line into a tiny window between 0 and 1. The maximum slope of that curve is only 0.25. When you chain several layers together, multiplying numbers less than 0.25 (like 0.25 × 0.25 × 0.25...) shrinks the signal down to practically zero!
                  </p>
                  <span className="text-[10px] font-mono text-indigo-400 block pt-1 border-t border-neutral-800">
                    Grounding Confidence: 96% · Verified from source slides
                  </span>
                </div>
              </div>
            )}
          </div>
        </motion.div>

        {/* ACTIVE STUDY PACK JUMP BAR */}
        {activePack && (
          <div className="p-6 rounded-3xl bg-neutral-900/60 border border-neutral-800/80 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="space-y-1 text-center md:text-left">
              <span className="text-[11px] font-bold text-indigo-400 uppercase tracking-wider">
                Current Active Session
              </span>
              <h3 className="text-base font-bold text-white">{activePack.title}</h3>
              <p className="text-xs text-neutral-400">
                {activePack.mcqs?.length || 0} Questions · {activePack.flashcards?.length || 0} Flashcards · {activePack.notes?.length || 0} Notes
              </p>
            </div>

            <Link
              href={`/study-pack/${activePack.id || "current"}`}
              className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all flex items-center gap-2"
            >
              <span>Open Study Studio</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
