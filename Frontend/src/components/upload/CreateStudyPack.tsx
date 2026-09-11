"use client";

import React, { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/apiClient";
import { useStudyStore } from "@/stores/useStudyStore";
import { Difficulty, StudyPackOutput } from "@/types";
import {
  UploadCloud,
  FileText,
  Sparkles,
  Layers,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Sliders,
  Flame,
  Zap,
  ShieldCheck,
  ArrowRight,
  BookOpen,
} from "lucide-react";
import { cn } from "@/lib/utils";

export function CreateStudyPack() {
  const router = useRouter();
  const { savePack, setActivePack } = useStudyStore();

  const [inputMode, setInputMode] = useState<"upload" | "paste">("upload");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [pastedText, setPastedText] = useState("");
  const [packTitle, setPackTitle] = useState("");
  const [selectedDifficulty, setSelectedDifficulty] = useState<Difficulty>("Medium");
  const [quizSize, setQuizSize] = useState<number>(10);

  const [isGenerating, setIsGenerating] = useState(false);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const steps = [
    "Analyzing document & extracting structural semantics",
    "Synthesizing comprehensive executive summary",
    "Generating adaptive MCQs (Easy, Medium, Tough)",
    "Formulating short answers with grading rubrics",
    "Extracting key glossary terminology & 3D flashcards",
    "Finalizing study pack materials",
  ];

  const handleFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === "application/pdf" || file.name.endsWith(".pdf")) {
        setSelectedFile(file);
        if (!packTitle) {
          setPackTitle(file.name.replace(/\.[^/.]+$/, "").replace(/[_-]/g, " "));
        }
        setErrorMessage(null);
      } else {
        setErrorMessage("Please upload a valid PDF document (.pdf)");
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      if (!packTitle) {
        setPackTitle(file.name.replace(/\.[^/.]+$/, "").replace(/[_-]/g, " "));
      }
      setErrorMessage(null);
    }
  };

  const handleGenerate = async () => {
    setErrorMessage(null);
    let extractedText = "";

    try {
      setIsGenerating(true);
      setCurrentStep(0);

      // 1. Get raw text either from PDF or pasted text
      if (inputMode === "upload") {
        if (!selectedFile) {
          setErrorMessage("Please upload a PDF file first.");
          setIsGenerating(false);
          return;
        }
        setCurrentStep(0);
        const extractRes = await api.extractPDF(selectedFile);
        extractedText = extractRes.extracted_text;
      } else {
        if (!pastedText.trim() || pastedText.trim().length < 50) {
          setErrorMessage("Please enter at least 50 characters of source notes or text.");
          setIsGenerating(false);
          return;
        }
        extractedText = pastedText;
      }

      if (!extractedText || extractedText.length < 50) {
        throw new Error("Extracted text was too brief to generate a meaningful study pack.");
      }

      // Step 1: Synthesis
      setCurrentStep(1);

      // Call generateStudyPack endpoint
      const generatedPack = await api.generateStudyPack(extractedText);

      setCurrentStep(2);

      // If user selected a custom initial difficulty or quiz size different from the default,
      // let's ensure MCQs are augmented/aligned with their requested difficulty level!
      if (selectedDifficulty !== "Medium" || quizSize !== 10) {
        try {
          const customQuizRes = await api.generateQuiz(
            extractedText,
            selectedDifficulty,
            quizSize
          );
          if (customQuizRes && customQuizRes.mcqs && customQuizRes.mcqs.length > 0) {
            generatedPack.mcqs = customQuizRes.mcqs;
          }
        } catch (quizErr) {
          console.warn("Custom quiz size generation fell back to study pack MCQs", quizErr);
        }
      }

      setCurrentStep(4);

      // Attach metadata
      const finalPack: StudyPackOutput = {
        ...generatedPack,
        id: `pack_${Date.now()}`,
        title: packTitle.trim() || (selectedFile?.name || "Comprehensive Study Pack"),
        created_at: new Date().toISOString(),
        source_file_name: selectedFile ? selectedFile.name : "Direct Input Notes",
        source_text: extractedText.slice(0, 3000), // retain excerpt for tutor context
      };

      setCurrentStep(5);

      // Save to store and localStorage
      savePack(finalPack);
      setActivePack(finalPack);

      setTimeout(() => {
        router.push(`/study-pack/${finalPack.id}`);
      }, 500);
    } catch (err: any) {
      console.error("Generation error:", err);
      setErrorMessage(
        err instanceof ApiError
          ? `Generation failed: ${err.message}`
          : err.message || "An unexpected error occurred during generation."
      );
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-10 space-y-8 animate-fade-in">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold tracking-wide uppercase">
          <Sparkles className="w-3.5 h-3.5" />
          AI Study Guide Synthesizer
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-white">
          Generate a Comprehensive Study Pack
        </h1>
        <p className="text-sm text-neutral-400 max-w-2xl leading-relaxed">
          Upload any lecture slides, textbook chapter, or paste your course notes.
          StudyPack AI creates an executive summary, tiered performance MCQs (Easy, Medium, Tough),
          3D interactive flashcards, short-answer rubrics, and key term glossaries.
        </p>
      </div>

      {/* Error Alert */}
      {errorMessage && (
        <div className="flex items-start gap-3 p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 text-rose-200 text-sm">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div className="flex-1 font-medium">{errorMessage}</div>
        </div>
      )}

      {/* Generating Progress Modal / Banner */}
      {isGenerating ? (
        <div className="p-8 rounded-2xl bg-neutral-900/90 border border-indigo-500/30 backdrop-blur-xl shadow-2xl space-y-6 animate-fade-in">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-600/20 flex items-center justify-center text-indigo-400">
                <Loader2 className="w-5 h-5 animate-spin" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-white">
                  Generating Study Pack
                </h3>
                <p className="text-xs text-neutral-400">
                  Dual-pipeline AI synthesis in progress (Gemini + Mistral)
                </p>
              </div>
            </div>
            <span className="text-xs font-mono font-medium text-indigo-400 px-2.5 py-1 rounded-md bg-indigo-500/10 border border-indigo-500/20">
              Step {currentStep + 1} of {steps.length}
            </span>
          </div>

          {/* Stepper list */}
          <div className="space-y-3 pt-2">
            {steps.map((stepText, idx) => {
              const isDone = idx < currentStep;
              const isCurrent = idx === currentStep;
              return (
                <div
                  key={stepText}
                  className={cn(
                    "flex items-center gap-3 px-4 py-3 rounded-lg text-xs font-medium transition-all",
                    isCurrent
                      ? "bg-indigo-500/10 border border-indigo-500/30 text-indigo-200 shadow-sm"
                      : isDone
                      ? "bg-neutral-800/40 text-neutral-400"
                      : "text-neutral-500 opacity-60"
                  )}
                >
                  {isDone ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  ) : isCurrent ? (
                    <Loader2 className="w-4 h-4 text-indigo-400 animate-spin shrink-0" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border border-neutral-700 shrink-0 flex items-center justify-center text-[10px]">
                      {idx + 1}
                    </div>
                  )}
                  <span>{stepText}</span>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Title & Mode Switcher */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2 space-y-1.5">
              <label className="text-xs font-semibold text-neutral-300 uppercase tracking-wider">
                Study Pack Title
              </label>
              <input
                type="text"
                placeholder="e.g. Distributed Systems & Consensus Algorithms"
                value={packTitle}
                onChange={(e) => setPackTitle(e.target.value)}
                className="w-full px-4 py-2.5 bg-neutral-900 border border-neutral-800 rounded-xl text-sm text-white placeholder:text-neutral-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-neutral-300 uppercase tracking-wider">
                Input Source
              </label>
              <div className="grid grid-cols-2 p-1 bg-neutral-900 border border-neutral-800 rounded-xl">
                <button
                  type="button"
                  onClick={() => setInputMode("upload")}
                  className={cn(
                    "py-1.5 text-xs font-medium rounded-lg transition-colors flex items-center justify-center gap-1.5",
                    inputMode === "upload"
                      ? "bg-neutral-800 text-white shadow-sm"
                      : "text-neutral-400 hover:text-white"
                  )}
                >
                  <FileText className="w-3.5 h-3.5" />
                  PDF Upload
                </button>
                <button
                  type="button"
                  onClick={() => setInputMode("paste")}
                  className={cn(
                    "py-1.5 text-xs font-medium rounded-lg transition-colors flex items-center justify-center gap-1.5",
                    inputMode === "paste"
                      ? "bg-neutral-800 text-white shadow-sm"
                      : "text-neutral-400 hover:text-white"
                  )}
                >
                  <Layers className="w-3.5 h-3.5" />
                  Paste Text
                </button>
              </div>
            </div>
          </div>

          {/* File Upload Dropzone or Textarea */}
          {inputMode === "upload" ? (
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleFileDrop}
              onClick={() => fileInputRef.current?.click()}
              className={cn(
                "border-2 border-dashed rounded-2xl p-10 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-200",
                selectedFile
                  ? "border-indigo-500/60 bg-indigo-500/5"
                  : "border-neutral-800 hover:border-neutral-700 bg-neutral-900/40 hover:bg-neutral-900/70"
              )}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,application/pdf"
                className="hidden"
                onChange={handleFileSelect}
              />
              <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4 shadow-inner">
                <UploadCloud className="w-7 h-7" />
              </div>
              {selectedFile ? (
                <div className="space-y-1">
                  <p className="text-sm font-semibold text-white">
                    {selectedFile.name}
                  </p>
                  <p className="text-xs text-neutral-400 font-mono">
                    {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB · Ready for processing
                  </p>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedFile(null);
                    }}
                    className="text-xs text-rose-400 hover:underline pt-2 inline-block"
                  >
                    Change document
                  </button>
                </div>
              ) : (
                <div className="space-y-1">
                  <p className="text-sm font-medium text-neutral-200">
                    Drag and drop your PDF syllabus or lecture notes here
                  </p>
                  <p className="text-xs text-neutral-500">
                    Supports textbook chapters, lecture slides, papers (up to 25 MB)
                  </p>
                  <span className="inline-block mt-3 px-3 py-1 text-xs font-semibold text-indigo-300 bg-indigo-500/15 border border-indigo-500/30 rounded-lg">
                    Browse Files
                  </span>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-2">
              <label className="text-xs font-semibold text-neutral-300 uppercase tracking-wider">
                Raw Study Notes or Syllabus Content
              </label>
              <textarea
                rows={10}
                placeholder="Paste lecture notes, syllabus concepts, textbook excerpts, or review guides here..."
                value={pastedText}
                onChange={(e) => setPastedText(e.target.value)}
                className="w-full p-4 bg-neutral-900 border border-neutral-800 rounded-2xl text-sm text-white placeholder:text-neutral-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 font-mono leading-relaxed"
              />
              <div className="flex justify-between text-[11px] text-neutral-500">
                <span>Minimum 50 characters required</span>
                <span>{pastedText.length} characters</span>
              </div>
            </div>
          )}

          {/* Assessment & Performance Configuration */}
          <div className="p-6 rounded-2xl bg-neutral-900/60 border border-neutral-800/80 space-y-5">
            <div className="flex items-center gap-2 text-sm font-semibold text-neutral-200">
              <Sliders className="w-4 h-4 text-indigo-400" />
              <span>Assessment & Difficulty Calibration</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {/* Difficulty Level */}
              <div className="space-y-2">
                <label className="text-xs font-medium text-neutral-400">
                  Target MCQ Difficulty Level
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(
                    [
                      { label: "Easy", icon: Zap, desc: "Direct Recall" },
                      { label: "Medium", icon: ShieldCheck, desc: "Application" },
                      { label: "Hard", icon: Flame, desc: "Tough / Synthesis" },
                    ] as const
                  ).map((tier) => {
                    const isSelected = selectedDifficulty === tier.label;
                    return (
                      <button
                        key={tier.label}
                        type="button"
                        onClick={() => setSelectedDifficulty(tier.label)}
                        className={cn(
                          "flex flex-col items-center justify-center py-2.5 px-3 rounded-xl border text-xs font-medium transition-all",
                          isSelected
                            ? "border-indigo-500 bg-indigo-500/15 text-white shadow-sm"
                            : "border-neutral-800 bg-neutral-900/80 text-neutral-400 hover:border-neutral-700 hover:text-neutral-200"
                        )}
                      >
                        <tier.icon
                          className={cn(
                            "w-4 h-4 mb-1",
                            isSelected ? "text-indigo-400" : "text-neutral-500"
                          )}
                        />
                        <span className="font-semibold">{tier.label === "Hard" ? "Tough" : tier.label}</span>
                        <span className="text-[10px] text-neutral-500 mt-0.5">{tier.desc}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Quiz Size */}
              <div className="space-y-2">
                <label className="text-xs font-medium text-neutral-400">
                  Number of Practice MCQs
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {[5, 10, 15].map((size) => {
                    const isSelected = quizSize === size;
                    return (
                      <button
                        key={size}
                        type="button"
                        onClick={() => setQuizSize(size)}
                        className={cn(
                          "py-2.5 px-3 rounded-xl border text-xs font-medium transition-all flex flex-col items-center justify-center",
                          isSelected
                            ? "border-indigo-500 bg-indigo-500/15 text-white shadow-sm"
                            : "border-neutral-800 bg-neutral-900/80 text-neutral-400 hover:border-neutral-700 hover:text-neutral-200"
                        )}
                      >
                        <span className="font-semibold text-sm">{size} Questions</span>
                        <span className="text-[10px] text-neutral-500 mt-0.5">
                          {size === 5 ? "Quick Drill" : size === 10 ? "Standard" : "Comprehensive"}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Generate Button */}
          <div className="pt-2 flex justify-end">
            <button
              type="button"
              onClick={handleGenerate}
              disabled={
                isGenerating ||
                (inputMode === "upload" && !selectedFile) ||
                (inputMode === "paste" && pastedText.trim().length < 50)
              }
              className="flex items-center gap-2.5 px-6 py-3 rounded-xl font-semibold text-sm text-white bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:opacity-95 shadow-lg shadow-indigo-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
            >
              <Sparkles className="w-4 h-4" />
              <span>Generate Study Pack</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
