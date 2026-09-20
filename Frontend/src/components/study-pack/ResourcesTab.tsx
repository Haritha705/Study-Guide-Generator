"use client";

import React, { useEffect, useRef, useState } from "react";
import { api, ApiError } from "@/lib/apiClient";
import { BookItem, StudyPackOutput, VideoItem } from "@/types";
import {
  BookOpen,
  ExternalLink,
  Loader2,
  Play,
  RefreshCw,
  Tv2,
  AlertCircle,
  BookMarked,
  Users,
  Calendar,
  Search,
  Tag,
  Sparkles,
} from "lucide-react";

interface ResourcesTabProps {
  pack: StudyPackOutput;
}

function isGenericTitle(text?: string): boolean {
  if (!text) return true;
  const clean = text.trim().toLowerCase().replace(/\.pdf$/i, "").replace(/[_-]/g, " ");
  const genericPatterns = [
    /^(unit|chapter|module|lecture|lesson|part|week|session|assignment|test|exam|notes?|doc(ument)?)\s*\d*$/i,
    /^(unit|chapter|module|lecture)\s*[-_:]?\s*\d+$/i,
    /^(final|midterm|internal|class|syllabus|slides?|presentation)\s*\d*$/i,
    /^[a-z0-9]{1,3}$/i,
  ];
  return genericPatterns.some((pattern) => pattern.test(clean)) || clean.length < 4;
}

// Derive the most relevant educational search topic from the study pack
function deriveTopic(pack: StudyPackOutput): string {
  // 1. Check notes topics first (these are actual conceptual topics like "Cloud Computing Architecture", "Virtualization")
  for (const note of pack.notes || []) {
    const noteTopic = (note.topic || note.title || "").trim();
    if (noteTopic && !isGenericTitle(noteTopic)) {
      return noteTopic.slice(0, 80);
    }
  }

  // 2. Check recommended study order
  for (const step of pack.recommended_study_order || []) {
    const cleaned = step.replace(/^(Read|Study|Review|Practice|Take|Consult|Understand|Master)\s+/i, "").trim();
    if (cleaned && !isGenericTitle(cleaned)) {
      return cleaned.slice(0, 80);
    }
  }

  // 3. If pack.title is NOT a generic filename like "unit 4" or "unit 4.pdf"
  if (pack.title && !isGenericTitle(pack.title)) {
    return pack.title.replace(/\.pdf$/i, "").replace(/[_-]/g, " ").trim();
  }

  // 4. Extract subject phrase from the summary
  if (pack.summary) {
    const firstSentence = pack.summary.split(/[.\n]/)[0].trim();
    const match = firstSentence.match(/(?:focuses on|covers|introduces|explores|discusses|overview of)\s+([^,.]+)/i);
    if (match && match[1] && !isGenericTitle(match[1])) {
      return match[1].trim().slice(0, 80);
    }
    if (firstSentence.length > 5 && firstSentence.length < 60 && !isGenericTitle(firstSentence)) {
      return firstSentence;
    }
  }

  return "Cloud Computing Fundamentals";
}

function getSuggestedTopics(pack: StudyPackOutput): string[] {
  const topics: string[] = [];
  for (const n of pack.notes || []) {
    const t = (n.topic || n.title || "").trim();
    if (t && !isGenericTitle(t) && !topics.includes(t)) {
      topics.push(t);
    }
  }
  for (const g of pack.glossary?.slice(0, 4) || []) {
    if (g.term && !isGenericTitle(g.term) && !topics.includes(g.term)) {
      topics.push(g.term);
    }
  }
  return topics.slice(0, 5);
}

// ── Skeleton Loaders ────────────────────────────────────────────────────────

