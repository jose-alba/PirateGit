---
name: explore
description: >-
  Use this skill whenever the user triggers `/explore` (e.g. `/explore pcb placement --50repos`),
  or wants to scout GitHub, Hacker News, and Reddit to find similar repositories, inspect READMEs,
  run anatomical X-rays, and get a ranked Loot Table with a SWOT (DAFO) analysis before coding.
---

# PirateGit: `/explore` — Multi-Agent Open-Source Radar & Forensic Scout

The `/explore` skill is the intelligence, intent-framing, and reconnaissance fleet of PirateGit. It formalizes the user's ultimate goal and technical requirements upfront, then dispatches **parallel scouting subagents ("Pirate Scouts")** to sweep public platforms, culls candidate READMEs against criteria, runs anatomical zero-clone `xray` inspections, and delivers a ranked **Loot Table + SWOT (DAFO) Analysis**.

## Self-Contained Skill Executables

Each helper is completely decoupled and self-contained in `scripts/`:
- Multi-channel search & scoring: [explore.py](./scripts/explore.py)
- Anatomical zero-clone X-ray: [xray.py](./scripts/xray.py)
- Zero-quota file peeker: [peek.py](./scripts/peek.py)

---

## Command Syntax

The user can invoke `/explore` with:
- `/explore <goal, feature, or project description>` *(Default scope: **50 repositories**)*
- `/explore <goal> --100repos` *(or `--20repos`, `--80repos`, etc. to override scope)*

---

## 6-Step Execution Protocol with Parallel Scouts

### Step 1: Goal Synthesis & Technical Requirements Framing (The North Star)
Analyze the user's prompt and explicitly define the **Objective & Requirements Frame**:
1. **Target Objective (North Star):** 1–2 sentences on what tangible system is being built and what "done" looks like.
2. **Hard Requirements (Must-Haves):** Target runtime/language, input/output data formats, and permissive licensing (`🟢 MIT`, `Apache-2.0`, `BSD`).
3. **Anti-Patterns & Red Lines (Discard Criteria):** Proprietary lock-in, GPU-only training when seeking lightweight heuristics, or incompatible copyleft (`🟡 GPL`).

### Step 2: Multi-Angle Keyword & Topic Expansion
Generate:
1. **5 to 8 short GitHub search queries** (1 to 3 core domain nouns per query).
2. **2 to 4 canonical GitHub Topic slugs** (e.g., `pcb-design`, `eda`, `autorouter`).

### Step 3: Dispatch Parallel Pirate Scouts (Subagent Search Fleet)
Run the self-contained explore script (installed globally or relative to project):
```powershell
# Windows (Antigravity / Gemini):
python "$env:USERPROFILE\.gemini\config\skills\explore\scripts\explore.py" "query 1" "query 2" "query 3" --topics topic-one topic-two --50repos

# (Or Claude Code: python "$env:USERPROFILE\.claude\skills\explore\scripts\explore.py" ... | Linux/macOS: python "$HOME/.gemini/config/skills/explore/scripts/explore.py" ... | Local repo: python skills/explore/scripts/explore.py ...)
```

This searches **GitHub Search + GitHub Topics + Hacker News (Algolia) + Reddit (Public JSON & PullPush archive)** in parallel, downloads clean `README.md` extracts via `raw.githubusercontent.com` (0 API quota), and scores candidates using the DeepGit composite signal formula (`relevance`, `maintenance`, `popularity`, `health`).

*Tip:* Read the untruncated digest saved at `.../agy_github_scout_cache/last_explore_digest.md` to ensure zero lost context.

### Step 4: README Triage & Criteria Filtering
Review candidate `README.md` digests strictly against the **Objective & Requirements from Step 1**:
- 🔥 **High Relevance:** Direct hits solving the core problem with scavengeable data, engines, or architecture.
- ⚖️ **Medium Relevance:** Secondary tools or inspiration.
- ❌ **Discarded:** Violates hard requirements, empty wrappers, abandoned toys, or AI-slop.

### Step 5: Parallel Anatomical X-Ray (`xray.py`) of Top Repositories
Run `xray.py` on the **top 10 relevant repositories** (highest composite score passing triage) in parallel to dissect their complete internal file trees without cloning:

```powershell
python "$env:USERPROFILE\.gemini\config\skills\explore\scripts\xray.py" owner1/repo1 owner2/repo2 owner3/repo3
# (Or: python skills/explore/scripts/xray.py ...)
```

*(Optional)* Inspect specific core algorithm or data files with `peek.py`:
```powershell
python "$env:USERPROFILE\.gemini\config\skills\explore\scripts\peek.py" owner/repo path/to/file.py --max-lines 120
# (Or: python skills/explore/scripts/peek.py ...)
```

### Step 6: Deliver Intelligence Report (in User's Language)
Respond in the language used by the user (e.g. Spanish if prompted in Spanish) with 4 structured sections:
1. **Marco de Objetivo y Requisitos (Target Frame):** North Star, Hard Requirements, and Discard Criteria.
2. **Resumen de la Flota de Exploración (Fleet Triage Summary):** Repos scanned across all channels and relevance breakdown.
3. **Tabla Comparativa de Botín (Comparative Loot Table — Máximo Top 10):**
   Presenta la tabla comparativa con **como mucho 10 repositorios** (los que tienen mayor puntuación compuesta `composite_score`).
   Columnas: Posición, Repositorio, Puntuación, Semáforo de Licencia (`🟢 Permisiva / 🟡 Copyleft / 🔴 Sin licencia`), Lenguaje/Tamaño y Botín Concreto Reutilizable.
4. **Análisis DAFO (SWOT) Enfocado al Objetivo (Máximo Top 10):**
   Muestra el desglose DAFO individual (Fortalezas, Debilidades, Oportunidades de Saqueo y Amenazas de Licencia/Riesgo) **únicamente para los 10 mejores repositorios**.

> [!NOTE]
> **Aviso de expansión obligatoria al final del reporte:**
> Incluye siempre al pie del reporte un mensaje claro ofreciendo consultar el resto de repositorios:
> *"💡 **Mostrando los Top 10 repositorios por puntuación.** Si deseas ver la tabla comparativa con los repositorios restantes o un desglose DAFO detallado de cualquier otro repositorio escaneado, indícalo y te lo muestro."*
