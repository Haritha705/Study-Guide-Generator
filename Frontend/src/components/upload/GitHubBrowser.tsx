"use client";

import React, { useEffect, useState } from "react";
import { CheckCircle2, FileCode2, Github, Loader2, RefreshCw, FolderGit2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface GitHubRepo {
  full_name: string;
  description: string | null;
  private: boolean;
}

interface GitHubFile {
  path: string;
  name: string;
  type: "file" | "dir";
}

interface GitHubBrowserProps {
  onFileSelect: (repo: string, path: string) => void;
  selectedRepo: string | null;
  selectedPath: string | null;
}

export function GitHubBrowser({ onFileSelect, selectedRepo, selectedPath }: GitHubBrowserProps) {
  const [token, setToken] = useState<string | null>(null);
  const [repos, setRepos] = useState<GitHubRepo[]>([]);
  const [files, setFiles] = useState<GitHubFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Active selection for browsing
  const [activeRepo, setActiveRepo] = useState<string | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem("github_mcp_token");
    if (stored) {
      setToken(stored);
      fetchRepos(stored);
    }
  }, []);

  const fetchRepos = async (authToken: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("https://api.github.com/user/repos?sort=updated&per_page=15", {
        headers: {
          Authorization: `Bearer ${authToken}`,
          Accept: "application/vnd.github.v3+json",
        }
      });
      if (!res.ok) throw new Error("Failed to fetch repositories.");
      const data = await res.json();
      setRepos(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchFiles = async (repoFullName: string, authToken: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`https://api.github.com/repos/${repoFullName}/contents`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
          Accept: "application/vnd.github.v3+json",
        }
      });
      if (!res.ok) throw new Error("Failed to fetch files.");
      const data = await res.json();
      setFiles(Array.isArray(data) ? data : []);
      setActiveRepo(repoFullName);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="flex flex-col items-center justify-center py-10 text-neutral-500">
        <Github className="w-8 h-8 mb-2 opacity-50" />
        <p className="text-sm font-medium">Please connect your GitHub account first.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm font-semibold text-neutral-200">
        <Github className="w-4 h-4 text-indigo-400" />
        <span>GitHub Repository Browser</span>
      </div>

      {error && (
        <div className="p-3 text-xs text-rose-200 bg-rose-950/30 border border-rose-800/50 rounded-xl">
          {error}
        </div>
      )}

      {!activeRepo ? (
        <div className="space-y-2">
          <p className="text-xs text-neutral-400 font-medium pb-1">Select a Repository:</p>
          {loading ? (
            <div className="flex items-center gap-2 text-neutral-500 text-sm py-4">
              <Loader2 className="w-4 h-4 animate-spin" /> Loading repositories...
            </div>
          ) : (
            <div className="space-y-1.5 max-h-60 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-neutral-800">
              {repos.map(repo => (
                <button
                  key={repo.full_name}
                  onClick={() => fetchFiles(repo.full_name, token)}
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-xl border border-neutral-800/70 bg-neutral-900/50 hover:bg-neutral-800 transition-colors text-left"
                >
                  <FolderGit2 className="w-4 h-4 text-neutral-400" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-neutral-200 truncate">{repo.full_name}</p>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-2">
          <div className="flex items-center justify-between pb-1">
            <p className="text-xs text-neutral-400 font-medium truncate">
              Browsing: <span className="text-indigo-400">{activeRepo}</span>
            </p>
            <button 
              onClick={() => setActiveRepo(null)}
              className="text-[10px] text-neutral-500 hover:text-neutral-300"
            >
              Back to Repos
            </button>
          </div>

          {loading ? (
             <div className="flex items-center gap-2 text-neutral-500 text-sm py-4">
               <Loader2 className="w-4 h-4 animate-spin" /> Loading files...
             </div>
          ) : (
            <div className="space-y-1.5 max-h-60 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-neutral-800">
              {files.filter(f => f.type === "file").map(file => {
                const isSelected = selectedRepo === activeRepo && selectedPath === file.path;
                return (
                  <button
                    key={file.path}
                    onClick={() => onFileSelect(activeRepo, file.path)}
                    className={cn(
                      "w-full flex items-center gap-3 px-4 py-3 rounded-xl border text-left transition-all duration-150",
                      isSelected
                        ? "border-indigo-500 bg-indigo-500/10 shadow-sm"
                        : "border-neutral-800/70 bg-neutral-900/50 hover:border-neutral-700 hover:bg-neutral-900/80"
                    )}
                  >
                    <FileCode2 className={cn("w-4 h-4", isSelected ? "text-indigo-400" : "text-neutral-400")} />
                    <span className={cn("text-sm truncate flex-1", isSelected ? "text-white font-medium" : "text-neutral-300")}>
                      {file.name}
                    </span>
                    {isSelected && <CheckCircle2 className="w-4 h-4 text-indigo-400" />}
                  </button>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
