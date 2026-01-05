"""
Author & Pattern Analysis Tools

Tools for analyzing reading patterns, managing author profiles, and book connections.
"""

from datetime import datetime

from ..config import PROGRESS_DIR, AUTHORS_DIR
from ..storage import load_json, save_json, slugify
from ..markdown import save_author_markdown, update_authors_index, save_patterns_markdown


def register_pattern_tools(mcp):
    """Register pattern analysis tools with the MCP server."""

    @mcp.tool()
    def analyze_reading_patterns() -> dict:
        """
        Analyze your reading history to identify patterns.

        Examines your completed books to find:
        - Themes you gravitate toward
        - Difficulty levels that work best
        - Reading pace insights
        - Author preferences

        Results are saved and used for smarter recommendations.
        """
        log = load_json("reading_log", PROGRESS_DIR)
        authors_data = load_json("authors")
        profile = load_json("profile")

        entries = log.get("entries", [])

        if len(entries) < 2:
            return {
                "message": "Need at least 2 books logged to analyze patterns.",
                "books_logged": len(entries),
                "suggestion": "Log more books with log_book to enable pattern analysis"
            }

        # Analyze ratings by domain
        domain_ratings = {}
        for entry in entries:
            domain = entry.get("domain", "other")
            rating = entry.get("rating")
            if rating:
                if domain not in domain_ratings:
                    domain_ratings[domain] = []
                domain_ratings[domain].append(rating)

        # Calculate average ratings per domain
        themes_loved = []
        for domain, ratings in domain_ratings.items():
            avg = round(sum(ratings) / len(ratings), 1)
            themes_loved.append({
                "theme": domain.replace("_", " ").title(),
                "frequency": len(ratings),
                "avg_rating": avg
            })

        themes_loved.sort(key=lambda x: (-x["avg_rating"], -x["frequency"]))

        # Analyze author preferences
        all_authors = authors_data.get("authors", {})
        repeat_authors = [
            a["name"] for _, a in all_authors.items()
            if a.get("total_books", 0) >= 2
        ]
        high_affinity_authors = [
            a["name"] for _, a in all_authors.items()
            if a.get("affinity") == "high"
        ]

        # Get avoidances from profile
        avoidances = profile.get("context", {}).get("avoidances", [])
        themes_avoided = [{"theme": a, "reason": "stated avoidance"} for a in avoidances]

        patterns = {
            "version": "1.0",
            "analyzed_at": datetime.now().isoformat(),
            "patterns": {
                "themes_loved": themes_loved,
                "themes_avoided": themes_avoided,
                "difficulty_sweet_spot": {
                    "preferred": "moderate",
                    "success_rate_by_difficulty": {}
                },
                "pacing_insights": {
                    "total_books": len(entries),
                    "books_with_reflections": len([e for e in entries if e.get("reflection")])
                },
                "author_preferences": {
                    "repeat_authors": repeat_authors,
                    "high_affinity": high_affinity_authors,
                    "total_authors": len(all_authors)
                }
            }
        }

        save_json("patterns", patterns)
        save_patterns_markdown(patterns)

        return {
            "status": "analyzed",
            "message": f"Analyzed {len(entries)} books across {len(domain_ratings)} domains",
            "patterns": patterns["patterns"],
            "file": str(PROGRESS_DIR / "_insights.md"),
            "suggestion": "These patterns will now inform your book recommendations"
        }

    @mcp.tool()
    def get_author_profile(author: str) -> dict:
        """
        Get or create a profile for an author.

        Args:
            author: Author name (e.g., "Leo Tolstoy")

        Returns author data including books read, ratings, and notes.
        """
        authors_data = load_json("authors")
        author_slug = slugify(author)

        if "authors" not in authors_data:
            authors_data = {"version": "1.0", "authors": {}}

        if author_slug in authors_data["authors"]:
            author_entry = authors_data["authors"][author_slug]
            return {
                "found": True,
                "author": author_entry,
                "file": str(AUTHORS_DIR / f"{author_slug}.md")
            }
        else:
            return {
                "found": False,
                "message": f"No books logged from {author} yet",
                "suggestion": f"Log a book by {author} with log_book to create their profile"
            }

    @mcp.tool()
    def update_author_notes(
        author: str,
        style_notes: dict = None,
        your_notes: str = None
    ) -> dict:
        """
        Update notes about an author's style and your impressions.

        Args:
            author: Author name
            style_notes: Dictionary with keys like:
                - prose: Description of writing style
                - themes: List of common themes
                - strengths: What they do well
                - comparable_to: Similar authors
            your_notes: Your personal notes about this author
        """
        authors_data = load_json("authors")
        author_slug = slugify(author)

        if "authors" not in authors_data or author_slug not in authors_data.get("authors", {}):
            return {
                "error": f"Author '{author}' not found",
                "suggestion": "Log a book by this author first"
            }

        author_entry = authors_data["authors"][author_slug]

        if style_notes:
            existing = author_entry.get("style_notes", {})
            for key, value in style_notes.items():
                if isinstance(value, list) and isinstance(existing.get(key), list):
                    existing[key] = list(set(existing[key] + value))
                else:
                    existing[key] = value
            author_entry["style_notes"] = existing

        if your_notes:
            author_entry["your_notes"] = your_notes

        save_json("authors", authors_data)
        save_author_markdown(author_slug, author_entry)

        return {
            "status": "updated",
            "author": author,
            "style_notes": author_entry.get("style_notes"),
            "your_notes": author_entry.get("your_notes"),
            "file": str(AUTHORS_DIR / f"{author_slug}.md")
        }

    @mcp.tool()
    def get_favorite_authors(limit: int = 10) -> dict:
        """
        Get your favorite authors ranked by affinity.

        Args:
            limit: Maximum number of authors to return (default 10)
        """
        authors_data = load_json("authors")
        all_authors = authors_data.get("authors", {})

        if not all_authors:
            return {
                "message": "No authors tracked yet",
                "suggestion": "Log books with log_book to start building author profiles"
            }

        affinity_order = {"high": 0, "medium": 1, "low": 2, "unknown": 3}

        sorted_authors = sorted(
            all_authors.items(),
            key=lambda x: (
                affinity_order.get(x[1].get("affinity", "unknown"), 3),
                -(x[1].get("average_rating") or 0),
                -x[1].get("total_books", 0)
            )
        )[:limit]

        result = []
        for _, data in sorted_authors:
            result.append({
                "name": data.get("name"),
                "books_read": data.get("total_books", 0),
                "average_rating": data.get("average_rating"),
                "affinity": data.get("affinity", "unknown"),
                "last_read": data.get("last_read", "")[:10] if data.get("last_read") else None
            })

        return {
            "total_authors": len(all_authors),
            "top_authors": result,
            "file": str(AUTHORS_DIR / "_index.md")
        }

    @mcp.tool()
    def add_book_connection(
        from_book: str,
        to_book: str,
        relationship: str,
        reason: str,
        strength: str = "moderate"
    ) -> dict:
        """
        Add a connection between two books for future recommendations.

        Args:
            from_book: Title of the first book
            to_book: Title of the second book
            relationship: Type of connection:
                - "similar_theme": Similar themes or topics
                - "complements": Different angles on same topic
                - "next_step": Natural progression from first to second
                - "contrast": Interesting contrast/counterpoint
            reason: Why these books are connected
            strength: "strong" | "moderate" | "weak"
        """
        connections = load_json("connections")

        if "connections" not in connections:
            connections = {"version": "1.0", "connections": [], "clusters": []}

        for conn in connections["connections"]:
            if conn.get("from") == from_book and conn.get("to") == to_book:
                conn["relationship"] = relationship
                conn["reason"] = reason
                conn["strength"] = strength
                conn["updated_at"] = datetime.now().isoformat()
                save_json("connections", connections)
                return {
                    "status": "updated",
                    "message": f"Updated connection: {from_book} → {to_book}"
                }

        new_connection = {
            "from": from_book,
            "to": to_book,
            "relationship": relationship,
            "reason": reason,
            "strength": strength,
            "created_at": datetime.now().isoformat()
        }

        connections["connections"].append(new_connection)
        save_json("connections", connections)

        return {
            "status": "added",
            "message": f"Connected: {from_book} → {to_book} ({relationship})",
            "connection": new_connection,
            "total_connections": len(connections["connections"])
        }

    @mcp.tool()
    def get_similar_books(title: str) -> dict:
        """
        Find books connected to one you've read.

        Args:
            title: Title of a book you've read

        Returns books that are connected to this one.
        """
        connections = load_json("connections")
        stacks = load_json("bookstacks")

        if not connections.get("connections"):
            return {
                "message": "No book connections recorded yet",
                "suggestion": "Use add_book_connection to link related books"
            }

        related = []
        for conn in connections.get("connections", []):
            if conn.get("from", "").lower() == title.lower():
                related.append({
                    "book": conn.get("to"),
                    "relationship": conn.get("relationship"),
                    "reason": conn.get("reason"),
                    "direction": "leads_to"
                })
            elif conn.get("to", "").lower() == title.lower():
                related.append({
                    "book": conn.get("from"),
                    "relationship": conn.get("relationship"),
                    "reason": conn.get("reason"),
                    "direction": "leads_from"
                })

        all_stack_books = []
        for _, stack in stacks.get("stacks", {}).items():
            for book in stack.get("books", []):
                all_stack_books.append(book.get("title", "").lower())

        for item in related:
            item["in_stack"] = item["book"].lower() in all_stack_books

        if not related:
            return {
                "message": f"No connections found for '{title}'",
                "suggestion": "Use add_book_connection to link this to related books"
            }

        return {
            "book": title,
            "connected_books": related,
            "total": len(related)
        }
