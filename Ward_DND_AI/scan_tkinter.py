import os

# File extensions to scan
FILE_EXTENSIONS = {".py"}

# Keywords to search for
KEYWORDS = [
    "import tkinter",
    "from tkinter",
    "import customtkinter",
    "from customtkinter",
    "tkinter.",
    "customtkinter.",
]


def scan_files(root_dir):
    issues = []
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in FILE_EXTENSIONS):
                filepath = os.path.join(subdir, file)
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        for kw in KEYWORDS:
                            if kw in line:
                                issues.append((filepath, i, line.strip()))
    return issues


if __name__ == "__main__":
    import sys

    root = sys.argv[1] if len(sys.argv) > 1 else "."
    found = scan_files(root)
    if not found:
        print("No tkinter or customtkinter usage found.")
    else:
        print("Found tkinter/customtkinter usage:")
        for filepath, line_no, line in found:
            print(f"{filepath}:{line_no}: {line}")
