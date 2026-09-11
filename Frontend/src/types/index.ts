export type Difficulty = "Easy" | "Medium" | "Hard";

export interface HighlightItem {
  type: "Important" | "Definition" | "Concept" | "Remember" | string;
  text: string;
}

export interface NoteItem {
  id?: number;
  topic?: string;
  title?: string;
  content?: string[];
  key_points?: string[];
  highlights?: HighlightItem[];
}

export interface GlossaryItem {
  term: string;
  definition: string;
}

export interface FlashcardItem {
  id?: number;
  term?: string;
  definition?: string;
  front?: string;
  back?: string;
  topic?: string;
}

export interface MCQItem {
  id: number;
  question: string;
  options: string[];
  answer: string;
  difficulty: Difficulty;
  topic: string;
  explanation: string;
}

export interface SAQItem {
  id?: number;
  question: string;
  model_answer?: string;
  sample_answer?: string;
  difficulty?: Difficulty;
  topic?: string;
  rubric?: string[];
}

export interface StudyPackOutput {
  id?: string;
  title?: string;
  created_at?: string;
  source_file_name?: string;
  source_text?: string;
  summary: string;
  recommended_study_order: string[];
  notes: NoteItem[];
  glossary: GlossaryItem[];
  flashcards: FlashcardItem[];
  mcqs: MCQItem[];
  short_answers: SAQItem[];
}

export interface TopicPerformance {
  total: number;
  correct: number;
  accuracy: number;
}

export interface QuizSubmission {
  studypack_id?: string;
  answers: Record<number, string>;
  mcqs?: MCQItem[];
  current_difficulty: Difficulty;
}

export interface QuizResult {
  score: number;
  weak_topics: string[];
  topic_performance: Record<string, TopicPerformance>;
  difficulty_breakdown: Record<string, number>;
  missed_question_ids: number[];
  next_difficulty: Difficulty;
}

export interface SourceChunk {
  chunk_id: string;
  text: string;
  relevance_score: number;
}

export interface TutorRequest {
  question: string;
  session_id?: string;
  context_id?: string;
}

export interface TutorResponse {
  answer: string;
  sources: SourceChunk[];
  confidence: number;
  follow_up_suggestions: string[];
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  avatar?: string;
}
