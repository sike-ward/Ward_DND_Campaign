import os
import re


def make_title_case_filename(text):
    text = text.strip().replace(" ", "_")
    text = re.sub(r"[^a-zA-Z0-9_\-]", "", text)
    text = "_".join(word.capitalize() for word in text.split("_") if word)
    return text[:50]


def get_note_names(vault_path):
    note_names = set()
    for folder_root, dirs, files in os.walk(vault_path):
        for fname in files:
            if fname.endswith(".md"):
                base = os.path.splitext(fname)[0]
                note_names.add(base)
    return note_names


def auto_link_notes(text, note_names):
    for name in sorted(note_names, key=len, reverse=True):
        pattern = r"\b" + re.escape(name) + r"\b"
        text = re.sub(pattern, f"[[{name}]]", text, flags=re.IGNORECASE)
    return text


def get_all_folders(vault_path):
    folders = []
    for folder_root, dirs, files in os.walk(vault_path):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for d in dirs:
            full_path = os.path.relpath(os.path.join(folder_root, d), vault_path)
            folders.append(full_path)
    folders.insert(0, "")
    return sorted(folders)


# ─── utils.py ─── Markdown highlighter ────────────────────────────────


# map :icon_name: → emoji
ICON_MAP = {
    "warning": "⚠️",
    "info": "ℹ️",
    "star": "⭐",
    "check": "✅",
    # …add more here
}


def highlight_markdown(text_widget):
    import re

    # get the real tk.Text inside CTkTextbox, or fallback to widget itself
    tv = getattr(text_widget, "_textbox", text_widget)

    # 1) clear all existing tags
    for tag in tv.tag_names():
        tv.tag_remove(tag, "1.0", "end")
    content = tv.get("1.0", "end-1c")

    # 2) Headings (#–######)
    for m in re.finditer(r"^(#{1,6})\s*(.+)$", content, flags=re.MULTILINE):
        lvl = len(m.group(1))
        start = f"1.0+{m.start(2)}c"
        end = f"1.0+{m.end(2)}c"
        tv.tag_add(f"heading{lvl}", start, end)

    # 3) Bold **text**
    for m in re.finditer(r"\*\*(.+?)\*\*", content):
        s = f"1.0+{m.start(1)}c"
        e = f"1.0+{m.end(1)}c"
        tv.tag_add("bold", s, e)

    # 4) Italic *text*
    for m in re.finditer(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", content):
        s = f"1.0+{m.start(1)}c"
        e = f"1.0+{m.end(1)}c"
        tv.tag_add("italic", s, e)

    # 5) Inline code `code`
    for m in re.finditer(r"`([^`]+?)`", content):
        s = f"1.0+{m.start(1)}c"
        e = f"1.0+{m.end(1)}c"
        tv.tag_add("code", s, e)

    # 6) Blockquotes > text
    for m in re.finditer(r"^(>\s+.+)$", content, flags=re.MULTILINE):
        s = f"1.0+{m.start(1)}c"
        e = f"1.0+{m.end(1)}c"
        tv.tag_add("blockquote", s, e)

    # 7) Lists (-, *, +)
    for m in re.finditer(r"^(?:[-\*\+])\s+(.+)$", content, flags=re.MULTILINE):
        s = f"1.0+{m.start(1)}c"
        e = f"1.0+{m.end(1)}c"
        tv.tag_add("list", s, e)

    # 8) Links [text](url)
    for m in re.finditer(r"\[([^\]]+)\]\([^)]+\)", content):
        s = f"1.0+{m.start(1)}c"
        e = f"1.0+{m.end(1)}c"
        tv.tag_add("link", s, e)

    # 9) Icons :icon_name:
    repls = []
    for m in re.finditer(r":(\w+):", content):
        name = m.group(1)
        if name in ICON_MAP:
            repls.append((m.start(), m.end(), ICON_MAP[name]))
    offset = 0
    for a, b, emoji in repls:
        s = f"1.0+{a+offset}c"
        e = f"1.0+{b+offset}c"
        tv.configure(state="normal")
        tv.delete(s, e)
        tv.insert(s, emoji, ("icon",))
        offset += len(emoji) - (b - a)
        tv.configure(state="disabled")

    # 10) Configure tag styles
    tv.tag_configure("bold", font=("Consolas", 12, "bold"))
    tv.tag_configure("italic", font=("Consolas", 12, "italic"))
    tv.tag_configure(
        "code", font=("Consolas", 12), background="#2e3440", foreground="#88c0d0"
    )
    tv.tag_configure(
        "blockquote", font=("Consolas", 12, "italic"), foreground="#657b83"
    )
    tv.tag_configure("list", foreground="#d8dee9")
    tv.tag_configure("link", foreground="#81a1c1", underline=True)
    tv.tag_configure("icon", font=("Consolas", 12))
    for lvl, (size, color) in enumerate(
        [
            (20, "#bf616a"),
            (18, "#d08770"),
            (16, "#ebcb8b"),
            (14, "#a3be8c"),
            (13, "#88c0d0"),
            (12, "#5e81ac"),
        ],
        start=1,
    ):
        tv.tag_configure(
            f"heading{lvl}", font=("Consolas", size, "bold"), foreground=color
        )
