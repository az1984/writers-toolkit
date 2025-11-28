#!/usr/bin/env python3
# codex.py

"""
Codex loading utilities for the fiction toolkit.

This module is responsible for loading and normalizing codex data:

- Characters (CHAR)
- Character-over-time cards (CHAR_OVERTIME)
- Locations (LOC)
- Threads (THREAD)
- Style guides (STYLE)
- Voice guides (VOICE)

It uses `codex/index.yaml` to understand where each type lives, then parses
markdown cards with YAML front matter at the top.

MVP implementation:
- Loads all cards of a given type when requested.
- Uses simple heuristics to derive `name` and `summary` fields.
- Character-over-time mapping is based on `unique-id` suffix `_OVER_TIME`.
- Relevance to a specific scene is not yet filtered (all characters/locations
  are currently considered relevant).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


# ------------------------------------------------------------------------------
# Core loading helpers
# ------------------------------------------------------------------------------


def _load_codex_index(story_root: str) -> Dict[str, Any]:
    """
    Load the codex index from `codex/index.yaml`.

    Args:
        story_root:
            Path to the story root directory.

    Returns:
        Parsed codex index dictionary.

    Raises:
        FileNotFoundError:
            If the codex index file is missing.
        yaml.YAMLError:
            If the file cannot be parsed.
    """
    index_path = Path(story_root) / "codex" / "index.yaml"

    with index_path.open("r", encoding="utf-8") as handle:
        index: Dict[str, Any] = yaml.safe_load(handle)

    return index


def _parse_markdown_card(path: Path) -> Dict[str, Any]:
    """
    Parse a markdown card file with optional YAML front matter.

    Expected format:

    ```markdown
    ---
    unique-id: [CHAR_EXAMPLE]
    tags: [character]
    names:
      - Example Name
    ---
    # Example Name

    Body text here...
    ```

    If the file does not start with a `---` front matter block, the entire
    file is treated as body text with an empty metadata dict.

    Args:
        path:
            Path to the markdown card file.

    Returns:
        A dictionary with:
            - "meta": parsed YAML metadata (or {} if none)
            - "body": the markdown body text
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {"meta": {}, "body": text}

    parts = text.split("\n", 1)
    if len(parts) == 1:
        return {"meta": {}, "body": text}

    # Split off the first line ("---") and find the closing "---".
    _, rest = parts
    fm_end = rest.find("\n---")
    if fm_end == -1:
        # Malformed front matter; treat whole file as body.
        return {"meta": {}, "body": text}

    fm_text = rest[:fm_end]
    body = rest[fm_end + len("\n---") :].lstrip("\n")

    try:
        meta = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        meta = {}

    return {"meta": meta, "body": body}


def _normalize_card(meta: Dict[str, Any], body: str) -> Dict[str, Any]:
    """
    Normalize a card into a common structure with useful fields.

    Normalized fields:
    - All keys from `meta`
    - "body": full markdown body
    - "raw_text": alias for body (for prompt building)
    - "name": first entry from `names` list if present
    - "summary": first non-empty line of body if no explicit summary exists

    Args:
        meta:
            Metadata dictionary parsed from YAML front matter.
        body:
            Markdown body text of the card.

    Returns:
        A normalized card dictionary.
    """
    card: Dict[str, Any] = dict(meta)
    card["body"] = body
    card["raw_text"] = body

    names = meta.get("names")
    if isinstance(names, list) and names:
        card["name"] = str(names[0]).strip()

    if "summary" not in card:
        lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
        if lines:
            card["summary"] = lines[0]

    return card


def _load_cards_for_type(
    story_root: str,
    type_key: str,
) -> Dict[str, Dict[str, Any]]:
    """
    Load all cards of a given codex type.

    Uses `codex/index.yaml` to find the folder for the given type key
    (e.g. "CHAR", "LOC", "THREAD").

    Args:
        story_root:
            Path to the story root directory.
        type_key:
            Codex type key as defined in `codex/index.yaml` under `types`.

    Returns:
        A mapping from card ID (usually the `unique-id` field if present) to
        normalized card dictionaries.
    """
    codex_root = Path(story_root) / "codex"
    index = _load_codex_index(story_root=story_root)
    types_cfg = index.get("types", {})

    type_cfg = types_cfg.get(type_key)
    if not type_cfg:
        return {}

    folder_name = type_cfg.get("folder")
    if not folder_name:
        return {}

    folder = codex_root / folder_name
    if not folder.exists():
        return {}

    cards: Dict[str, Dict[str, Any]] = {}

    for path in folder.glob("*.md"):
        parsed = _parse_markdown_card(path)
        meta = parsed.get("meta", {})
        body = parsed.get("body", "")

        card = _normalize_card(meta=meta, body=body)

        card_id = meta.get("unique-id") or path.stem
        card_id = str(card_id)

        cards[card_id] = card

    return cards


# ------------------------------------------------------------------------------
# Public APIs: Characters
# ------------------------------------------------------------------------------


