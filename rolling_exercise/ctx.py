from pathlib import Path

# Add individual files or entire folders to this list
PATHS_TO_CONCATENATE = [
    "calculate_aqi.py",
    "database.py",  
    "main.py",
    "models.py",
    "schemas.py",
    "routers",
    "tools",
    "logger.py",
    "tests"                
]

OUTPUT_FILE = "output.txt"

# File patterns or folder names you want to skip (optional)
IGNORE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}


def collect_file_paths(paths_list):
    """Resolves directories into individual files."""
    files_to_process = []

    for path_str in paths_list:
        path = Path(path_str)

        if not path.exists():
            print(f"Skipped (does not exist): {path}")
            continue

        if path.is_file():
            files_to_process.append(path)
        elif path.is_dir():
            # Recursively iterate through all files inside the directory
            for item in sorted(path.rglob("*")):
                # Skip directories themselves and ignored folders
                if item.is_file() and not any(part in IGNORE_DIRS for part in item.parts):
                    files_to_process.append(item)

    return files_to_process


def concatenate_paths(input_paths, output_path):
    files = collect_file_paths(input_paths)

    with open(output_path, "w", encoding="utf-8") as outfile:
        for path in files:
            # Header format separating each file
            outfile.write(f"\n{'=' * 80}\n")
            outfile.write(f"FILE: {path}\n")
            outfile.write(f"{'=' * 80}\n\n")

            try:
                content = path.read_text(encoding="utf-8", errors="replace")
                outfile.write(content)
                if not content.endswith("\n"):
                    outfile.write("\n")
                print(f"Added: {path}")

            except Exception as e:
                outfile.write(f"[ERROR reading file {path}: {e}]\n\n")
                print(f"Error reading {path}: {e}")

    print(f"\nDone! Processed {len(files)} files into: {output_path}")


if __name__ == "__main__":
    concatenate_paths(PATHS_TO_CONCATENATE, OUTPUT_FILE)