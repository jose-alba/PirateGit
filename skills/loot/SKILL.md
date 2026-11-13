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
2. **Unrestricted PoC & Prototype Looting:** In exploratory, prototyping, and greenfield phases, innovation and velocity come first. **You may harvest and port code or data from ANY candidate repository regardless of license** (including Copyleft `GPL/AGPL`, restrictive, or unlicensed code). Ninguna licencia descalifica ni puntúa negativo.
3. **Mandatory In-Code Provenance Tagging (Taint Tracking):** Because unvetted code must never silently seep into production later on, **every single scavenged function, class, data file, or schema MUST be explicitly tagged with a standardized `[PIRATEGIT LOOT PROVENANCE]` docstring/header**.
4. **Empty Project or Greenfield Scenarios (Fast-Track Baseline):** If the workspace is empty or starting from scratch, evaluate if one of the top explored repositories already possesses a mature, battle-tested architecture and class hierarchy matching the target. If so, adopt that repository as the **Architectural Baseline**, extracting its structural foundation, and building on top of it.
5. **Adopción de Subsistemas como Caja Negra (Black-Box Reuse):** Si un repositorio o paquete explorado está tan bien montado y desacoplado que resuelve una parte completa de nuestro sistema (ej. motor de subtítulos, ducking de audio, rendering FFmpeg), **podemos mantenerlo entero y usarlo directamente como caja negra**. No modificamos código que ya funciona bien; simplemente lo ubicamos en su propio módulo (ej. `src/modules/<componente>/`), creamos una interfaz o wrapper limpio y registramos su procedencia.
5. **Standard Project Conventions:** Enforces enterprise industry standards for project layout:
   - `src/`: All application source code, domain models, and core logic.
   - `tests/`: Automated unit and integration test suites.
   - `assets/` (or `data/`): Curated datasets, static fixtures, schemas, and configurations.
   - `docs/`: User guides, API references, and architecture documentation.
6. **Quarantine Harvest (`others/`):** Clones or extracts candidates into local `others/` quarantine for safe inspection and surgery.
7. **Surgical Transfusion:** Refactors, cleans, and ports selected assets into the target project layout.
8. **Mandatory Final Step — The Quality Tribunal (Critic & Judge):** Launches an adversary **Critic Subagent** to audit for dead code, architecture drift, and **verify 100% provenance tag coverage**, followed by a **Judge Subagent** that delivers the final **Provenance Inventory & Production Verdict**.

## Self-Contained Skill Executables

Each helper is completely decoupled and self-contained in `scripts/`:
- Quarantine & selective downloader: [harvest.py](./scripts/harvest.py)
- Staging queue & burn-down minitool: [stage.py](./scripts/stage.py)
- File tree path filter: [files.py](./scripts/files.py)
- Zero-quota file peeker: [peek.py](./scripts/peek.py)

---

## Command Syntax & Input Flexibility

The user may invoke `/loot` with freeform natural-language instructions or zero arguments:
- `/loot` *(Zero-args mode: automatically takes the top candidates and key assets identified in the last `/explore` scan, harvests them into `others/`, populates `staging/`, and starts the burn-down pipeline)*
- `/loot <owner/repo1> <owner/repo2> with instructions...`
- Examples:
  - `/loot` *(Full automatic pipeline: inherit explore recommendations, harvest, stage, and burn down)*
  - `/loot use the dataset from viaduct and the placement engine from eda-agent, but ignore altium stuff`
  - `/loot this project is empty, use the repo structure of repoA as baseline and port repoB algorithms into src/`
  - `/loot only the stackup json and routing algorithms, adapt them to our src layout with assets/ and tests/`

---

## 4-Phase Execution Protocol

### Phase 1: Objective Alignment & Architecture Blueprint

#### 1. Zero-Args Auto-Inference or Prompt Interpretation
- **Zero-Args `/loot`:** Read `.../agy_github_scout_cache/last_explore_digest.md`. Automatically select the top 2–4 candidates and their identified loot assets (data files, core algorithms, prompt templates) as the target harvest list.
- **Prompted `/loot`:** Interpret user preferences, filters, and exclusions to define the exact target assets.

#### 2. Baseline & Subsystem Architecture Strategy
Evaluate the project state and the candidate repositories:
- **Case A: Empty Project + Strong Architectural Match Exists in `/explore`**
  If an explored repository has a mature, battle-tested layout and class hierarchy matching our North Star:
  - Adopt it as the **Architectural Baseline** (regardless of license for prototyping).
  - Extract its foundation into the project layout (`src/`, `tests/`, `assets/`, `docs/`).
  - Prune unneeded parts and swap in specialized algorithms from secondary repos.
