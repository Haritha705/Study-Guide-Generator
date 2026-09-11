"use client";

import React, { useState } from "react";
import { StudyPackOutput } from "@/types";
import { BookOpen, CheckCircle, Circle, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

export function NotesTab({ pack }: { pack: StudyPackOutput }) {
  const [understoodNotes, setUnderstoodNotes] = useState<Record<number, boolean>>({});

  const toggleUnderstood = (id: number) => {
    setUnderstoodNotes((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const rawNotes = pack.notes || [];

  if (!rawNotes || rawNotes.length === 0) {
    return (
      <div className="p-8 text-center rounded-2xl bg-neutral-900 border border-neutral-800 text-neutral-400">
        No notes available in this study pack.
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">
            High-Yield Structured Notes
          </h2>
          <p className="text-xs text-neutral-400">
            Synthesized hierarchical concepts and breakdown of core ideas
          </p>
        </div>
        <div className="text-xs font-mono text-neutral-400 bg-neutral-900 px-3 py-1.5 rounded-lg border border-neutral-800">
          {Object.values(understoodNotes).filter(Boolean).length} of {rawNotes.length} Sections Mastered
        </div>
      </div>

      <div className="space-y-4">
        {rawNotes.map((note: any, idx: number) => {
          const noteKey = typeof note === "object" && note?.id !== undefined ? note.id : idx;
          const isMastered = !!understoodNotes[noteKey];

          // Handle string notes or object notes with any field name
          let title = `Section ${idx + 1}`;
          let points: string[] = [];
          let highlights: any[] = [];

          if (typeof note === "string") {
            title = `Key Concept ${idx + 1}`;
            points = [note];
          } else if (typeof note === "object" && note !== null) {
            title = note.title || note.topic || note.heading || `Note Section ${idx + 1}`;
            
            const rawPoints = note.key_points || note.content || note.points || note.body || [];
            if (Array.isArray(rawPoints)) {
              points = rawPoints.map((p) => (typeof p === "string" ? p : JSON.stringify(p)));
            } else if (typeof rawPoints === "string") {
              points = rawPoints.split("\n").filter((l) => l.trim().length > 0);
            }

            if (Array.isArray(note.highlights)) {
              highlights = note.highlights;
            }
          }

          return (
            <div
              key={noteKey}
              className={cn(
                "p-6 rounded-2xl border transition-all duration-200 space-y-4",
                isMastered
                  ? "bg-neutral-900/40 border-neutral-800 opacity-80"
                  : "bg-neutral-900/80 border-neutral-800 hover:border-neutral-700 shadow-lg"
              )}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-3">
                  <span className="w-7 h-7 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 font-mono text-xs font-bold flex items-center justify-center shrink-0">
                    {idx + 1}
                  </span>
                  <h3 className="text-base font-semibold text-white tracking-tight">
                    {title}
                  </h3>
                </div>

                <button
                  type="button"
                  onClick={() => toggleUnderstood(noteKey)}
                  className={cn(
                    "flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium transition-colors border shrink-0",
                    isMastered
                      ? "bg-emerald-950/40 text-emerald-400 border-emerald-800/60"
                      : "bg-neutral-800/60 text-neutral-400 border-neutral-700/40 hover:text-white"
                  )}
                >
                  {isMastered ? (
                    <>
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Mastered</span>
                    </>
                  ) : (
                    <>
                      <Circle className="w-3.5 h-3.5" />
                      <span>Mark Read</span>
                    </>
                  )}
                </button>
              </div>

              {/* Highlights tags if provided by backend */}
              {highlights.length > 0 && (
                <div className="flex flex-wrap gap-2 pt-1">
                  {highlights.map((h: any, hIdx: number) => (
                    <div
                      key={hIdx}
                      className="px-2.5 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-300 flex items-center gap-1.5"
                    >
                      <Sparkles className="w-3 h-3 text-indigo-400 shrink-0" />
                      <span className="font-semibold text-indigo-200 uppercase text-[10px]">
                        {h.type || "Key"}:
                      </span>
                      <span>{typeof h === "string" ? h : h.text}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Key points list */}
              {points.length > 0 ? (
                <ul className="space-y-2.5 pl-2">
                  {points.map((point: string, pIdx: number) => (
                    <li key={pIdx} className="flex items-start gap-3 text-sm text-neutral-300 leading-relaxed">
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-2 shrink-0" />
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>
          );
        })}
      </div>
    </div>
  );
}
