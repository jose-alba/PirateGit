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
               across GitHub, Topics, HN & Reddit, and runs zero-clone X-rays + Unified Loot & SWOT Table.

/loot     ──►  Architecture, Black-Box & Quality Tribunal: Adopts baseline or black-box modules, harvests
               to others/, transplants clean code into src/, assets/ & tests/, and runs Critic + Judge.
```

---

## 1. `/explore` — Multi-Agent Scouting & Intelligence

<div align="center">
  <img src="docs/assets/pirate_explore.jpg" alt="PirateGit Explore" width="85%" style="border-radius: 12px; margin: 15px 0;">
</div>

Synthesizes your ultimate objective, deploys a **fleet of parallel scouting subagents** across public platforms, reads candidate READMEs without burning API quota, runs anatomical zero-clone `xray` checks, and returns a single **Unified Loot & SWOT (DAFO) Table** followed by an **Architectural Reference Strategy**.

### Core Exploration Principles:
- **Zero License Red Lines for Prototyping:** Copyleft (`GPL`, `AGPL`, `MPL`) and unlicensed repos are **never** discarded or penalized. All code can be scavenged for rapid prototyping, tracking origin via docstrings to plan Clean-Room rewrites only if monetizing.
- **Utility Over Fame:** Star counts and popularity don't drive rankings. A 2-star repo with the exact mathematical algorithm or parser is prioritized over a 40k-star generic wrapper.

### Chat Syntax
```text
/explore                                  # Context-aware: reads current repo & finds similar projects
/explore <your goal or feature>           # Scans 100 repositories by default
/explore <your goal> --150repos           # Override default scope
/explore <your goal> --50repos
```

### Examples
```text
/explore automatic pcb placement in python
/explore markdown parsing with AST and table support
/explore local rag vector search without external apis --50repos
```

### What You Get in Response:
1. **Target Frame:** Your North Star goal, hard technical requirements (runtime, stack, headless pipeline), and real technical red lines (without license/star bias).
2. **Multi-Angle Expansion & Fleet Triage:** Expands queries across 3 vectors (Direct Synonyms, Lateral Domains, Subsystems/Internal Parts) and reviews candidate repositories across GitHub, Topics, Hacker News, and Reddit.
3. **Unified Loot & SWOT (DAFO) Table:** A single, consolidated evaluation table combining:
   - `Repo` (markdown link)
   - `Puntuación y estrellas` (e.g. `0.92 | ⭐ 15`)
   - `Qué hace (idea rápida)` (concise summary)
   - `Debilidades` (technical caveats, bloat, missing tests)
   - `Fortalezas` (algorithmic excellence, modularity, speed)
   - `Oportunidades` (direct value injected to the North Star)
   - `Amenazas` (technical risks or license replacement note if commercializing)
   - `Qué vamos a aprovechar (en texto)` (conceptual component breakdown)
   - `Qué vamos a aprovechar (en código)` (exact file paths, classes, and functions identified via `xray`)
4. **Architectural Reference Strategy:** Concrete guidance for `/loot` deciding whether to adopt a top repo as baseline structure, integrate full modules as black boxes, or design a custom architecture from scratch.

---

## 2. `/loot` — Blueprints, Black-Box Subsystems & Quality Tribunal

<div align="center">
  <img src="docs/assets/pirate_loot.jpg" alt="PirateGit Loot" width="85%" style="border-radius: 12px; margin: 15px 0;">
</div>

Takes the intelligence gathered from `/explore`, establishes the target architecture, harvests selected repositories into a local quarantine cache (`others/`), stages files for burn-down, transplants clean code into your codebase, and subjects everything to an **adversarial Quality Tribunal (Critic + Judge)**.

### Architectural Flexibility:
- **Baseline Adoption (Greenfield):** If starting from scratch and a candidate has a battle-tested layout, adopt it as the **Architectural Baseline** and prune/modify on top.
- **Black-Box Subsystem Integration:** If an explored repository or package already solves an entire subsystem with high quality and decoupling (e.g. subtitle renderer, audio ducking, format demuxer), **keep it intact as a black box** (e.g. in `src/modules/<subsystem>/`). Do not reinvent or rewrite working code; consume it cleanly via typed adapters.
- **Surgical Transfusion:** Transplant individual algorithms, schemas, or datasets directly into `src/` or `assets/`.

### Chat Syntax
```text
/loot [freeform instructions, preferences, exclusions, or repo targets...]
```

### Examples
```text
# Inherit top recommendations from /explore automatically:
/loot