def get_characters_for_scene(
    story_root: str,
    scene_outline: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    """
    Get character cards relevant to a scene.

    MVP implementation:
    - Returns all CHAR cards defined in the codex.
    - Ignores scene-specific filtering until a reliable tagging system is
      established.

    Args:
        story_root:
            Path to the story root directory.
        scene_outline:
            Dictionary from `load_scene_outline`. Currently unused by this
            implementation but accepted for future expansion.

    Returns:
        A mapping from character ID to normalized card dictionaries.
    """
    _ = scene_outline
    return _load_cards_for_type(story_root=story_root, type_key="CHAR")


def get_characters_over_time(
    story_root: str,
    character_ids: List[str],
) -> Dict[str, Dict[str, Any]]:
    """
    Get character-over-time cards for a set of base character IDs.

    Mapping relies on the convention:

        base card unique-id: [CHAR_SOMETHING]
        over-time unique-id: [CHAR_SOMETHING_OVER_TIME]

    Args:
        story_root:
            Path to the story root directory.
        character_ids:
            List of base character IDs (as used in `get_characters_for_scene`).

    Returns:
        A mapping from base character ID to over-time card dictionaries.
    """
    all_over_time = _load_cards_for_type(
        story_root=story_root,
        type_key="CHAR_OVERTIME",
    )

    result: Dict[str, Dict[str, Any]] = {}

    # Build a reverse map from base id -> over-time card.
    for ot_id, ot_card in all_over_time.items():
        base_id = str(ot_id).replace("_OVER_TIME", "")
        result[base_id] = ot_card

    # Filter to only requested IDs.
    filtered: Dict[str, Dict[str, Any]] = {}
    for char_id in character_ids:
        if char_id in result:
            filtered[char_id] = result[char_id]

    return filtered


# ------------------------------------------------------------------------------
# Public APIs: Locations
# ------------------------------------------------------------------------------


def get_locations_for_scene(
    story_root: str,
    scene_outline: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    """
    Get location cards relevant to a scene.

    MVP implementation:
    - Returns all LOC cards defined in the codex.
    - Ignores scene-specific filtering until a reliable tagging system is
      established.

    Args:
        story_root:
            Path to the story root directory.
        scene_outline:
            Dictionary from `load_scene_outline`. Currently unused by this
            implementation but accepted for future expansion.

    Returns:
        A mapping from location ID to normalized card dictionaries.
    """
    _ = scene_outline
    return _load_cards_for_type(story_root=story_root, type_key="LOC")


# ------------------------------------------------------------------------------
# Public APIs: Threads, Style, Voice
# ------------------------------------------------------------------------------


def get_threads(story_root: str) -> Dict[str, Dict[str, Any]]:
    """
    Get all thread cards.

    MVP implementation:
    - Returns all THREAD cards defined in the codex without additional
      time-filtering (time-aware logic is handled in `beat_spec`).

    Args:
        story_root:
            Path to the story root directory.

    Returns:
        A mapping from thread ID to normalized card dictionaries.
    """
    return _load_cards_for_type(story_root=story_root, type_key="THREAD")


def get_style_guide(story_root: str) -> Optional[Dict[str, Any]]:
    """
    Get the primary style guide card for the story.

    MVP implementation:
    - Loads all STYLE cards.
    - Prefers a card with unique-id "STYLE_PROJECT_DEFAULT" if present.
    - Falls back to the first available STYLE card.
    - Returns None if no STYLE cards are found.

    Args:
        story_root:
            Path to the story root directory.

    Returns:
        The chosen style guide card dictionary, or None.
    """
    styles = _load_cards_for_type(story_root=story_root, type_key="STYLE")
    if not styles:
        return None

    for style_id, style_card in styles.items():
        if str(style_id) == "STYLE_PROJECT_DEFAULT":
            return style_card

    # Fallback to arbitrary first style.
    style_id = next(iter(styles.keys()))
    return styles[style_id]


def get_pov_voice(
    story_root: str,
    pov_char_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Get a voice guide card appropriate for the POV character.

    MVP implementation:
    - Loads all VOICE cards.
    - Attempts to match a card whose `character` field equals the POV
      character's name.
    - If no match is found, returns the first VOICE card.
    - Returns None if no VOICE cards exist.

    Note:
        This function currently reloads character cards to resolve the POV
        character's name. If this becomes a performance issue, the beat_spec
        builder can be extended to pass the character name directly.

    Args:
        story_root:
            Path to the story root directory.
        pov_char_id:
            The ID of the POV character (e.g. the `unique-id` of a character
            card).

    Returns:
        A voice guide card dictionary, or None if no suitable card exists.
    """
    voices = _load_cards_for_type(story_root=story_root, type_key="VOICE")
    if not voices:
        return None

    # Attempt to resolve the POV character's name.
    chars = _load_cards_for_type(story_root=story_root, type_key="CHAR")
    pov_card = chars.get(pov_char_id)
    pov_name: Optional[str] = None
    if pov_card is not None:
        pov_name = pov_card.get("name")

    if pov_name:
        for voice_card in voices.values():
            if voice_card.get("character") == pov_name:
                return voice_card

    # Fallback: return the first available voice card.
    voice_id = next(iter(voices.keys()))
    return voices[voice_id]
