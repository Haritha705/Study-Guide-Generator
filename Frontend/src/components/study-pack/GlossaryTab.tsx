"use client";

import React, { useState } from "react";
import { StudyPackOutput } from "@/types";
import { Search, BookA, Sparkles, Filter } from "lucide-react";

export function GlossaryTab({ pack }: { pack: StudyPackOutput }) {
  const glossary = pack.glossary || [];
  const [searchQuery, setSearchQuery] = useState("");

  const filtered = glossary.filter(
    (item) =>
      item.term.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.definition.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (!glossary || glossary.length === 0) {
    return (
      <div className="p-10 text-center rounded-2xl bg-neutral-900 border border-neutral-800 text-neutral-400">
        No glossary definitions available in this pack.
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">
            Key Terminology & Glossary
          </h2>
          <p className="text-xs text-neutral-400">
            Authoritative definitions and semantic explanations extracted from source
          </p>
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-neutral-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search terms..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-neutral-900 border border-neutral-800 rounded-xl text-xs text-white placeholder:text-neutral-500 focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>
      </div>

      {/* Grid of Glossary Terms */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map((item, idx) => (
          <div
            key={idx}
            className="p-5 rounded-2xl bg-neutral-900/80 border border-neutral-800/80 hover:border-neutral-700 transition-colors space-y-2 shadow-sm"
          >
            <div className="flex items-center justify-between gap-2">
              <span className="text-sm font-bold text-white tracking-tight">
                {item.term}
              </span>
              <span className="w-5 h-5 rounded-md bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center font-mono text-[10px] font-semibold shrink-0">
                T{idx + 1}
              </span>
            </div>
            <p className="text-xs text-neutral-300 leading-relaxed pt-1">
              {item.definition}
            </p>
          </div>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="p-8 text-center rounded-2xl bg-neutral-900/50 border border-neutral-800 text-neutral-400 text-xs">
          No terms matching &quot;{searchQuery}&quot;
        </div>
      )}
    </div>
  );
}
