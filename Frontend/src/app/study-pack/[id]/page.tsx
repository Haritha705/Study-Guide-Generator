"use client";

import React, { use } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { StudyPackView } from "@/components/study-pack/StudyPackView";
import { useStudyStore } from "@/stores/useStudyStore";
import Link from "next/link";
import { PlusCircle, BookOpen } from "lucide-react";

export default function StudyPackDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const { studyPacks, activePack } = useStudyStore();

  const currentPack =
    studyPacks.find((p) => p.id === resolvedParams.id) || activePack;

  if (!currentPack) {
    return (
      <AppLayout>
        <div className="max-w-md mx-auto py-24 text-center space-y-4">
          <BookOpen className="w-12 h-12 text-neutral-600 mx-auto" />
          <h2 className="text-lg font-semibold text-white">Study Pack Not Found</h2>
          <p className="text-xs text-neutral-400">
            This study pack may have been removed or does not exist.
          </p>
          <Link
            href="/create"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 text-white hover:bg-indigo-500 transition-colors"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Generate a New Study Pack</span>
          </Link>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <StudyPackView pack={currentPack} />
    </AppLayout>
  );
}
