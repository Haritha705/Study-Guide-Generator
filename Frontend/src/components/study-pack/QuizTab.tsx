"use client";

import React, { useState, useEffect } from "react";
import { StudyPackOutput, MCQItem, Difficulty, QuizResult } from "@/types";
import { api } from "@/lib/apiClient";
import {
  HelpCircle,
  CheckCircle2,
  XCircle,
  Award,
  ArrowRight,
  ArrowLeft,
  RotateCcw,
  Zap,
  ShieldCheck,
  Flame,
  Loader2,
  Sparkles,
  TrendingUp,
  AlertTriangle,
} from "lucide-react";
import { cn } from "@/lib/utils";

export function QuizTab({ pack }: { pack: StudyPackOutput }) {
  const [activeDifficulty, setActiveDifficulty] = useState<Difficulty>("Medium");
  const [questions, setQuestions] = useState<MCQItem[]>(pack.mcqs || []);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGeneratingTier, setIsGeneratingTier] = useState(false);
  const [quizResult, setQuizResult] = useState<QuizResult | null>(null);
  const [showReview, setShowReview] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);

  // Filter or initialize questions when pack changes
  useEffect(() => {
    if (pack.mcqs && pack.mcqs.length > 0) {
      setQuestions(pack.mcqs);
      if (pack.mcqs[0]?.difficulty) {
        setActiveDifficulty(pack.mcqs[0].difficulty);
      }
    }
  }, [pack]);

  const currentQ = questions[currentIndex];

  const handleSelectOption = (optionStr: string) => {
    if (!currentQ || quizResult) return;
    setSelectedAnswers((prev) => ({
      ...prev,
      [currentQ.id]: optionStr,
    }));
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    }
  };

  const handleSubmitQuiz = async () => {
    if (Object.keys(selectedAnswers).length === 0) {
      alert("Please answer at least one question before submitting.");
      return;
    }

    try {
      setIsSubmitting(true);
      const result = await api.submitQuiz({
        studypack_id: pack.id,
        answers: selectedAnswers,
        mcqs: questions,
        current_difficulty: activeDifficulty,
      });
      setQuizResult(result);
    } catch (err: any) {
      console.error("Quiz submission error:", err);
      // Client-side fallback grading if offline
      let correctCount = 0;
      const missed: number[] = [];
      const topicPerf: Record<string, { total: number; correct: number; accuracy: number }> = {};

      questions.forEach((q) => {
        const userChoice = selectedAnswers[q.id];
        const isCorrect = userChoice && userChoice.trim().charAt(0) === q.answer.trim().charAt(0);
        if (isCorrect) {
          correctCount++;
        } else {
          missed.push(q.id);
        }

        const t = q.topic || "General";
        if (!topicPerf[t]) topicPerf[t] = { total: 0, correct: 0, accuracy: 0 };
        topicPerf[t].total++;
        if (isCorrect) topicPerf[t].correct++;
      });

      Object.values(topicPerf).forEach((tp) => {
        tp.accuracy = Math.round((tp.correct / tp.total) * 100);
      });

      const scorePercent = Math.round((correctCount / questions.length) * 100);
      let nextDiff: Difficulty = activeDifficulty;
      if (scorePercent >= 80) {
        nextDiff = activeDifficulty === "Easy" ? "Medium" : "Hard";
      } else if (scorePercent < 60) {
        nextDiff = activeDifficulty === "Hard" ? "Medium" : "Easy";
      }

      setQuizResult({
        score: scorePercent,
        weak_topics: Object.entries(topicPerf)
          .filter(([_, perf]) => perf.accuracy < 60)
          .map(([k]) => k),
        topic_performance: topicPerf,
        difficulty_breakdown: { [activeDifficulty]: questions.length },
        missed_question_ids: missed,
        next_difficulty: nextDiff,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Generate MCQs for specific difficulty level on-demand
  const handleGenerateTier = async (difficulty: Difficulty) => {
    setGenerationError(null);
    try {
      setIsGeneratingTier(true);
      const textToUse = pack.source_text || pack.summary;
      const response = await api.generateQuiz(textToUse, difficulty, 5);
      if (response && response.mcqs && response.mcqs.length > 0) {
        setQuestions(response.mcqs);
        setActiveDifficulty(difficulty);
        setCurrentIndex(0);
        setSelectedAnswers({});
        setQuizResult(null);
        setShowReview(false);
      } else {
        throw new Error("No questions were returned from the generator.");
      }
    } catch (err: any) {
      setGenerationError(`Could not generate ${difficulty} questions: ${err.message || "Unknown error"}`);
    } finally {
      setIsGeneratingTier(false);
    }
  };

  const handleRestart = () => {
    setSelectedAnswers({});
    setQuizResult(null);
    setCurrentIndex(0);
    setShowReview(false);
  };

  if (!questions || questions.length === 0) {
    return (
      <div className="p-10 text-center rounded-2xl bg-neutral-900 border border-neutral-800 space-y-4">
        <HelpCircle className="w-10 h-10 text-neutral-500 mx-auto" />
        <h3 className="text-base font-semibold text-white">No MCQs Generated Yet</h3>
        <p className="text-xs text-neutral-400 max-w-sm mx-auto">
          Generate an initial practice round calibrated to your performance target.
        </p>
        <button
          onClick={() => handleGenerateTier("Medium")}
          disabled={isGeneratingTier}
          className="px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 text-white hover:bg-indigo-500 transition-colors"
        >
          {isGeneratingTier ? "Generating..." : "Generate 5 Medium MCQs"}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl animate-fade-in">
      {/* Tier Selector & Status Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl bg-neutral-900/70 border border-neutral-800/80">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">
            Performance Level:
          </span>
          <div className="flex items-center gap-1.5 p-1 bg-neutral-950 rounded-xl border border-neutral-800">
            {(
              [
                { level: "Easy", icon: Zap, label: "Easy" },
                { level: "Medium", icon: ShieldCheck, label: "Medium" },
                { level: "Hard", icon: Flame, label: "Tough" },
              ] as const
            ).map((tier) => {
              const isActive = activeDifficulty === tier.level;
              return (
                <button
                  key={tier.level}
                  onClick={() => handleGenerateTier(tier.level)}
                  disabled={isGeneratingTier}
                  className={cn(
                    "flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all",
                    isActive
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                      : "text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/50"
                  )}
                  title={`Switch to ${tier.label} questions`}
                >
                  <tier.icon className="w-3.5 h-3.5" />
                  <span>{tier.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex items-center gap-3">
          {isGeneratingTier && (
            <div className="flex items-center gap-2 text-xs text-indigo-400">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>Generating questions...</span>
            </div>
          )}
          <span className="text-xs font-mono font-medium text-neutral-400">
            {Object.keys(selectedAnswers).length} of {questions.length} Answered
          </span>
        </div>
      </div>

      {generationError && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs">
          {generationError}
        </div>
      )}

      {/* QUIZ RESULTS VIEW */}
      {quizResult ? (
        <div className="space-y-6 animate-fade-in">
          {/* Score Header Card */}
          <div className="p-8 rounded-3xl bg-gradient-to-b from-neutral-900 via-neutral-900 to-neutral-950 border border-neutral-800 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="space-y-2 text-center md:text-left">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold">
                  <Award className="w-3.5 h-3.5" />
                  Quiz Evaluation Complete
                </div>
                <h2 className="text-2xl font-bold text-white tracking-tight">
                  Assessment Performance Summary
                </h2>
                <p className="text-xs text-neutral-400">
                  Difficulty Level:{" "}
                  <span className="font-semibold text-white">
                    {activeDifficulty === "Hard" ? "Tough" : activeDifficulty}
                  </span>
                </p>
              </div>

              {/* Big Score Dial */}
              <div className="flex flex-col items-center justify-center w-32 h-32 rounded-3xl bg-neutral-950/80 border border-neutral-700/80 shadow-inner">
                <span
                  className={cn(
                    "text-3xl font-extrabold tracking-tight",
                    quizResult.score >= 80
                      ? "text-emerald-400"
                      : quizResult.score >= 60
                      ? "text-amber-400"
                      : "text-rose-400"
                  )}
                >
                  {quizResult.score}%
                </span>
                <span className="text-[10px] text-neutral-400 uppercase tracking-widest mt-1">
                  Accuracy
                </span>
              </div>
            </div>

            {/* Performance Level Recommendation */}
            <div className="mt-8 p-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-indigo-500/20 flex items-center justify-center text-indigo-400 shrink-0">
                  <TrendingUp className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-indigo-200 uppercase tracking-wider">
                    Recommended Next Difficulty:
                  </h4>
                  <p className="text-sm font-semibold text-white">
                    {quizResult.next_difficulty === "Hard" ? "Tough Tier (Synthesis)" : `${quizResult.next_difficulty} Tier`}
                  </p>
                </div>
              </div>

              <button
                onClick={() => handleGenerateTier(quizResult.next_difficulty)}
                disabled={isGeneratingTier}
                className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition-all"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Start {quizResult.next_difficulty === "Hard" ? "Tough" : quizResult.next_difficulty} Round</span>
              </button>
            </div>

            {/* Weak Topics If Any */}
            {quizResult.weak_topics && quizResult.weak_topics.length > 0 && (
              <div className="mt-6 p-4 rounded-2xl bg-amber-950/20 border border-amber-800/40">
                <div className="flex items-center gap-2 text-xs font-semibold text-amber-300 mb-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  <span>Targeted Review Suggested For:</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {quizResult.weak_topics.map((topic) => (
                    <span
                      key={topic}
                      className="px-2.5 py-1 rounded-lg bg-amber-500/15 border border-amber-500/30 text-amber-200 text-xs font-medium"
                    >
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Action Row: Review Mistakes vs Retake */}
          <div className="flex items-center justify-between">
            <button
              onClick={() => setShowReview(!showReview)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-neutral-200 bg-neutral-800 hover:bg-neutral-700 transition-colors border border-neutral-700"
            >
              {showReview ? "Hide Question Explanations" : "Review All Questions & Explanations"}
            </button>

            <button
              onClick={handleRestart}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold text-neutral-300 hover:text-white bg-neutral-900 border border-neutral-800 hover:border-neutral-700 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Retake Current Set</span>
            </button>
          </div>

          {/* Full Review Breakdown */}
          {showReview && (
            <div className="space-y-4 pt-2">
              {questions.map((q, idx) => {
                const userChoice = selectedAnswers[q.id];
                const isCorrect = userChoice && userChoice.trim().charAt(0) === q.answer.trim().charAt(0);

                return (
                  <div
                    key={q.id}
                    className={cn(
                      "p-6 rounded-2xl border space-y-3 transition-colors",
                      isCorrect
                        ? "bg-emerald-950/15 border-emerald-900/50"
                        : "bg-rose-950/15 border-rose-900/50"
                    )}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-center gap-2.5">
                        <span className="w-6 h-6 rounded-md bg-neutral-800 text-neutral-300 font-mono text-xs font-bold flex items-center justify-center shrink-0">
                          {idx + 1}
                        </span>
                        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-neutral-800 text-neutral-300">
                          {q.topic}
                        </span>
                      </div>
                      {isCorrect ? (
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400">
                          <CheckCircle2 className="w-4 h-4" />
                          <span>Correct</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-rose-400">
                          <XCircle className="w-4 h-4" />
                          <span>Missed</span>
                        </div>
                      )}
                    </div>

                    <p className="text-sm font-medium text-white pt-1">{q.question}</p>

                    {/* Options */}
                    <div className="space-y-1.5 pt-2">
                      {q.options.map((opt) => {
                        const isChosen = userChoice === opt;
                        const isAnswer = opt.trim().charAt(0) === q.answer.trim().charAt(0);

                        return (
                          <div
                            key={opt}
                            className={cn(
                              "px-3.5 py-2 rounded-xl text-xs flex items-center justify-between border",
                              isAnswer
                                ? "bg-emerald-500/10 border-emerald-500/40 text-emerald-300 font-medium"
                                : isChosen
                                ? "bg-rose-500/10 border-rose-500/40 text-rose-300 line-through"
                                : "bg-neutral-900/60 border-neutral-800/80 text-neutral-400"
                            )}
                          >
                            <span>{opt}</span>
                            {isAnswer && <span className="font-semibold text-[10px]">Correct Answer</span>}
                            {isChosen && !isAnswer && <span className="font-semibold text-[10px]">Your Answer</span>}
                          </div>
                        );
                      })}
                    </div>

                    {/* Explanation */}
                    {q.explanation && (
                      <div className="mt-3 p-3 rounded-xl bg-neutral-900/80 border border-neutral-800 text-xs text-neutral-300 leading-relaxed">
                        <span className="font-semibold text-indigo-400">Explanation: </span>
                        {q.explanation}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      ) : (
        /* LIVE QUIZ RUNNER */
        <div className="p-8 rounded-3xl bg-neutral-900/80 border border-neutral-800/80 shadow-2xl space-y-6">
          {/* Progress Bar & Counter */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-neutral-400 font-medium">
              <span>
                Question <strong className="text-white">{currentIndex + 1}</strong> of {questions.length}
              </span>
              <span className="font-mono text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                {currentQ.topic || "Core Material"}
              </span>
            </div>
            <div className="w-full h-1.5 bg-neutral-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-300"
                style={{
                  width: `${((currentIndex + 1) / questions.length) * 100}%`,
                }}
              />
            </div>
          </div>

          {/* Question Title */}
          <div className="py-2">
            <h3 className="text-base md:text-lg font-semibold text-white leading-relaxed">
              {currentQ.question}
            </h3>
          </div>

          {/* Options */}
          <div className="space-y-3">
            {currentQ.options.map((option) => {
              const isSelected = selectedAnswers[currentQ.id] === option;
              return (
                <button
                  key={option}
                  type="button"
                  onClick={() => handleSelectOption(option)}
                  className={cn(
                    "w-full text-left p-4 rounded-xl text-sm font-medium transition-all duration-150 flex items-center justify-between border group",
                    isSelected
                      ? "bg-indigo-600/15 border-indigo-500 text-white shadow-md shadow-indigo-600/15"
                      : "bg-neutral-900/70 border-neutral-800 text-neutral-300 hover:border-neutral-700 hover:bg-neutral-800/60 hover:text-white"
                  )}
                >
                  <span>{option}</span>
                  <div
                    className={cn(
                      "w-5 h-5 rounded-full border flex items-center justify-center shrink-0 transition-colors",
                      isSelected
                        ? "border-indigo-400 bg-indigo-500 text-white"
                        : "border-neutral-700 group-hover:border-neutral-500"
                    )}
                  >
                    {isSelected && <div className="w-2 h-2 rounded-full bg-white" />}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Navigation & Submit */}
          <div className="flex items-center justify-between pt-4 border-t border-neutral-800">
            <button
              type="button"
              onClick={handlePrev}
              disabled={currentIndex === 0}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold text-neutral-300 hover:text-white disabled:opacity-40 disabled:pointer-events-none transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Previous</span>
            </button>

            {currentIndex < questions.length - 1 ? (
              <button
                type="button"
                onClick={handleNext}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold text-white bg-neutral-800 hover:bg-neutral-700 border border-neutral-700 transition-colors"
              >
                <span>Next Question</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                type="button"
                onClick={handleSubmitQuiz}
                disabled={isSubmitting}
                className="flex items-center gap-2 px-6 py-2.5 rounded-xl text-xs font-semibold text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:opacity-95 shadow-lg shadow-indigo-500/25 transition-all"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Grading Answers...</span>
                  </>
                ) : (
                  <>
                    <Award className="w-4 h-4" />
                    <span>Submit for Assessment</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
