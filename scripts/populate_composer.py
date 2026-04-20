#!/usr/bin/env python
"""
populate_composer.py — Populate all Composer records using Claude AI (claude-haiku-4-5).

Usage:
    # Populate ALL composers in the database
    python scripts/populate_composer.py --api-key sk-ant-...

    # Populate only composers whose name contains a substring
    python scripts/populate_composer.py --api-key sk-ant-... --name "Bach"

    # Dry run — print what Claude would write without saving
    python scripts/populate_composer.py --api-key sk-ant-... --dry-run

    # Skip composers that already have a bio filled in
    python scripts/populate_composer.py --api-key sk-ant-... --skip-populated
"""

import os
import sys
import json
import argparse
import django

# ── Django setup ─────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyc_warmup.settings")
django.setup()

from songs.models import Composer  # noqa: E402

MODEL = "claude-haiku-4-5"

# ── Prompts ───────────────────────────────────────────────────────────────────
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
- "bio": Write 150–300 words. Vary the style — it may open with a striking quote
  by or about the composer, a vivid anecdote, a brief story, a reflection on their
  legacy, or a straightforward but lyrical biography. Do NOT always start with the
  composer's name. Make it feel human and interesting.
- "born": A human-readable date/year, e.g. "21 March 1685" or "c. 1650".
  If only the year is known, just give the year.
- "died": Same format, or "still living" / "unknown" as appropriate.
- "nationality": e.g. "German", "Nigerian", "American–British".
- "website": Official website URL if one exists, else an empty string "".

Return ONLY valid JSON — no markdown fences, no extra keys, no commentary.
If a field is genuinely unknown, use an empty string for text fields.
""".strip()


# ── Claude call ───────────────────────────────────────────────────────────────
def call_claude(client, name: str) -> dict:
    print(f"    → Querying Claude for: {name!r} ...")
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f'Populate the composer info for: "{name}"'}],
    )
    raw = message.content[0].text.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"    ✗ Invalid JSON from Claude:\n{raw}\n    Error: {e}")
        return {}


# ── Single composer populate ──────────────────────────────────────────────────
def populate_one(client, composer, dry_run: bool) -> bool:
    data = call_claude(client, composer.name)
    if not data:
        return False

    for k, v in data.items():
        display = (str(v)[:100] + "...") if len(str(v)) > 100 else v
        print(f"      {k:12s}: {display}")

    if dry_run:
        print("      [DRY RUN — not saved]\n")
        return True

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
    print("      ✓ Saved\n")
    return True


# ── Main ──────────────────────────────────────────────────────────────────────
def run(api_key: str, name_filter: str = None, dry_run: bool = False, skip_populated: bool = False):
    try:
        import anthropic
    except ImportError:
        print("ERROR: 'anthropic' package not installed. Run:  pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    qs = Composer.objects.all().order_by("name")
    if name_filter:
        qs = qs.filter(name__icontains=name_filter)
    if skip_populated:
        qs = qs.filter(bio="")

    total = qs.count()
    if total == 0:
        print("No composers found matching the given criteria.")
        return

    print(f"\nModel       : {MODEL}")
    print(f"Composers   : {total}")
    print(f"Dry run     : {dry_run}")
    print(f"Skip filled : {skip_populated}")
    print("─" * 50)

    ok = 0
    for i, composer in enumerate(qs, 1):
        print(f"\n[{i}/{total}] {composer.name} (id={composer.pk})")
        if populate_one(client, composer, dry_run):
            ok += 1

    print("─" * 50)
    print(f"Done — {ok}/{total} composers {'previewed' if dry_run else 'updated'}.")


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Populate all Composer records using Claude AI (claude-haiku-4-5)."
    )
    parser.add_argument("--api-key", required=True, help="Anthropic API key (sk-ant-...)")
    parser.add_argument(
        "--name",
        default=None,
        help="Optional: filter composers by name substring (default: all composers)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated data without writing to the database",
    )
    parser.add_argument(
        "--skip-populated",
        action="store_true",
        help="Skip composers that already have a bio filled in",
    )

    args = parser.parse_args()
    run(
        api_key=args.api_key,
        name_filter=args.name,
        dry_run=args.dry_run,
        skip_populated=args.skip_populated,
    )
