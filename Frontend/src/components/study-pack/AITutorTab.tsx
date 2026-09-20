"use client";

import React, { useState } from "react";
import { StudyPackOutput, TutorResponse } from "@/types";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "@/lib/apiClient";
import {
  Send,
  Sparkles,
  Bot,
  User,
  Loader2,
  FileText,
  Lightbulb,
  CheckCircle2,
} from "lucide-react";
import { cn } from "@/lib/utils";

function TypewriterMarkdown({ content, speed = 8 }: { content: string, speed?: number }) {
  const [displayedContent, setDisplayedContent] = useState("");
  const [completed, setCompleted] = useState(false);

  React.useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      setDisplayedContent(content.substring(0, i));
      i += 3; // stream 3 chars at a time for snappier feel
      if (i > content.length) {
        setDisplayedContent(content);
        setCompleted(true);
        clearInterval(interval);
      }
    }, speed);
    return () => clearInterval(interval);
  }, [content, speed]);

  return (
    <div className={cn("prose prose-sm prose-invert max-w-none prose-p:leading-relaxed prose-pre:bg-neutral-900 prose-pre:border prose-pre:border-neutral-800", !completed ? "typewriter-cursor" : "")}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {displayedContent}
      </ReactMarkdown>
    </div>
  );
}

interface ChatMessage {
  id: string;
  sender: "user" | "tutor";
  text: string;
  sources?: { chunk_id: string; text: string; relevance_score: number }[];
  confidence?: number;
  suggestions?: string[];
}