# Greenfield project: adopt repoA structure as baseline and port repoB engines:
/loot empty project, adopt repoA architecture as baseline and port repoB algorithms into src/

# Black-box subsystem reuse:
/loot use repoA subtitle engine as black-box in src/modules/subtitles, and transplant repoB shaders

# Specify exact sources and exclusions:
/loot use the dataset from viaduct and the placement engine from eda-agent, but ignore altium stuff
```

### How the Agent Executes `/loot`:
1. **Architectural Alignment & Zero-Args Inference:** Automatically inherits top candidate repositories and identified loot from `/explore` (or interprets user-specified exclusions).
2. **Harvest (`others/`) & Stage (`staging/`):** Downloads candidate repositories into quarantine (`others/`) and stages only the specific files selected for integration into a temporary `staging/` work queue.
3. **Progressive Burn-Down Transfusion (`staging/` $\rightarrow$ `src/`):**
   - Transfuses one staged file at a time into `src/` or `assets/` with clean architecture and unit tests in `tests/`.
   - The minitool (`stage.py complete`) automatically stamps the `[PIRATEGIT LOOT PROVENANCE]` block into the code, logs it in `projects.md`, and burns down (deletes) the file from `staging/`.
4. **Mandatory Quality Tribunal:**
   - 🕵️ **The Critic Subagent:** Verifies that all unit tests pass, zero dead dependencies remain, and `staging/` is 100% burned down (empty).
   - ⚖️ **The Judge Subagent:** Reviews findings and outputs the **Loot Provenance Inventory Table** (Origin, License, Production Status) and signs off (`🟢 PROVENANCE AUDITED & READY FOR EXPERIMENTATION`).

---

## ⚡ Quick Install (100% Zero-Dependency Python Stdlib)

```powershell
# Windows (PowerShell)
irm https://raw.githubusercontent.com/jose-alba/PirateGit/main/install.ps1 | iex
```

```bash
# macOS & Linux (Bash)
curl -fsSL https://raw.githubusercontent.com/jose-alba/PirateGit/main/install.sh | bash
```

*Installs into Google Antigravity (`~/.gemini`) and Claude Code (`~/.claude`) with zero external dependencies.*

---

## 📂 100% Self-Contained Skill Architecture

Each skill is completely decoupled and self-contained with its own executable scripts inside its folder:

```text
PirateGit/
├── skills/
│   ├── common/                       # Single shared core (network, scoring, channels, tree)
│   │   ├── utils.py                  # Zero-quota HTTP, caching, licenses & slug parser
│   │   ├── channels.py               # GitHub API, Topics, HN Algolia & Reddit public search
│   │   ├── scoring.py                # DeepGit composite scoring formula
│   │   └── tree.py                   # Anatomical zero-clone tree parser & hygiene calculator
│   │
│   ├── explore/
│   │   ├── SKILL.md                  # Reconnaissance protocol
│   │   └── scripts/
│   │       ├── explore.py            # 4-channel search & DeepGit scoring
│   │       ├── xray.py               # Zero-clone anatomical tree inspection
│   │       └── peek.py               # Zero-quota file reader
│   │
│   └── loot/
│       ├── SKILL.md                  # Architecture, baseline adoption, harvesting & tribunal protocol
│       └── scripts/
│           ├── harvest.py            # Quarantine downloader into others/
│           ├── stage.py              # Staging queue & progressive burn-down minitool
│           ├── files.py              # File-tree path filter
│           └── peek.py               # Zero-quota file reader
│
├── docs/assets/                      # Badges, logo, and illustrations
├── install.ps1 / install.sh          # One-line cross-platform installers (distributes common to skills)
├── README.md
└── LICENSE
```

---

## 🛠️ Direct Terminal CLI Usage

Because each script is a standalone Python stdlib utility, you can also run them directly from your terminal:

```bash
# 1. Multi-channel search, README triage & composite signal scoring
python skills/explore/scripts/explore.py "query 1" "query 2" --topics topic-name --limit 25

# 2. Anatomical file-tree dissection of repos without cloning
python skills/explore/scripts/xray.py owner1/repo1 owner2/repo2

# 3. Read specific files with zero API quota
python skills/explore/scripts/peek.py owner/repo path/to/file.py --max-lines 80

# 4. Filter repository paths by keywords
python skills/loot/scripts/files.py owner/repo placement router

# 5. Harvest selective files or full repository ZIP into others/
python skills/loot/scripts/harvest.py owner/repo --dest others --paths path/to/file.py

# 6. Manage staging queue and burn down transfusions
python skills/loot/scripts/stage.py status
```

---

## 📄 License

MIT License — Free for personal and commercial use.
