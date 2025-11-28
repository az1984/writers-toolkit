#!/usr/bin/env python3
# blocks.py

"""
Beat-spec to prompt-block converters for the fiction toolkit.

This module transforms a structured `beat_spec` dictionary (constructed by
`beat_spec.build_beat_spec`) into a set of text blocks suitable for prompt
templates:

- CODEX_BLOCK        -> `<codex>` contents: character/location/thread lore
- STORY_SO_FAR_BLOCK -> `<storySoFar>` contents: chapter/scene summaries
- INSTRUCTIONS_BLOCK -> `<instructions>` contents: POV, beat goal, tone, etc.
- TARGET_WORDS       -> numeric word target as a string

These blocks are then consumed by the prompt rendering layer in `prompts.py`,
which substitutes them into NovelCrafter-style templates.
"""

from __future__ import annotations

from typing import Any, Dict, List


# ------------------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------------------


def build_blocks_from_beat_spec(beat_spec: Dict[str, Any]) -> Dict[str, str]:
    """
    Build prompt blocks (CODEX_BLOCK, STORY_SO_FAR_BLOCK, etc.) from a beat_spec.

    Args:
        beat_spec:
            Structured description of a beat, as returned by
            `build_beat_spec` in `beat_spec.py`.

    Returns:
        A dictionary mapping block names (e.g. "CODEX_BLOCK") to rendered
        string content ready for substitution into prompt templates.
    """
    codex_block = _build_codex_block(beat_spec=beat_spec)
    story_so_far_block = _build_story_so_far_block(beat_spec=beat_spec)
    instructions_block = _build_instructions_block(beat_spec=beat_spec)

    generator_cfg = beat_spec.get("generator_config", {})
    prompt_params = generator_cfg.get("prompt_parameters", {})
    target_words = str(prompt_params.get("target_words", 400))

    return {
        "CODEX_BLOCK": codex_block,
        "STORY_SO_FAR_BLOCK": story_so_far_block,
        "INSTRUCTIONS_BLOCK": instructions_block,
        "TARGET_WORDS": target_words,
    }


# ------------------------------------------------------------------------------
# CODEX_BLOCK helpers
# ------------------------------------------------------------------------------


def _build_codex_block(beat_spec: Dict[str, Any]) -> str:
    """
    Build the CODEX_BLOCK string from characters, locations, and threads.

    The structure is a simple sequence of `<lore name=\"...\">...</lore>`
    entries. This keeps the format close to what NovelCrafter expects, while
    allowing the codex parsing logic to evolve independently.

    Expected minimal fields (if available):

    - characters:
        - name
        - base_card.summary or base_card.description
        - chapter_state
    - locations:
        - name
        - summary or description
    - threads:
        - name
        - chapter_state or summary

    Missing fields are simply omitted from the output.
    """
    lines: List[str] = []

    # Characters
    for char_id, merged in beat_spec.get("characters", {}).items():
        name = merged.get("name", char_id)
        base = merged.get("base_card", {}) or {}
        chapter_state = merged.get("chapter_state")

        # Prefer an explicit summary / description if available.
        summary = (
            base.get("summary")
            or base.get("description")
            or base.get("raw_text")
        )

        desc_parts: List[str] = []
        if summary:
            desc_parts.append(str(summary).strip())
        if chapter_state:
            desc_parts.append(f"In this chapter: {str(chapter_state).strip()}")

        if not desc_parts:
            # Nothing to say about this character yet.
            continue

        desc_text = "\n".join(desc_parts)
        lines.append(f'<lore name="CHAR: {name}">\n{desc_text}\n</lore>')

    # Locations
    for loc_id, loc in beat_spec.get("locations", {}).items():
        name = loc.get("name", loc_id)
        summary = (
            loc.get("summary")
            or loc.get("description")
            or loc.get("raw_text")
        )

        if not summary:
            continue

        desc_text = str(summary).strip()
        lines.append(f'<lore name="LOC: {name}">\n{desc_text}\n</lore>')

    # Threads (story logic)
    for thread_id, thread in beat_spec.get("threads", {}).items():
        name = thread.get("name", thread_id)
        chapter_state = thread.get("chapter_state")
        summary = thread.get("summary")

        # Use the most specific information available.
        text = chapter_state or summary
        if not text:
            continue

        desc_text = str(text).strip()
        lines.append(f'<lore name="THREAD: {name}">\n{desc_text}\n</lore>')

    return "\n\n".join(lines).strip()


