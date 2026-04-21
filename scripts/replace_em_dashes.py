#!/usr/bin/env python
"""
replace_em_dashes.py — Replace em dashes in BlogPost excerpts and bodies.

Usage:
    python scripts/replace_em_dashes.py
    python scripts/replace_em_dashes.py --dry-run
    python scripts/replace_em_dashes.py --published-only
"""

import argparse
import os
import sys

import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyc_warmup.settings")
django.setup()

from django.db import transaction  # noqa: E402
from blog.models import BlogPost  # noqa: E402

EM_DASH = "—"
NORMAL_DASH = "-"


def replace_text(value: str) -> tuple[str, int]:
    if not value:
        return value or "", 0
    count = value.count(EM_DASH)
    return value.replace(EM_DASH, NORMAL_DASH), count


def run(dry_run: bool = False, published_only: bool = False) -> None:
    queryset = BlogPost.objects.all().order_by("id")
    if published_only:
        queryset = queryset.filter(published=True)

    posts_scanned = 0
    posts_changed = 0
    excerpt_replacements = 0
    body_replacements = 0

    with transaction.atomic():
        for post in queryset.iterator():
            posts_scanned += 1
            new_excerpt, excerpt_count = replace_text(post.excerpt)
            new_body, body_count = replace_text(post.body)

            if excerpt_count == 0 and body_count == 0:
                continue

            posts_changed += 1
            excerpt_replacements += excerpt_count
            body_replacements += body_count

            print(
                f"• {post.id}: {post.title} "
                f"(excerpt={excerpt_count}, body={body_count})"
            )

            if dry_run:
                continue

            post.excerpt = new_excerpt
            post.body = new_body
            post.save(update_fields=["excerpt", "body", "updated_at"])

        if dry_run:
            transaction.set_rollback(True)

    mode = "DRY RUN" if dry_run else "UPDATED"
    print("\n=== Summary ===")
    print(f"Mode: {mode}")
    print(f"Posts scanned: {posts_scanned}")
    print(f"Posts changed: {posts_changed}")
    print(f"Excerpt replacements: {excerpt_replacements}")
    print(f"Body replacements: {body_replacements}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Replace em dashes (—) with normal dashes (-) in blog excerpts and bodies."
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without saving")
    parser.add_argument("--published-only", action="store_true", help="Only process published posts")
    args = parser.parse_args()

    run(dry_run=args.dry_run, published_only=args.published_only)
