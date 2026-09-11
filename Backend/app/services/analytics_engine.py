# app/services/analytics_engine.py

"""Quiz analytics, grading, topic performance, and adaptive difficulty."""

from typing import Dict, List

from app.schemas.quiz import (
    QuizSubmission,
    QuizResult,
    TopicPerformance,
    DifficultyBreakdown,
)
from app.schemas.studypack import MCQItem
from app.core.constants import DIFFICULTY_LEVELS


# ============================================================
# MAIN QUIZ EVALUATION
# ============================================================

def evaluate_quiz(
    submission: QuizSubmission,
    mcqs: List[MCQItem],
) -> QuizResult:
    """
    Evaluate the student's quiz attempt.

    Responsibilities:
    - Calculate score
    - Track correct/incorrect answers
    - Track topic performance
    - Track difficulty performance
    - Identify weak topics
    - Decide next quiz difficulty

    Quiz size is NOT changed here.
    The next quiz keeps the user's selected quiz size.
    """

    if not mcqs:
        raise ValueError("No MCQs provided for evaluation.")

    # --------------------------------------------------------
    # Overall counters
    # --------------------------------------------------------

    total_questions = len(mcqs)
    correct_answers = 0
    missed_question_ids: List[int] = []

    # --------------------------------------------------------
    # Topic analytics
    # --------------------------------------------------------

    topic_stats: Dict[str, Dict[str, int]] = {}

    # --------------------------------------------------------
    # Difficulty analytics
    # --------------------------------------------------------

    difficulty_stats: Dict[str, Dict[str, int]] = {
        difficulty: {
            "total": 0,
            "correct": 0,
        }
        for difficulty in DIFFICULTY_LEVELS
    }

    # --------------------------------------------------------
    # Evaluate every question
    # --------------------------------------------------------

    for mcq in mcqs:

        student_answer = submission.answers.get(mcq.id)

        # Initialize topic
        if mcq.topic not in topic_stats:
            topic_stats[mcq.topic] = {
                "total": 0,
                "correct": 0,
            }

        topic_stats[mcq.topic]["total"] += 1

        # Initialize difficulty if necessary
        if mcq.difficulty not in difficulty_stats:
            difficulty_stats[mcq.difficulty] = {
                "total": 0,
                "correct": 0,
            }

        difficulty_stats[mcq.difficulty]["total"] += 1

        # ----------------------------------------------------
        # Check answer
        # ----------------------------------------------------

        if student_answer is not None:

            is_correct = (
                student_answer.strip().lower()
                == mcq.answer.strip().lower()
            )

            if is_correct:

                correct_answers += 1

                topic_stats[mcq.topic]["correct"] += 1

                difficulty_stats[mcq.difficulty]["correct"] += 1

            else:

                missed_question_ids.append(mcq.id)

        else:

            # Unanswered questions are considered incorrect
            missed_question_ids.append(mcq.id)

    # --------------------------------------------------------
    # Calculate score
    # --------------------------------------------------------

    score = round(
        (correct_answers / total_questions) * 100,
        2,
    )

    # --------------------------------------------------------
    # Topic performance
    # --------------------------------------------------------

    topic_performance: Dict[str, TopicPerformance] = {}

    for topic, stats in topic_stats.items():

        topic_score = round(
            (stats["correct"] / stats["total"]) * 100,
            2,
        )

        topic_performance[topic] = TopicPerformance(
            topic=topic,
            score=topic_score,
            total_questions=stats["total"],
            correct_answers=stats["correct"],
        )

    # --------------------------------------------------------
    # Identify weak topics
    # --------------------------------------------------------

    weak_topics = [
        topic
        for topic, performance in topic_performance.items()
        if performance.score < 60
    ]

    # --------------------------------------------------------
    # Difficulty breakdown
    # --------------------------------------------------------

    difficulty_breakdown: Dict[str, float] = {}

    for difficulty, stats in difficulty_stats.items():

        if stats["total"] == 0:
            difficulty_breakdown[difficulty] = 0.0
        else:
            difficulty_breakdown[difficulty] = round(
                (stats["correct"] / stats["total"]) * 100,
                2,
            )

    # --------------------------------------------------------
    # Decide next difficulty
    # --------------------------------------------------------

    current_difficulty = submission.current_difficulty

    next_difficulty = _next_difficulty(
        current=current_difficulty,
        score=score,
    )

    # --------------------------------------------------------
    # Return final analytics result
    # --------------------------------------------------------

    return QuizResult(
        score=score,
        weak_topics=weak_topics,
        topic_performance=topic_performance,
        difficulty_breakdown=difficulty_breakdown,
        missed_question_ids=missed_question_ids,
        next_difficulty=next_difficulty,
    )


# ============================================================
# ADAPTIVE DIFFICULTY ENGINE
# ============================================================

def _next_difficulty(
    current: str,
    score: float,
) -> str:
    """
    Determine the difficulty of the next quiz.

    Rules:

        Score < 40%
            ↓
        Decrease difficulty

        40% - 69%
            ↓
        Keep same difficulty

        70%+
            ↓
        Increase difficulty

    Difficulty is always clamped between Easy and Hard.
    """

    # Safety fallback
    if current not in DIFFICULTY_LEVELS:
        current = "Medium"

    current_index = DIFFICULTY_LEVELS.index(current)

    # --------------------------------------------------------
    # Very poor performance
    # --------------------------------------------------------

    if score < 40:

        next_index = max(
            current_index - 1,
            0,
        )

    # --------------------------------------------------------
    # Average performance
    # --------------------------------------------------------

    elif score < 70:

        next_index = current_index

    # --------------------------------------------------------
    # Strong performance
    # --------------------------------------------------------

    else:

        next_index = min(
            current_index + 1,
            len(DIFFICULTY_LEVELS) - 1,
        )

    return DIFFICULTY_LEVELS[next_index]