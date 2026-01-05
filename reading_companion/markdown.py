"""
Markdown file generators.

Each function generates human-readable markdown files from JSON data.
"""

from datetime import datetime

from .config import (
    DATA_DIR,
    BOOKSTACKS_DIR,
    PROGRESS_DIR,
    REFLECTIONS_DIR,
    AUTHORS_DIR,
    ensure_dirs,
)
from .storage import load_json, slugify


def save_profile_markdown(profile: dict) -> None:
    """Generate human-readable profile.md from profile data."""
    ensure_dirs()

    name = profile.get("identity", {}).get("name", "Reader")
    created = profile.get("created_at", "")[:10]
    domains = profile.get("goals", {}).get("domains", [])
    prefs = profile.get("preferences", {})
    context = profile.get("context", {})
    latent = profile.get("latent_features", {})

    lines = [
        f"# My Reading Profile",
        f"",
        f"**Name**: {name}",
        f"**Created**: {created}",
        f"",
        f"---",
        f"",
        f"## Reading Domains",
        f"",
    ]

    for domain in domains:
        lines.append(f"### {domain.get('name', domain.get('id'))}")
        lines.append(f"- **Purpose**: {domain.get('purpose', 'Not specified')}")
        lines.append(f"- **Target**: {domain.get('target_books', '?')} books")
        if domain.get('why'):
            lines.append(f"- **Why**: {domain.get('why')}")
        lines.append("")

    lines.extend([
        f"---",
        f"",
        f"## Preferences",
        f"",
        f"- **Pacing**: {prefs.get('pacing', 'Not set')}",
        f"- **Challenge tolerance**: {prefs.get('challenge_tolerance', 'Not set')}",
        f"- **Parallel books**: {prefs.get('parallel_books', 1)}",
        f"",
    ])

    if context.get("avoidances"):
        lines.append("## Avoidances")
        lines.append("")
        for item in context.get("avoidances", []):
            lines.append(f"- {item}")
        lines.append("")

    if latent:
        lines.extend([
            f"---",
            f"",
            f"## Reader Profile (Extracted)",
            f"",
            f"- **Exploration score**: {latent.get('exploration_score', 'N/A')}",
            f"- **Style**: {latent.get('depth_vs_breadth', 'N/A')}",
            f"- **Archetype**: {latent.get('reader_archetype', 'N/A')}",
            f"",
        ])
        if latent.get("notes"):
            lines.append(f"**Notes**: {latent.get('notes')}")
            lines.append("")

    path = DATA_DIR / "profile.md"
    path.write_text("\n".join(lines))


def save_bookstack_markdown(domain: str, stack_data: dict, domain_name: str = None) -> None:
    """Generate human-readable markdown for a book stack."""
    ensure_dirs()

    books = stack_data.get("books", [])
    description = stack_data.get("description", "")
    generated = stack_data.get("generated_at", "")[:10]
    display_name = domain_name or domain.replace("_", " ").title()

    lines = [
        f"# {display_name} Reading Stack",
        f"",
        f"*Generated: {generated}*",
        f"",
    ]

    if description:
        lines.extend([description, ""])

    lines.extend([
        f"---",
        f"",
        f"## Books ({len(books)} total)",
        f"",
    ])

    for i, book in enumerate(books, 1):
        difficulty = book.get("difficulty", "moderate")
        difficulty_emoji = {"light": "🟢", "moderate": "🟡", "challenging": "🔴"}.get(difficulty, "⚪")

        lines.append(f"### {i}. {book.get('title')}")
        lines.append(f"**{book.get('author')}** {difficulty_emoji} {difficulty}")
        lines.append("")
        if book.get("why"):
            lines.append(f"> {book.get('why')}")
            lines.append("")
        if book.get("time_estimate"):
            lines.append(f"- **Time**: {book.get('time_estimate')}")
        if book.get("craft_focus"):
            lines.append(f"- **Focus**: {book.get('craft_focus')}")
        lines.append("")

    path = BOOKSTACKS_DIR / f"{domain}.md"
    path.write_text("\n".join(lines))
    update_bookstacks_index()


