#!/usr/bin/env python3
# model_client.py

"""
Model client utilities for the fiction toolkit.

This module provides a single high-level function, `call_model`, which:
- Loads model configuration from `toolkit/config/model.yaml` under a given story root
- Reads the API key from an environment variable (name defined in the config)
- Calls an OpenAI-compatible chat completion endpoint via the v1 OpenAI client
- Returns the primary completion text along with optional token usage metadata

The goal is to keep all model-specific wiring and environment concerns here, so the
rest of the toolkit can treat language models as a simple function call.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from openai import OpenAI


# ------------------------------------------------------------------------------
# Configuration loading
# ------------------------------------------------------------------------------


def _load_model_config(story_root: str) -> Dict[str, Any]:
    """
    Load model configuration for the given story root.

    The configuration file is expected at:
        <story_root>/toolkit/config/model.yaml

    Expected YAML structure (example):

    ```yaml
    provider: "openai-compatible"
    base_url: "http://localhost:8080/v1"
    model: "Eurayle-70B-Instruct"
    api_key_env: "LLM_API_KEY"
    timeout_seconds: 120

    default_params:
      temperature: 0.85
      top_p: 0.95
      max_tokens: 1024
    ```

    Args:
        story_root:
            Path to the story root directory. This directory should contain the
            `toolkit/` folder with a `config/model.yaml` file.

    Returns:
        A dictionary representing the parsed YAML configuration.

    Raises:
        FileNotFoundError:
            If the configuration file cannot be found.
        yaml.YAMLError:
            If the configuration file cannot be parsed.
    """
    config_path = Path(story_root) / "toolkit" / "config" / "model.yaml"

    with config_path.open("r", encoding="utf-8") as handle:
        config: Dict[str, Any] = yaml.safe_load(handle)

    return config


# ------------------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------------------


def call_model(
    story_root: str,
    messages: List[Dict[str, str]],
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Call an OpenAI-compatible chat completion model using project-local config.

    This function is the single point where the toolkit interacts with the model
    provider. It reads configuration from `toolkit/config/model.yaml` under the
    given `story_root`, obtains the API key from the environment, and sends a
    chat completion request using the `openai` client.

    The `messages` argument should match the standard OpenAI Chat API format:

    ```python
    messages = [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."},
        # optionally: {"role": "assistant", "content": "..."},
    ]
    ```

    Args:
        story_root:
            Path to the story root directory. Used to resolve the model
            configuration file.
        messages:
            Ordered list of messages forming the chat conversation. Each entry
            must contain `role` and `content` keys.
        params:
            Optional dictionary of additional generation parameters. These will
            be merged on top of any `default_params` from the model config,
            allowing per-call overrides.

    Returns:
        A dictionary with the following keys:

        - "text": str
            The primary completion text returned by the model.
        - "tokens_used": Dict[str, Optional[int]]
            A summary of token usage, if provided by the backend.
            Contains "prompt_tokens", "completion_tokens", and "total_tokens".
        - "raw": Any
            The raw response object returned by the `openai` client. Useful for
            debugging or advanced inspection.

    Raises:
        RuntimeError:
            If the required API key environment variable is not set.
        openai.error.OpenAIError:
            If an error occurs while calling the model.
    """
    config = _load_model_config(story_root=story_root)

    base_url: Optional[str] = config.get("base_url")
    model_name: str = config["model"]
    api_key_env: str = config.get("api_key_env", "OPENAI_API_KEY")
    timeout_seconds: int = int(config.get("timeout_seconds", 120))

    api_key: Optional[str] = os.getenv(api_key_env)
    if not api_key:
        raise RuntimeError(
            f"Environment variable {api_key_env!r} is not set; cannot call model."
        )

    # Configure the OpenAI-compatible client using the v1 client class.
    client_kwargs: Dict[str, Any] = {"api_key": api_key}
    if base_url:
        # Many local or proxy servers expose an OpenAI-compatible API at a custom base URL.
        client_kwargs["base_url"] = base_url

    client = OpenAI(**client_kwargs)

    default_params: Dict[str, Any] = config.get("default_params", {})
    final_params: Dict[str, Any] = {**default_params, **(params or {})}

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        timeout=timeout_seconds,
        **final_params,
    )

    # Extract the primary completion text and token usage.
    first_choice = response.choices[0]
    text: str = first_choice.message.content

    usage = getattr(response, "usage", None)
    tokens_used: Dict[str, Optional[int]] = {
        "prompt_tokens": getattr(usage, "prompt_tokens", None) if usage is not None else None,
        "completion_tokens": getattr(usage, "completion_tokens", None) if usage is not None else None,
        "total_tokens": getattr(usage, "total_tokens", None) if usage is not None else None,
    }

    return {
        "text": text,
        "tokens_used": tokens_used,
        "raw": response,
    }
