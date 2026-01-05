"""
Stage 3: Syllabus Builder Tools

Tools for building and managing curated book stacks.
"""

from datetime import datetime

from ..config import BOOKSTACKS_DIR, PROGRESS_DIR
from ..storage import load_json, save_json, load_prompt
from ..markdown import save_bookstack_markdown


def get_reading_history_context() -> dict:
    """
    Gather all reading history context for recommendations.
    Returns a rich context dict with patterns, authors, and connections.
    """
    log = load_json("reading_log", PROGRESS_DIR)
    authors_data = load_json("authors")
    patterns = load_json("patterns")
    connections = load_json("connections")
    profile = load_json("profile")

    entries = log.get("entries", [])

    # Get top authors by affinity
    all_authors = authors_data.get("authors", {})
    favorite_authors = [
        {"name": a["name"], "books": a["total_books"], "rating": a.get("average_rating")}
        for _, a in all_authors.items()
        if a.get("affinity") == "high"
    ]

    avoidances = profile.get("context", {}).get("avoidances", [])

    return {
        "books_read": [
            {
                "title": e.get("title"),
                "author": e.get("author"),
                "domain": e.get("domain"),
                "rating": e.get("rating"),
                "had_reflection": e.get("reflection") is not None
            }
            for e in entries
        ],
        "total_books": len(entries),
        "favorite_authors": favorite_authors,
        "patterns": patterns.get("patterns", {}),
        "themes_loved": patterns.get("patterns", {}).get("themes_loved", []),
        "themes_avoided": [{"theme": a, "reason": "stated avoidance"} for a in avoidances],
        "connections": connections.get("connections", []),
        "clusters": connections.get("clusters", [])
    }


def register_syllabus_tools(mcp):
    """Register syllabus builder tools with the MCP server."""

    @mcp.tool()
    def build_bookstack(domain: str) -> dict:
        """
        Build a curated reading stack for a specific domain.

        Args:
            domain: The domain ID to build a stack for (e.g., "classic_lit").

        Returns the syllabus builder prompt with user context.
        After generating recommendations, call save_bookstack to persist them.
        """
        profile = load_json("profile")
        if not profile:
            return {"error": "No profile found. Run start_interview first."}

        prompt = load_prompt("syllabus_builder")

        # Find the matching domain
        domain_goal = None
        for d in profile.get("goals", {}).get("domains", []):
            if d.get("id") == domain:
                domain_goal = d
                break

        if not domain_goal:
            available = [d.get("id") for d in profile.get("goals", {}).get("domains", [])]
            return {
                "error": f"Domain '{domain}' not found in profile",
                "available_domains": available
            }

        reading_history = get_reading_history_context()

        return {
            "instruction": f"Create a curated book stack for the '{domain}' domain",
            "prompt": prompt,
            "domain": domain,
            "goal": domain_goal,
            "preferences": profile.get("preferences", {}),
            "context": profile.get("context", {}),
            "latent_features": profile.get("latent_features", {}),
            "reading_history": reading_history
        }

    @mcp.tool()
    def save_bookstack(domain: str, books: list[dict], description: str = None) -> dict:
        """
        Save a curated book stack for a domain.

        Args:
            domain: The domain ID this stack belongs to
            books: List of book recommendations
            description: Optional description of what this stack will achieve
        """
        stacks = load_json("bookstacks")

        if "stacks" not in stacks:
            stacks = {"version": "1.0", "stacks": {}}

        stack_data = {
            "generated_at": datetime.now().isoformat(),
            "description": description,
            "books": books
        }

        stacks["stacks"][domain] = stack_data
        save_json("bookstacks", stacks)

        # Get domain name for markdown
        profile = load_json("profile")
        domain_name = None
        for d in profile.get("goals", {}).get("domains", []):
            if d.get("id") == domain:
                domain_name = d.get("name")
                break

        save_bookstack_markdown(domain, stack_data, domain_name)

        return {
            "status": "saved",
            "domain": domain,
            "book_count": len(books),
            "titles": [b.get("title") for b in books],
            "file": str(BOOKSTACKS_DIR / f"{domain}.md")
        }

    @mcp.tool()
    def get_bookstacks(domain: str = None) -> dict:
        """Get all book stacks, or a specific domain's stack."""
        stacks = load_json("bookstacks")
        if not stacks.get("stacks"):
            return {"message": "No bookstacks yet. Use build_bookstack to create some."}

        if domain:
            if domain in stacks["stacks"]:
                return {domain: stacks["stacks"][domain]}
            else:
                return {
                    "error": f"No stack found for '{domain}'",
                    "available": list(stacks["stacks"].keys())
                }

        return stacks

    @mcp.tool()
    def get_next_book(domain: str = None) -> dict:
        """Get the next recommended book to read."""
        stacks = load_json("bookstacks")
        log = load_json("reading_log", PROGRESS_DIR)

        if not stacks.get("stacks"):
            return {"message": "No bookstacks yet. Use build_bookstack first."}

        completed = [e.get("title", "").lower() for e in log.get("entries", [])]

        for stack_domain, stack_data in stacks.get("stacks", {}).items():
            if domain and stack_domain != domain:
                continue

            for book in stack_data.get("books", []):
                if book.get("title", "").lower() not in completed:
                    return {
                        "domain": stack_domain,
                        "book": book,
                        "message": f"Next up in {stack_domain}"
                    }

        return {
            "message": "All books in stacks completed! Time to refresh recommendations.",
            "suggestion": "Use build_bookstack to add more books"
        }

    @mcp.tool()
    def add_book_to_stack(
        domain: str,
        title: str,
        author: str,
        why: str = None,
        difficulty: str = "moderate"
    ) -> dict:
        """Manually add a book to an existing stack."""
        stacks = load_json("bookstacks")

        if "stacks" not in stacks:
            stacks = {"version": "1.0", "stacks": {}}

        if domain not in stacks["stacks"]:
            stacks["stacks"][domain] = {
                "generated_at": datetime.now().isoformat(),
                "books": []
            }

        current_books = stacks["stacks"][domain].get("books", [])
        position = len(current_books) + 1

        new_book = {
            "title": title,
            "author": author,
            "why": why or "Manually added",
            "difficulty": difficulty,
            "position": position,
            "added_at": datetime.now().isoformat()
        }

        stacks["stacks"][domain]["books"].append(new_book)
        save_json("bookstacks", stacks)

        # Update markdown
        profile = load_json("profile")
        domain_name = None
        for d in profile.get("goals", {}).get("domains", []):
            if d.get("id") == domain:
                domain_name = d.get("name")
                break

        save_bookstack_markdown(domain, stacks["stacks"][domain], domain_name)

        return {
            "status": "added",
            "domain": domain,
            "book": title,
            "position": position,
            "total_in_stack": len(stacks["stacks"][domain]["books"])
        }