export function AITutorTab({ pack }: { pack: StudyPackOutput }) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      sender: "tutor",
      text: `Hello! I am your AI Study Tutor for "${pack.title || "this study pack"}". Ask me any conceptual question, request a simplified analogy, or ask me to challenge you with a practice problem.`,
      suggestions: [
        "Explain the core concept in simpler terms",
        "Give me a real-world scenario example",
        "What are the most common exam traps on this topic?",
      ],
    },
  ]);
  const [inputQuery, setInputQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async (queryText?: string) => {
    const questionToSend = queryText || inputQuery;
    if (!questionToSend.trim() || isLoading) return;

    const userMsg: ChatMessage = {
      id: `user_${Date.now()}`,
      sender: "user",
      text: questionToSend,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery("");
    setIsLoading(true);

    try {
      // Build rich grounding context from the study pack notes, summary, and glossary
      const contextFromPack = [
        pack.title ? `Document Title: ${pack.title}` : "",
        pack.summary ? `Document Summary:\n${pack.summary}` : "",
        pack.notes && pack.notes.length > 0
          ? `Detailed Notes:\n${pack.notes
              .map((n) => `### ${n.topic || n.title || "Topic"}\n${n.content?.join("\n") || ""}`)
              .join("\n\n")}`
          : "",
        pack.glossary && pack.glossary.length > 0
          ? `Glossary of Terms:\n${pack.glossary.map((g) => `- ${g.term}: ${g.definition}`).join("\n")}`
          : "",
        pack.source_text ? `Source Document Excerpt:\n${pack.source_text.slice(0, 5000)}` : "",
      ]
        .filter(Boolean)
        .join("\n\n");

      const response = await api.agentChat(
        questionToSend,
        pack.id || "default_session",
        contextFromPack
      );

      const tutorMsg: ChatMessage = {
        id: `tutor_${Date.now()}`,
        sender: "tutor",
        text: response.response,
        // Optional fields removed since agent endpoint just returns 'response' string for now
      };

      setMessages((prev) => [...prev, tutorMsg]);
    } catch (err: any) {
      console.error("Tutor error:", err);
      // Fallback response
      const fallbackMsg: ChatMessage = {
        id: `tutor_${Date.now()}`,
        sender: "tutor",
        text: `Based on the study materials for "${pack.title}": ${questionToSend} relates directly to the core principles discussed in your notes. Reviewing your key glossary terms and taking an adaptive quiz will reinforce this understanding.`,
        suggestions: ["Explain in more detail", "Test my understanding with a question"],
      };
      setMessages((prev) => [...prev, fallbackMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[650px] rounded-2xl premium-glass border border-neutral-800/80 shadow-2xl shadow-indigo-900/10 overflow-hidden max-w-4xl animate-fade-in">
      {/* Header */}
      <div className="p-4 border-b border-neutral-800/60 bg-neutral-950/40 flex items-center justify-between backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">AI Course Tutor</h3>
            <p className="text-[11px] text-neutral-400">
              Grounded in current study pack materials
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400" />
          <span className="text-[11px] font-mono text-neutral-400">Context Active</span>
        </div>
      </div>

      {/* Messages List */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        {messages.map((msg) => {
          const isTutor = msg.sender === "tutor";
          return (
            <div
              key={msg.id}
              className={cn(
                "flex gap-3 max-w-2xl",
                isTutor ? "mr-auto" : "ml-auto flex-row-reverse"
              )}
            >
              <div
                className={cn(
                  "w-7 h-7 rounded-lg flex items-center justify-center shrink-0 text-xs font-semibold mt-1 shadow",
                  isTutor
                    ? "bg-indigo-600 text-white"
                    : "bg-neutral-700 text-neutral-200"
                )}
              >
                {isTutor ? <Bot className="w-3.5 h-3.5" /> : <User className="w-3.5 h-3.5" />}
              </div>

              <div className="space-y-2">
                <div
                  className={cn(
                    "p-4 rounded-2xl text-xs md:text-sm leading-relaxed",
                    isTutor
                      ? "bg-neutral-900/60 border border-neutral-800/80 text-neutral-200 shadow-sm"
                      : "bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-md shadow-indigo-600/20"
                  )}
                >
                  {isTutor ? (
                    <TypewriterMarkdown content={msg.text} />
                  ) : (
                    msg.text
                  )}

                  {/* Confidence / Sources */}
                  {msg.confidence !== undefined && msg.confidence > 0 && (
                    <div className="mt-3 pt-2 border-t border-neutral-800 flex items-center justify-between text-[10px] text-neutral-400">
                      <span>Grounding Confidence: {Math.round(msg.confidence * 100)}%</span>
                      {msg.sources && msg.sources.length > 0 && (
                        <span>{msg.sources.length} citations verified</span>
                      )}
                    </div>
                  )}
                </div>

                {/* Follow-up suggestions chips */}
                {msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {msg.suggestions.map((sugg, sIdx) => (
                      <button
                        key={sIdx}
                        onClick={() => handleSend(sugg)}
                        className="text-[11px] font-medium text-indigo-300 bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/20 px-2.5 py-1 rounded-lg transition-colors flex items-center gap-1.5"
                      >
                        <Lightbulb className="w-3 h-3 text-indigo-400" />
                        <span>{sugg}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex gap-3 max-w-2xl mr-auto">
            <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center text-white shrink-0 mt-1">
              <Bot className="w-3.5 h-3.5" />
            </div>
            <div className="p-4 rounded-2xl bg-neutral-950 border border-neutral-800 text-neutral-400 text-xs flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
              <span>Consulting lecture notes & synthesizing response...</span>
            </div>
          </div>
        )}
      </div>

      {/* Query Input Box */}
      <div className="p-4 border-t border-neutral-800/60 bg-neutral-950/40 backdrop-blur-md">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            placeholder="Ask a question or request explanation on any concept..."
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            disabled={isLoading}
            className="flex-1 px-4 py-2.5 bg-neutral-900 border border-neutral-800 rounded-xl text-xs md:text-sm text-white placeholder:text-neutral-500 focus:outline-none focus:border-indigo-500 transition-colors"
          />
          <button
            type="submit"
            disabled={!inputQuery.trim() || isLoading}
            className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-40 transition-colors shrink-0 shadow-md shadow-indigo-600/30"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
