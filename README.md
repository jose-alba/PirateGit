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

/loot     ──►  Architecture & Quality Tribunal: Designs or forks baseline project structure, harvests
               to others/, transplants clean code into src/, assets/ & tests/, and runs Critic + Judge.
```

---

## 📂 100% Self-Contained Skill Architecture

Each skill is completely decoupled and self-contained with its own executable scripts inside its folder:

```text
PirateGit/
├── skills/
│   ├── explore/
│   │   ├── SKILL.md                  # Reconnaissance protocol
│   │   └── scripts/
│   │       ├── explore.py            # 4-channel search & DeepGit scoring
│   │       ├── xray.py               # Zero-clone anatomical tree inspection
│   │       ├── peek.py               # Zero-quota file reader
│   │       └── lib/                  # Shared client, scoring, and channel helpers
│   │
│   └── loot/
│       ├── SKILL.md                  # Architecture, baseline adoption, harvesting & tribunal protocol
│       └── scripts/
│           ├── harvest.py            # Quarantine downloader into others/
│           ├── files.py              # File-tree path filter
│           ├── peek.py               # Zero-quota file reader
│           └── lib/                  # Shared client, scoring, and tree helpers
│
├── docs/assets/                      # Badges, logo, and illustrations
├── install.ps1 / install.sh          # One-line cross-platform installers
├── README.md
└── LICENSE
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

## 2. `/loot` — Blueprints, Baseline Adoption & Quality Tribunal

<div align="center">
  <img src="docs/assets/pirate_loot.jpg" alt="PirateGit Loot" width="85%" style="border-radius: 12px; margin: 15px 0;">
</div>

Takes the intelligence gathered from `/explore`, establishes or aligns the target architecture, harvests selected repositories into a local quarantine cache (`others/`), transplants clean data and code step-by-step into your codebase, and subjects all ported code to an **adversarial Quality Tribunal (Critic + Judge)**.

### Empty Workspace? Fast-Track Baseline Adoption
If your project is empty or greenfield and one of the explored repositories already has a solid, battle-tested architecture matching your goal:
- `/loot` proposes adopting that repository as the **Architectural Baseline**.
- Extracts its structural foundation into standard industry layout:
  - `src/`: Core domain logic, engines, models, and interfaces.
  - `tests/`: Unit and integration test suites.
  - `assets/` (or `data/`): Curated datasets, fixtures, and schemas.
- Then prunes unneeded modules and transplants superior algorithms from other candidates.

### Chat Syntax
```text
/loot [freeform instructions, preferences, exclusions, or repo targets...]
```

### Examples
```text
# Inherit top recommendations from /explore automatically:
/loot

# Greenfield project: adopt repoA structure as baseline and transplant repoB engines:
/loot empty project, adopt repoA architecture as baseline and port repoB algorithms into src/

# Specify exact sources and exclusions:
/loot use the dataset from viaduct and the placement engine from eda-agent, but ignore altium stuff

# Direct to a specific architectural target:
/loot only the stackup json and routing algorithms, adapt them to our src layout with assets/ and tests/
```

### How the Agent Executes `/loot`:
1. **Architectural Alignment & Baseline Selection:** Evaluates your workspace, proposes standard `src/`, `tests/`, `assets/` layout (or baseline adoption), and maps code/data sources. Asks for confirmation before modifying files.
2. **Harvest to `others/`:** Downloads candidate repositories or specific subdirectories into a local `others/<repo>` folder (kept in `.gitignore` so your repo stays lightweight).
3. **Surgical Transfusion:**
   - Adapts datasets into `assets/` (or `data/`) with typed loaders.
   - Refactors core engines into `src/`: strips proprietary dependencies, cleans imports, applies your coding style, and adds unit tests in `tests/`.
   - Logs source attribution and license provenance in `projects.md`.
4. **Mandatory Quality Tribunal:**
   - 🕵️ **The Critic Subagent:** Relentlessly audits ported code for license contamination (`GPL` leaks), dead code, zombie dependencies, and architecture drift.
   - ⚖️ **The Judge Subagent:** Reviews findings and issues a formal verdict (`🟢 APPROVED FOR PRODUCTION` or `🟡 NEEDS REFACTORING`) with instant remediation before sign-off.

---

## 🛠️ Direct Terminal CLI Usage

Because each script is a standalone Python stdlib utility, you can also run them directly from your terminal:

```bash
# 1. Multi-channel search, README triage & composite signal scoring
python skills/explore/scripts/explore.py "query 1" "query 2" --topics topic-name --50repos

# 2. Anatomical file-tree dissection of repos without cloning
python skills/explore/scripts/xray.py owner1/repo1 owner2/repo2

# 3. Read specific files with zero API quota
python skills/explore/scripts/peek.py owner/repo path/to/file.py --max-lines 80

# 4. Filter repository paths by keywords
python skills/loot/scripts/files.py owner/repo placement router

# 5. Harvest selective files or full repository ZIP into others/
python skills/loot/scripts/harvest.py owner/repo --dest others --paths path/to/file.py
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

### Manual Installation (Drop into any project)
Simply copy the `skills/explore` and `skills/loot` folders directly into any project's `.agents/skills/` directory:

```text
MyProject/
└── .agents/
    └── skills/
        ├── explore/       # 👈 Self-contained, works out of the box
        └── loot/          # 👈 Self-contained, works out of the box
```

---

## 📄 License

MIT License — Free for personal and commercial use.
