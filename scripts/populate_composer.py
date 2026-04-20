#!/usr/bin/env python
"""
populate_composer.py — Populate a Composer's info using Claude AI.

Usage:
    python scripts/populate_composer.py --api-key sk-ant-... --name "Johann Sebastian Bach"
    python scripts/populate_composer.py --api-key sk-ant-... --name "Handel" --dry-run

Reads the Composer record from the DB by name (case-insensitive partial match),
calls Claude to generate rich content, then saves bio, born, died, nationality, website.
"""

import os
import sys
import json
import argparse
import django

# ── Django setup ────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyc_warmup.settings")
django.setup()

from songs.models import Composer  # noqa: E402  (after django.setup)

# ── Prompt templates ─────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are a music historian and writer with a flair for engaging, varied prose.
You will be given a composer's name and you must return a JSON object with the
following fields populated as richly as possible:

{
  "bio": "<string>",
  "born": "<string>",
  "died": "<string>",
  "nationality": "<string>",
  "website": "<string>"
}

Rules:
- "bio": Write 150–300 words. Vary the style each time — it may open with a
  striking quote by or about the composer, a vivid anecdote, a brief story, a
  reflection on their legacy, or a straightforward but lyrical biography. Do
  NOT always start with the composer's name. Make it feel human and interesting.
- "born": A human-readable date/year, e.g. "21 March 1685" or "c. 1650".
  If only the year is known, just give the year.
- "died": Same format, or "still living" / "unknown" as appropriate.
- "nationality": e.g. "German", "Nigerian", "American–British".
- "website": Official website URL if one exists, else an empty string "".

Return ONLY valid JSON — no markdown fences, no extra keys, no commentary.
If a field is genuinely unknown, use an empty string for text fields.
""".strip()


def build_user_message(name: str) -> str:
    return f'Populate the composer info for: "{name}"'


# ── Claude API call ──────────────────────────────────────────────────────────
def call_claude(api_key: str, name: str, model: str = "claude-opus-4-5") -> dict:
    try:
        import anthropic
    except ImportError:
        print("ERROR: 'anthropic' package not installed. Run:  pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print(f"  → Calling Claude ({model}) for: {name!r} ...")
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": build_user_message(name)},
        ],
    )

    raw = message.content[0].text.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Claude returned invalid JSON:\n{raw}\n\nParse error: {e}")
        sys.exit(1)

    return data


# ── Main function ─────────────────────────────────────────────────────────────
def populate_composer(api_key: str, name: str, dry_run: bool = False, model: str = "claude-opus-4-5"):
    """
    Find or create a Composer by name, populate their fields via Claude, and save.

    Args:
        api_key:  Anthropic API key.
        name:     Composer name (used for DB lookup and AI prompt).
        dry_run:  If True, print what would be saved without writing to DB.
        model:    Claude model to use.
    """
    # Look up existing composer (case-insensitive)
    qs = Composer.objects.filter(name__icontains=name)
    if qs.count() == 0:
        print(f"  No composer found matching '{name}'. Creating new record.")
        composer = Composer(name=name)
    elif qs.count() == 1:
        composer = qs.first()
        print(f"  Found composer: {composer.name} (id={composer.pk})")
    else:
        print(f"  Multiple matches for '{name}':")
        for c in qs:
            print(f"    [{c.pk}] {c.name}")
        choice = input("  Enter ID to use: ").strip()
        composer = qs.get(pk=int(choice))

    # Fetch data from Claude
    data = call_claude(api_key, composer.name, model=model)

    # Show what we got
    print("\n  ── Claude response ──────────────────────────────────")
    for k, v in data.items():
        display = (v[:120] + "...") if len(str(v)) > 120 else v
        print(f"  {k:12s}: {display}")
    print("  ─────────────────────────────────────────────────────\n")

    if dry_run:
        print("  DRY RUN — no changes written to database.")
        return data

    # Apply fields (only overwrite if Claude returned a non-empty value)
    if data.get("bio"):
        composer.bio = data["bio"]
    if data.get("born"):
        composer.born = data["born"]
    if data.get("died"):
        composer.died = data["died"]
    if data.get("nationality"):
        composer.nationality = data["nationality"]
    if data.get("website"):
        composer.website = data["website"]

    composer.save()
    print(f"  ✓ Saved composer '{composer.name}' (id={composer.pk})")
    return data


# ── CLI entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Populate a Composer record using Claude AI."
    )
    parser.add_argument("--api-key", required=True, help="Anthropic API key (sk-ant-...)")
    parser.add_argument("--name", required=True, help="Composer name to look up / create")
    parser.add_argument(
        "--model",
        default="claude-opus-4-5",
        help="Claude model to use (default: claude-opus-4-5)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated data without writing to the database",
    )

    args = parser.parse_args()

    populate_composer(
        api_key=args.api_key,
        name=args.name,
        dry_run=args.dry_run,
        model=args.model,
    )
