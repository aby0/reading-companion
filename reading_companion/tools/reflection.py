"""
Stage 4: Reflection Tools

Tools for logging books, conducting reflections, and tracking progress.
"""

from datetime import datetime

from ..config import PROGRESS_DIR, REFLECTIONS_DIR
from ..storage import load_json, save_json, load_prompt, slugify
from ..markdown import (
    save_reflection_markdown,
    update_progress_markdown,
    save_author_markdown,
    update_authors_index,
)


def update_author_on_book_log(author: str, title: str, rating: int = None, finished_date: str = None):
    """
    Update author tracking when a book is logged.
    Creates author profile if it doesn't exist.
    """
    authors_data = load_json("authors")

    if "authors" not in authors_data:
        authors_data = {"version": "1.0", "authors": {}}

    author_slug = slugify(author)

    if author_slug not in authors_data["authors"]:
        authors_data["authors"][author_slug] = {
            "name": author,
            "books_read": [],
            "total_books": 0,
            "ratings": [],
            "average_rating": None,
            "first_read": finished_date,
            "last_read": finished_date,
            "affinity": "unknown",
            "style_notes": {},
            "your_notes": ""
        }

    author_entry = authors_data["authors"][author_slug]

    # Add book if not already tracked
    if title not in author_entry["books_read"]:
        author_entry["books_read"].append(title)
        author_entry["total_books"] = len(author_entry["books_read"])

    # Update rating
    if rating:
        author_entry["ratings"].append(rating)
        author_entry["average_rating"] = round(
            sum(author_entry["ratings"]) / len(author_entry["ratings"]), 1
        )
        avg = author_entry["average_rating"]
        if avg >= 4.5:
            author_entry["affinity"] = "high"
        elif avg >= 3.5:
            author_entry["affinity"] = "medium"
        else:
            author_entry["affinity"] = "low"

    # Update dates
    if finished_date:
        author_entry["last_read"] = finished_date
        if not author_entry["first_read"]:
            author_entry["first_read"] = finished_date

    save_json("authors", authors_data)
    save_author_markdown(author_slug, author_entry)
    update_authors_index()


