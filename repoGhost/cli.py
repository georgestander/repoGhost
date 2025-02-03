import os
import json
import argparse
import pyperclip
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.text import Text
import hashlib
import sys
import datetime

# Initialize rich console
console = Console()

# Constants
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

HASH_CACHE_FILE = "hash_cache.json"   # Stores file-level hashes and old summaries
SUMMARIES_OUTPUT = "summaries.json"   # Final combined summaries

def valid_source_file(file_path):
    """
    Check if the file is a valid source file based on its extension and name.
    """
    _, ext = os.path.splitext(file_path)
    filename = os.path.basename(file_path)
    
    return (
        ext.lower() in VALID_EXTENSIONS
        and ext.lower() not in EXCLUDED_EXTENSIONS
        and filename not in EXCLUDED_FILES
    )

def scan_repo(repo_path):
    """
    Recursively walk the repo and return a list of valid source file paths.
    Skips excluded directories and files.
    """
    file_paths = []
    try:
        for root, dirs, files in os.walk(repo_path):
            # Filter directories
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            
            for f in files:
                fp = os.path.join(root, f)
                if valid_source_file(fp):
                    file_paths.append(fp)
    except Exception as e:
        console.print(f"[red]Error during repository scan: {str(e)}[/red]")
    
    return file_paths