def update_bookstacks_index() -> None:
    """Update the _index.md file listing all bookstacks."""
    ensure_dirs()

    stacks = load_json("bookstacks")
    all_stacks = stacks.get("stacks", {})

    lines = [
        "# My Reading Stacks",
        "",
        "Overview of all curated book stacks.",
        "",
        "---",
        "",
    ]

    for domain, data in all_stacks.items():
        book_count = len(data.get("books", []))
        display_name = domain.replace("_", " ").title()
        lines.append(f"## [{display_name}]({domain}.md)")
        lines.append(f"- **Books**: {book_count}")
        if data.get("description"):
            lines.append(f"- {data.get('description')}")
        lines.append("")

    path = BOOKSTACKS_DIR / "_index.md"
    path.write_text("\n".join(lines))


def save_reflection_markdown(entry: dict) -> None:
    """Generate a markdown file for a book reflection."""
    ensure_dirs()

    title = entry.get("title", "Unknown")
    author = entry.get("author", "Unknown")
    domain = entry.get("domain", "").replace("_", " ").title()
    finished = entry.get("finished_at", "")[:10]
    rating = entry.get("rating")
    reflection = entry.get("reflection", {})

    lines = [
        f"# {title}",
        f"",
        f"**Author**: {author}",
        f"**Domain**: {domain}",
        f"**Finished**: {finished}",
    ]

    if rating:
        lines.append(f"**Rating**: {'⭐' * rating}")

    lines.extend(["", "---", ""])

    if reflection:
        if reflection.get("key_takeaway"):
            lines.extend([
                "## Key Takeaway",
                "",
                reflection.get("key_takeaway"),
                "",
            ])

        if reflection.get("craft_lessons"):
            lines.extend(["## Craft Lessons", ""])
            for lesson in reflection.get("craft_lessons", []):
                lines.append(f"- {lesson}")
            lines.append("")

        if reflection.get("personal_insights"):
            lines.extend(["## Personal Insights", ""])
            for insight in reflection.get("personal_insights", []):
                lines.append(f"- {insight}")
            lines.append("")

        if reflection.get("favorite_quotes"):
            lines.extend(["## Favorite Quotes", ""])
            for quote in reflection.get("favorite_quotes", []):
                lines.append(f"> {quote}")
                lines.append("")

        if reflection.get("next_appetite"):
            appetite_map = {
                "more_like_this": "Ready for more like this",
                "ready_for_challenge": "Ready for a challenge",
                "palette_cleanser": "Need something different"
            }
            appetite = appetite_map.get(reflection.get("next_appetite"), reflection.get("next_appetite"))
            lines.extend([
                "## What's Next",
                "",
                appetite,
                "",
            ])
    else:
        lines.extend([
            "*No reflection added yet. Use 'reflect on [title]' to add one.*",
            "",
        ])

    slug = slugify(title)
    path = REFLECTIONS_DIR / f"{slug}.md"
    path.write_text("\n".join(lines))
    update_reflections_index()


def update_reflections_index() -> None:
    """Update the _index.md file listing all reflections."""
    ensure_dirs()

    log = load_json("reading_log", PROGRESS_DIR)
    entries = log.get("entries", [])

    lines = [
        "# My Book Reflections",
        "",
        f"Total books read: {len(entries)}",
        "",
        "---",
        "",
    ]

    # Group by domain
    by_domain = {}
    for entry in entries:
        domain = entry.get("domain", "other")
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append(entry)

    for domain, books in by_domain.items():
        display_name = domain.replace("_", " ").title()
        lines.append(f"## {display_name}")
        lines.append("")

        for book in books:
            title = book.get("title", "Unknown")
            slug = slugify(title)
            rating = book.get("rating")
            rating_str = f" {'⭐' * rating}" if rating else ""
            has_reflection = "✓" if book.get("reflection") else "○"
            lines.append(f"- [{title}]({slug}.md){rating_str} {has_reflection}")

        lines.append("")

    path = REFLECTIONS_DIR / "_index.md"
    path.write_text("\n".join(lines))