# ------------------------------------------------------------------------------
# STORY_SO_FAR_BLOCK helpers
# ------------------------------------------------------------------------------


def _build_story_so_far_block(beat_spec: Dict[str, Any]) -> str:
    """
    Build the STORY_SO_FAR_BLOCK string from outline context.

    The format is a small XML-ish snippet that mirrors NovelCrafter's
    `<storySoFar>` structure:

    ```xml
    <act number="1" title="Novel">
      <chapter title="Chapter 3" number="3">
        <scene title="Previous Scene" number="2">
          ...
        </scene>
        <scene title="Current Scene" number="3">
          ...
        </scene>
      </chapter>
    </act>
    ```

    MVP implementation:
    - Always uses a single act (number=1, title="Novel").
    - Uses current chapter number and an optional chapter title.
    - Optionally includes a "previous scene" summary if provided.
    - Includes the current scene summary.
    """
    ids = beat_spec.get("ids", {})
    outline = beat_spec.get("outline", {})

    chapter_num = ids.get("chapter_num", 1)
    scene_num = ids.get("scene_num", 1)

    chapter_title = outline.get("chapter_title") or f"Chapter {chapter_num}"
    scene_title = outline.get("scene_title") or f"Scene {scene_num}"
    scene_summary = outline.get("scene_summary", "").strip()

    prev_scene_title = outline.get("previous_scene_title") or "Previous Scene"
    prev_scene_summary = (outline.get("previous_scene_summary") or "").strip()
    prev_scene_num = scene_num - 1 if scene_num > 1 else max(scene_num - 1, 0)

    # Build XML-ish structure.
    lines: List[str] = []
    lines.append('<act number="1" title="Novel">')
    lines.append(f'  <chapter title="{chapter_title}" number="{chapter_num}">')

    if prev_scene_summary:
        lines.append(
            f'    <scene title="{prev_scene_title}" number="{prev_scene_num}">'
        )
        lines.append(f"      {prev_scene_summary}")
        lines.append("    </scene>")

    lines.append(f'    <scene title="{scene_title}" number="{scene_num}">')
    if scene_summary:
        lines.append(f"      {scene_summary}")
    lines.append("    </scene>")

    lines.append("  </chapter>")
    lines.append("</act>")

    return "\n".join(lines)


# ------------------------------------------------------------------------------
# INSTRUCTIONS_BLOCK helpers
# ------------------------------------------------------------------------------


def _build_instructions_block(beat_spec: Dict[str, Any]) -> str:
    """
    Build the INSTRUCTIONS_BLOCK string from POV and outline information.

    The format is a small XML-ish structure intended to live inside an
    `<instructions>` element in the prompt:

    ```xml
    <pointOfView type="third person limited" focus="Maya Santos"/>

    <beatGoal>
      Continue the scene where Maya and Jess walk home, deepening their
      chemistry while hinting at Jess's secrets.
    </beatGoal>

    <tone>
      Sensual tension with undercurrents of humor and unease.
    </tone>
    ```

    MVP implementation:
    - Uses `pov.mode` and `pov.name` if available.
    - Uses `outline.beat_goal` as the core beat objective.
    - Optionally includes a simple `<tone>` element if present in outline.
    """
    pov = beat_spec.get("pov") or {}
    outline = beat_spec.get("outline") or {}
    style = beat_spec.get("style") or {}

    pov_mode = pov.get("mode", "third person limited")
    pov_name = pov.get("name")

    beat_goal = outline.get("beat_goal") or "Continue the story from the current point."
    beat_goal = str(beat_goal).strip()

    tone = outline.get("tone") or style.get("default_tone")
    tone_text = str(tone).strip() if tone else ""

    lines: List[str] = []

    # <pointOfView .../>
    if pov_name:
        lines.append(
            f'<pointOfView type="{pov_mode}" focus="{pov_name}"/>'
        )
    else:
        lines.append(f'<pointOfView type="{pov_mode}"/>')

    # <beatGoal>...</beatGoal>
    lines.append("")
    lines.append("<beatGoal>")
    lines.append(f"  {beat_goal}")
    lines.append("</beatGoal>")

    # Optional <tone>...</tone>
    if tone_text:
        lines.append("")
        lines.append("<tone>")
        lines.append(f"  {tone_text}")
        lines.append("</tone>")

    return "\n".join(lines)
