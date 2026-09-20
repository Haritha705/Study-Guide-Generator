import {
  StudyPackOutput,
  MCQItem,
  QuizSubmission,
  QuizResult,
  TutorRequest,
  TutorResponse,
  Difficulty,
  DriveStatus,
  DriveFilesResponse,
  BooksResponse,
  VideosResponse,
} from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = new Headers(options.headers || {});

  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    let data: unknown = null;
    try {
      data = await response.json();
      if (typeof data === "object" && data !== null && "detail" in data) {
        errorDetail = String((data as { detail: unknown }).detail);
      }
    } catch {
      // response wasn't JSON
    }
    throw new ApiError(errorDetail, response.status, data);
  }

  return response.json();
}

export const api = {
  // 1. Health check
  async getHealth(): Promise<{ status: string; service: string }> {
    return request<{ status: string; service: string }>("/health");
  },

  // 2. PDF Text Extraction
  async extractPDF(file: File): Promise<{ extracted_text: string }> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/api/v1/extract/`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      let detail = "Failed to extract text from PDF";
      try {
        const data = await response.json();
        if (data?.detail) detail = data.detail;
      } catch {}
      throw new ApiError(detail, response.status);
    }

    return response.json();
  },

  // 3. Generate Complete Study Pack
  async generateStudyPack(textContent: string): Promise<StudyPackOutput> {
    return request<StudyPackOutput>("/api/v1/generate/", {
      method: "POST",
      body: JSON.stringify({ text_content: textContent }),
    });
  },

  // 4. Generate Adaptive MCQs with Difficulty (Easy, Medium, Hard/Tough)
  async generateQuiz(
    textContent: string,
    difficulty: Difficulty = "Medium",
    quizSize: number = 10
  ): Promise<{ mcqs: MCQItem[] }> {
    return request<{ mcqs: MCQItem[] }>("/api/v1/quiz/generate", {
      method: "POST",
      body: JSON.stringify({
        text_content: textContent,
        difficulty,
        quiz_size: quizSize,
      }),
    });
  },

  // 5. Submit Quiz Answers for Grading
  async submitQuiz(submission: QuizSubmission): Promise<QuizResult> {
    return request<QuizResult>("/api/v1/quiz/submit", {
      method: "POST",
      body: JSON.stringify(submission),
    });
  },

  // 6. AI Tutor Interaction (Legacy)
  async askTutor(tutorRequest: TutorRequest): Promise<TutorResponse> {
    return request<TutorResponse>("/api/v1/tutor/ask", {
      method: "POST",
      body: JSON.stringify(tutorRequest),
    });
  },

  // 6.1 Multi-Agent LangGraph Chat
  async agentChat(query: string, studyPackId?: string, contextText?: string): Promise<{ response: string }> {
    return request<{ response: string }>("/api/v1/agent/chat", {
      method: "POST",
      body: JSON.stringify({
        query,
        study_pack_id: studyPackId,
        context_text: contextText,
      }),
    });
  },

  // 7. Export Study Pack to PDF
  async exportPDF(studyPackData: StudyPackOutput): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/api/v1/export/pdf`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(studyPackData),
    });

    if (!response.ok) {
      throw new ApiError("Failed to export PDF", response.status);
    }

    return response.blob();
  },

  // 8. Export MCQs to CSV
  async exportCSV(mcqs: MCQItem[]): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/api/v1/export/csv`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(mcqs),
    });

    if (!response.ok) {
      throw new ApiError("Failed to export CSV", response.status);
    }

    return response.blob();
  },

  // ─── 9. Google Drive MCP ────────────────────────────────────────────────

  drive: {
    /** Check if Google Drive MCP server is reachable and authenticated. */
    async getStatus(): Promise<DriveStatus> {
      return request<DriveStatus>("/api/v1/drive/status");
    },

    /** Disconnect Google Drive account and revoke tokens. */
    async disconnect(): Promise<{ status: string; message: string }> {
      return request<{ status: string; message: string }>("/api/v1/auth/google/disconnect", {
        method: "POST",
      });
    },

    /** List or search Drive files (PDFs). */
    async listFiles(
      query: string = "",
      pageSize: number = 10
    ): Promise<DriveFilesResponse> {
      const params = new URLSearchParams();
      if (query) params.set("query", query);
      params.set("page_size", String(pageSize));
      return request<DriveFilesResponse>(`/api/v1/drive/files?${params}`);
    },

    /** Extract raw text from a Drive PDF file. */
    async extractText(fileId: string): Promise<{ file_id: string; extracted_text: string }> {
      return request<{ file_id: string; extracted_text: string }>(
        `/api/v1/drive/files/${encodeURIComponent(fileId)}/extract`
      );
    },

    /** Generate a full StudyPack directly from a Drive file ID. */
    async generate(fileId: string): Promise<StudyPackOutput> {
      return request<StudyPackOutput>("/api/v1/drive/generate", {
        method: "POST",
        body: JSON.stringify({ file_id: fileId }),
      });
    },
  },

  // ─── 10. Study Resources (Books + Videos) ───────────────────────────────

  resources: {
    /** Fetch relevant books for a study topic from Google Books API. */
    async getBooks(topic: string, maxResults: number = 5): Promise<BooksResponse> {
      const params = new URLSearchParams({ topic, max_results: String(maxResults) });
      return request<BooksResponse>(`/api/v1/study-pack/books?${params}`);
    },

    /** Fetch educational YouTube videos for a study topic. */
    async getVideos(topic: string, maxResults: number = 5): Promise<VideosResponse> {
      const params = new URLSearchParams({ topic, max_results: String(maxResults) });
      return request<VideosResponse>(`/api/v1/study-pack/videos?${params}`);
    },
  },
};
