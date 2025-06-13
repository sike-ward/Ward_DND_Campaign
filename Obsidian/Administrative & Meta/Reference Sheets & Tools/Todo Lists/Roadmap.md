# 🎯 Obsidian Lore Assistant: Master Roadmap & Checklist

---

## Phase 1: Preparation and Setup (Infrastructure)
- [x] Install Obsidian  
  - [x] Create your main campaign “Vault”  
  - [x] Establish initial folder structure  
- [x] Set up GitHub repository  
  - [x] Sign up or log in to GitHub  
  - [x] Create a private repository (e.g. `DND_Campaign_Lore`)  
  - [x] Connect your Obsidian vault to GitHub for automatic backups  

## Phase 2: Create Document Templates
- [ ] Decide core document types (NPCs, Locations, History Events, Magic Items, etc.)  
- [ ] Ask ChatGPT for each template in Markdown  
  - e.g. “Give me an NPC profile template.”  
- [ ] Copy each template into Obsidian as a new template file  

## Phase 3: Initial Lore Content Creation
- [ ] List initial lore priorities (key kingdoms, cities, NPCs, events)  
- [ ] For each, prompt ChatGPT for draft content  
  - e.g. “Write lore for the City of Emberhaven…”  
- [ ] Save drafts into the appropriate folders using your templates  

## Phase 4: Establish Naming & Tagging Conventions
- [ ] Select and finalize naming conventions  
  - e.g. `NPC_[Region]_[Name]`, `Loc_[Name]`, `Quest_[Name]`  
- [ ] Choose tagging standards (`#npc`, `#location`, `#lore`, etc.)  
- [ ] Document conventions in Obsidian (e.g. `Campaign Standards.md`)  

## Phase 5: AI-Assisted Document Management
- [x] Sign up for OpenAI API access  
- [x] Choose retrieval tool (LlamaIndex)  
- [x] Integrate your Obsidian documents  
  - [x] Set up Python environment  
  - [x] Install LlamaIndex  
  - [x] Index Markdown files from your vault  
- [x] Integrate GPT-4o via LlamaIndex (ask/summarize/propose links)  

## Phase 6: Visual & Interactive Layer (Optional)
- [ ] Sign up for World Anvil or Campfire  
- [ ] Import or sync foundational lore docs  
- [ ] Create initial maps, timelines, and visual aids  

## Phase 7: Collaboration & Logging Tools
- [ ] Choose Notion or Airtable (for sessions, NPCs, player notes)  
- [ ] Set up basic databases and link back to Obsidian  

## Phase 8: Maintenance & Optimization
- [ ] Schedule regular (monthly) reviews  
- [ ] Use ChatGPT to identify redundant/duplicate content  
- [ ] Archive or refactor old/irrelevant documents  

---

## Browse-Tab & UI Improvements
- [ ] **Editable Note Preview** (not just read-only)  
- [ ] Scrollable edit history in “Browse” pane  
- [ ] Clear, contextual status messages  
- [ ] Polished formatting (fonts, spacing, colors)  
- [ ] **Drag-and-Drop** support (e.g. images, maps into notes)  
- [ ] Advanced note-editing features (Ctrl+S to save, autosave, undo/redo)  
- [ ] AI-powered actions in Browse:  
  - [ ] Ctrl+G: Summarize current folder  
  - [ ] Ctrl+L: Propose links for selected note  
  - [ ] Ctrl+T: Jump to “Tokens” tab  

---

## Recommended Additional Tabs
- [ ] **Dashboard**  
  - At-a-glance: next session date, recently updated notes, quick links  
- [ ] **Session Manager**  
  - Live DM log, session notes, “flag” items for follow-up  
- [ ] **Player Management**  
  - Character roster, attendance, private player notes  
- [ ] **Initiative/Combat Tracker**  
  - Initiative order, HP/conditions tracker  
- [ ] **Calendar/Time Tracker**  
  - In-world calendar, moon phases, countdown to events  
