# 🧠 Ward_DND_AI: Core System Planning

## 🎯 Product Goal

Ward_DND_AI is a desktop-first personal AI toolset for D&D campaigns, starting as a solo vault assistant and evolving into a full AI-powered campaign engine.

- Built first for solo Dungeon Masters
- Expands to support co-DM, full DM automation, and multiplayer
- Long-term target: integrate or replace tools like Obsidian or D&D Beyond
- Enables solo play, collaborative prep, and AI-driven sessions

---

## 🧱 Core Systems Blueprint

| System               | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| VaultManager         | Reads, loads, manages world content and notes                        |
| PromptPlanner        | Builds dynamic prompts from session context and user input           |
| WorldMemoryEngine    | Tracks persistent facts, characters, factions, events                |
| SceneRunner          | Generates and narrates scenes using AI                               |
| DialogueAgent        | Handles NPC dialogue, reactions, and decisions                       |
| RuleEngine           | Enforces game rules and resolves turns/actions                       |
| ActionResolver       | Calculates outcomes and dice logic                                   |
| PersonaCore          | Maintains NPC motivation, memory, consistency                        |
| SaveManager          | Stores and loads full session state and world state                  |
| PluginLoader         | Loads user-made extensions for rules, tools, or modules              |

---

## 🛠️ Suggested Build Order

### 🔹 PHASE 1: Personal Vault + AI Co-DM
1. VaultManager
2. PromptPlanner
3. WorldMemoryEngine
4. SceneRunner

### 🔹 PHASE 2: AI Simulation
5. DialogueAgent
6. RuleEngine
7. ActionResolver
8. PersonaCore

### 🔹 PHASE 3: Expansion + Persistence
9. SaveManager
10. PluginLoader

---

## 🖥️ UI / Interface Layer

Each system has minimal UI:

| UI Component        | Connects to           | When it's built        |
|---------------------|------------------------|-------------------------|
| File browser        | VaultManager           | Phase 1 start           |
| Chat input/output   | PromptPlanner, SceneRunner | Phase 1            |
| Note preview/editor | VaultManager           | Phase 1                 |
| Memory inspector    | WorldMemoryEngine      | Phase 1-2               |
| NPC/Scene pane      | DialogueAgent          | Phase 2                 |
| Dice/action log     | ActionResolver         | Phase 2                 |
| Turn tracker        | RuleEngine             | Phase 2                 |
| Plugin dropdown     | PluginLoader           | Phase 3                 |

---

## 🔒 Security + 🕸️ Networking

| Concern              | Recommendation                                           |
|----------------------|-----------------------------------------------------------|
| Local mode           | Fully offline, no network required                        |
| API use              | Secure API keys via .env                                  |
| Multiplayer (future) | Use WebSocket or REST sync only after core works          |
| Plugin safety        | Optional sandbox or trust-based plugin model              |
