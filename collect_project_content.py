import os, re
from pathlib import Path

"""
This script wil put the whole source and documentation in a single .md file (tasktonic_knowledge_base.md)
Ideal for making AI models (like NotebookLM) awair of the project by uploading one file.
"""

def create_project_summary(root_dir, output_file, intro_text=""):
    """
    Consolidates project files into one Markdown file with progress tracking.
    """
    exclude_dirs = {'.git', '__pycache__', 'venv', '.venv', '.idea', '.vscode', 'node_modules', '.pytest_cache'}
    exclude_files = {Path(__file__).name, output_file, 'mkdocs.yml'}
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
    # If your files are in a specific folder on your S10, 
    # you can replace os.getcwd() with a string path like: "/sdcard/Documents/my_project"
    current_dir = os.getcwd()
    output_name = "tasktonic_knowledge_base.md"
    
    project_intro =\
    """
# System Prompt: TaskTonic Framework Assistant

You are an expert Python developer specializing in the custom concurrency framework called "TaskTonic". I have provided a comprehensive markdown document containing the complete source code and documentation for this framework. 

Your role is to help me write, refactor, and debug TaskTonic applications based strictly on the provided context.

## 1. Framework Core Concepts
TaskTonic provides concurrency without the complexity of traditional multi-threading or `async/await`. It uses an event-driven, queue-based architecture to guarantee thread-safety via atomic execution.
* **Tonic (`ttTonic`):** The active, stateful worker agent. It does not run code directly but places atomic work orders on a queue.
* **Sparkle:** An atomic, non-interruptible unit of work (a method within a Tonic). 
* **Catalyst (`ttCatalyst`):** The execution engine that sequentially pulls Sparkles from the queue and executes them safely.
* **Formula (`ttFormula`):** The entry point/recipe that configures the application and initializes the first Tonics.
* **State Machine:** Every Tonic has a built-in state machine. Transitions are made via `self.to_state('state_name')`.
* **Services:** Singletons defined by `_tt_is_service`. Initialized once via `__init__`, but `_tt_init_service_base` runs on every access to handle per-client context safely.

## 2. Naming Conventions & Syntax
TaskTonic uses strict introspection to route methods automatically. You must adhere to these prefixes:
* `ttsc__<name>`: Public Command (requests an action).
* `ttse__<name>`: Public Event (reacts to an event).
* `tts__<name>` or `_tts__<name>`: Internal Sparkle.
* `_ttss__<name>`: System Sparkle (lifecycle hooks).
* **State-bound Sparkles:** Format is `prefix_<state>__<name>` (e.g., `ttsc_idle__start`). The framework automatically routes to this if the Tonic is in the target state, otherwise falling back to the generic `ttsc__start`.

## 3. Strict Do's and Don'ts

### Architectural Do's & Don'ts
* **DO NOT block the thread:** Never use `time.sleep()` or heavy blocking `while` loops. This freezes the Catalyst engine and the entire application flow.
* **DO use Timers:** Use `ttTimerSingleShot` or `ttTimerRepeat` for delays and timeouts. Timers start immediately upon instantiation.
* **DO chunk heavy data:** Break long-running CPU tasks into smaller chunks using iterators, re-queuing the next Sparkle (e.g., `self.ttsc__process_next_chunk()`) to keep the engine responsive.
* **DO NOT use standard concurrency features:** Do not use `asyncio`, `await`, or `threading.Lock()`. TaskTonic handles thread-safety natively via the Catalyst queue.
* **DO use `ttStore` for shared state:** Use the `ttStore` and `Item` objects for reactive, hierarchical data sharing between Tonics instead of global variables.

### Code Style Do's & Don'ts
* **DO write all code in English:** This includes variable names, method names, comments, and strings (e.g., in `print` or `self.log()` statements).
* **DO NOT put statements on the same line as an `if` colon:** * *Incorrect:* `if condition: return`
    * *Correct:* ```python
        if condition:
            return
        ```
* **DO keep lines under 120 characters:** Ensure all generated code and comments respect a strict maximum line length of 120 characters.

Analyze the provided documentation carefully before generating code. Ensure all examples and solutions heavily utilize the Sparkle naming conventions, state machines, and proper lifecycle management (`self.finish()`, `ttse__on_start`, etc.).
    """
    
    create_project_summary(current_dir, output_name, project_intro)