- [x] **Timeline/History** (built-in)  
- [x] **Random Generator** (built-in)  
- [x] **Campaign Settings** (built-in)  
- [ ] **Import/Export/Backup**  
- [ ] **AI Prompt Workshop** (save & edit custom prompts)  
- [ ] **Quick Reference** (house rules, cheat sheets)  
- [ ] **Encounter Builder** (AI-assisted)  
- [ ] **Image/Map Gallery**  
- [ ] **Player Handout Manager**  
- [ ] **Feedback/Help** (bug reports, docs, support link)  

🔷 Phase 0: Prep & Hygiene
Version Control & Backups

Ensure your project is in Git (or your VCS of choice).

Commit your current “working” prototype as v0-prototype.

Push to a remote (GitHub, GitLab, etc.) so you have an off-site backup.

Virtual Environment & Dependencies

Create a clean venv or Conda env pinned to Python 3.11+.

Generate a requirements.txt or use Poetry/Poetry’s pyproject.toml for your deps (customtkinter, llama_index, openai, etc.).

Lock your versions (pip freeze > requirements.txt).

Project Structure Baseline

Draft your future directory layout (e.g. src/gui/, src/ai/, src/storage/, tests/).

Move your current files into src/ and update imports (you can stub __init__.py to avoid import errors).

Code Style & Tooling

Add a .flake8 or pyproject.toml with Black/Flake8/Isort settings.

Install pre-commit and enable hooks for formatting and linting on each commit.

Basic Test Harness

Create a tests/ folder with one smoke test (e.g., instantiate LoreMainApp and call a no-op method).

Add a CI config (GitHub Actions) that installs your env, runs pytest and flake8.

Documentation Stub

Create a README.md with:

Quick install (git clone, pip install -r requirements.txt)

How to launch (python main.py)

High-level module map (where gui, ai_engine, utils, etc. live).

Once Phase 0 is in place, you’ll have:

A safe rollback point

A reproducible environment

Enforced code quality checks

A test harness catching regressions

Clarity on where files belong



Refactor Plan: Phase-by-Phase
🔹 Phase 1: Storage Abstraction
Create storage.py with BaseStorage interface.

Implement ObsidianStorage.

Wire your app to use storage.list_notes() / storage.read_note() instead of raw file I/O.
Why first? All other modules depend on where data comes from.

🔹 Phase 2: Modularize the GUI
Split gui.py into packages:

browse/ (browse tab UI + controller)

ask/ (Ask AI tab)

session/, etc.

Move all CTk layout calls into view_*.py and event logic into controller_*.py.

Have each controller depend only on storage and LoreAI.

🔹 Phase 3: Introduce Persistent State
Add SQLite via SQLAlchemy / Peewee.

Migrate your in-memory lists (note metadata, session logs) into tables.

Build a “Vault watcher” with watchdog to sync external edits.

🔹 Phase 4: Background Tasks & Responsiveness
Turn AI calls and indexing into background threads or asyncio tasks.

Add progress bars and “Cancel” buttons for long jobs.

🔹 Phase 5: Testing & CI
Write unit tests for storage.py, utils.py, and ai_engine.py (mock OpenAI).

Add integration tests that spin up a temp vault and exercise browse & AI features.

Configure GitHub Actions to run linting, tests, and builds on every push.

🔹 Phase 6: Packaging & Deployment (MVP)
Choose a packager (PyInstaller / Briefcase / Tauri).

Automate builds for Windows/macOS/Linux in CI.

Bundle a simple installer or AppImage for friends to download.

🔹 Phase 7: Polish & Commercial-Grade Enhancements
Auto-updates + code signing.

Robust error handling & logging.

Detailed docs (in-app guide + online).

Telemetry & support channels.

How to Remember & Stay on Track
One file to rule them all: create REFACTOR_PLAN.md at your project root with the phases above.

Kanban or project board: move each checklist item into a Trello/GitHub Project column (“To Do” → “In Progress” → “Done”).

Daily stand-up reminder: pick one task per day—even 30 min of work on “Phase 1.1: Define BaseStorage” moves you forward.

Version branches: for each phase, create a Git branch (phase-1-storage, phase-2-modularize, etc.) so you can freely refactor without fear.

By attacking one small phase at a time, you’ll keep momentum and avoid the me

