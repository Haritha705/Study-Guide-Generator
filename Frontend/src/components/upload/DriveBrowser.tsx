"use client";

import React, { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "@/lib/apiClient";
import { DriveFile, DriveStatus } from "@/types";
import {
  Cloud,
  FileText,
  HardDrive,
  Loader2,
  RefreshCw,
  Search,
  WifiOff,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Clock,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface DriveBrowserProps {
  /** Called when the user confirms a Drive file selection. */
  onFileSelect: (file: DriveFile) => void;
  /** Currently selected file, if any. */
  selectedFile: DriveFile | null;
}

function formatBytes(bytes?: number): string {
  if (!bytes) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function formatModified(ts?: string): string {
  if (!ts) return "";
  try {
    return new Date(ts).toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return "";
  }
}

export function DriveBrowser({ onFileSelect, selectedFile }: DriveBrowserProps) {
  const [status, setStatus] = useState<DriveStatus | null>(null);
  const [statusLoading, setStatusLoading] = useState(true);
  const [files, setFiles] = useState<DriveFile[]>([]);
  const [filesLoading, setFilesLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [error, setError] = useState<string | null>(null);

  // ── 1. Fetch Drive connection status ────────────────────────────────────
  const fetchStatus = useCallback(async () => {
    setStatusLoading(true);
    setError(null);
    try {
      const s = await api.drive.getStatus();
      setStatus(s);
    } catch (err) {
      setStatus(null);
      setError(err instanceof ApiError ? err.message : "Failed to reach Drive MCP server.");
    } finally {
      setStatusLoading(false);
    }
  }, []);

  // ── 2. Fetch file list ────────────────────────────────────────────────────
  const fetchFiles = useCallback(
    async (query: string) => {
      if (!status?.connected) return;
      setFilesLoading(true);
      setError(null);
      try {
        const res = await api.drive.listFiles(query, 15);
        setFiles(res.files || []);
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Failed to list Drive files.");
      } finally {
        setFilesLoading(false);
      }
    },
    [status?.connected]
  );

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  useEffect(() => {
    if (status?.connected) {
      fetchFiles("");
    }
  }, [status?.connected, fetchFiles]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchQuery(searchInput);
    fetchFiles(searchInput);
  };

  const handleRefresh = () => {
    fetchFiles(searchQuery);
  };

  // ── Render: Status Banner ─────────────────────────────────────────────────
  const renderStatusBanner = () => {
    if (statusLoading) {
      return (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-neutral-900/70 border border-neutral-800 text-neutral-400 text-sm animate-pulse">
          <Loader2 className="w-4 h-4 animate-spin shrink-0" />
          <span>Connecting to Google Drive MCP…</span>
        </div>
      );
    }

    if (!status?.connected || error) {
      return (
        <div className="flex items-start gap-3 p-4 rounded-xl bg-rose-950/30 border border-rose-800/50 text-rose-200 text-sm">
          <WifiOff className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div className="space-y-1 min-w-0">
            <p className="font-semibold text-rose-100">Google Drive MCP Not Connected</p>
            <p className="text-xs text-rose-300 leading-relaxed">
              {error ||
                "The Drive MCP server is unreachable. Run the backend and ensure your OAuth token is valid."}
            </p>
            <button
              type="button"
              onClick={fetchStatus}
              className="mt-2 inline-flex items-center gap-1.5 text-xs font-semibold text-rose-300 hover:text-white transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Retry connection
            </button>
          </div>
        </div>
      );
    }

    return (
      <div className="flex items-center gap-3 p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-800/50 text-emerald-200 text-sm">
        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
        <span className="text-xs font-medium">
          Connected · {status.tools_count} tool{status.tools_count !== 1 ? "s" : ""} available
        </span>
        <span className="ml-auto text-[10px] font-mono text-emerald-600 truncate hidden sm:block">
          {status.server_url}
        </span>
      </div>
    );
  };

  // ── Render: File List ─────────────────────────────────────────────────────
  const renderFiles = () => {
    if (!status?.connected) return null;

    return (
      <div className="space-y-3">
        {/* Search bar */}
        <form onSubmit={handleSearch} className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-neutral-500 pointer-events-none" />
            <input
              type="text"
              placeholder="Search Drive PDFs…"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-neutral-900 border border-neutral-800 rounded-xl text-sm text-white placeholder:text-neutral-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
            />
          </div>
          <button
            type="submit"
            className="px-3 py-2 rounded-xl text-xs font-semibold bg-indigo-600/80 hover:bg-indigo-600 text-white border border-indigo-500/50 transition-colors"
          >
            Search
          </button>
          <button
            type="button"
            onClick={handleRefresh}
            className="p-2 rounded-xl text-neutral-400 hover:text-white bg-neutral-900 border border-neutral-800 transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </form>

        {/* File list */}
        {filesLoading ? (
          <div className="space-y-2">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="h-14 rounded-xl bg-neutral-900/60 border border-neutral-800/60 animate-pulse"
              />
            ))}
          </div>
        ) : files.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10 text-center space-y-2 text-neutral-500">
            <HardDrive className="w-8 h-8" />
            <p className="text-sm font-medium">No files found</p>
            <p className="text-xs">
              {searchQuery
                ? `No results for "${searchQuery}". Try a different search.`
                : "No PDFs found in your recent Drive files."}
            </p>
          </div>
        ) : (
          <div className="space-y-1.5 max-h-64 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-neutral-800 scrollbar-track-transparent">
            {files.map((file) => {
              const isSelected = selectedFile?.id === file.id;
              return (
                <button
                  key={file.id}
                  type="button"
                  onClick={() => onFileSelect(file)}
                  className={cn(
                    "w-full flex items-center gap-3 px-4 py-3 rounded-xl border text-left transition-all duration-150",
                    isSelected
                      ? "border-indigo-500 bg-indigo-500/10 shadow-sm"
                      : "border-neutral-800/70 bg-neutral-900/50 hover:border-neutral-700 hover:bg-neutral-900/80"
                  )}
                >
                  <div
                    className={cn(
                      "shrink-0 w-8 h-8 rounded-lg flex items-center justify-center",
                      isSelected ? "bg-indigo-600/20 text-indigo-400" : "bg-neutral-800 text-neutral-400"
                    )}
                  >
                    <FileText className="w-4 h-4" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <p
                      className={cn(
                        "text-sm font-medium truncate",
                        isSelected ? "text-white" : "text-neutral-200"
                      )}
                    >
                      {file.name}
                    </p>
                    <div className="flex items-center gap-2 mt-0.5">
                      {file.modifiedTime && (
                        <span className="inline-flex items-center gap-1 text-[10px] text-neutral-500">
                          <Clock className="w-3 h-3" />
                          {formatModified(file.modifiedTime)}
                        </span>
                      )}
                      {file.size !== undefined && (
                        <span className="text-[10px] text-neutral-600">
                          {formatBytes(file.size)}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    {file.webViewLink && (
                      <a
                        href={file.webViewLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="text-neutral-600 hover:text-neutral-300 transition-colors"
                        title="Open in Drive"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    )}
                    {isSelected && (
                      <CheckCircle2 className="w-4 h-4 text-indigo-400" />
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        )}

        {/* File count */}
        {!filesLoading && files.length > 0 && (
          <p className="text-[11px] text-neutral-600 text-right">
            {files.length} file{files.length !== 1 ? "s" : ""}
            {searchQuery ? ` matching "${searchQuery}"` : " (recent)"}
          </p>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2 text-sm font-semibold text-neutral-200">
        <Cloud className="w-4 h-4 text-indigo-400" />
        <span>Google Drive File Browser</span>
      </div>

      {/* Connection status */}
      {renderStatusBanner()}

      {/* Error alert (file listing errors, separate from status error) */}
      {error && status?.connected && (
        <div className="flex items-start gap-3 p-3.5 rounded-xl bg-amber-950/30 border border-amber-700/40 text-amber-200 text-xs">
          <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* File browser */}
      {renderFiles()}

      {/* Selected file indicator */}
      {selectedFile && (
        <div className="flex items-center gap-3 p-3.5 rounded-xl bg-indigo-950/30 border border-indigo-700/50">
          <FileText className="w-4 h-4 text-indigo-400 shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold text-indigo-200 truncate">
              Selected: {selectedFile.name}
            </p>
            <p className="text-[10px] text-indigo-400">
              Click “Generate Study Pack” to process this file
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
