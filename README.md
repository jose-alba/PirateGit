<div align="center">

<img src="docs/assets/pirategit_logo.jpg" alt="PirateGit Logo" width="220" style="border-radius: 16px;">

# 🏴‍☠️ PirateGit

**Don't reinvent the wheel — plunder it.**  
*Multi-channel open-source intelligence, architectural blueprinting & surgical code scavenger skills for AI coding agents.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-brightgreen.svg)](https://python.org)
[![Compatible with: Antigravity & Claude Code](https://img.shields.io/badge/Agents-Antigravity%20%7C%20Claude%20Code%20%7C%20Cursor-orange.svg)](#installation)

</div>

---

## ⚡ The 2 Core Commands

PirateGit adds two high-leverage slash commands powered by specialized subagents to your AI coding assistant (Antigravity, Claude Code, Cursor, Codex):

```text
/explore  ──►  Reconnaissance Fleet: Synthesizes your North Star, dispatches parallel Pirate Scouts
               across GitHub, Topics, HN & Reddit, and runs zero-clone X-rays + DAFO.

/loot     ──►  Plunder & Quality Tribunal: Designs the blueprint, harvests to others/, transplants
               clean code, and runs a Critic + Judge Tribunal to guarantee production readiness.
```

---

## 1. `/explore` — Multi-Agent Scouting & Intelligence

<div align="center">
  <img src="docs/assets/pirate_explore.jpg" alt="PirateGit Explore" width="85%" style="border-radius: 12px; margin: 15px 0;">
</div>

Synthesizes your ultimate objective, deploys a **fleet of parallel scouting subagents** across public platforms, reads candidate READMEs without burning API quota, runs anatomical zero-clone `xray` checks, and returns a ranked **Loot Table** + **SWOT (DAFO)** analysis.

### Chat Syntax
```text
/explore <your goal or feature>
/explore <your goal> --100repos
/explore <your goal> --20repos
```

### Examples
```text
/explore automatic pcb placement in python
/explore markdown parsing with AST and table support --50repos
/explore local rag vector search without external apis --20repos
```

### What You Get in Response:
1. **Target Frame:** Your North Star goal, hard requirements, and discard criteria (red lines).
2. **Fleet Triage Summary:** Breakdown of 50+ repositories scanned across GitHub, Topics, Hacker News, and Reddit.
3. **Ranked Loot Table:** Sorted by composite score, commercial license traffic light (`🟢 Permissive / 🟡 Copyleft / 🔴 No License`), and exact scavengeable assets (datasets, algorithms, prompts, libraries).
4. **Individual SWOT (DAFO) Analysis:** Focused strengths, weaknesses, loot opportunities, and licensing threats for each top repository.

---

## 2. `/loot` — Blueprints, Surgical Transfusion & Quality Tribunal

<div align="center">
  <img src="docs/assets/pirate_loot.jpg" alt="PirateGit Loot" width="85%" style="border-radius: 12px; margin: 15px 0;">
</div>

Takes the intelligence gathered from `/explore`, designs the target project architecture, downloads selected repositories into a local quarantine cache (`others/`), transplants clean data and code step-by-step into your codebase, and subjects all ported code to an **adversarial Quality Tribunal (Critic + Judge)**.

### Chat Syntax
```text
/loot [freeform instructions, preferences, exclusions, or repo targets...]
```

### Examples
```text
# Inherit top recommendations from /explore automatically:
/loot

# Specify exact sources and exclusions:
/loot use the dataset from viaduct and the placement engine from eda-agent, but ignore altium stuff

# Direct to a specific architectural target:
/loot only the stackup json and routing algorithms, adapt them to our src_clean structure
```

### How the Agent Executes `/loot`:
1. **Architectural Alignment:** Validates your project layout and maps which piece of code/data will be scavenged from which repository. Asks for confirmation before modifying files.
2. **Harvest to `others/`:** Downloads candidate repositories or specific subdirectories into a local `others/<repo>` folder (kept in `.gitignore` so your repo stays lightweight).
3. **Surgical Transfusion:**
   - Adapts datasets into your `data/` folder with typed loaders.
   - Refactors core engines: strips proprietary dependencies, cleans imports, applies your coding style, and integrates them into your active codebase.
   - Logs source attribution and license provenance in `projects.md`.
4. **Mandatory Quality Tribunal:**
   - 🕵️ **The Critic Subagent:** Relentlessly audits ported code for license contamination (`GPL` leaks), dead code, zombie dependencies, and architecture drift.
   - ⚖️ **The Judge Subagent:** Reviews findings and issues a formal verdict (`🟢 APPROVED FOR PRODUCTION` or `🟡 NEEDS REFACTORING`) with instant remediation before sign-off.

---

## 🛠️ Standalone Terminal CLI (`pirategit.py`)

You can also run the zero-dependency CLI engine directly from your terminal:

```bash
# 1. Multi-channel search, README triage & composite signal scoring
python scripts/pirategit.py explore "query 1" "query 2" --topics topic-name --50repos

# 2. Anatomical file-tree dissection of repos without cloning
python scripts/pirategit.py xray owner1/repo1 owner2/repo2

# 3. Filter file trees by keyword
python scripts/pirategit.py files owner/repo placement router

# 4. Zero-API-quota file reader (via raw.githubusercontent.com)
python scripts/pirategit.py peek owner/repo path/to/file.py --max-lines 80

# 5. Harvest selective files or full repository ZIP into others/
python scripts/pirategit.py harvest owner/repo --dest others --paths path/to/file.py
```

---

## 🚀 One-Line Installation

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/username/PirateGit/main/install.ps1 | iex
```

### macOS / Linux (Bash)
```bash
curl -fsSL https://raw.githubusercontent.com/username/PirateGit/main/install.sh | bash
```

### Manual Installation
Copy the `skills/` folder into your agent's skills directory:
- **Antigravity / Gemini:** `~/.gemini/config/skills/`
- **Claude Code:** `~/.claude/skills/`

*(Optional)* Set `GITHUB_TOKEN` or `GH_TOKEN` in your environment to raise GitHub's search rate limit from 60 req/hr to 5,000 req/hr.

---

## 📄 License

MIT License — Free for personal and commercial use.
