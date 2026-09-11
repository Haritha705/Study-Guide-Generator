"use client";

import React, { useEffect } from "react";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { useStudyStore } from "@/stores/useStudyStore";

export function AppLayout({ children }: { children: React.ReactNode }) {
  const { loadPacksFromStorage } = useStudyStore();

  useEffect(() => {
    loadPacksFromStorage();
  }, [loadPacksFromStorage]);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-[#09090b]">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0 h-full overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto bg-[#09090b] relative">
          {children}
        </main>
      </div>
    </div>
  );
}
