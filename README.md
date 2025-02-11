# 👻 repoGhost

`repoGhost` is a command-line tool to scan a local code repository, split files into chunks, and summarize each chunk using an LLM (e.g., GPT-4o). Summaries are stored in a dedicated `summary` directory, and repeated runs skip unchanged files to save cost.

## Features

- **Hash-based caching**: Skips unchanged files (no repeated LLM calls).
- **Auto `.gitignore`**: Automatically adds the summary directory to `.gitignore` if found.
- **Dedicated Summary Directory**: Creates a `summary` folder for all outputs.
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

### Parameters

- `--repo_path`: Optional path to the local repo (defaults to current directory).
- `--lines_per_chunk`: Lines per chunk for summarizing (default `30`).
- `--context-size, -c`: Controls the snippet size extracted from files. The default value is 8192 characters, but users can set it higher up to a maximum of 32768. If an unsupported value (e.g., negative or too large) is supplied, the application exits with an error message.
- `--api-key`: Provide the OpenAI API key. If not provided, the tool checks the OPENAI_API_KEY environment variable or the config file at ~/.repoghostconfig.json.

### Example

```bash
# Analyze current directory
repoGhost

# Analyze specific directory with custom chunk size
repoGhost /path/to/project --lines_per_chunk 50

# Analyze specific directory with custom context size
repoGhost /path/to/project -c 16384
```

This generates a summary directory containing:
- `hash_cache.json`: Contains file hashes and chunk summaries (used to skip unchanged files).
- `summaries.json`: Contains all chunk summaries (the final output).

The last chunk’s summary is copied to your clipboard automatically.

## API Key Configuration

The tool will look for your OpenAI API key in the following order:
 1. Via the command-line argument `--api-key`.
 2. Via the environment variable `OPENAI_API_KEY`.
 3. Via a configuration file located at `~/.repoghostconfig.json`.

If no API key is found, the tool will exit with an error message. This allows you to avoid passing the API key every time you run the command.

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
    "summary",  # Excludes the summary directory itself
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
    temperature=0.1,
    max_tokens=1000
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
