"use client";

import React from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { CreateStudyPack } from "@/components/upload/CreateStudyPack";

export default function CreatePage() {
  return (
    <AppLayout>
      <CreateStudyPack />
    </AppLayout>
  );
}
