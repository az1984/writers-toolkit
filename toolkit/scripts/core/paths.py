#!/usr/bin/env python3
# paths.py

"""
Path helpers for the fiction toolkit.

This module provides small, centralized helpers for resolving common
filesystem locations inside a story project, such as:

- manuscript root
- codex root
- outlines root
- config root
- specific scene and beat files

MVP implementation:

- Uses a simple, hardcoded layout that matches the current test story:

    manuscript/chapters/chXX/scenes/scYY.md
    manuscript/chapters/chXX/beats/scYY_bZZ.md

  where XX, YY, ZZ are zero-padded numeric identifiers.

In the future, this module can be extended to read index files
(e.g. manuscript/index.yaml) instead of hardcoding the patterns.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


# ------------------------------------------------------------------------------
# Root helpers
# ------------------------------------------------------------------------------


def manuscript_root(story_root: str) -> Path:
    """
    Return the root path for the manuscript domain.

    Args:
        story_root:
            Path to the story root directory.

    Returns:
        Path to `<story_root>/manuscript`.
    """
    return Path(story_root) / "manuscript"


def codex_root(story_root: str) -> Path:
    """
    Return the root path for the codex domain.

    Args:
        story_root:
            Path to the story root directory.

    Returns:
        Path to `<story_root>/codex`.
    """
    return Path(story_root) / "codex"


def outlines_root(story_root: str) -> Path:
    """
    Return the root path for the outlines domain.

    Args:
        story_root:
            Path to the story root directory.

    Returns:
        Path to `<story_root>/outlines`.
    """
    return Path(story_root) / "outlines"


def config_root(story_root: str) -> Path:
    """
    Return the root path for toolkit configuration files.

    Args:
        story_root:
            Path to the story root directory.

    Returns:
        Path to `<story_root>/toolkit/config`.
    """
    return Path(story_root) / "toolkit" / "config"


# ------------------------------------------------------------------------------
# Manuscript: scene and beat paths (MVP)
# ------------------------------------------------------------------------------


def scene_file(
    story_root: str,
    chapter_num: int,
    scene_num: int,
) -> Path:
    """
    Resolve the path for a scene outline file under the manuscript tree.

    MVP implementation assumes:

        manuscript/chapters/chXX/scenes/scYY.md

    where:
        chXX = chapter_num as 2 digits (e.g. 1 -> "ch01")
        scYY = scene_num   as 2 digits (e.g. 1 -> "sc01")

    Args:
        story_root:
            Path to the story root directory.
        chapter_num:
            Numeric chapter index (1-based).
        scene_num:
            Numeric scene index within the chapter (1-based).

    Returns:
        Path to the scene markdown file.
    """
    chapter_id = f"ch{chapter_num:02d}"
    scene_id = f"sc{scene_num:02d}"

    return (
        manuscript_root(story_root)
        / "chapters"
        / chapter_id
        / "scenes"
        / f"{scene_id}.md"
    )


def beat_file(
    story_root: str,
    chapter_num: int,
    scene_num: int,
    beat_num: int,
) -> Path:
    """
    Resolve the path for a beat file under the manuscript tree.

    MVP implementation assumes:

        manuscript/chapters/chXX/beats/scYY_bZZ.md

    where:
        chXX = chapter_num as 2 digits (e.g. 1 -> "ch01")
        scYY = scene_num   as 2 digits (e.g. 1 -> "sc01")
        bZZ  = beat_num    as 2 digits (e.g. 1 -> "b01")

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
        Path to the beat markdown file.
    """
    chapter_id = f"ch{chapter_num:02d}"
    scene_id = f"sc{scene_num:02d}"
    beat_id = f"b{beat_num:02d}"

    return (
        manuscript_root(story_root)
        / "chapters"
        / chapter_id
        / "beats"
        / f"{scene_id}_{beat_id}.md"
    )