def update_progress_markdown() -> None:
    """Update the current progress view."""
    ensure_dirs()

    log = load_json("reading_log", PROGRESS_DIR)
    profile = load_json("profile")

    entries = log.get("entries", [])
    domains = profile.get("goals", {}).get("domains", [])

    lines = [
        "# Reading Progress",
        "",
        f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
        f"## Overview",
        "",
        f"**Total books read**: {len(entries)}",
        "",
        "---",
        "",
        "## By Domain",
        "",
    ]

    for domain in domains:
        domain_id = domain.get("id")
        domain_name = domain.get("name", domain_id)
        target = domain.get("target_books", 0)

        domain_entries = [e for e in entries if e.get("domain") == domain_id]
        completed = len(domain_entries)

        # Progress bar
        if target > 0:
            pct = min(100, int(completed / target * 100))
            filled = int(pct / 10)
            bar = "█" * filled + "░" * (10 - filled)
            status = f"[{bar}] {completed}/{target}"
        else:
            status = f"{completed} books"

        lines.append(f"### {domain_name}")
        lines.append(f"{status}")
        lines.append("")

        if domain_entries:
            for book in domain_entries[-3:]:
                lines.append(f"- {book.get('title')}")
            lines.append("")

    if entries:
        lines.extend([
            "---",
            "",
            "## Recent Activity",
            "",
        ])
        for entry in entries[-5:]:
            date = entry.get("finished_at", "")[:10]
            lines.append(f"- **{date}**: {entry.get('title')}")
        lines.append("")

    path = PROGRESS_DIR / "_current.md"
    path.write_text("\n".join(lines))


def save_author_markdown(author_slug: str, author_data: dict) -> None:
    """Generate a markdown file for an author."""
    ensure_dirs()

    name = author_data.get("name", author_slug)
    books = author_data.get("books_read", [])
    avg_rating = author_data.get("average_rating")
    affinity = author_data.get("affinity", "unknown")
    style = author_data.get("style_notes", {})
    notes = author_data.get("your_notes", "")

    lines = [
        f"# {name}",
        "",
        f"**Books Read**: {len(books)}",
    ]

    if avg_rating:
        full_stars = int(avg_rating)
        half = "½" if avg_rating - full_stars >= 0.5 else ""
        lines.append(f"**Average Rating**: {'⭐' * full_stars}{half}")

    lines.append(f"**Affinity**: {affinity.title()}")
    lines.extend(["", "---", ""])

    if books:
        lines.append("## Books You've Read")
        lines.append("")
        log = load_json("reading_log", PROGRESS_DIR)
        for book_title in books:
            for entry in log.get("entries", []):
                if entry.get("title") == book_title:
                    date = entry.get("finished_at", "")[:7]
                    rating = entry.get("rating")
                    rating_str = f" - {'⭐' * rating}" if rating else ""
                    lines.append(f"- **{book_title}** ({date}){rating_str}")
                    break
            else:
                lines.append(f"- {book_title}")
        lines.append("")

    if style:
        lines.append("## Style Notes")
        lines.append("")
        if style.get("prose"):
            lines.append(f"- **Prose**: {style.get('prose')}")
        if style.get("themes"):
            themes = ", ".join(style.get("themes", []))
            lines.append(f"- **Themes**: {themes}")
        if style.get("strengths"):
            strengths = ", ".join(style.get("strengths", []))
            lines.append(f"- **Strengths**: {strengths}")
        if style.get("comparable_to"):
            similar = ", ".join(style.get("comparable_to", []))
            lines.append(f"- **Similar to**: {similar}")
        lines.append("")

    if notes:
        lines.append("## Your Notes")
        lines.append("")
        lines.append(notes)
        lines.append("")

    path = AUTHORS_DIR / f"{author_slug}.md"
    path.write_text("\n".join(lines))


