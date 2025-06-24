#!/usr/bin/env python3
"""
Run Codex against a prompt read from STDIN and save the Git diff to codex.patch.

Usage:
    echo "Implement X" | poetry run python scripts/run_codex.py
"""

from __future__ import annotations

import os
import sys

from openai import OpenAI, BadRequestError  # type: ignore


def main() -> None:  # pragma: no cover
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        sys.exit("❌  OPENAI_API_KEY is not set")

    prompt = sys.stdin.read().strip()
    if not prompt:
        sys.exit("❌  No prompt supplied on STDIN")

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",          # 失敗したら手動で gpt-4o にリトライ
            temperature=0.1,
            max_tokens=2048,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an experienced Python 3.12 engineer working on the "
                        "Claude Session Manager project. Follow project conventions "
                        "(Poetry, TDD, MIT license) and output ONLY a valid unified diff."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
    except BadRequestError as exc:
        sys.exit(f"❌  OpenAI error: {exc}")

    diff_text: str = response.choices[0].message.content or ""
    with open("codex.patch", "w", encoding="utf-8") as fh:
        fh.write(diff_text)

    print("📝  Patch written to codex.patch")


if __name__ == "__main__":
    main()
