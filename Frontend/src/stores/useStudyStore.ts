import { create } from "zustand";
import {
  StudyPackOutput,
  MCQItem,
  QuizResult,
  Difficulty,
  UserProfile,
} from "@/types";

interface QuizSessionState {
  questions: MCQItem[];
  currentDifficulty: Difficulty;
  currentIndex: number;
  answers: Record<number, string>;
  isCompleted: boolean;
  result: QuizResult | null;
  timeSpentSeconds: number;
}

interface StudyState {
  // Study Packs
  studyPacks: StudyPackOutput[];
  activePack: StudyPackOutput | null;
  isLoading: boolean;
  error: string | null;

  // Active Quiz State
  quizSession: QuizSessionState | null;

  // User Profile
  user: UserProfile;

  // Actions
  setActivePack: (pack: StudyPackOutput | null) => void;
  savePack: (pack: StudyPackOutput) => void;
  deletePack: (id: string) => void;
  loadPacksFromStorage: () => void;
  
  // Quiz Actions
  startQuiz: (mcqs: MCQItem[], initialDifficulty?: Difficulty) => void;
  selectQuizAnswer: (questionId: number, answer: string) => void;
  nextQuizQuestion: () => void;
  prevQuizQuestion: () => void;
  jumpToQuizQuestion: (index: number) => void;
  setQuizResult: (result: QuizResult) => void;
  resetQuiz: () => void;

  // User Actions
  setUser: (user: Partial<UserProfile>) => void;
}

const STORAGE_KEY = "studypack_saved_packs_v1";

const DEFAULT_USER: UserProfile = {
  id: "usr_101",
  name: "Haritha",
  email: "student@studypack.ai",
  avatar: "H",
};