def chunk_file(file_path, lines_per_chunk=50):
    """
    Splits the file content into chunks of N lines.
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.readlines()

    chunks = []
    for i in range(0, len(content), lines_per_chunk):
        chunk_lines = content[i:i+lines_per_chunk]
        chunks.append("".join(chunk_lines))
    return chunks

def calculate_file_hash(file_path):
    """
    Compute a hash (SHA-256) for the file content.
    """
    hasher = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        console.print(f"[red]Error reading file for hashing: {file_path} - {e}[/red]")
        return None

def load_hash_cache():
    """
    Load existing hash/summaries from HASH_CACHE_FILE, if exists.
    Returns a dict: { file_path: { 'hash': <str>, 'summaries': [ {chunk_id, summary} ... ] } }
    """
    if not os.path.exists(HASH_CACHE_FILE):
        return {}
    try:
        with open(HASH_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        console.print(f"[red]Error loading hash cache from file {HASH_CACHE_FILE}[/red]")
        return {}

def save_hash_cache(cache_data):
    """
    Save hash cache to file.
    """
    with open(HASH_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=2)

def summarize_chunk(chunk, progress=None):
    """
    Summarize a code chunk using OpenAI's GPT-4o model.
    Assumes OPENAI_API_KEY is set in environment variables.
    """
    from openai import OpenAI
    import os
    
    client = OpenAI()  # Uses OPENAI_API_KEY from environment by default
    
    try:
        if progress:
            progress.update(progress.task_ids[-1], description="[yellow]🤔 Analyzing with AI...[/yellow]")
        
        completion = client.chat.completions.create(
            model="gpt-4o",  
            store=True,  # Store the completion
            messages=[
                {
                    "role": "user",
                    "content": f"Please summarize this code chunk concisely:\n\n{chunk}"
                }
            ]
        )
        
        return completion.choices[0].message.content.strip()
    except Exception as e:
        error_msg = f"Error summarizing chunk: {str(e)}"
        console.print(f"[red]❌ {error_msg}[/red]")
        return error_msg

def generate_repo_map(repo_path, max_depth=5):
    """
    Generate hierarchical repository structure with depth limiting
    """
    repo_map = {
        'name': os.path.basename(repo_path),
        'type': 'directory',
        'path': '.',
        'children': []
    }
    
    def traverse(current_path, node, current_depth=0):
        if current_depth >= max_depth:
            return
        try:
            with os.scandir(current_path) as entries:
                for entry in entries:
                    if entry.name in EXCLUDED_DIRS:
                        continue
                    
                    if entry.is_dir():
                        child = {
                            'name': entry.name,
                            'type': 'directory',
                            'path': os.path.relpath(entry.path, repo_path),
                            'children': []
                        }
                        node['children'].append(child)
                        traverse(entry.path, child, current_depth + 1)
                    elif valid_source_file(entry.path):
                        node['children'].append({
                            'name': entry.name,
                            'type': 'file',
                            'path': os.path.relpath(entry.path, repo_path)
                        })
        except Exception as e:
            console.print(f"[yellow]⚠️ Directory traversal error: {str(e)}[/yellow]")
    
    traverse(repo_path, repo_map)
    return repo_map

def process_repository(repo_path):
    """
    Process the repository at the given path.
    This contains the main logic previously in the main() function.
    """
    console.print(Panel.fit(
        Text("🚀 Repository Summarizer", justify="center", style="bold cyan"),
        subtitle="Let's make your code talk to some LLMs!"
    ))
    
    # Ensure we have an absolute path
    repo_path = os.path.abspath(repo_path)
    
    # Load the existing hash cache to skip unchanged files
    hash_cache = load_hash_cache()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        # Scan repository task
        scan_task = progress.add_task("[cyan]🔍 Scanning repository...", total=None)
        files = scan_repo(repo_path)
        progress.update(scan_task, total=1, completed=1)
        console.print(f"[green]✨ Found {len(files)} source files to analyze![/green]")
        
        overall_task = progress.add_task("[cyan]📝 Processing files...", total=len(files))
        combined_summaries = []
        
        for f in files:
            file_task = progress.add_task(
                f"[yellow]Processing {os.path.basename(f)}...",
                total=1
            )

            # Calculate current file hash
            current_hash = calculate_file_hash(f)
            old_hash_data = hash_cache.get(f, {})
            old_hash = old_hash_data.get("hash")
            old_summaries = old_hash_data.get("summaries", [])

            if current_hash and current_hash == old_hash:
                # File unchanged => reuse old summaries
                progress.update(file_task, description="[green]Skipping unchanged file[/green]")
                for s in old_summaries:
                    combined_summaries.append({
                        "file": f,
                        "chunk_id": s["chunk_id"],
                        "summary": s["summary"]
                    })
            else:
                # File changed or not in cache => re-summarize
                chunks = chunk_file(f, lines_per_chunk=30)
                new_summaries = []
                for idx, chunk_content in enumerate(chunks):
                    chunk_task = progress.add_task(
                        f"[blue]Analyzing chunk {idx+1}/{len(chunks)}...",
                        total=1
                    )
                    summary = summarize_chunk(chunk_content, progress)
                    new_summaries.append({"chunk_id": idx, "summary": summary})
                    combined_summaries.append({
                        "file": f,
                        "chunk_id": idx,
                        "summary": summary
                    })
                    progress.update(chunk_task, completed=1)
                    progress.remove_task(chunk_task)

                # Update hash_cache after summarizing
                hash_cache[f] = {
                    "hash": current_hash,
                    "summaries": new_summaries
                }
            
            progress.update(file_task, completed=1)
            progress.remove_task(file_task)
            progress.update(overall_task, advance=1)

        # Generate repository structure
        repo_structure = generate_repo_map(repo_path)
        
        # Create combined output structure
        combined_output = {
            "repository_map": repo_structure,
            "file_summaries": combined_summaries,
            "metadata": {
                "generated_at": datetime.datetime.now().isoformat(),
                "max_depth": 5,
                "repo_ghost_version": "1.1" 
            }
        }

        # Save combined output
        with open(SUMMARIES_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(combined_output, f, indent=2)

        # Save the updated hash cache
        save_hash_cache(hash_cache)

        # Copy the latest summary to the clipboard
        if combined_summaries:
            latest_summary = combined_summaries[-1]["summary"]
            pyperclip.copy(latest_summary)
            console.print("\n[bold green]📋 Latest summary has been copied to your clipboard![/bold green]")
            preview = latest_summary[:200] + "..." if len(latest_summary) > 200 else latest_summary
            console.print(Panel(preview))
        else:
            console.print("[red]⚠️ No summaries generated or found.[/red]")

def main():
    parser = argparse.ArgumentParser(
        description="Summarize a local repo's code in chunked form."
    )
    parser.add_argument(
        "repo_path",
        type=str,
        nargs='?',
        default=os.getcwd(),
        help="Path to the local repository you want to summarize (default: current directory)."
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Verify path exists
    if not os.path.exists(args.repo_path):
        console.print(f"[red]Error: Path does not exist: {args.repo_path}[/red]")
        sys.exit(1)
    
    if not os.path.isdir(args.repo_path):
        console.print(f"[red]Error: Path is not a directory: {args.repo_path}[/red]")
        sys.exit(1)
    
    process_repository(args.repo_path)

if __name__ == "__main__":
    main()
