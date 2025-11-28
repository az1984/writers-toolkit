#!/usr/bin/env python3
# outline.py

"""
Outline and scene parsing utilities for the fiction toolkit.

This module is responsible for loading and lightly parsing:

- The master outline file (overall story structure)
- Per-scene outline files under the manuscript tree

It then provides:

- `load_master_outline`:
    Returns a simple structure containing the raw master outline text.
- `load_scene_outline`:
    Returns a structure containing the raw scene outline text.
- `build_outline_context`:
    Produces a compact summary for use in beat generation:
      - chapter_title
      - scene_title
      - scene_summary
      - previous_scene_title / summary (if known)
      - beat_goal
      - tone
- `determine_pov_character`:
    Selects a POV character for the scene, currently using simple heuristics.

MVP implementation:
- Keeps parsing heuristics intentionally simple (first heading, first paragraph).
- Does not depend on a specific markdown structure beyond basic headings.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional


# ------------------------------------------------------------------------------
# Basic file loading
# ------------------------------------------------------------------------------


def load_master_outline(story_root: str) -> Dict[str, Any]:
    """
    Load the master outline for the story.

    Expected location:

        <story_root>/outlines/master_outline.md

    MVP implementation:
    - Reads the file if it exists.
    - Returns a dictionary with a single key "raw_text".

    Args:
        story_root:
            Path to the story root directory.

    Returns:
        A dictionary with:
            - "raw_text": full contents of the master outline, or an empty
              string if not present.
    """
    path = Path(story_root) / "outlines" / "master_outline.md"

    if not path.exists():
        return {"raw_text": ""}

    raw_text = path.read_text(encoding="utf-8")
    return {"raw_text": raw_text}


def load_scene_outline(
    story_root: str,
    chapter_num: int,
    scene_num: int,
) -> Dict[str, Any]:
    """
    Load the outline for a specific scene.

    MVP implementation assumes the following layout:

        <story_root>/manuscript/chapters/chXX/scenes/scYY.md

    where:
        chXX = formatted chapter_num (e.g. 1 -> "ch01")
        scYY = formatted scene_num   (e.g. 1 -> "sc01")

    Args:
        story_root:
            Path to the story root directory.
        chapter_num:
            Numeric chapter index (1-based).
        scene_num:
            Numeric scene index within the chapter (1-based).

    Returns:
        A dictionary with:
            - "raw_text": full contents of the scene file, or an empty string.
            - "path": Path object for the scene file.
    """
    chapter_id = f"ch{chapter_num:02d}"
    scene_id = f"sc{scene_num:02d}"

    path = (
        Path(story_root)
        / "manuscript"
        / "chapters"
        / chapter_id
        / "scenes"
        / f"{scene_id}.md"
    )

    if not path.exists():
        return {"raw_text": "", "path": path}

    raw_text = path.read_text(encoding="utf-8")
    return {"raw_text": raw_text, "path": path}


# ------------------------------------------------------------------------------
# Simple markdown heuristics
# ------------------------------------------------------------------------------


def _extract_first_heading(lines: List[str], level: int) -> Optional[str]:
    """
    Extract the first heading of a given markdown level.

    Args:
        lines:
            List of lines (strings) from a markdown file.
        level:
            Heading level, e.g. 1 for "#", 2 for "##".

    Returns:
        The heading text without the leading "#" symbols, or None if not found.
    """
    prefix = "#" * level + " "
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


def _extract_first_nonempty_line(lines: List[str]) -> Optional[str]:
    """
    Extract the first non-empty line from a list of lines.

    Args:
        lines:
            List of lines (strings).

    Returns:
        The first non-empty line, stripped, or None if all lines are empty.
    """
    for line in lines:
        stripped = line.strip()
        if stripped:
            return stripped
    return None


def _extract_scene_summary_from_text(text: str) -> str:
    """
    Extract a simple scene summary from raw markdown text.

    MVP heuristic:
    - Skip initial heading lines.
    - Return the first non-empty line after headings as the summary.

    Args:
        text:
            Raw markdown content.

    Returns:
        A one-line summary string (possibly the first meaningful line), or
        an empty string if nothing suitable is found.
    """
    lines = text.splitlines()
    # Skip leading headings
    i = 0
    while i < len(lines) and lines[i].lstrip().startswith("#"):
        i += 1

    summary = _extract_first_nonempty_line(lines[i:])
    return summary or ""


# ------------------------------------------------------------------------------
# Outline context assembly
# ------------------------------------------------------------------------------


def build_outline_context(
    master_outline: Dict[str, Any],
    scene_outline: Dict[str, Any],
    chapter_num: int,
    context_rules: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a compact outline context dictionary for a given scene.

    The context is intended to be passed into the beat generator and prompt
    builders. It captures chapter/scene titles and basic summaries.

    MVP implementation:
    - Uses the scene file's first-level and second-level headings as
      `chapter_title` and `scene_title` if present.
    - Derives a `scene_summary` from the first non-heading line.
    - Uses `scene_summary` as a fallback `beat_goal` if none is present.
    - Leaves `previous_scene_title` and `previous_scene_summary` empty.

    Args:
        master_outline:
            Dictionary returned by `load_master_outline`. Currently used only
            for future expansion.
        scene_outline:
            Dictionary returned by `load_scene_outline`, with at least a
            "raw_text" field.
        chapter_num:
            Numeric chapter index (1-based).
        context_rules:
            Context-related configuration from `beatgen.yaml`. Currently
            unused by this MVP implementation, but included for forward
            compatibility.

    Returns:
        A dictionary with keys:

        - "chapter_title"
        - "scene_title"
        - "scene_summary"
        - "previous_scene_title"
        - "previous_scene_summary"
        - "beat_goal"
        - "tone"
    """
    _ = master_outline
    _ = context_rules

    raw_text = scene_outline.get("raw_text", "")
    lines = raw_text.splitlines()

    # Try to infer titles from headings.
    chapter_title = _extract_first_heading(lines, level=1)
    if not chapter_title:
        chapter_title = f"Chapter {chapter_num}"

    scene_title = _extract_first_heading(lines, level=2)
    if not scene_title:
        scene_title = "Scene"

    scene_summary = _extract_scene_summary_from_text(raw_text)

    # MVP: previous scene context is not yet derived.
    previous_scene_title = ""
    previous_scene_summary = ""

    # MVP: beat_goal is the same as scene_summary unless later overridden.
    beat_goal = scene_summary or "Continue the story from the current point."

    tone = ""

    return {
        "chapter_title": chapter_title,
        "scene_title": scene_title,
        "scene_summary": scene_summary,
        "previous_scene_title": previous_scene_title,
        "previous_scene_summary": previous_scene_summary,
        "beat_goal": beat_goal,
        "tone": tone,
    }


# ------------------------------------------------------------------------------
# POV selection
# ------------------------------------------------------------------------------


def determine_pov_character(
    scene_outline: Dict[str, Any],
    characters: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Determine the POV character for a scene.

    MVP implementation:
    - If no characters are provided, returns None.
    - Otherwise, selects the first character in the dictionary.
    - Assumes a default narrative mode of "third person limited".

    In the future, this function can be extended to:
    - Parse explicit POV hints from the scene outline (e.g. metadata or tags).
    - Use chapter/scene metadata to pick POV based on author preferences.

    Args:
        scene_outline:
            Dictionary returned by `load_scene_outline`. Currently unused by
            this implementation but accepted for future expansion.
        characters:
            Mapping of character IDs to character card dictionaries.

    Returns:
        A dictionary with keys:
            - "id"
            - "name"
            - "mode"
        or None if no POV can be determined.
    """
    _ = scene_outline

    if not characters:
        return None

    char_id, card = next(iter(characters.items()))
    name = card.get("name", char_id)

    return {
        "id": char_id,
        "name": name,
        "mode": "third person limited",
    }
