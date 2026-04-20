#!/usr/bin/env python
"""
populate_blog.py — Generate and save a blog post using Claude AI.

Usage:
    python scripts/populate_blog.py \
      --api-key sk-ant-... \
      --topic "How to warm up before choir rehearsal"

    python scripts/populate_blog.py \
      --api-key sk-ant-... \
      --topic "Breathing for altos" \
      --category technique \
      --published

    python scripts/populate_blog.py \
      --api-key sk-ant-... \
      --topic "Healthy singing during cold season" \
      --author admin \
      --dry-run
"""

import argparse
import json
import os
import re
import sys
from html import escape

import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyc_warmup.settings")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from blog.models import BlogPost  # noqa: E402

MODEL = "claude-haiku-4-5"
CATEGORY_CHOICES = [choice for choice, _label in BlogPost.CATEGORY_CHOICES]

SYSTEM_PROMPT = f"""
You are a strong choir educator and blog writer.
Generate a complete blog post for a choir-training website.
Return ONLY valid JSON with exactly these keys:

{{
  "title": "<string>",
  "category": "<one of: {', '.join(CATEGORY_CHOICES)}>",
  "excerpt": "<html string>",
  "body": "<html string>"
}}

Rules:
- Write for choir singers, choir trainers, section leaders, and music learners.
- `title`: clear, catchy, practical, and specific.
- `category`: must be one of the allowed values.
- `excerpt`: 1 short paragraph in HTML, usually wrapped in <p>...</p>.
- `body`: 500–1000 words in HTML.
- Use semantic HTML like <p>, <h2>, <h3>, <ul>, <li>, <blockquote>, <strong>, <em>.
- Make the writing engaging, practical, warm, and clear.
- Include concrete tips, examples, and actionable advice.
- Do not include markdown fences.
- Do not include any keys beyond the four specified.
""".strip()


def extract_json_payload(text: str) -> str:
    stripped = text.strip()
    fenced_match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", stripped, flags=re.IGNORECASE | re.DOTALL)
    if fenced_match:
        return fenced_match.group(1).strip()

    first_brace = stripped.find("{")
    last_brace = stripped.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return stripped[first_brace:last_brace + 1]

    return stripped


def normalize_html(value: str) -> str:
    if not value:
        return ""

    text = value.strip()
    if not text:
        return ""

    if re.search(r"<\s*[a-zA-Z][^>]*>", text):
        return text

    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
    if not paragraphs:
        return f"<p>{escape(text)}</p>"

    return "\n".join(f"<p>{escape(paragraph)}</p>" for paragraph in paragraphs)


def resolve_category(category: str) -> str:
    if category in CATEGORY_CHOICES:
        return category
    return "other"


def call_claude(client, topic: str, forced_category: str | None = None) -> dict:
    user_prompt = f'Write a blog post about: "{topic}".'
    if forced_category:
        user_prompt += f" Use category '{forced_category}'."

    print(f"→ Querying Claude for blog topic: {topic!r}")
    message = client.messages.create(
        model=MODEL,
        max_tokens=2200,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = message.content[0].text.strip()
    payload = extract_json_payload(raw)
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as error:
        print(f"✗ Invalid JSON from Claude:\n{raw}\nError: {error}")
        return {}

    return data


def resolve_author(author_value: str | None):
    if not author_value:
        return None

    User = get_user_model()
    try:
        return User.objects.get(username=author_value)
    except User.DoesNotExist:
        try:
            return User.objects.get(pk=int(author_value))
        except (ValueError, User.DoesNotExist):
            print(f"Warning: no user found for author '{author_value}'. Leaving author empty.")
            return None


def build_post_data(data: dict, topic: str, category: str | None) -> dict:
    title = (data.get("title") or topic).strip()
    excerpt = normalize_html(data.get("excerpt", ""))
    body = normalize_html(data.get("body", ""))
    resolved_category = resolve_category(category or data.get("category", "other"))

    return {
        "title": title,
        "category": resolved_category,
        "excerpt": excerpt,
        "body": body,
    }


def populate_blog(api_key: str, topic: str, category: str | None = None, author_value: str | None = None,
                  published: bool = False, dry_run: bool = False):
    try:
        import anthropic
    except ImportError:
        print("ERROR: 'anthropic' package not installed. Run: pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    author = resolve_author(author_value)

    data = call_claude(client, topic, forced_category=category)
    if not data:
        return None

    post_data = build_post_data(data, topic, category)

    print("\n── Generated blog ─────────────────────────")
    print(f"title    : {post_data['title']}")
    print(f"category : {post_data['category']}")
    print(f"excerpt  : {post_data['excerpt'][:120]}{'...' if len(post_data['excerpt']) > 120 else ''}")
    print(f"body     : {post_data['body'][:120]}{'...' if len(post_data['body']) > 120 else ''}")
    print("──────────────────────────────────────────\n")

    if dry_run:
        print("DRY RUN — not saved.")
        return post_data

    post = BlogPost.objects.create(
        title=post_data["title"],
        category=post_data["category"],
        excerpt=post_data["excerpt"],
        body=post_data["body"],
        author=author,
        published=published,
    )
    print(f"✓ Saved blog post '{post.title}' (slug={post.slug})")
    return post


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and save a blog post using Claude AI.")
    parser.add_argument("--api-key", required=True, help="Anthropic API key (sk-ant-...)")
    parser.add_argument("--topic", required=True, help="Topic or working title for the blog post")
    parser.add_argument("--category", choices=CATEGORY_CHOICES, help="Optional fixed category")
    parser.add_argument("--author", help="Optional author username or user ID")
    parser.add_argument("--published", action="store_true", help="Mark the post as published")
    parser.add_argument("--dry-run", action="store_true", help="Generate without saving")

    args = parser.parse_args()
    populate_blog(
        api_key=args.api_key,
        topic=args.topic,
        category=args.category,
        author_value=args.author,
        published=args.published,
        dry_run=args.dry_run,
    )
