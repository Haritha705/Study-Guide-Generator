"use client";

import React, { useState } from "react";
import Link from "next/link";
import { AppLayout } from "@/components/layout/AppLayout";
import { useStudyStore } from "@/stores/useStudyStore";
import {
  Layers,
  BookOpen,
  HelpCircle,
  Clock,
  PlusCircle,
  ArrowRight,
  Sparkles,
  Award,
  ChevronRight,
  Trash2,
  FileText,
  FileSpreadsheet,
  Download,
  Zap,
  ShieldCheck,
  Flame,
  Bot,
  CheckCircle2,
  TrendingUp,
  Target,
} from "lucide-react";
import { formatDate, cn } from "@/lib/utils";
import { api } from "@/lib/apiClient";
import { useUser } from "@clerk/nextjs";

export default function DashboardPage() {
  const { studyPacks, activePack, setActivePack, deletePack, user } = useStudyStore();
  const { user: clerkUser } = useUser();
  const [downloadingPackId, setDownloadingPackId] = useState<string | null>(null);

  const totalMCQs = studyPacks.reduce((acc, p) => acc + (p.mcqs?.length || 0), 0);
  const totalFlashcards = studyPacks.reduce((acc, p) => acc + (p.flashcards?.length || 0), 0);
  const totalNotes = studyPacks.reduce((acc, p) => acc + (p.notes?.length || 0), 0);
  const totalGlossary = studyPacks.reduce((acc, p) => acc + (p.glossary?.length || 0), 0);

  const handleExportPDF = async (e: React.MouseEvent, pack: any) => {
    e.stopPropagation();
    try {
      setDownloadingPackId(pack.id || "pdf");
      const blob = await api.exportPDF(pack);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${(pack.title || "study_pack").replace(/[\s\W]+/g, "_")}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert("Failed to export PDF study guide.");
    } finally {
      setDownloadingPackId(null);
    }
  };

  const handleExportCSV = async (e: React.MouseEvent, pack: any) => {
    e.stopPropagation();
    if (!pack.mcqs || pack.mcqs.length === 0) {
      alert("No MCQs available to export in this pack.");
      return;
    }
    try {
      setDownloadingPackId(pack.id || "csv");
      const blob = await api.exportCSV(pack.mcqs);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${(pack.title || "mcq_questions").replace(/[\s\W]+/g, "_")}_mcqs.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert("Failed to export CSV.");
    } finally {
      setDownloadingPackId(null);
    }
  };

  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto px-6 py-10 space-y-10 animate-fade-in">
        {/* TOP WELCOME & METRICS STRIP */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 p-8 rounded-3xl bg-gradient-to-r from-[#11111a] via-neutral-900 to-[#0e0e14] border border-white/[0.08] shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 right-10 w-80 h-80 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

          <div className="space-y-2 relative z-10">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Live Learning Studio
              </span>
              <span className="text-xs text-neutral-400">· Study Session Active</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Welcome back, {clerkUser?.firstName || clerkUser?.fullName || user.name || "Student"}
            </h1>
            <p className="text-xs md:text-sm text-neutral-400 max-w-xl leading-relaxed">
              Your personalized cognitive workspace. Select a study pack to practice adaptive MCQs,
              flip 3D recall flashcards, inspect model answers, or consult the AI tutor.
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0 relative z-10">
            <Link
              href="/create"
              className="flex items-center gap-2 px-5 py-3 rounded-xl font-semibold text-xs text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:opacity-95 shadow-lg shadow-indigo-600/30 transition-all"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Create New Pack</span>
            </Link>
          </div>
        </div>

        {/* STATS OVERVIEW CARDS */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-6 rounded-2xl bg-neutral-900/80 border border-neutral-800/80 space-y-2 hover:border-neutral-700 transition-all shadow-md">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                Study Guides
              </span>
              <BookOpen className="w-4 h-4 text-indigo-400" />
            </div>
            <p className="text-3xl font-extrabold text-white">{studyPacks.length}</p>
            <span className="text-[11px] text-neutral-400">Synthesized knowledge packs</span>
          </div>

          <div className="p-6 rounded-2xl bg-neutral-900/80 border border-neutral-800/80 space-y-2 hover:border-neutral-700 transition-all shadow-md">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                MCQs Synthesized
              </span>
              <HelpCircle className="w-4 h-4 text-purple-400" />
            </div>
            <p className="text-3xl font-extrabold text-white">{totalMCQs}</p>
            <span className="text-[11px] text-neutral-400">Easy, Medium, and Tough tiers</span>
          </div>

          <div className="p-6 rounded-2xl bg-neutral-900/80 border border-neutral-800/80 space-y-2 hover:border-neutral-700 transition-all shadow-md">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                3D Flashcards
              </span>
              <Layers className="w-4 h-4 text-amber-400" />
            </div>
            <p className="text-3xl font-extrabold text-white">{totalFlashcards}</p>
            <span className="text-[11px] text-neutral-400">Spatial recall flip cards</span>
          </div>

          <div className="p-6 rounded-2xl bg-neutral-900/80 border border-neutral-800/80 space-y-2 hover:border-neutral-700 transition-all shadow-md">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                Model Notes & Terms
              </span>
              <Award className="w-4 h-4 text-emerald-400" />
            </div>
            <p className="text-3xl font-extrabold text-white">{totalNotes + totalGlossary}</p>
            <span className="text-[11px] text-neutral-400">Verified notes & glossary items</span>
          </div>
        </div>

        {/* QUICK ACTION LAUNCHPAD */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Link
            href="/create"
            className="p-5 rounded-2xl bg-gradient-to-br from-indigo-950/30 via-neutral-900 to-neutral-950 border border-indigo-500/20 hover:border-indigo-500/50 transition-all space-y-2 group shadow-lg"
          >
            <div className="flex items-center justify-between">
              <div className="w-8 h-8 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
                <PlusCircle className="w-4 h-4" />
              </div>
              <ArrowRight className="w-4 h-4 text-neutral-600 group-hover:text-indigo-400 group-hover:translate-x-1 transition-all" />
            </div>
            <h3 className="text-sm font-bold text-white">Upload New Syllabus or PDF</h3>
            <p className="text-xs text-neutral-400">Extracts summary, questions, notes, and terms with dual AI.</p>
          </Link>

          <Link
            href="/quiz"
            className="p-5 rounded-2xl bg-gradient-to-br from-purple-950/30 via-neutral-900 to-neutral-950 border border-purple-500/20 hover:border-purple-500/50 transition-all space-y-2 group shadow-lg"
          >
            <div className="flex items-center justify-between">
              <div className="w-8 h-8 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center">
                <HelpCircle className="w-4 h-4" />
              </div>
              <ArrowRight className="w-4 h-4 text-neutral-600 group-hover:text-purple-400 group-hover:translate-x-1 transition-all" />
            </div>
            <h3 className="text-sm font-bold text-white">Adaptive Quiz Drill</h3>
            <p className="text-xs text-neutral-400">Take an instant assessment at Easy, Medium, or Tough tiers.</p>
          </Link>

          <Link
            href="/tutor"
            className="p-5 rounded-2xl bg-gradient-to-br from-emerald-950/30 via-neutral-900 to-neutral-950 border border-emerald-500/20 hover:border-emerald-500/50 transition-all space-y-2 group shadow-lg"
          >
            <div className="flex items-center justify-between">
              <div className="w-8 h-8 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
                <Bot className="w-4 h-4" />
              </div>
              <ArrowRight className="w-4 h-4 text-neutral-600 group-hover:text-emerald-400 group-hover:translate-x-1 transition-all" />
            </div>
            <h3 className="text-sm font-bold text-white">Consult Course AI Tutor</h3>
            <p className="text-xs text-neutral-400">Ask conceptual queries grounded directly in your syllabus.</p>
          </Link>
        </div>

        {/* RECENT STUDY PACKS GALLERY */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight">Your Study Packs</h2>
              <p className="text-xs text-neutral-400">Click any pack to explore all study materials</p>
            </div>
            <span className="text-xs font-mono text-neutral-400 bg-neutral-900 px-3 py-1.5 rounded-lg border border-neutral-800">
              {studyPacks.length} Guides Available
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {studyPacks.map((pack) => {
              const isCurrent = activePack?.id === pack.id;

              return (
                <div
                  key={pack.id || pack.title}
                  onClick={() => setActivePack(pack)}
                  className={cn(
                    "p-6 rounded-3xl border transition-all duration-200 space-y-4 shadow-xl cursor-pointer group relative overflow-hidden",
                    isCurrent
                      ? "bg-neutral-900/90 border-indigo-500/50 shadow-indigo-500/10"
                      : "bg-neutral-900/70 border-neutral-800 hover:border-neutral-700 hover:bg-neutral-900/90"
                  )}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1.5 flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        {isCurrent && (
                          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                            Current Active
                          </span>
                        )}
                        <span className="text-[11px] text-neutral-500 font-mono">
                          {formatDate(pack.created_at)}
                        </span>
                      </div>
                      <h3 className="text-base font-bold text-white truncate group-hover:text-indigo-300 transition-colors">
                        {pack.title}
                      </h3>
                      {pack.source_file_name && (
                        <p className="text-xs text-neutral-400 font-mono truncate">
                          {pack.source_file_name}
                        </p>
                      )}
                    </div>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (pack.id) deletePack(pack.id);
                      }}
                      className="text-neutral-600 hover:text-rose-400 p-1.5 rounded-lg hover:bg-neutral-800 transition-colors opacity-0 group-hover:opacity-100 shrink-0"
                      title="Delete study pack"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <p className="text-xs text-neutral-300 line-clamp-2 leading-relaxed font-normal">
                    {pack.summary}
                  </p>

                  {/* Components Badges */}
                  <div className="flex flex-wrap items-center gap-1.5 pt-1">
                    <span className="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-neutral-950 text-neutral-300 border border-neutral-800">
                      {pack.mcqs?.length || 0} MCQs
                    </span>
                    <span className="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-neutral-950 text-neutral-300 border border-neutral-800">
                      {pack.flashcards?.length || 0} Flashcards
                    </span>
                    <span className="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-neutral-950 text-neutral-300 border border-neutral-800">
                      {pack.notes?.length || 0} Notes
                    </span>
                    <span className="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-neutral-950 text-neutral-300 border border-neutral-800">
                      {pack.glossary?.length || 0} Terms
                    </span>
                  </div>

                  {/* Bottom Actions Bar */}
                  <div className="pt-3 border-t border-neutral-800/80 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={(e) => handleExportPDF(e, pack)}
                        className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-medium text-neutral-400 hover:text-white bg-neutral-950 border border-neutral-800 hover:border-neutral-700 transition-colors"
                        title="Download PDF study guide"
                      >
                        <FileText className="w-3 h-3 text-rose-400" />
                        <span>PDF</span>
                      </button>

                      <button
                        onClick={(e) => handleExportCSV(e, pack)}
                        className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-medium text-neutral-400 hover:text-white bg-neutral-950 border border-neutral-800 hover:border-neutral-700 transition-colors"
                        title="Download MCQs as CSV"
                      >
                        <FileSpreadsheet className="w-3 h-3 text-emerald-400" />
                        <span>CSV</span>
                      </button>
                    </div>

                    <Link
                      href={`/study-pack/${pack.id || "current"}`}
                      className="flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
                    >
                      <span>Open Studio</span>
                      <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