- **Case B: Black-Box Integration of Complete Subsystems**
  If a repository or submodule is exceptionally well engineered and covers an entire subsystem needed by our application:
  - Keep the component **entirely intact as a black box** (e.g. `src/modules/<subsystem>/` or `src/vendor/<subsystem>/`).
  - Do not rewrite or modify working code; build a clean typed wrapper/adapter to interface with the rest of `src/`.
  - Tag the module root with `[PIRATEGIT LOOT PROVENANCE]` and register it in `projects.md`.
- **Case C: Custom Greenfield Architecture + Surgical Transfusion**
  Design our own clean architecture in `src/` and surgically harvest only specific algorithms, schemas, or data files from the candidates.

#### 3. Propose the Target Blueprint & Staging Plan
Present the directory map and the files to be staged before writing:
```text
<project-root>/
├── others/             # Quarantine cache for raw third-party repos (gitignored)
├── staging/            # Temporary visual work queue (gitignored burn-down list)
├── src/                # Core domain logic, engines, interfaces
├── tests/              # Unit and integration test suites
├── assets/ (or data/)  # Knowledge bases, JSON/SQLite schemas, fixtures
└── projects.md         # Provenance inventory and license tracking log
```

---

### Phase 2: Harvest to Quarantine (`others/`) & Populate Staging (`staging/`)

1. **Harvest Candidate Repositories into `others/`:**
   ```powershell
   python "$env:USERPROFILE\.gemini\config\skills\loot\scripts\harvest.py" owner/repo --dest others --paths path/to/data path/to/engine
   # (Or download full repository zip: python .../harvest.py owner/repo --dest others)
   ```
2. **Populate the Staging Queue (`others/` $\rightarrow$ `staging/`):**
   Stage only the specific files identified for transfusion into `staging/` using the minitool:
   ```powershell
   python "$env:USERPROFILE\.gemini\config\skills\loot\scripts\stage.py" add others/repo/path/to/file.py --repo owner/repo --license MIT
   ```
   Verify the queue with:
   ```powershell
   python "$env:USERPROFILE\.gemini\config\skills\loot\scripts\stage.py" status
   ```

---

### Phase 3: Progressive Transfusion & Burn-Down (`staging/` $\rightarrow$ `src/`, `assets/`, `tests/`)

Work through `staging/` file by file. This keeps context tokens minimal and ensures continuous visible progress:

1. **Inspect & Adapt Staged File:**
   - Read the single file from `staging/<repo>/...`.
   - Adapt it cleanly into `src/` (or `assets/`), applying project naming standards, typing, and removing framework bloat.
   - Write corresponding unit tests in `tests/`.
2. **Burn-Down via Minitool (`complete`):**
   Once the file is integrated and tested, execute `stage.py complete`:
   ```powershell
   python "$env:USERPROFILE\.gemini\config\skills\loot\scripts\stage.py" complete staging/repo/file.py --dest src/core/engine.py
   ```
   **The minitool automatically handles the mechanical plumbing:**
   - Injects the `[PIRATEGIT LOOT PROVENANCE]` block into the destination file's docstring.
   - Logs the entry in `projects.md`.
   - Deletes `staging/repo/file.py` from the staging queue.
3. **Repeat** until `stage.py status` reports that `staging/` is 100% empty.

---

### Phase 4: Mandatory Quality Tribunal (The Critic & The Judge)
Before declaring any `/loot` task complete, the agent **MUST** run the Quality Tribunal:

#### 1. The Devil's Advocate / Critic (`critic` subagent or adversarial review):
Review the ported code in `src/` and `tests/` relentlessly looking for:
- 🏷️ **100% Provenance Tag Coverage:** Every function/class/schema must have its `[PIRATEGIT LOOT PROVENANCE]` docstring tag.
- 🧹 **Dead Code & Zombie Dependencies:** Clean imports, no mock relics, no hardcoded paths.
- ⚡ **Architecture Drift:** Business logic in `src/`, fixtures in `assets/`, tests in `tests/`.
- 🧪 **Test Suite Verification:** Run all unit tests in `tests/` to confirm green execution.
- 🗑️ **Queue Burn-Down Verification:** Confirm that `staging/` is completely burned down (empty).

#### 2. The Judge Verdict (`judge` subagent or formal sign-off):
The Judge reviews the Critic's report and outputs the **Loot Provenance Inventory Table**:

| Componente Portado | Archivo Destino | Repositorio Origen | Licencia Origen | Estado para Producción |
|---|---|---|---|---|
| `ejemplo_funcion()` | `src/core/engine.py` | `owner/repo1` | `GPL-3.0` | ⚠️ PoC Only (Reescribir Clean-Room antes de producción) |
| `dataset_schema.json` | `assets/data.json` | `owner/repo2` | `MIT` | 🟢 Listo para producción comercial |

- **Verdict:** `🟢 PROVENANCE AUDITED & READY FOR EXPERIMENTATION`
- **Remediation:** If any function lacked provenance tags or failed tests, apply the fix immediately before closing the task.
