#!/usr/bin/env python3
# beat_spec.py

"""
Beat specification builder for the fiction toolkit.

This module is responsible for constructing a structured `beat_spec` dictionary
for a single beat, combining:

- Outline information (master + scene/beat level)
- Codex data (characters, locations, threads, style, voice)
- Time-aware overlays (character-over-time, thread state)
- Generator configuration for the beat generator

The resulting `beat_spec` is then consumed by:

- `build_blocks_from_beat_spec` in `blocks.py`
- Prompt rendering helpers in `prompts.py`
- The `WRITE_BEAT` job orchestration in `write_beat.py`

The goal of this module is to centralize *what the model should know* about a
beat, while keeping the exact parsing of outlines and codex cards delegated to
other modules (`outline.py`, `codex.py`).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from toolkit.scripts.core import outline as outline_mod
from toolkit.scripts.core import codex as codex_mod


# ------------------------------------------------------------------------------
# Configuration loading
# ------------------------------------------------------------------------------


def _load_beatgen_config(story_root: str) -> Dict[str, Any]:
    """
    Load beat generation configuration for the given story root.

    The configuration file is expected at:

        <story_root>/toolkit/config/beatgen.yaml

    The YAML should at minimum define:

    ```yaml
    context_rules:
      include_outline: true
      include_threads: true
      include_characters: true
      include_locations: true

    character_over_time:
      use_over_time: true

    threads:
      use_threads: true

    prompt_parameters:
      target_words: 400
      temperature: 0.85
    ```

    Args:
        story_root:
            Path to the story root directory.

    Returns:
        Dictionary with beat generation configuration options.

    Raises:
        FileNotFoundError:
            If the configuration file is missing.
        yaml.YAMLError:
            If the configuration file cannot be parsed.
    """
    config_path = Path(story_root) / "toolkit" / "config" / "beatgen.yaml"

    with config_path.open("r", encoding="utf-8") as handle:
        config: Dict[str, Any] = yaml.safe_load(handle)

    return config


# ------------------------------------------------------------------------------
# Time-aware merging helpers (MVP implementation)
# ------------------------------------------------------------------------------


def _filter_threads_by_chapter(
    threads: Dict[str, Any],
    chapter_num: int,
    thread_cfg: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Filter thread data to produce a time-aware view for the given chapter.

    MVP implementation:
    - Returns the threads unmodified, but preserves the shape and call-site
      semantics so that time filtering can be implemented later without
      changing callers.

    In the future, this function should:
    - Parse chapter-tagged sections like `## [ch3]` from thread cards.
    - Respect options like `forbid_future_truths` from `thread_cfg`.
    - Produce a per-thread `chapter_state` summary for the current chapter.

    Args:
        threads:
            Mapping of thread IDs to their parsed card structures.
        chapter_num:
            Numeric chapter index (1-based).
        thread_cfg:
            Configuration subsection from `beatgen.yaml` relevant to thread
            handling.

    Returns:
        A dictionary representing the time-filtered threads. For now, this is
        identical to `threads`.
    """
    # Placeholder implementation: pass-through.
    # This keeps the API stable while you define the exact structure of
    # thread cards and chapter-tagged sections.
    _ = chapter_num
    _ = thread_cfg
    return threads