function BookSkeleton() {
  return (
    <div className="flex gap-4 p-4 rounded-2xl bg-neutral-900/60 border border-neutral-800/60 animate-pulse">
      <div className="w-16 h-24 rounded-lg bg-neutral-800 shrink-0" />
      <div className="flex-1 space-y-2 pt-1">
        <div className="h-3.5 bg-neutral-800 rounded w-3/4" />
        <div className="h-3 bg-neutral-800 rounded w-1/2" />
        <div className="h-3 bg-neutral-800 rounded w-full" />
        <div className="h-3 bg-neutral-800 rounded w-5/6" />
      </div>
    </div>
  );
}

function VideoSkeleton() {
  return (
    <div className="rounded-2xl overflow-hidden bg-neutral-900/60 border border-neutral-800/60 animate-pulse">
      <div className="w-full aspect-video bg-neutral-800" />
      <div className="p-3 space-y-2">
        <div className="h-3.5 bg-neutral-800 rounded w-4/5" />
        <div className="h-3 bg-neutral-800 rounded w-1/2" />
      </div>
    </div>
  );
}

// ── Book Card ───────────────────────────────────────────────────────────────

function BookCard({ book }: { book: BookItem }) {
  return (
    <div className="group flex gap-4 p-4 rounded-2xl bg-neutral-900/60 border border-neutral-800/60 hover:border-neutral-700 hover:bg-neutral-900/80 transition-all duration-200">
      {/* Cover thumbnail */}
      <div className="shrink-0 w-16 h-24 rounded-lg overflow-hidden bg-neutral-800 border border-neutral-700/50">
        {book.thumbnail ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={book.thumbnail}
            alt={book.title}
            className="w-full h-full object-cover"
            onError={(e) => {
              (e.currentTarget as HTMLImageElement).style.display = "none";
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-neutral-600">
            <BookOpen className="w-6 h-6" />
          </div>
        )}
      </div>

      <div className="flex-1 min-w-0 space-y-1.5">
        <h3 className="text-sm font-semibold text-white leading-snug line-clamp-2 group-hover:text-indigo-200 transition-colors">
          {book.title}
        </h3>

        {book.authors.length > 0 && (
          <div className="flex items-center gap-1.5 text-[11px] text-neutral-400">
            <Users className="w-3 h-3 shrink-0" />
            <span className="truncate">{book.authors.slice(0, 2).join(", ")}</span>
          </div>
        )}

        {book.publisher && (
          <div className="flex items-center gap-1.5 text-[11px] text-neutral-500">
            <BookMarked className="w-3 h-3 shrink-0" />
            <span className="truncate">{book.publisher}</span>
          </div>
        )}

        {book.publishedDate && (
          <div className="flex items-center gap-1.5 text-[11px] text-neutral-500">
            <Calendar className="w-3 h-3 shrink-0" />
            <span>{book.publishedDate.slice(0, 4)}</span>
          </div>
        )}

        {book.description && (
          <p className="text-xs text-neutral-400 line-clamp-2 leading-relaxed pt-0.5">
            {book.description}
          </p>
        )}

        {book.previewLink && (
          <a
            href={book.previewLink}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 transition-colors font-medium pt-1"
          >
            <span>Preview on Google Books</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>
    </div>
  );
}

// ── Video Card ──────────────────────────────────────────────────────────────

function VideoCard({ video }: { video: VideoItem }) {
  return (
    <a
      href={video.video_url}
      target="_blank"
      rel="noopener noreferrer"
      className="group block rounded-2xl overflow-hidden bg-neutral-900/60 border border-neutral-800/60 hover:border-neutral-700 hover:bg-neutral-900/80 transition-all duration-200"
    >
      <div className="relative w-full aspect-video bg-neutral-800 overflow-hidden">
        {video.thumbnail ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={video.thumbnail}
            alt={video.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            onError={(e) => {
              (e.currentTarget as HTMLImageElement).style.display = "none";
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-neutral-600">
            <Tv2 className="w-8 h-8" />
          </div>
        )}

        <div className="absolute inset-0 bg-black/30 group-hover:bg-black/10 transition-colors flex items-center justify-center">
          <div className="w-10 h-10 rounded-full bg-red-600/90 group-hover:bg-red-600 group-hover:scale-110 flex items-center justify-center shadow-lg transition-all">
            <Play className="w-4 h-4 text-white fill-white translate-x-0.5" />
          </div>
        </div>
      </div>

      <div className="p-3.5 space-y-1.5">
        <h4 className="text-xs font-semibold text-white leading-snug line-clamp-2 group-hover:text-indigo-200 transition-colors">
          {video.title}
        </h4>

        {video.channel_title && (
          <p className="text-[11px] text-neutral-400 truncate">{video.channel_title}</p>
        )}

        {video.description && (
          <p className="text-[11px] text-neutral-500 line-clamp-2 leading-relaxed">
            {video.description}
          </p>
        )}
      </div>
    </a>
  );
}

// ── Main Component ──────────────────────────────────────────────────────────

export function ResourcesTab({ pack }: ResourcesTabProps) {
  const initialTopic = deriveTopic(pack);
  const [topic, setTopic] = useState(initialTopic);
  const [searchInput, setSearchInput] = useState(initialTopic);
  const suggestedTopics = getSuggestedTopics(pack);

  const [books, setBooks] = useState<BookItem[]>([]);
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [booksLoading, setBooksLoading] = useState(true);
  const [videosLoading, setVideosLoading] = useState(true);
  const [booksError, setBooksError] = useState<string | null>(null);
  const [videosError, setVideosError] = useState<string | null>(null);

  const loadBooks = (queryTopic = topic) => {
    setBooksLoading(true);
    setBooksError(null);
    api.resources
      .getBooks(queryTopic, 5)
      .then((res) => setBooks(res.books || []))
      .catch((err) => setBooksError(err instanceof ApiError ? err.message : "Failed to load books."))
      .finally(() => setBooksLoading(false));
  };

  const loadVideos = (queryTopic = topic) => {
    setVideosLoading(true);
    setVideosError(null);
    api.resources
      .getVideos(queryTopic, 5)
      .then((res) => setVideos(res.videos || []))
      .catch((err) => setVideosError(err instanceof ApiError ? err.message : "Failed to load videos."))
      .finally(() => setVideosLoading(false));
  };

  const loadResources = (queryTopic: string) => {
    loadBooks(queryTopic);
    loadVideos(queryTopic);
  };

  useEffect(() => {
    loadResources(topic);
  }, [topic]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      setTopic(searchInput.trim());
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* ── Search & Topic Bar ────────────────────────────────────────── */}
      <div className="p-4 rounded-2xl bg-neutral-900/60 border border-neutral-800/80 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-violet-400" /> Curated Educational Resources
            </h2>
            <p className="text-xs text-neutral-400 mt-0.5">
              Targeted textbooks and lecture videos tailored to your study material.
            </p>
          </div>
          <button
            type="button"
            onClick={() => loadResources(topic)}
            disabled={booksLoading || videosLoading}
            className="self-start sm:self-auto flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium text-neutral-300 hover:text-white bg-neutral-800 hover:bg-neutral-700/80 border border-neutral-700/60 transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${booksLoading || videosLoading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>

        {/* Search query input */}
        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500" />
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Search books & videos for any topic (e.g. Cloud Computing)..."
              className="w-full pl-9 pr-4 py-2 text-xs bg-neutral-950 border border-neutral-800 rounded-xl text-white placeholder-neutral-500 focus:outline-none focus:border-violet-500 transition-colors"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-xl text-xs font-medium transition-colors shrink-0"
          >
            Search
          </button>
        </form>

        {/* Topic Suggestion Chips */}
        {suggestedTopics.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5 pt-1">
            <span className="text-[11px] text-neutral-500 flex items-center gap-1 mr-1">
              <Tag className="w-3 h-3" /> Topics:
            </span>
            {suggestedTopics.map((sTopic) => {
              const active = topic.toLowerCase() === sTopic.toLowerCase();
              return (
                <button
                  key={sTopic}
                  type="button"
                  onClick={() => {
                    setSearchInput(sTopic);
                    setTopic(sTopic);
                  }}
                  className={`text-[11px] px-2.5 py-1 rounded-lg transition-all border ${
                    active
                      ? "bg-violet-600/30 text-violet-300 border-violet-500/50 font-medium"
                      : "bg-neutral-950 text-neutral-400 border-neutral-800 hover:border-neutral-700 hover:text-white"
                  }`}
                >
                  {sTopic}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* ── Books Section ─────────────────────────────────────────────── */}
      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-violet-500/15 text-violet-400">
            <BookOpen className="w-4 h-4" />
          </div>
          <h3 className="text-sm font-bold text-white">Recommended Books</h3>
          {!booksLoading && books.length > 0 && (
            <span className="ml-auto text-xs text-neutral-500">
              {books.length} result{books.length !== 1 ? "s" : ""} via Google Books
            </span>
          )}
        </div>

        {booksLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => <BookSkeleton key={i} />)}
          </div>
        ) : booksError ? (
          <div className="flex items-start gap-3 p-4 rounded-2xl bg-rose-950/30 border border-rose-800/50 text-rose-200 text-sm">
            <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Failed to load books</p>
              <p className="text-xs text-rose-300 mt-0.5">{booksError}</p>
              <button
                type="button"
                onClick={() => loadBooks(topic)}
                className="mt-2 text-xs font-semibold text-rose-300 hover:text-white inline-flex items-center gap-1 transition-colors"
              >
                <RefreshCw className="w-3 h-3" /> Retry
              </button>
            </div>
          </div>
        ) : books.length === 0 ? (
          <div className="flex items-center justify-center py-10 text-center text-neutral-500">
            <div className="space-y-2">
              <BookOpen className="w-8 h-8 mx-auto" />
              <p className="text-sm">No books found for this topic.</p>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {books.map((book, idx) => (
              <BookCard key={`${book.title}-${idx}`} book={book} />
            ))}
          </div>
        )}
      </section>

      {/* ── Videos Section ────────────────────────────────────────────── */}
      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-rose-500/15 text-rose-400">
            <Tv2 className="w-4 h-4" />
          </div>
          <h3 className="text-sm font-bold text-white">Lecture Videos</h3>
          {!videosLoading && videos.length > 0 && (
            <span className="ml-auto text-xs text-neutral-500">
              {videos.length} result{videos.length !== 1 ? "s" : ""} via YouTube
            </span>
          )}
        </div>

        {videosLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => <VideoSkeleton key={i} />)}
          </div>
        ) : videosError ? (
          <div className="flex items-start gap-3 p-4 rounded-2xl bg-rose-950/30 border border-rose-800/50 text-rose-200 text-sm">
            <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Failed to load videos</p>
              <p className="text-xs text-rose-300 mt-0.5">{videosError}</p>
              <button
                type="button"
                onClick={() => loadVideos(topic)}
                className="mt-2 text-xs font-semibold text-rose-300 hover:text-white inline-flex items-center gap-1 transition-colors"
              >
                <RefreshCw className="w-3 h-3" /> Retry
              </button>
            </div>
          </div>
        ) : videos.length === 0 ? (
          <div className="flex items-center justify-center py-10 text-center text-neutral-500">
            <div className="space-y-2">
              <Tv2 className="w-8 h-8 mx-auto" />
              <p className="text-sm">No videos found for this topic.</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {videos.map((video) => (
              <VideoCard key={video.video_id} video={video} />
            ))}
          </div>
        )}
      </section>

      {/* Attribution footer */}
      <div className="flex items-center gap-4 pt-4 border-t border-neutral-800/50 text-[10px] text-neutral-600">
        <span className="flex items-center gap-1">
          <BookOpen className="w-3 h-3" /> Powered by Google Books API
        </span>
        <span className="flex items-center gap-1">
          <Tv2 className="w-3 h-3" /> Powered by YouTube Data API v3
        </span>
      </div>
    </div>
  );
}
