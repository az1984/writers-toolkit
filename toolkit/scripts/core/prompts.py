#!/usr/bin/env python3
# prompts.py

"""
Prompt utilities for the fiction toolkit.

This module provides helpers to:
- Turn rendered prompt strings (system/user/user2) into OpenAI-style
  `messages` lists for model calls.
- In the future, respect `toolkit/config/prompting.yaml` to determine which
  slots are used for each high-level action.
"""

from __future__ import annotations

from typing import Dict, List, Optional


def build_messages_from_prompts(
    system: str,
    user: str,
    user2: Optional[str] = None,
) -> List[Dict[str, str]]:
    """
    Build an OpenAI-style `messages` list from rendered prompt strings.

    This helper is intentionally minimal: it assumes that the caller has
    already:
      - chosen the correct templates for the action
      - rendered all placeholders (e.g. {{CODEX_BLOCK}})
      - decided whether a third "user2" message is needed

    Args:
        system:
            The full system prompt text. This becomes the single `system`
            message in the conversation.
        user:
            The primary user/context message. This typically contains codex
            information, story-so-far summaries, etc.
        user2:
            Optional secondary user message. For NovelCrafter-style beat
            generation, this is often a "visible task" instruction like
            "Write 400 words that continue the story...". For simpler
            transformations (e.g. tense conversion), this can be omitted.

    Returns:
        A list of messages of the form:

        ```python
        [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
            # optionally:
            {"role": "user",   "content": user2},
        ]
        ```
    """
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    if user2 is not None and user2.strip():
        messages.append({"role": "user", "content": user2})

    return messages