// Initial starter pack so the user can immediately experience the UI if they want to preview
const DEMO_PACK: StudyPackOutput = {
  id: "demo-pack-cs101",
  title: "Machine Learning & Neural Networks Fundamentals",
  source_file_name: "lecture_03_neural_nets.pdf",
  created_at: new Date(Date.now() - 3600000 * 24).toISOString(),
  summary:
    "This study pack explores the mathematical foundations of artificial neural networks, gradient descent optimization, backpropagation via the chain rule, and common activation functions including ReLU, Sigmoid, and GELU. It contrasts shallow architectures with deep multi-layer perceptrons, explaining the vanishing gradient problem and how modern regularization techniques mitigate overfitting.",
  recommended_study_order: [
    "Read the Executive Summary to grasp foundational concepts",
    "Study the Core Architectural Notes on Forward and Backward propagation",
    "Review Glossary terms especially Gradient Vanishing, Learning Rate, and Overfitting",
    "Practice Active Recall with the 3D Interactive Flashcards",
    "Take the Adaptive Quiz starting at Medium difficulty to benchmark comprehension",
    "Review Short Answer explanations to solidify theoretical proofs",
    "Consult the AI Tutor to clarify any ambiguous derivations",
  ],
  notes: [
    {
      id: 1,
      title: "Perceptron & Forward Propagation",
      key_points: [
        "A biological neuron inspired mathematical abstraction: inputs are multiplied by weights, summed with a bias term, and passed through a non-linear activation function.",
        "Without non-linear activations, stacking linear layers collapses into a single affine transformation, eliminating the capacity to model complex non-linear boundaries.",
        "Mathematical formulation: z = W · x + b, followed by activation a = σ(z).",
      ],
    },
    {
      id: 2,
      title: "Backpropagation & Gradient Descent",
      key_points: [
        "Backpropagation systematically computes the partial derivative of the loss function with respect to every weight using the chain rule of calculus.",
        "Loss gradients flow backward through network layers; weights update via w := w - η * (∂L/∂w), where η represents learning rate.",
        "Stochastic Gradient Descent (SGD) introduces noise to escape shallow local minima, while Adam optimizer uses adaptive moment estimation.",
      ],
    },
    {
      id: 3,
      title: "Vanishing & Exploding Gradients",
      key_points: [
        "Traditional saturating activations (Sigmoid/Tanh) produce derivatives between 0 and 0.25, causing gradient magnitudes to decay exponentially across deep layers.",
        "Rectified Linear Unit (ReLU) f(x) = max(0, x) prevents gradient decay in positive regimes, though can suffer from the 'dying ReLU' issue if weights shift excessively negative.",
        "Modern architectures employ LayerNorm, Residual Skip Connections, and He/Xavier weight initialization to guarantee stable gradient flow.",
      ],
    },
  ],
  glossary: [
    {
      term: "Activation Function",
      definition:
        "A non-linear mathematical transformation applied to a neuron's affine output to enable neural networks to learn non-linear patterns.",
    },
    {
      term: "Backpropagation",
      definition:
        "The standard algorithm for training feedforward neural networks using the differential chain rule to compute gradients backward from loss.",
    },
    {
      term: "Overfitting",
      definition:
        "A modeling error occurring when a network memorizes training noise and idiosyncrasies rather than generalizing to unseen validation distributions.",
    },
    {
      term: "Learning Rate (η)",
      definition:
        "A critical hyperparameter governing step magnitude along the negative gradient vector during parameter optimization.",
    },
    {
      term: "Loss Function",
      definition:
        "A scalar metric quantifying prediction error against ground truth targets (e.g., Cross-Entropy for classification, MSE for regression).",
    },
  ],
  flashcards: [
    {
      id: 1,
      front: "Why are non-linear activation functions essential in multi-layer neural networks?",
      back: "Without non-linearities, multiple stacked layers collapse mathematically into a single linear regression, incapable of learning non-linear relationships.",
      topic: "Neural Architecture",
    },
    {
      id: 2,
      front: "What mathematical principle enables the backpropagation algorithm?",
      back: "The differential Chain Rule from calculus, which propagates error derivatives backward layer by layer.",
      topic: "Optimization",
    },
    {
      id: 3,
      front: "What causes the Vanishing Gradient problem with Sigmoid activations?",
      back: "Sigmoid derivative has a maximum value of 0.25. Multiplying many values < 0.25 across deep layers causes gradients to approach zero rapidly.",
      topic: "Gradient Dynamics",
    },
    {
      id: 4,
      front: "How does a Residual Skip Connection resolve degradation in deep networks?",
      back: "It introduces identity mappings F(x) + x, allowing gradients to flow unimpeded directly through the identity shortcut during backpropagation.",
      topic: "Deep Architectures",
    },
  ],
  mcqs: [
    {
      id: 1,
      question:
        "Which activation function helps avoid the vanishing gradient problem in positive regimes?",
      options: [
        "A. Sigmoid",
        "B. Hyperbolic Tangent (Tanh)",
        "C. Rectified Linear Unit (ReLU)",
        "D. Linear Activation",
      ],
      answer: "C. Rectified Linear Unit (ReLU)",
      difficulty: "Easy",
      topic: "Activation Functions",
      explanation:
        "ReLU has a derivative of 1 for all positive inputs, ensuring gradients do not decay across deep layers in the active regime.",
    },
    {
      id: 2,
      question:
        "In gradient descent optimization, what occurs if the learning rate is chosen excessively large?",
      options: [
        "A. The model converges exponentially fast to the global minimum",
        "B. The loss oscillates uncontrollably and may diverge completely",
        "C. The weights vanish to absolute zero",
        "D. The training transitions automatically to L-BFGS",
      ],
      answer: "B. The loss oscillates uncontrollably and may diverge completely",
      difficulty: "Medium",
      topic: "Optimization",
      explanation:
        "An oversized learning rate causes parameter updates to overshoot optimal valleys, leading to numerical divergence.",
    },
    {
      id: 3,
      question:
        "Given a cross-entropy loss L and softmax probabilities p, why do residual connections preserve gradient magnitude in very deep networks?",
      options: [
        "A. The derivative includes an additive identity term ∂(x)/∂x = 1, ensuring gradients never vanish unconditionally",
        "B. They eliminate the need for matrix multiplications during forward pass",
        "C. They strictly normalize all weights to unit variance at each epoch",
        "D. They convert non-convex loss surfaces into convex quadratic paraboloids",
      ],
      answer:
        "A. The derivative includes an additive identity term ∂(x)/∂x = 1, ensuring gradients never vanish unconditionally",
      difficulty: "Hard",
      topic: "Deep Architectures",
      explanation:
        "Because of the skip connection x + F(x), the gradient of loss with respect to earlier activations always contains a constant +1 term.",
    },
  ],
  short_answers: [
    {
      id: 1,
      question:
        "Explain the tradeoff between Stochastic Gradient Descent (SGD) and Batch Gradient Descent.",
      sample_answer:
        "Batch Gradient Descent calculates exact gradients across the entire dataset, yielding smooth convergence but high computational expense per step. SGD evaluates single or mini-batch samples, introducing stochastic variance that allows escape from shallow saddle points with much faster wall-clock updates per epoch.",
      rubric: [
        "Mentions computational cost differences",
        "Explains gradient variance/noise in SGD",
        "Mentions saddle point escape and convergence properties",
      ],
    },
    {
      id: 2,
      question:
        "What is the mathematical definition and purpose of L2 weight regularization (Ridge/Weight Decay)?",
      sample_answer:
        "L2 regularization appends a penalty term (λ/2) Σ w² to the objective loss. In backpropagation, this effectively shrinks weights proportionally to their magnitude at each update step, preventing any single feature weight from growing disproportionately large and thereby mitigating overfitting.",
      rubric: [
        "Identifies penalty formulation proportional to squared weights",
        "Explains weight shrinkage effect during gradient update",
        "Relates directly to capacity reduction and overfit mitigation",
      ],
    },
  ],
};

