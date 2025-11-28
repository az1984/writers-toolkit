#!/usr/bin/env python3
# prompts.py

"""
Prompt utilities for the fiction toolkit.

This module provides helpers to:
- Render prompt templates from `toolkit/prompts/<template_set>/` by performing
  simple `{{PLACEHOLDER}}` substitution using a blocks dictionary.
- Respect `toolkit/config/prompting.yaml` so that each high-level action
  (e.g. ACTIONS_WRITE_BEAT, ACTIONS_MAKE_PRESENT_TENSE) can declare:
    - which template_set to use
    - which slots (system, user, user2, etc.) are active
    - which roles those slots map to in the OpenAI-style messages list.
- Turn rendered prompt strings (system/user/user2) into OpenAI-style
  `messages` lists for model calls.

The intent is to keep all wiring about "which templates, which slots, which
roles" in configuration, not hardcoded in Python.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# ------------------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------------------


def _load_prompting_config(story_root: str) -> Dict[str, Any]:
    """Load prompting configuration from `toolkit/config/prompting.yaml`.

    The expected structure is:

    ```yaml
    actions:
      ACTIONS_WRITE_BEAT:
        template_set: "nc/beat"
        slots:
          - slot: system
            role: system
            required: true
          - slot: user
            role: user
            required: true
          - slot: user2
            role: user
            required: false
    ```

    Args:
        story_root:
            Path to the story root directory.

    Returns:
        Parsed prompting configuration as a dictionary.

    Raises:
        FileNotFoundError:
            If the prompting.yaml file does not exist.
        yaml.YAMLError:
            If the file cannot be parsed.
    """
    cfg_path = Path(story_root) / "toolkit" / "config" / "prompting.yaml"

    with cfg_path.open("r", encoding="utf-8") as handle:
        cfg: Dict[str, Any] = yaml.safe_load(handle)

    return cfg


def _render_template_file(template_path: Path, blocks: Dict[str, str]) -> str:
    """Render a single template file using `{{KEY}}` placeholder substitution.

    Args:
        template_path:
            Path to the template file to render.
        blocks:
            Mapping from placeholder names (without braces) to replacement
            strings.

    Returns:
        The fully rendered template as a string.
    """
    raw_text = template_path.read_text(encoding="utf-8")
    rendered = raw_text

    for key, value in blocks.items():
        placeholder = f"{{{{{key}}}}}"
        rendered = rendered.replace(placeholder, str(value))

    return rendered


def _slot_to_filename(slot: str) -> str:
    """Map a logical slot name to its template filename.

    Known mappings:
    - system -> system_message.txt
    - user   -> user.txt
    - user2  -> user_2.txt

    Any other slot falls back to "<slot>.txt".
    """
    if slot == "system":
        return "system_message.txt"
    if slot == "user":
        return "user.txt"
    if slot == "user2":
        return "user_2.txt"

    return f"{slot}.txt"


# ------------------------------------------------------------------------------
# Template rendering APIs
# ------------------------------------------------------------------------------


def render_template_set(story_root: str, template_set: str, blocks: Dict[str, str]) -> Dict[str, str]:
    """Render all standard templates for a given template set.

    This helper:
      - Looks in `toolkit/prompts/<template_set>/`
      - Attempts to load the standard filenames: system_message.txt, user.txt,
        user_2.txt
      - Applies placeholder substitution for each file found

    It returns a dictionary keyed by logical slot name: "system", "user",
    and "user2" for any files that exist in the template set.
    """
    prompts_root = Path(story_root) / "toolkit" / "prompts" / template_set

    results: Dict[str, str] = {}

    for slot in ("system", "user", "user2"):
        filename = _slot_to_filename(slot)
        path = prompts_root / filename

        if path.exists():
            results[slot] = _render_template_file(path, blocks)

    return results


def render_prompts_for_action(story_root: str, action_key: str, blocks: Dict[str, str]) -> Dict[str, str]:
    """Render prompts for a specific high-level action using prompting.yaml.

    This function:
      - Reads `toolkit/config/prompting.yaml`
      - Looks up configuration for `action_key`
      - Determines which `template_set` and slots to use
      - Renders only those slots using the provided `blocks`

    It returns a dictionary mapping slot names (e.g. "system", "user",
    "user2") to rendered prompt strings.
    """
    prompting_cfg = _load_prompting_config(story_root=story_root)
    actions_cfg = prompting_cfg.get("actions", {})

    if action_key not in actions_cfg:
        available = ", ".join(sorted(actions_cfg.keys()))
        raise KeyError(
            f"Action {action_key!r} not found in prompting.yaml. "
            f"Available actions: {available}"
        )

    action_cfg: Dict[str, Any] = actions_cfg[action_key]
    template_set: str = action_cfg["template_set"]
    slots_cfg: List[Dict[str, Any]] = action_cfg.get("slots", [])

    prompts_root = Path(story_root) / "toolkit" / "prompts" / template_set
    rendered: Dict[str, str] = {}

    for slot_def in slots_cfg:
        slot_name: str = slot_def["slot"]
        filename: str = _slot_to_filename(slot_name)
        path = prompts_root / filename

        if not path.exists():
            is_required: bool = bool(slot_def.get("required", False))
            if is_required:
                raise FileNotFoundError(
                    f"Required template file for slot {slot_name!r} "
                    f"not found at: {path}"
                )
            continue

        rendered[slot_name] = _render_template_file(path, blocks)

    return rendered


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
