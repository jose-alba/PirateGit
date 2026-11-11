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
2. It designs the target architecture and harvests candidate repos into local quarantine (`others/`).
3. It transplants selected assets step-by-step into clean, production-ready project code.
4. **Mandatory Final Step — The Quality Tribunal (Critic & Judge):** It launches an adversary **Critic Subagent** to relentlessly find flaws, edge cases, license contamination, and dead code, followed by a **Judge Subagent** that delivers the final pass/fail verdict and guarantees enterprise readiness.

## Executable CLI Engine

Uses the `harvest`, `peek`, and `files` subcommands of:
- Local path: `scripts/pirategit.py`
- Global path: `C:\Users\jose_\.gemini\config\skills\github-repo-scout\scripts\github_scout.py`

---

## Command Syntax & Input Flexibility

The user may invoke `/loot` with freeform natural-language instructions, preferences, or exclusions:
- `/loot` *(Takes the top recommendations and North Star from `/explore` and proposes the blueprint)*
- `/loot <owner/repo1> <owner/repo2> with instructions...`
- Examples:
  - `/loot use the dataset from viaduct and the placement engine from eda-agent, but ignore altium stuff`
  - `/loot only the stackup json and routing algorithms, adapt them to our src_clean structure`

---

## 4-Phase Execution Protocol

### Phase 1: Objective Alignment & Architecture Blueprint
1. **Inherit & Refine the Target Frame:**
   Recall the **Objective (North Star)**, **Hard Requirements**, and **Red Lines** from `/explore`. Parse any new constraints or exclusions from the user's `/loot` prompt.
2. **Propose the Target Architecture (Blueprint):**
   Present a clear proposed directory structure (e.g. `src/core/`, `src/domains/`, `data/`, `tests/`).
   - Map which harvested repo will supply which piece of the blueprint.
   - Verify commercial licenses: warn immediately if a requested repo is `🟡 Copyleft (GPL)` or `🔴 No License`.
3. **Ask for User Approval:**
   Present the plan concisely and wait for user confirmation or adjustments before downloading and writing files.

### Phase 2: Harvest to Contraband Cache (`others/`)
Once the plan is approved:
1. Harvest approved repositories (or specific subdirectories) into the `others/` folder using `pirategit harvest`:
   ```powershell
   # Download specific directories or files into others/<repo>/
   python scripts/pirategit.py harvest owner/repo --dest others --paths path/to/data path/to/engine

   # Or download the complete repository archive
   python scripts/pirategit.py harvest owner/repo --dest others
   ```
2. Ensure `others/` is added to `.gitignore` so raw third-party code does not bloat your git history.

### Phase 3: Surgical Transfusion & Porting (Step-by-Step in Chat)
Do not dump raw third-party code directly into the source tree. Execute clean transfusions:
1. **Curated Datasets / Knowledge Bases:**
   - Copy or adapt JSON/CSV/SQLite files from `others/<repo>/...` into `data/`.
   - Write clean, typed loaders with error handling and validation.
2. **Core Engines & Algorithms (The Clean Port):**
   - Read the source file from `others/<repo>/...`.
   - Strip unwanted dependencies, proprietary bridges, and framework bloat.
   - Refactor to match your project's clean architecture, naming standards, Pydantic models, and logging.
   - Integrate into the active codebase.
3. **Provenance & License Compliance (`projects.md`):**
   - Document the scavenged module in `projects.md`: record origin repo, original author, license type, and modifications made.

---

### Phase 4: Mandatory Quality Tribunal (The Critic & The Judge)
Before declaring any `/loot` task complete, the agent **MUST** run the Quality Tribunal:

#### 1. The Devil's Advocate / Critic (`critic` subagent or adversarial review):
Review the ported code relentlessly looking for:
- 🕵️ **License Contamination:** Did any copyleft or unknown-license snippet slip into our commercial code?
- 🧹 **Dead Code & Zombie Dependencies:** Are there unused imports, remnants of the third-party repo's helper utils, or hardcoded paths?
- ⚡ **Architecture Drift:** Does the ported code violate our project's modular standards or leak internal abstractions?
- 🧪 **Test & Typing Coverage:** Are types complete (no `Any` escape hatches)? Are edge cases handled?

#### 2. The Judge Verdict (`judge` subagent or formal sign-off):
The Judge evaluates the Critic's findings and issues a structured ruling:
- **Verdict:** `🟢 APPROVED FOR PRODUCTION` or `🟡 NEEDS REFACTORING`.
- **Actionable Remediation:** If anything failed the Critic's inspection, provide the exact 1–2 line fixes and apply them immediately.
- **Enterprise Provenance Badge:** A final sign-off confirming zero license risk and clean architectural integration.
