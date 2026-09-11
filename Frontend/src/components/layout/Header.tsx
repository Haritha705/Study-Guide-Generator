"use client";

import React, { useState } from "react";
import { useStudyStore } from "@/stores/useStudyStore";
import { api } from "@/lib/apiClient";
import {
  Download,
  FileSpreadsheet,
  FileText,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { UserButton, Show } from "@clerk/nextjs";

export function Header() {
  const { activePack } = useStudyStore();
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [isExportingCsv, setIsExportingCsv] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showNotification = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleExportPDF = async () => {
    if (!activePack) return;
    try {
      setIsExportingPdf(true);
      const blob = await api.exportPDF(activePack);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${(activePack.title || "study_pack").replace(/[\s\W]+/g, "_")}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      showNotification("PDF study guide downloaded successfully");
    } catch (err: any) {
      showNotification(`Export failed: ${err.message || "Unknown error"}`);
    } finally {
      setIsExportingPdf(false);
    }
  };

  const handleExportCSV = async () => {
    if (!activePack || !activePack.mcqs || activePack.mcqs.length === 0) {
      showNotification("No MCQs available to export");
      return;
    }
    try {
      setIsExportingCsv(true);
      const blob = await api.exportCSV(activePack.mcqs);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${(activePack.title || "mcq_questions").replace(/[\s\W]+/g, "_")}_mcqs.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      showNotification("MCQs exported to CSV successfully");
    } catch (err: any) {
      showNotification(`Export failed: ${err.message || "Unknown error"}`);
    } finally {
      setIsExportingCsv(false);
    }
  };

  return (
    <header className="h-16 border-b border-neutral-800/80 bg-[#0d0d11]/80 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-20">
      {/* Active Pack Info */}
      <div className="flex items-center gap-3 min-w-0">
        <div className="flex flex-col min-w-0">
          <div className="flex items-center gap-2">
            <h1 className="text-sm font-semibold text-neutral-100 truncate max-w-md">
              {activePack?.title || "Welcome to StudyPack AI"}
            </h1>
            {activePack?.source_file_name && (
              <span className="px-2 py-0.5 text-[10px] font-mono text-neutral-400 bg-neutral-800/80 rounded-md border border-neutral-700/50 truncate max-w-xs">
                {activePack.source_file_name}
              </span>
            )}
          </div>
          <span className="text-[11px] text-neutral-400">
            {activePack
              ? `${activePack.mcqs?.length || 0} MCQs · ${activePack.flashcards?.length || 0} Flashcards · ${activePack.glossary?.length || 0} Terms`
              : "Generate or choose a study pack to begin learning"}
          </span>
        </div>
      </div>

      {/* Quick Action & Export Buttons */}
      <div className="flex items-center gap-2.5">
        {toastMessage && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-neutral-800 border border-neutral-700 text-xs text-neutral-200 animate-fade-in shadow-lg">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>{toastMessage}</span>
          </div>
        )}

        {activePack && (
          <>
            <button
              onClick={handleExportPDF}
              disabled={isExportingPdf}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium text-neutral-300 bg-neutral-800/80 hover:bg-neutral-800 hover:text-white border border-neutral-700/80 transition-colors disabled:opacity-50"
              title="Download compiled study guide PDF"
            >
              {isExportingPdf ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400" />
              ) : (
                <FileText className="w-3.5 h-3.5 text-rose-400" />
              )}
              <span>Export PDF</span>
            </button>

            <button
              onClick={handleExportCSV}
              disabled={isExportingCsv}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium text-neutral-300 bg-neutral-800/80 hover:bg-neutral-800 hover:text-white border border-neutral-700/80 transition-colors disabled:opacity-50"
              title="Export MCQ questions to CSV"
            >
              {isExportingCsv ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400" />
              ) : (
                <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
              )}
              <span>Export CSV</span>
            </button>
          </>
        )}

        <Show when="signed-in">
          <div className="pl-2 border-l border-neutral-800">
            <UserButton
              appearance={{
                elements: {
                  avatarBox: "w-8 h-8 rounded-full ring-2 ring-indigo-500/30",
                },
              }}
            />
          </div>
        </Show>
      </div>
    </header>
  );
}
