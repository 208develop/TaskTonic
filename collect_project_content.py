import os, re
from pathlib import Path

"""
This script wil put the whole source and documentation in a single .md file (ttContext.md)
Ideal for making AI models (like NotebookLM) awair of the project by uploading one file.
"""


def create_project_summary(root_dir, output_file, intro_text=""):
    """
    Consolidates project files into one Markdown file with progress tracking.
    """
    exclude_dirs = {'.git', '.github', '__pycache__', 'venv', '.venv', '.idea', '.vscode',
                    'node_modules', '.pytest_cache', 'TaskTonic.egg-info', 'build', 'dist'}
    exclude_files = {Path(__file__).name, output_file, 'mkdocs.yml', 'py_to_test_stuf_and_trow_away.py'}
    valid_extensions = {'.py', '.md', '.json', '.yaml', '.yml', '.toml', '.ini', '.txt'}

    sensitive_patterns = [
        r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"].+['\"]",
        r"(?i)(api_key|apikey|secret|token)\s*[:=]\s*['\"].+['\"]",
        r"(?i)bearer\s+[a-zA-Z0-9\-\._~+/]+=*",
    ]

    redaction_log = []
    processed_count = 0

    def redact_sensitive_info(content, file_path):
        new_content = content
        for pattern in sensitive_patterns:
            matches = re.findall(pattern, new_content)
            if matches:
                for match in matches:
                    redaction_log.append(f"File: {file_path} - Match found: '{match[:20]}...'")
                new_content = re.sub(pattern, "[REDACTED: Sensitive information removed]", new_content)
        return new_content

    print(f"--- Starting Scan in: {root_dir} ---")

    with open(output_file, 'w', encoding='utf-8') as outfile:
        # 1. Introduction
        if intro_text:
            outfile.write("# Introduction\n")
            outfile.write(f"{intro_text}\n\n")
            outfile.write("---\n\n")

        # 2. Directory Structure
        print("[1/2] Generating directory tree...")
        outfile.write("# Project Structure\n\n")
        outfile.write("```text\n")
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            level = root.replace(root_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            outfile.write(f"{indent}{os.path.basename(root)}/\n")
            sub_indent = ' ' * 4 * (level + 1)
            for f in files:
                if any(f.endswith(ext) for ext in valid_extensions):
                    outfile.write(f"{sub_indent}{f}\n")
        outfile.write("```\n\n---\n\n")

        # 3. File Contents
        print("[2/2] Processing file contents:")
        outfile.write("# File Contents\n\n")
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            # Print current directory being scanned to terminal
            relative_root = os.path.relpath(root, root_dir)
            if relative_root != ".":
                print(f"  Scanning folder: {relative_root}")

            for file in files:
                if any(file.endswith(ext) for ext in valid_extensions) and file not in exclude_files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, root_dir)

                    print(f"    + Adding file: {relative_path}")
                    outfile.write(f"## `File: {relative_path}`\n")

                    ext = os.path.splitext(file)[1][1:].lower()
                    syntax_map = {
                        'py': 'python', 'md': 'markdown', 'json': 'json',
                        'yaml': 'yaml', 'yml': 'yaml', 'toml': 'toml', 'ini': 'ini'
                    }
                    syntax = syntax_map.get(ext, "text")

                    if syntax != 'markdown': outfile.write(f"```{syntax}\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f_content:
                            raw_content = f_content.read()
                            safe_content = redact_sensitive_info(raw_content, relative_path)
                            outfile.write(safe_content)
                            processed_count += 1
                    except Exception as e:
                        print(f"    ! Error reading {relative_path}: {e}")
                        outfile.write(f"Error reading file: {e}")
                    if syntax != 'markdown': outfile.write("\n```\n\n")

    # Add the Security Report to the top
    if redaction_log:
        print(f"--- Found {len(redaction_log)} sensitive items. Redacting... ---")
        with open(output_file, 'r+', encoding='utf-8') as f:
            content = f.read()
            f.seek(0, 0)
            log_header = "# Security Report (Redaction Log)\n"
            log_header += f"> Action: {len(redaction_log)} items redacted for safety.\n\n"
            for entry in redaction_log:
                log_header += f"* {entry}\n"
            log_header += "\n---\n\n"
            f.write(log_header + content)

    print(f"\n--- Success! ---")
    print(f"Total files processed: {processed_count}")
    print(f"Output saved to: {output_file}")


if __name__ == "__main__":
    current_dir = os.getcwd()
    output_name = "ttContext.md"

    project_intro = \
        """
        # System Prompt: TaskTonic Framework Assistant
        
        You are an expert Python developer specializing in the TaskTonic concurrency framework. Your goal is to help write, refactor, and debug TaskTonic applications. You must base all your code and architectural decisions strictly on the provided documentation and source code in `ttContext.md`.
        
        ## 1. Core Concepts
        * **Tonic (`ttTonic`):** Stateful worker agent; places atomic work orders on a queue.
        * **Sparkle:** Atomic, non-interruptible unit of work (a method).
        * **Catalyst (`ttCatalyst`):** Execution engine; pulls Sparkles from the queue sequentially.
        * **Formula (`ttFormula`):** Entry point; configures the app and initializes Tonics.
        * **State Machine:** Built-in transitions via `self.to_state('state_name')`.
        * **Services:** Singletons defined by `_tt_is_service`.
        
        ## 2. Naming Conventions & Syntax Reference
        
        | Prefix | Type | Role |
        | :--- | :--- | :--- |
        | `ttsc__` | Command | Public request for an action |
        | `ttse__` | Event | Reactive trigger (e.g., timer, init) |
        | `tts__`  | Internal | Private logic for chunking tasks |
        | `_ttss__`| System | Lifecycle hooks |
        | `p_s__n` | State-bound | `prefix_state__name` (e.g., `ttsc_idle__start`) |
        | `ttqt__` | Specials | Use special sparkle when integrating a module (like PySide6)  |
        
        ## 3. Framework Best Practices (Must-Follow)
        
        | Category | Rule |
        | :--- | :--- |
        | **Concurrency** | NEVER block threads (`time.sleep`, heavy loops). Use `ttTimer` instead. |
        | **Concurrency** | NO `asyncio`, `await`, or `threading.Lock`. TaskTonic is natively safe. |
        | **Concurrency** | If true multi-threading is required, spawn a dedicated ttCatalyst that runs in its own thread. Use this for blocking system calls or heavy CPU-bound tasks to keep the Main Catalyst responsive. |
        | **Data** | Use `ttStore` and `Item` objects for reactive, shared state and data. |
        | **State depending** | Use state machine transitions via `self.to_state('state_name')`, not all kinds of flags |
        | **State depending** | Don't se state machines when you don't need them, there not mandatory |
        | **Performance** | Chunk heavy CPU tasks into smaller Sparkles using iterators. |
        | **Code Style** | English only (variables, methods, comments, logs). |
        | **Formatting** | Line length: Strictly under 120 characters. |
        
        Analyze the documentation carefully. Ensure all solutions heavily utilize Sparkle naming conventions, state machine transitions, and proper lifecycle management (e.g., `self.finish()`, `ttse__on_start`).
        """
    create_project_summary(current_dir, output_name, project_intro)
