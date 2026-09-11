"""Topic sequencing engine — orders subtopics by prerequisite logic."""

import logging
from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langsmith import traceable

from app.core.constants import SYSTEM_PROMPT
from app.core.exceptions import AIGenerationError

logger = logging.getLogger(__name__)

SEQUENCING_PROMPT = """Given the following list of subtopics extracted from study material,
reorder them into the optimal study sequence based on prerequisite dependencies.

Topics that introduce foundational concepts should come first,
and topics that build upon earlier concepts should come later.

**Input Topics:**
{topics}

**Rules:**
1. Return ALL topics — do not add or remove any.
2. Order from most foundational to most advanced.
3. If two topics are independent, keep their original relative order.

**Output Format:** Return a JSON array of strings in the recommended order.
Example: ["Topic A", "Topic B", "Topic C"]

Return ONLY the JSON array."""


@traceable(name="topic_sequencing")
def order_topics(topics: List[str], llm=None) -> List[str]:
    """
    Use AI to determine the optimal prerequisite-based study order.

    Args:
        topics: List of subtopic strings to order.
        llm: Optional LLM instance. If None, uses the secondary (Mistral) model
             for speed since this is a lightweight task.

    Returns:
        Reordered list of topic strings.
    """
    if not topics:
        return []

    if len(topics) == 1:
        return topics

    if llm is None:
        from app.services.ai_pipeline import get_secondary_model
        llm = get_secondary_model()

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", SEQUENCING_PROMPT),
    ])

    parser = JsonOutputParser()
    chain = prompt | llm | parser

    try:
        ordered = chain.invoke({"topics": "\n".join(f"- {t}" for t in topics)})

        # Validate: ensure all original topics are present
        original_set = set(topics)
        ordered_set = set(ordered)

        if original_set != ordered_set:
            logger.warning(
                "AI sequencing returned different topics than input. "
                "Falling back to original order."
            )
            return topics

        logger.info(f"Topics sequenced: {len(ordered)} items.")
        return ordered

    except Exception as e:
        logger.error(f"Topic sequencing failed: {e}. Falling back to alphabetical order.")
        return sorted(topics)
