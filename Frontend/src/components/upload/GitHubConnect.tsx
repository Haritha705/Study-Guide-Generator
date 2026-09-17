"use client";

import React, { useEffect, useState } from "react";
import { CheckCircle2, Github, LogOut } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";

export function GitHubConnect() {
  const [token, setToken] = useState<string | null>(null);
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    // 1. Check URL for newly minted token from OAuth callback
    const urlToken = searchParams.get("github_token");
    if (urlToken) {
      localStorage.setItem("github_mcp_token", urlToken);
      setToken(urlToken);
      // Clean up URL
      router.replace("/");
      return;
    }

    // 2. Check local storage for existing token
    const stored = localStorage.getItem("github_mcp_token");
    if (stored) {
      setToken(stored);
    }
  }, [searchParams, router]);

  const handleConnect = () => {
    // Redirect to the backend OAuth login route
    window.location.href = "http://localhost:8000/api/v1/auth/github/login";
  };

  const handleDisconnect = () => {
    localStorage.removeItem("github_mcp_token");
    setToken(null);
  };

  return (
    <div className="flex flex-col items-center space-y-4 p-6 border rounded-lg bg-card/50 shadow-sm w-full max-w-md mx-auto mt-4">
      <div className="p-3 bg-muted rounded-full">
        <Github className="w-8 h-8 text-primary" />
      </div>
      
      <div className="text-center space-y-1">
        <h3 className="font-semibold text-lg">GitHub MCP Integration</h3>
        <p className="text-sm text-muted-foreground">
          {token 
            ? "Your GitHub account is connected. You can now fetch repositories and markdown files for AI processing."
            : "Connect your GitHub account to directly import code, READMEs, and markdown notes as study materials."}
        </p>
      </div>

      {token ? (
        <div className="flex flex-col items-center w-full gap-3">
          <div className="flex items-center gap-2 text-green-600 dark:text-green-400 font-medium bg-green-500/10 px-4 py-2 rounded-full">
            <CheckCircle2 className="w-4 h-4" />
            <span>Connected</span>
          </div>
          <button 
            className="w-full flex items-center justify-center py-2 px-4 rounded-md border border-destructive text-destructive hover:bg-destructive/10 transition-colors"
            onClick={handleDisconnect}
          >
            <LogOut className="w-4 h-4 mr-2" />
            Disconnect
          </button>
        </div>
      ) : (
        <button 
          onClick={handleConnect} 
          className="w-full flex items-center justify-center py-2 px-4 rounded-md bg-indigo-600 hover:bg-indigo-700 text-white gap-2 transition-colors"
        >
          <Github className="w-4 h-4" />
          Connect to GitHub
        </button>
      )}
    </div>
  );
}
