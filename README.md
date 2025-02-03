# 👻 repoGhost

`repoGhost` is a command-line tool to scan a local code repository, split files into chunks, and summarize each chunk using an LLM (e.g., GPT-4o). Summaries are stored in `summaries.json`, and repeated runs skip unchanged files to save cost.

## Features

- **Hash-based caching**: Skips unchanged files (no repeated LLM calls).
- **Auto `.gitignore`**: Automatically adds the cache and summary files to `.gitignore` if found.
- **Clipboard**: Copies the last summary to your clipboard for easy reference.
- **Configurable chunk size**: Choose how many lines per chunk.
- **Repository Map**: Generates a hierarchical view of your repository structure at the top of the summary.
- **CWD Defaults**: Defaults to analyzing the current working directory if no path is specified.

## Installation

```bash
pip install repoGhost
```

## Usage

Simply run in your project directory:
```bash
repoGhost
```

Or specify a different repository path:
```bash
repoGhost /path/to/your/repo
```

### Command-Line Arguments
- `--repo_path`: Optional path to the local repo (defaults to current directory).
- `--lines_per_chunk`: Lines per chunk for summarizing (default `30`).

### Example

```bash
# Analyze current directory
repoGhost

# Analyze specific directory with custom chunk size
repoGhost /path/to/project --lines_per_chunk 50
```

This generates two files in the specified repo path:
- `hash_cache.json`: Contains file hashes and chunk summaries (used to skip unchanged files).
- `summaries.json`: Contains all chunk summaries (the final output).

The last chunk’s summary is copied to your clipboard automatically.

## Constants

In the code, the following constants can be modified to suit your needs:

```python
EXCLUDED_DIRS = {
    "migrations",
    "static",
    "media",
    "__pycache__",
    ".git",
    "venv",
    "node_modules",
}
EXCLUDED_EXTENSIONS = {
    ".pyc", ".css", ".scss", ".png", ".jpg", ".jpeg", ".svg", ".sqlite3"
}
EXCLUDED_FILES = {"manage.py", "wsgi.py", "asgi.py", "package-lock.json"}
VALID_EXTENSIONS = {".py", ".js", ".html", ".json"}
```

Feel free to **add or remove** items based on the files you want to skip or process.

## Customizing the Prompt & Model

Inside the script, the `summarize_chunk` function calls an OpenAI model:

```python
openai.ChatCompletion.create(
    model="gpt-4o",  # or your custom model name
    messages=[
        {"role": "user", "content": f"Please summarize this code chunk concisely:\n\n{chunk}"}
    ],
    temperature=0.3,
    max_tokens=150
)
```

You can **modify**:
- The `model` parameter (e.g., `gpt-3.5-turbo`, `gpt-4`, `gpt-4o-mini`, etc.).
- The prompt text (if you want a different style of summary).
- The `temperature` or `max_tokens` values.

## OpenAI API Key

You need an `OPENAI_API_KEY` set in your environment variables for the script to call OpenAI’s API. For instance:

```bash
export OPENAI_API_KEY="sk-1234..."
```

Then run:

```bash
repoGhost --repo_path /path/to/repo
```

## Requirements

See `requirements.txt`. Python 3.7+ recommended.

- `openai`
- `pyperclip`
- `rich`

## Development / Local Install

1. Clone this repo:
   ```bash
   git clone https://github.com/georgestander/repoGhost.git
   cd repoGhost
   ```
2. Install in editable mode:
   ```bash
   pip install -e .
   ```
3. Verify the CLI is installed:
   ```bash
   repoGhost --help
   ```

## License

MIT License.