def update_authors_index() -> None:
    """Update the _index.md file listing all authors."""
    ensure_dirs()

    authors_data = load_json("authors")
    all_authors = authors_data.get("authors", {})

    sorted_authors = sorted(
        all_authors.items(),
        key=lambda x: (
            {"high": 0, "medium": 1, "low": 2, "unknown": 3}.get(x[1].get("affinity", "unknown"), 3),
            -x[1].get("total_books", 0)
        )
    )

    lines = [
        "# Authors You've Read",
        "",
        f"Total authors: {len(all_authors)}",
        "",
        "---",
        "",
    ]

    current_affinity = None
    for slug, data in sorted_authors:
        affinity = data.get("affinity", "unknown")
        if affinity != current_affinity:
            current_affinity = affinity
            affinity_emoji = {"high": "💚", "medium": "💛", "low": "🔶", "unknown": "⚪"}.get(affinity, "")
            lines.append(f"## {affinity_emoji} {affinity.title()} Affinity")
            lines.append("")

        name = data.get("name", slug)
        book_count = data.get("total_books", 0)
        avg = data.get("average_rating")
        rating_str = f" (avg ⭐{avg})" if avg else ""
        lines.append(f"- [{name}]({slug}.md) - {book_count} books{rating_str}")

    lines.append("")

    path = AUTHORS_DIR / "_index.md"
    path.write_text("\n".join(lines))


def save_patterns_markdown(patterns: dict) -> None:
    """Generate the reading patterns insights markdown."""
    ensure_dirs()

    analyzed = patterns.get("analyzed_at", datetime.now().isoformat())[:10]
    p = patterns.get("patterns", {})

    lines = [
        "# Your Reading Patterns",
        "",
        f"*Last analyzed: {analyzed}*",
        "",
        "---",
        "",
    ]

    themes_loved = p.get("themes_loved", [])
    if themes_loved:
        lines.append("## Themes You Love")
        lines.append("")
        for theme in themes_loved[:5]:
            name = theme.get("theme", "Unknown")
            freq = theme.get("frequency", 0)
            avg = theme.get("avg_rating", 0)
            lines.append(f"- **{name}** ({freq} books, avg ⭐{avg})")
        lines.append("")

    difficulty = p.get("difficulty_sweet_spot", {})
    if difficulty:
        lines.append("## Your Sweet Spot")
        lines.append("")
        preferred = difficulty.get("preferred", "moderate")
        lines.append(f"- **Preferred difficulty**: {preferred.title()}")

        by_diff = difficulty.get("success_rate_by_difficulty", {})
        if by_diff:
            lines.append("")
            lines.append("### Success by Difficulty")
            for level, stats in by_diff.items():
                completed = stats.get("completed", 0)
                avg = stats.get("avg_rating", 0)
                emoji = {"light": "🟢", "moderate": "🟡", "challenging": "🔴"}.get(level, "⚪")
                lines.append(f"- {emoji} {level.title()}: {completed} books, avg ⭐{avg}")
        lines.append("")

    pacing = p.get("pacing_insights", {})
    if pacing:
        lines.append("## Pacing")
        lines.append("")
        avg_days = pacing.get("avg_days_per_book")
        if avg_days:
            lines.append(f"- **Average**: ~{avg_days} days per book")
        longest = pacing.get("longest_read", {})
        if longest:
            lines.append(f"- **Longest read**: {longest.get('title')} ({longest.get('days')} days)")
        lines.append("")

    author_prefs = p.get("author_preferences", {})
    if author_prefs:
        lines.append("## Author Patterns")
        lines.append("")
        repeat = author_prefs.get("repeat_authors", [])
        if repeat:
            lines.append(f"- **Repeat authors**: {', '.join(repeat[:5])}")
        want_more = author_prefs.get("want_more_from", [])
        if want_more:
            lines.append(f"- **Want more from**: {', '.join(want_more[:5])}")
        lines.append("")

    avoided = p.get("themes_avoided", [])
    if avoided:
        lines.append("## Avoiding")
        lines.append("")
        for theme in avoided:
            name = theme.get("theme", "Unknown")
            reason = theme.get("reason", "")
            lines.append(f"- {name}" + (f" ({reason})" if reason else ""))
        lines.append("")

    path = PROGRESS_DIR / "_insights.md"
    path.write_text("\n".join(lines))