def register_reflection_tools(mcp):
    """Register reflection tools with the MCP server."""

    @mcp.tool()
    def log_book(
        title: str,
        author: str,
        domain: str,
        rating: int = None,
        quick_note: str = None
    ) -> dict:
        """
        Log a completed book (quick mode).

        Args:
            title: Book title
            author: Author name
            domain: Which domain this book belongs to
            rating: Optional 1-5 rating
            quick_note: Optional brief note
        """
        log = load_json("reading_log", PROGRESS_DIR)

        if "entries" not in log:
            log = {"version": "1.0", "entries": []}

        entry = {
            "id": f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": title,
            "author": author,
            "domain": domain,
            "finished_at": datetime.now().isoformat(),
            "rating": rating,
            "quick_note": quick_note,
            "reflection": None
        }

        log["entries"].append(entry)
        save_json("reading_log", log, PROGRESS_DIR)

        save_reflection_markdown(entry)
        update_progress_markdown()

        update_author_on_book_log(
            author=author,
            title=title,
            rating=rating,
            finished_date=entry["finished_at"]
        )

        return {
            "status": "logged",
            "message": f"'{title}' by {author} logged!",
            "file": str(REFLECTIONS_DIR / f"{slugify(title)}.md"),
            "suggestion": "Want to do a quick reflection or deep dive? Say 'reflect on [title]'"
        }

    @mcp.tool()
    def start_reflection(title: str) -> dict:
        """Start a deep reflection session for a book."""
        prompt = load_prompt("reflection")
        log = load_json("reading_log", PROGRESS_DIR)
        profile = load_json("profile")

        book_entry = None
        for entry in log.get("entries", []):
            if entry.get("title", "").lower() == title.lower():
                book_entry = entry
                break

        if not book_entry:
            return {
                "error": f"'{title}' not found in reading log",
                "suggestion": "Log the book first with log_book, then reflect"
            }

        domain_goal = None
        book_domain = book_entry.get("domain")
        for d in profile.get("goals", {}).get("domains", []):
            if d.get("id") == book_domain:
                domain_goal = d
                break

        return {
            "instruction": f"Guide a reflection session for '{title}'",
            "prompt": prompt,
            "book": book_entry,
            "domain_goal": domain_goal,
            "user_context": profile.get("context", {})
        }

    @mcp.tool()
    def save_reflection(
        title: str,
        key_takeaway: str,
        craft_lessons: list[str] = None,
        personal_insights: list[str] = None,
        favorite_quotes: list[str] = None,
        next_appetite: str = None
    ) -> dict:
        """
        Save a deep reflection for a book.

        Args:
            title: Book title
            key_takeaway: One sentence distillation
            craft_lessons: What you learned about writing/craft
            personal_insights: How this connects to your life
            favorite_quotes: Memorable passages
            next_appetite: "more_like_this" | "ready_for_challenge" | "palette_cleanser"
        """
        log = load_json("reading_log", PROGRESS_DIR)

        found_entry = None
        for entry in log.get("entries", []):
            if entry.get("title", "").lower() == title.lower():
                entry["reflection"] = {
                    "key_takeaway": key_takeaway,
                    "craft_lessons": craft_lessons or [],
                    "personal_insights": personal_insights or [],
                    "favorite_quotes": favorite_quotes or [],
                    "next_appetite": next_appetite,
                    "reflected_at": datetime.now().isoformat()
                }
                found_entry = entry
                break

        if not found_entry:
            return {"error": f"'{title}' not found in reading log"}

        save_json("reading_log", log, PROGRESS_DIR)
        save_reflection_markdown(found_entry)
        update_progress_markdown()

        return {
            "status": "saved",
            "message": f"Reflection saved for '{title}'",
            "file": str(REFLECTIONS_DIR / f"{slugify(title)}.md"),
            "key_takeaway": key_takeaway,
            "next_appetite": next_appetite
        }

    @mcp.tool()
    def get_reading_log(limit: int = None) -> dict:
        """Get reading log entries."""
        log = load_json("reading_log", PROGRESS_DIR)
        entries = log.get("entries", [])

        if not entries:
            return {"message": "No books logged yet. Use log_book to start tracking."}

        if limit:
            entries = entries[-limit:]

        return {
            "total_books": len(log.get("entries", [])),
            "entries": entries
        }

    @mcp.tool()
    def get_progress(period: str = "all") -> dict:
        """Get reading progress summary across all domains."""
        log = load_json("reading_log", PROGRESS_DIR)
        profile = load_json("profile")

        entries = log.get("entries", [])
        domains = profile.get("goals", {}).get("domains", [])

        if not domains:
            return {"error": "No profile found. Run start_interview first."}

        by_domain = {}
        for domain in domains:
            domain_id = domain.get("id")
            domain_entries = [e for e in entries if e.get("domain") == domain_id]

            target = domain.get("target_books", 0)
            completed = len(domain_entries)

            if completed == 0:
                status = "not_started"
            elif target > 0 and completed >= target:
                status = "completed"
            elif target > 0 and completed >= target * 0.5:
                status = "on_track"
            else:
                status = "behind"

            by_domain[domain_id] = {
                "name": domain.get("name"),
                "target": target,
                "completed": completed,
                "status": status,
                "titles": [e.get("title") for e in domain_entries]
            }

        total_target = sum(d.get("target_books", 0) for d in domains)
        total_completed = len(entries)

        update_progress_markdown()

        return {
            "total_books": total_completed,
            "total_target": total_target,
            "by_domain": by_domain,
            "recent": entries[-3:] if entries else [],
            "message": f"You've read {total_completed} books across {len(by_domain)} domains",
            "file": str(PROGRESS_DIR / "_current.md")
        }
