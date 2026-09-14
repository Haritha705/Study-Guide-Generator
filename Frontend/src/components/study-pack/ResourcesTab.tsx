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
} from "lucide-react";

interface ResourcesTabProps {
  pack: StudyPackOutput;
}

// Derive the most relevant search topic from the study pack
function deriveTopic(pack: StudyPackOutput): string {
  if (pack.title && pack.title.length > 3) return pack.title;
  if (pack.recommended_study_order?.[0]) {
    return pack.recommended_study_order[0].replace(/^(Read|Study|Review|Practice|Take|Consult)\s+/i, "").slice(0, 80);
  }
  if (pack.notes?.[0]?.title) return pack.notes[0].title;
  return "Study Material";
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

        {book.description && (
          <p className="text-[11px] text-neutral-500 leading-relaxed line-clamp-2">
            {book.description}
          </p>
        )}

        {(book.previewLink || book.infoLink) && (
          <a
            href={book.previewLink || book.infoLink}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-[11px] font-semibold text-indigo-400 hover:text-indigo-300 transition-colors mt-1"
          >
            <ExternalLink className="w-3 h-3" />
            Preview on Google Books
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
      className="group block rounded-2xl overflow-hidden bg-neutral-900/60 border border-neutral-800/60 hover:border-indigo-500/50 hover:bg-neutral-900/80 transition-all duration-200 shadow-sm hover:shadow-indigo-500/10"
    >
      {/* Thumbnail */}
      <div className="relative w-full aspect-video overflow-hidden bg-neutral-800">
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
        {/* Play overlay */}
        <div className="absolute inset-0 flex items-center justify-center bg-black/0 group-hover:bg-black/30 transition-colors duration-200">
          <div className="w-10 h-10 rounded-full bg-white/0 group-hover:bg-white/90 flex items-center justify-center transition-all duration-200 scale-0 group-hover:scale-100">
            <Play className="w-4 h-4 text-neutral-900 ml-0.5" />
          </div>
        </div>
      </div>

      {/* Info */}
      <div className="p-3 space-y-1">
        <h3 className="text-xs font-semibold text-neutral-100 leading-snug line-clamp-2 group-hover:text-white transition-colors">
          {video.title}
        </h3>
        <div className="flex items-center justify-between gap-2">
          <span className="text-[10px] text-neutral-500 truncate">{video.channel_title}</span>
          {video.published_at && (
            <span className="text-[10px] text-neutral-600 shrink-0 flex items-center gap-1">
              <Calendar className="w-2.5 h-2.5" />
              {new Date(video.published_at).getFullYear()}
            </span>
          )}
        </div>
      </div>
    </a>
  );
}

// ── Main Component ──────────────────────────────────────────────────────────

export function ResourcesTab({ pack }: ResourcesTabProps) {
  const topic = deriveTopic(pack);

  const [books, setBooks] = useState<BookItem[]>([]);
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [booksLoading, setBooksLoading] = useState(true);
  const [videosLoading, setVideosLoading] = useState(true);
  const [booksError, setBooksError] = useState<string | null>(null);
  const [videosError, setVideosError] = useState<string | null>(null);

  // Use ref to track if the initial fetch has been triggered to avoid double-fetch in StrictMode
  const fetched = useRef(false);

  const loadBooks = async () => {
    setBooksLoading(true);
    setBooksError(null);
    try {
      const res = await api.resources.getBooks(topic, 5);
      setBooks(res.books || []);
    } catch (err) {
      setBooksError(err instanceof ApiError ? err.message : "Failed to load books.");
    } finally {
      setBooksLoading(false);
    }
  };

  const loadVideos = async () => {
    setVideosLoading(true);
    setVideosError(null);
    try {
      const res = await api.resources.getVideos(topic, 5);
      setVideos(res.videos || []);
    } catch (err) {
      setVideosError(err instanceof ApiError ? err.message : "Failed to load videos.");
    } finally {
      setVideosLoading(false);
    }
  };

  useEffect(() => {
    if (fetched.current) return;
    fetched.current = true;
    loadBooks();
    loadVideos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleRefresh = () => {
    fetched.current = false;
    loadBooks();
    loadVideos();
  };

  return (
    <div className="space-y-10 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-lg font-bold text-white">Study Resources</h2>
          <p className="text-xs text-neutral-400">
            Supplementary books and videos for{" "}
            <span className="text-indigo-300 font-medium">"{topic}"</span>
          </p>
        </div>
        <button
          type="button"
          onClick={handleRefresh}
          className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium text-neutral-400 hover:text-white bg-neutral-900 border border-neutral-800 hover:border-neutral-700 transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
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
                onClick={loadBooks}
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
                onClick={loadVideos}
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
