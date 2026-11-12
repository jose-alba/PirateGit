---
name: loot
description: >-
  Use this skill whenever the user triggers `/loot` (e.g. `/loot`, `/loot viaduct and eda-agent but no altium parts`),
  or wants to architect a project based on explored repositories, harvest candidates into `others/`,
  and step-by-step scavenge, clean, and adapt open-source code, algorithms, and datasets into local architecture.
---

# PirateGit: `/loot` — Architecture Blueprint, Surgical Scavenger & Quality Audit Tribunal

The `/loot` skill follows the intelligence gathered by `/explore`. It acts as an **Architect, Surgical Scavenger, and Quality Tribunal**:
1. It inherits the **Objective & Requirements Frame** from `/explore` and applies any user exclusions/constraints.
2. **Empty Project or Greenfield Scenarios (Fast-Track Baseline):** If the workspace is empty or starting from scratch, it evaluates if one of the top explored repositories already possesses a mature, battle-tested architecture and class hierarchy matching the target. If so, it proposes adopting that repository as the **Architectural Baseline**, extracting its structural foundation, and pruning/modifying on top of it rather than building from a blank slate.
3. **Standard Project Conventions:** Enforces enterprise industry standards for project layout:
   - `src/`: All application source code, domain models, and core logic.
   - `tests/`: Automated unit and integration test suites.
   - `assets/` (or `data/`): Curated datasets, static fixtures, schemas, and configurations.
   - `docs/`: User guides, API references, and architecture documentation.
4. **Quarantine Harvest (`others/`):** Clones or extracts candidates into local `others/` quarantine for safe inspection and surgery.
5. **Surgical Transfusion:** Refactors, cleans, and ports selected assets into the target project layout.
6. **Mandatory Final Step — The Quality Tribunal (Critic & Judge):** Launches an adversary **Critic Subagent** to audit for license contamination, dead code, and architecture drift, followed by a **Judge Subagent** that delivers the final production verdict.

## Self-Contained Skill Executables

Each helper is completely decoupled and self-contained in `scripts/`:
- Quarantine & selective downloader: [harvest.py](./scripts/harvest.py)
- File tree path filter: [files.py](./scripts/files.py)
- Zero-quota file peeker: [peek.py](./scripts/peek.py)

---

## Command Syntax & Input Flexibility

The user may invoke `/loot` with freeform natural-language instructions, preferences, or exclusions:
- `/loot` *(Inherits top recommendations and North Star from `/explore` and proposes the blueprint)*
- `/loot <owner/repo1> <owner/repo2> with instructions...`
- Examples:
  - `/loot use the dataset from viaduct and the placement engine from eda-agent, but ignore altium stuff`
  - `/loot this project is empty, use the repo structure of repoA as baseline and port repoB algorithms into src/`
  - `/loot only the stackup json and routing algorithms, adapt them to our src layout with assets/ and tests/`

---

## 4-Phase Execution Protocol

### Phase 1: Objective Alignment & Architecture Blueprint

#### 1. Baseline Architecture Strategy (Greenfield / Empty Workspace)
Check if the current workspace is empty or lacks clear structure:
- **Case A: Empty Project + Strong Architectural Match Exists in `/explore`**
  If one explored repository (with a permissive license `🟢 MIT/Apache`) already has an exceptional, battle-tested layout, class hierarchy, and dependency setup closely matching our North Star:
  - Recommend adopting it as the **Architectural Baseline**.
  - Harvest its foundation into the project (creating standard `src/`, `tests/`, `assets/`, `docs/` directories).
  - Then plan surgical modifications, pruning unneeded parts and swapping in better algorithms from secondary repos.
- **Case B: Existing Project Structure or Custom Design**
  Align with the existing workspace structure, ensuring all ported code cleanly integrates into standard directories (`src/`, `tests/`, `assets/`).

#### 2. Propose the Target Blueprint (Plan)
Present the exact directory map before writing any files:
```text
<project-root>/
├── src/                # Core domain logic, engines, interfaces
│   ├── core/
│   └── domains/
├── tests/              # Unit and integration test suites
├── assets/ (or data/)  # Knowledge bases, JSON/SQLite schemas, fixtures
├── others/             # Quarantine cache for raw third-party repos (gitignored)
└── projects.md         # Provenance and license compliance log
```
Map which harvested repository supplies which piece of the blueprint and verify commercial licenses.

#### 3. Ask for User Approval
Present the plan concisely and wait for user confirmation or adjustments.

---

### Phase 2: Harvest to Contraband Cache (`others/`)
Once the plan is approved:
1. Harvest approved repositories (or specific subdirectories) into `others/` using `harvest.py`:
   ```powershell
   # Windows (Antigravity / Gemini):
   python "$env:USERPROFILE\.gemini\config\skills\loot\scripts\harvest.py" owner/repo --dest others --paths path/to/data path/to/engine

   # Or download the complete repository archive
   python "$env:USERPROFILE\.gemini\config\skills\loot\scripts\harvest.py" owner/repo --dest others

   # (Or Claude Code: "$env:USERPROFILE\.claude\skills\loot\scripts\harvest.py" | Linux/macOS: "$HOME/.gemini/config/skills/loot/scripts/harvest.py" | Local: python skills/loot/scripts/harvest.py)
   ```
2. Ensure `others/` is added to `.gitignore` so raw third-party code is never tracked.

---

### Phase 3: Surgical Transfusion & Porting (Step-by-Step in Chat)
Do not dump raw third-party code directly into `src/`. Execute clean transfusions:

1. **Curated Datasets / Knowledge Bases:**
   - Move or adapt JSON/CSV/SQLite files from `others/<repo>/...` into `assets/` (or `data/`).
   - Write clean, typed loaders with error handling and validation.
2. **Core Engines & Algorithms (The Clean Port):**
   - Read the source file from `others/<repo>/...`. Inspect with `peek.py` if needed.
   - Strip unwanted dependencies, proprietary bridges, and framework bloat.
   - Refactor to match your project's clean architecture in `src/`, naming standards, Pydantic models, and logging.
   - Add corresponding unit tests in `tests/`.
3. **Provenance & License Compliance (`projects.md`):**
   - Document the scavenged module in `projects.md`: record origin repo, original author, license type, and modifications made.

---

### Phase 4: Mandatory Quality Tribunal (The Critic & The Judge)
Before declaring any `/loot` task complete, the agent **MUST** run the Quality Tribunal:

#### 1. The Devil's Advocate / Critic (`critic` subagent or adversarial review):
Review the ported code in `src/` and `tests/` relentlessly looking for:
- 🕵️ **License Contamination:** Did any copyleft or unknown-license snippet slip into our commercial code?
- 🧹 **Dead Code & Zombie Dependencies:** Are there unused imports, remnants of third-party helper utils, or hardcoded paths?
- ⚡ **Architecture Drift:** Is all business code confined to `src/`? Are fixtures properly placed in `assets/` or `tests/`?
- 🧪 **Test & Typing Coverage:** Are types complete (no `Any` escape hatches)? Are tests present in `tests/`?

#### 2. The Judge Verdict (`judge` subagent or formal sign-off):
The Judge evaluates the Critic's findings and issues a structured ruling:
- **Verdict:** `🟢 APPROVED FOR PRODUCTION` or `🟡 NEEDS REFACTORING`.
- **Actionable Remediation:** If anything failed the Critic's inspection, provide the exact 1–2 line fixes and apply them immediately.
- **Enterprise Provenance Badge:** A final sign-off confirming zero license risk and clean architectural integration.