export const useStudyStore = create<StudyState>((set, get) => ({
  studyPacks: [DEMO_PACK],
  activePack: DEMO_PACK,
  isLoading: false,
  error: null,
  quizSession: null,
  user: DEFAULT_USER,

  setActivePack: (pack) => set({ activePack: pack }),

  savePack: (pack) => {
    const existingPacks = get().studyPacks;
    const exists = existingPacks.some((p) => p.id === pack.id);
    let updatedPacks: StudyPackOutput[];

    if (exists) {
      updatedPacks = existingPacks.map((p) => (p.id === pack.id ? pack : p));
    } else {
      updatedPacks = [pack, ...existingPacks];
    }

    set({ studyPacks: updatedPacks, activePack: pack });

    if (typeof window !== "undefined") {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedPacks));
      } catch (err) {
        console.error("Failed to save to localStorage", err);
      }
    }
  },

  deletePack: (id) => {
    const updated = get().studyPacks.filter((p) => p.id !== id);
    set({
      studyPacks: updated,
      activePack: get().activePack?.id === id ? updated[0] || null : get().activePack,
    });
    if (typeof window !== "undefined") {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      } catch (err) {}
    }
  },

  loadPacksFromStorage: () => {
    if (typeof window === "undefined") return;
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed) && parsed.length > 0) {
          set({ studyPacks: parsed, activePack: parsed[0] });
          return;
        }
      }
    } catch (err) {
      console.error("Failed to load from localStorage", err);
    }
    set({ studyPacks: [DEMO_PACK], activePack: DEMO_PACK });
  },

  // Quiz Actions
  startQuiz: (mcqs, initialDifficulty = "Medium") => {
    set({
      quizSession: {
        questions: mcqs,
        currentDifficulty: initialDifficulty,
        currentIndex: 0,
        answers: {},
        isCompleted: false,
        result: null,
        timeSpentSeconds: 0,
      },
    });
  },

  selectQuizAnswer: (questionId, answer) => {
    const session = get().quizSession;
    if (!session) return;
    set({
      quizSession: {
        ...session,
        answers: {
          ...session.answers,
          [questionId]: answer,
        },
      },
    });
  },

  nextQuizQuestion: () => {
    const session = get().quizSession;
    if (!session) return;
    if (session.currentIndex < session.questions.length - 1) {
      set({
        quizSession: {
          ...session,
          currentIndex: session.currentIndex + 1,
        },
      });
    }
  },

  prevQuizQuestion: () => {
    const session = get().quizSession;
    if (!session) return;
    if (session.currentIndex > 0) {
      set({
        quizSession: {
          ...session,
          currentIndex: session.currentIndex - 1,
        },
      });
    }
  },

  jumpToQuizQuestion: (index) => {
    const session = get().quizSession;
    if (!session) return;
    if (index >= 0 && index < session.questions.length) {
      set({
        quizSession: {
          ...session,
          currentIndex: index,
        },
      });
    }
  },

  setQuizResult: (result) => {
    const session = get().quizSession;
    if (!session) return;
    set({
      quizSession: {
        ...session,
        isCompleted: true,
        result,
      },
    });
  },

  resetQuiz: () => {
    set({ quizSession: null });
  },

  setUser: (userUpdate) => {
    set({ user: { ...get().user, ...userUpdate } });
  },
}));
