"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useStudyStore } from "@/stores/useStudyStore";
import {
  BookOpen,
  Sparkles,
  PlusCircle,
  HelpCircle,
  Layers,
  GraduationCap,
  MessageSquare,
  BarChart3,
  ChevronRight,
  FolderOpen,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { UserButton, useUser, Show, SignInButton } from "@clerk/nextjs";

export function Sidebar() {
  const pathname = usePathname();
  const { studyPacks, activePack, setActivePack, user } = useStudyStore();
  const { user: clerkUser } = useUser();

  const navItems = [
    {
      name: "Dashboard",
      href: "/dashboard",
      icon: Layers,
    },
    {
      name: "Create Study Pack",
      href: "/create",
      icon: PlusCircle,
      highlight: true,
    },
    {
      name: "Active Study Pack",
      href: activePack ? `/study-pack/${activePack.id || "current"}` : "/create",
      icon: BookOpen,
      disabled: !activePack,
    },
    {
      name: "Adaptive Quiz",
      href: "/quiz",
      icon: HelpCircle,
    },
    {
      name: "AI Tutor",
      href: "/tutor",
      icon: MessageSquare,
    },
    {
      name: "Analytics & Mastery",
      href: "/analytics",
      icon: BarChart3,
    },
  ];

  return (
    <aside className="w-64 h-screen border-r border-neutral-800/80 bg-[#0d0d11] flex flex-col flex-shrink-0 select-none z-30">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-neutral-800/80 gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20 text-white font-bold text-base">
          <Sparkles className="w-5 h-5" />
        </div>
        <div className="flex flex-col">
          <span className="font-semibold text-neutral-100 tracking-tight text-base leading-none">
            StudyPack<span className="text-indigo-400">AI</span>
          </span>
          <span className="text-[11px] text-neutral-400 font-medium tracking-wide uppercase mt-1">
            Intelligent Study Studio
          </span>
        </div>
      </div>

      {/* Main Navigation */}
      <div className="px-3 py-4 flex flex-col gap-1">
        <div className="px-3 pb-2 text-[11px] font-semibold text-neutral-400 tracking-wider uppercase">
          Menu
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.name === "Active Study Pack" && pathname.startsWith("/study-pack"));

          return (
            <Link
              key={item.name}
              href={item.disabled ? "#" : item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 relative group",
                isActive
                  ? "bg-indigo-600/15 text-indigo-300 border border-indigo-500/30"
                  : item.highlight
                  ? "text-neutral-200 hover:bg-neutral-800/60 hover:text-white"
                  : "text-neutral-300 hover:bg-neutral-800/50 hover:text-neutral-100",
                item.disabled && "opacity-40 cursor-not-allowed pointer-events-none"
              )}
            >
              <Icon
                className={cn(
                  "w-4 h-4 transition-colors",
                  isActive ? "text-indigo-400" : "text-neutral-400 group-hover:text-neutral-300"
                )}
              />
              <span className="flex-1 truncate">{item.name}</span>
              {item.highlight && (
                <span className="px-1.5 py-0.5 text-[10px] font-semibold rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  New
                </span>
              )}
            </Link>
          );
        })}
      </div>

      {/* Study Packs List */}
      <div className="flex-1 overflow-y-auto px-3 py-2 flex flex-col gap-1">
        <div className="px-3 py-1 flex items-center justify-between text-[11px] font-semibold text-neutral-400 tracking-wider uppercase">
          <span>Saved Packs ({studyPacks.length})</span>
          <FolderOpen className="w-3.5 h-3.5" />
        </div>

        <div className="space-y-1 mt-1">
          {studyPacks.map((pack) => {
            const isCurrent = activePack?.id === pack.id;
            return (
              <button
                key={pack.id || pack.title}
                onClick={() => setActivePack(pack)}
                className={cn(
                  "w-full text-left px-3 py-2 rounded-lg text-xs transition-all flex items-center gap-2 group",
                  isCurrent
                    ? "bg-neutral-800 text-white font-medium border border-neutral-700"
                    : "text-neutral-300 hover:bg-neutral-800/50 hover:text-neutral-200"
                )}
              >
                <div
                  className={cn(
                    "w-1.5 h-1.5 rounded-full shrink-0",
                    isCurrent ? "bg-indigo-400" : "bg-neutral-600 group-hover:bg-neutral-500"
                  )}
                />
                <span className="truncate flex-1">
                  {pack.title || "Untitled Study Pack"}
                </span>
                <ChevronRight className="w-3 h-3 text-neutral-400 opacity-0 group-hover:opacity-100 transition-opacity" />
              </button>
            );
          })}
        </div>
      </div>

      {/* User Footer */}
      <div className="p-3 border-t border-neutral-800/80 bg-[#0b0b0e]">
        <Show when="signed-in">
          <div className="flex items-center gap-2.5 min-w-0">
            <UserButton
              appearance={{
                elements: {
                  avatarBox: "w-8 h-8 rounded-full ring-2 ring-indigo-500/30",
                },
              }}
            />
            <div className="flex flex-col flex-1 min-w-0">
              <span className="text-xs font-semibold text-neutral-200 truncate">
                {clerkUser?.fullName || clerkUser?.username || user.name}
              </span>
              <span className="text-[10px] text-neutral-400 truncate">
                {clerkUser?.primaryEmailAddress?.emailAddress || user.email}
              </span>
            </div>
            <div className="w-2 h-2 rounded-full bg-emerald-400 shrink-0" title="Session Active" />
          </div>
        </Show>
        <Show when="signed-out">
          <SignInButton mode="modal">
            <button className="w-full py-2 px-3 text-xs font-semibold rounded-lg bg-indigo-600 text-white hover:bg-indigo-500 transition-colors flex items-center justify-center gap-2">
              <span>Sign In</span>
            </button>
          </SignInButton>
        </Show>
      </div>
    </aside>
  );
}
