#!/usr/bin/env python3
# write_beat.py

"""
End-to-end orchestration for the WRITE_BEAT action.

This module demonstrates the full flow for generating a single beat:

    beat_spec
      -> blocks
      -> render_prompts_for_action (using prompting.yaml)
      -> build_messages_from_prompts
      -> call_model
      -> write beat file to manuscript

The actual sub-functions (`build_beat_spec`, `build_blocks_from_beat_spec`,
`render_prompts_for_action`, `build_messages_from_prompts`, `call_model`)
are defined in their respective core modules.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict

from toolkit.scripts.core.beat_spec import build_beat_spec
from toolkit.scripts.core.blocks import build_blocks_from_beat_spec
from toolkit.scripts.core.prompts import (
    render_prompts_for_action,
    build_messages_from_prompts,
)
from toolkit.scripts.core.model_client import call_model
from toolkit.scripts.core.paths import beat_file


# ------------------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------------------


def run_write_beat_job(
    story_root: str,
    chapter_num: int,
    scene_num: int,
    beat_num: int,
) -> Dict[str, Any]:
    """
    Run the WRITE_BEAT action for a single beat.

    This function ties together all the separate pieces of the pipeline:

    1. Build a `beat_spec` (structured description of what this beat should do)
    2. Derive prompt `blocks` from the beat_spec
    3. Render the appropriate prompt templates for ACTIONS_WRITE_BEAT
    4. Convert the rendered prompts into an OpenAI-style `messages` list
    5. Call the model and obtain generated prose
    6. Write the generated text into the correct beat file under `manuscript/`

    Args:
        story_root:
            Path to the story root directory.
        chapter_num:
            Numeric chapter index (e.g. 1 for chapter 1).
        scene_num:
            Numeric scene index within the chapter.
        beat_num:
            Numeric beat index within the scene.

    Returns:
        A dictionary containing:
        - "beat_path": Path to the written beat file
        - "tokens_used": Token usage summary (if available)
        - "status": "ok" on success
        - "raw": The raw model response (for debugging / logging)
    """
    # 1. Build the beat specification (outline + codex + time-aware state)
    beat_spec: Dict[str, Any] = build_beat_spec(
        story_root=story_root,
        chapter_num=chapter_num,
        scene_num=scene_num,
        beat_num=beat_num,
    )

    # 2. Convert the beat spec into prompt blocks
    #    E.g. CODEX_BLOCK, STORY_SO_FAR_BLOCK, INSTRUCTIONS_BLOCK, TARGET_WORDS
    blocks: Dict[str, str] = build_blocks_from_beat_spec(beat_spec=beat_spec)

    # 3. Render the prompts for our action key using prompting.yaml
    #    This will:
    #      - Find `template_set` for ACTIONS_WRITE_BEAT (e.g. "nc/beat")
    #      - Render system/user/user2 templates using the blocks
    rendered_prompts: Dict[str, str] = render_prompts_for_action(
        story_root=story_root,
        action_key="ACTIONS_WRITE_BEAT",
        blocks=blocks,
    )

    system_text: str = rendered_prompts["system"]
    user_text: str = rendered_prompts["user"]
    user2_text: str = rendered_prompts.get("user2", "")

    # 4. Build the OpenAI-style messages list
    messages = build_messages_from_prompts(
        system=system_text,
        user=user_text,
        user2=user2_text or None,
    )

    # 5. Call the model
    model_result: Dict[str, Any] = call_model(
        story_root=story_root,
        messages=messages,
        params=None,  # Optional per-call overrides; can merge in from beat_spec if needed
    )

    generated_text: str = model_result["text"]

    # 6. Write the beat file into the manuscript tree
    beat_path: Path = beat_file(
        story_root=story_root,
        chapter_num=chapter_num,
        scene_num=scene_num,
        beat_num=beat_num,
    )
    beat_path.parent.mkdir(parents=True, exist_ok=True)
    beat_path.write_text(generated_text, encoding="utf-8")

    return {
        "beat_path": str(beat_path),
        "tokens_used": model_result.get("tokens_used", {}),
        "status": "ok",
        "raw": model_result.get("raw"),
    }


# ------------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
    """Build an argument parser for the WRITE_BEAT CLI."""
    parser = argparse.ArgumentParser(
        description="Generate a single beat using ACTIONS_WRITE_BEAT.",
    )
    parser.add_argument(
        "--story-root",
        type=str,
        default=".",
        help="Path to the story root directory (default: current directory).",
    )
    parser.add_argument(
        "--chapter",
        type=int,
        required=True,
        help="Chapter number (1-based).",
    )
    parser.add_argument(
        "--scene",
        type=int,
        required=True,
        help="Scene number within the chapter (1-based).",
    )
    parser.add_argument(
        "--beat",
        type=int,
        required=True,
        help="Beat number within the scene (1-based).",
    )
    return parser


def main() -> None:
    """CLI entrypoint for generating a single beat."""
    parser = _build_arg_parser()
    args = parser.parse_args()

    result = run_write_beat_job(
        story_root=args.story_root,
        chapter_num=args.chapter,
        scene_num=args.scene,
        beat_num=args.beat,
    )

    print(f"Beat written to: {result['beat_path']}")
    tokens_used = result.get("tokens_used")
    if tokens_used:
        print(f"Tokens used: {tokens_used}")


if __name__ == "__main__":
    main()
