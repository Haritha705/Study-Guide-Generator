"""CSV export service for MCQs."""

import csv
import io
import logging
from typing import List, Dict, Any

from app.core.exceptions import ExportError

logger = logging.getLogger(__name__)


def generate_csv(mcqs: List[Dict[str, Any]]) -> str:
    """
    Export MCQs to CSV format.

    Columns: ID, Question, Option_A, Option_B, Option_C, Option_D,
             Answer, Difficulty, Topic, Explanation

    Args:
        mcqs: List of MCQ dicts matching MCQItem schema.

    Returns:
        CSV content as a string.

    Raises:
        ExportError: If CSV generation fails.
    """
    if not mcqs:
        raise ExportError("No MCQs provided for CSV export.")

    try:
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow([
            "ID", "Question",
            "Option_A", "Option_B", "Option_C", "Option_D",
            "Answer", "Difficulty", "Topic", "Explanation",
        ])

        for mcq in mcqs:
            options = mcq.get("options", [])
            # Pad options to ensure exactly 4 columns
            while len(options) < 4:
                options.append("")

            writer.writerow([
                mcq.get("id", ""),
                mcq.get("question", ""),
                options[0] if len(options) > 0 else "",
                options[1] if len(options) > 1 else "",
                options[2] if len(options) > 2 else "",
                options[3] if len(options) > 3 else "",
                mcq.get("answer", ""),
                mcq.get("difficulty", ""),
                mcq.get("topic", ""),
                mcq.get("explanation", ""),
            ])

        csv_content = output.getvalue()
        output.close()

        logger.info(f"CSV generated: {len(mcqs)} MCQs exported.")
        return csv_content

    except ExportError:
        raise
    except Exception as e:
        logger.error(f"CSV generation failed: {e}")
        raise ExportError(f"CSV generation failed: {str(e)}")