def _merge_character_cards_with_over_time(
    characters: Dict[str, Any],
    characters_over_time: Dict[str, Any],
    chapter_num: int,
    over_time_cfg: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Merge base character cards with their chapter-specific over-time state.

    MVP implementation:
    - Wraps each character card together with its over-time card (if present).
    - Does not yet implement detailed field-level overrides, leaving that for
      later once over-time card structure is fully defined.

    The returned structure for each character ID is:

    ```python
    {
        "id": <CHAR_ID>,
        "name": <character name>,
        "base_card": {...},      # original character card
        "over_time": {...},      # raw over-time card (if any)
        "chapter_state": None,   # placeholder for future refinement
    }
    ```

    Args:
        characters:
            Mapping from character IDs to their base card data.
        characters_over_time:
            Mapping from character IDs to their over-time card data (if any).
        chapter_num:
            Numeric chapter index (1-based).
        over_time_cfg:
            Configuration subsection from `beatgen.yaml` for character
            over-time behavior.

    Returns:
        A dictionary keyed by character ID, where each value is a merged view
        including both base and over-time cards.
    """
    _ = chapter_num
    _ = over_time_cfg

    merged: Dict[str, Any] = {}

    for char_id, base_card in characters.items():
        ot_card = characters_over_time.get(char_id, {})

        name = base_card.get("name", char_id)

        merged[char_id] = {
            "id": char_id,
            "name": name,
            "base_card": base_card,
            "over_time": ot_card,
            # Placeholder: this will later become a chapter-specific summary
            # derived from the over-time card.
            "chapter_state": ot_card.get("chapter_state"),
        }

    return merged


# ------------------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------------------


def build_beat_spec(
    story_root: str,
    chapter_num: int,
    scene_num: int,
    beat_num: int,
) -> Dict[str, Any]:
    """
    Build a structured beat specification for a single beat.

    This function orchestrates the collection of all relevant data for the
    specified beat:

    1. Loads beat generation configuration.
    2. Loads master and scene outlines, and builds an outline context view.
    3. Loads codex entries relevant to this scene (characters, locations).
    4. Loads threads, style guide, and POV voice card.
    5. Applies time-aware merging for character and thread data.
    6. Produces a `beat_spec` dictionary consumed by the rest of the pipeline.

    Args:
        story_root:
            Path to the story root directory.
        chapter_num:
            Numeric chapter index (1-based).
        scene_num:
            Numeric scene index within the chapter (1-based).
        beat_num:
            Numeric beat index within the scene (1-based).

    Returns:
        A dictionary describing the beat in a structured form. The expected
        top-level keys include:

        - "ids"
        - "pov"
        - "outline"
        - "characters"
        - "locations"
        - "threads"
        - "style"
        - "voice"
        - "generator_config"
    """
    cfg = _load_beatgen_config(story_root=story_root)

    # 1. Outline context
    master_outline = outline_mod.load_master_outline(story_root=story_root)
    scene_outline = outline_mod.load_scene_outline(
        story_root=story_root,
        chapter_num=chapter_num,
        scene_num=scene_num,
    )

    outline_context = outline_mod.build_outline_context(
        master_outline=master_outline,
        scene_outline=scene_outline,
        chapter_num=chapter_num,
        context_rules=cfg.get("context_rules", {}),
    )

    # 2. Codex: characters, over-time, locations, threads, style, voice
    characters = codex_mod.get_characters_for_scene(
        story_root=story_root,
        scene_outline=scene_outline,
    )

    characters_over_time = codex_mod.get_characters_over_time(
        story_root=story_root,
        character_ids=list(characters.keys()),
    )

    locations = codex_mod.get_locations_for_scene(
        story_root=story_root,
        scene_outline=scene_outline,
    )

    threads = codex_mod.get_threads(story_root=story_root)
    style_guide = codex_mod.get_style_guide(story_root=story_root)

    pov_info = outline_mod.determine_pov_character(
        scene_outline=scene_outline,
        characters=characters,
    )

    pov_voice = None
    if pov_info is not None:
        pov_id = pov_info.get("id")
        if pov_id is not None:
            pov_voice = codex_mod.get_pov_voice(
                story_root=story_root,
                pov_char_id=pov_id,
            )

    # 3. Time-aware views
    time_filtered_threads = _filter_threads_by_chapter(
        threads=threads,
        chapter_num=chapter_num,
        thread_cfg=cfg.get("threads", {}),
    )

    merged_characters = _merge_character_cards_with_over_time(
        characters=characters,
        characters_over_time=characters_over_time,
        chapter_num=chapter_num,
        over_time_cfg=cfg.get("character_over_time", {}),
    )

    # 4. Assemble beat_spec
    beat_spec: Dict[str, Any] = {
        "ids": {
            "chapter_num": chapter_num,
            "scene_num": scene_num,
            "beat_num": beat_num,
            "chapter_id": f"ch{chapter_num:02d}",
            "scene_id": f"sc{scene_num:02d}",
            "beat_id": f"b{beat_num:02d}",
        },
        "pov": pov_info,
        "outline": outline_context,
        "characters": merged_characters,
        "locations": locations,
        "threads": time_filtered_threads,
        "style": style_guide,
        "voice": pov_voice,
        "generator_config": cfg,
    }

    return beat_spec
