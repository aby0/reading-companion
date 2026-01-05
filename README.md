# Reading Companion

A 4-stage reading companion that helps you set goals, discover books, track progress, and deepen learning through reflection.

Works as an MCP (Model Context Protocol) server integrated with Claude Desktop.

## The 4 Stages

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   STAGE 1    │     │   STAGE 2    │     │   STAGE 3    │
│ Interviewer  │ ──▶ │   Context    │ ──▶ │   Syllabus   │
│              │     │   Builder    │     │   Builder    │
│ "Who are you │     │  "Extract    │     │ "Build your  │
│  as a reader"│     │   patterns"  │     │  book stacks"│
└──────────────┘     └──────────────┘     └──────────────┘
       │                                          │
       │              ┌──────────────┐            │
       └────────────▶ │   STAGE 4    │ ◀──────────┘
                      │  Reflection  │
                      │   Partner    │
                      │              │
                      │ "What did    │
                      │  you learn?" │
                      └──────────────┘
```

1. **Interviewer** - Builds your reading profile through conversation
2. **Context Builder** - Extracts deeper patterns from your profile
3. **Syllabus Builder** - Creates curated book stacks for each domain
4. **Reflection Partner** - Helps process books and track growth

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install reading-companion
```

Or with uv:
```bash
uv pip install reading-companion
```

### Option 2: Install from Source

```bash
git clone https://github.com/aby0/reading-companion
cd reading-companion
pip install -e .
```

### Configure Claude Desktop

Add to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "reading-companion": {
      "command": "reading-companion"
    }
  }
}
```

Restart Claude Desktop. You should see "Reading Companion" in the MCP servers list (hammer icon).

### Prerequisites

- Python 3.10+
- Claude Desktop

## Usage

### Initial Setup (Do Once)

**Step 1: Run the Interview**
```
You: "Interview me for my reading goals"
```
Claude will ask about your goals, preferences, and context. At the end, your profile is saved.

**Step 2: Extract Context (Optional)**
```
You: "Analyze my reading profile"
```
Claude extracts deeper patterns to improve recommendations.

**Step 3: Build Your Book Stacks**
```
You: "Build me a reading stack for classic literature"
```
Get curated book recommendations for each domain.

### Ongoing Use

**Log a completed book:**
```
You: "I just finished Anna Karenina by Tolstoy"
```

**Reflect on a book:**
```
You: "I want to reflect on Anna Karenina"
```

**Check progress:**
```
You: "How's my reading progress?"
```

**Get next recommendation:**
```
You: "What should I read next?"
```

**Add a book manually:**
```
You: "Add 'War and Peace' to my classic lit stack"
```

## Available Tools

### Stage 1: Interviewer
| Tool | Description |
|------|-------------|
| `start_interview` | Begin the reading goal interview |
| `save_profile` | Save interview results as profile |
| `get_profile` | View current profile |

### Stage 2: Context Builder
| Tool | Description |
|------|-------------|
| `extract_context` | Analyze profile for deeper patterns |
| `update_latent_features` | Save extracted features |

### Stage 3: Syllabus Builder
| Tool | Description |
|------|-------------|
| `build_bookstack` | Generate recommendations for a domain |
| `save_bookstack` | Save generated book stack |
| `get_bookstacks` | View all book stacks |
| `get_next_book` | Get next unread book |
| `add_book_to_stack` | Manually add a book |

### Stage 4: Reflection
| Tool | Description |
|------|-------------|
| `log_book` | Quick log a completed book |
| `start_reflection` | Begin deep reflection session |
| `save_reflection` | Save reflection insights |
| `get_reading_log` | View reading history |
| `get_progress` | Get progress summary |

### Author & Pattern Analysis
| Tool | Description |
|------|-------------|
| `analyze_reading_patterns` | Analyze your reading history for patterns |
| `get_author_profile` | View profile for an author you've read |
| `update_author_notes` | Add style notes about an author |
| `get_favorite_authors` | List your top authors by affinity |
| `add_book_connection` | Link related books together |
| `get_similar_books` | Find books connected to one you've read |

## Data Storage

All your reading data is stored in `~/reading-companion-data/` (separate from the code):

```
~/reading-companion-data/
├── profile.md                    # Your profile (human-readable)
├── profile.json                  # Profile data (system)
├── bookstacks.json               # All stacks data (system)
├── authors.json                  # Author tracking (system)
├── patterns.json                 # Reading patterns (system)
├── connections.json              # Book connections (system)
│
├── bookstacks/                   # Book recommendations
│   ├── _index.md                 # Overview of all stacks
│   ├── classic_lit.md            # One file per domain
│   └── neuroscience.md
│
├── progress/                     # Progress tracking
│   ├── _current.md               # Current status with progress bars
│   ├── _insights.md              # Reading pattern insights
│   └── reading_log.json          # Structured log (system)
│
├── authors/                      # Author profiles
│   ├── _index.md                 # All authors by affinity
│   ├── leo-tolstoy.md            # One file per author
│   └── james-clear.md
│
└── reflections/                  # Book reflections
    ├── _index.md                 # Index of all books read
    ├── anna-karenina.md          # One file per book
    └── atomic-habits.md
```

**Key feature**: All `.md` files are human-readable and can be opened in VS Code, Obsidian, or any text editor.

## Customization

### Prompts

The prompts that guide each stage are in the `reading_companion/prompts/` directory:

- `interviewer.md` - How interviews are conducted
- `context_builder.md` - How profiles are analyzed
- `syllabus_builder.md` - How books are curated
- `reflection.md` - How reflections are guided

Feel free to customize these to match your preferences.

### Domains

You can have any reading domains you want - they're not hardcoded. During the interview, define whatever areas interest you:
- Classic Literature
- Science Fiction
- Neuroscience
- Philosophy
- Engineering
- History
- Whatever you're curious about!

## Principles

- **Intentional over random** - Every book serves a purpose
- **Learning over consuming** - Reflection matters as much as reading
- **Progress over perfection** - Steady beats ambitious
- **Personal over popular** - What fits YOU, not bestseller lists

## Troubleshooting

**"Reading Companion not appearing in Claude Desktop"**
- Check that the path in `claude_desktop_config.json` is correct
- Restart Claude Desktop
- Check the MCP logs for errors

**"No profile found"**
- Run `start_interview` first to create your profile

**"Domain not found"**
- Check your domain ID matches what's in your profile
- Use `get_profile` to see available domains

## Development

To run the server directly for testing:
```bash
uv run server.py
```

To test with the MCP inspector:
```bash
npx @modelcontextprotocol/inspector uv run server.py
```

## License

MIT
