---
name: explore
description: >-
  Use this skill whenever the user triggers `/explore` (e.g. `/explore pcb placement --50repos`),
  or wants to scout GitHub, Hacker News, and Reddit to find similar repositories, inspect READMEs,
  run anatomical X-rays, and get a ranked Loot Table with a SWOT (DAFO) analysis before coding.
---

# PirateGit: `/explore` — Multi-Agent Open-Source Radar & Forensic Scout

The `/explore` skill is the intelligence, intent-framing, and reconnaissance fleet of PirateGit. It formalizes the user's ultimate goal and technical requirements upfront, then dispatches **parallel scouting subagents ("Pirate Scouts")** to sweep public platforms, culls candidate READMEs against criteria, runs anatomical zero-clone `xray` inspections, and delivers a ranked **Loot Table + SWOT (DAFO) Analysis**.

## Executable CLI Engine

Always run the zero-dependency script:
- Local path: `scripts/pirategit.py`
- Global path: `C:\Users\jose_\.gemini\config\skills\github-repo-scout\scripts\github_scout.py`

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
To maximize throughput and cross-validation, dispatch parallel scouting tasks:
- **Scout A (GitHub & Topics):** Executes `scripts/pirategit.py explore ... --50repos` across GitHub Search API and canonical topic feeds.
- **Scout B (Discussion Feeds - HN & Reddit):** Searches Hacker News stories/comments and public Reddit archive feeds for real engineer recommendations and hidden gems.
- *Execution:* If subagents are supported in the runtime (`invoke_subagent` / task pool), dispatch scouts in parallel; otherwise, execute the multi-threaded `pirategit.py explore` command which runs all 4 channels concurrently.

*Tip:* Read the untruncated digest saved at `.../agy_github_scout_cache/last_explore_digest.md` to ensure zero lost context.

### Step 4: README Triage & Criteria Filtering
Review candidate `README.md` digests strictly against the **Objective & Requirements from Step 1**:
- 🔥 **High Relevance:** Direct hits solving the core problem with scavengeable data, engines, or architecture.
- ⚖️ **Medium Relevance:** Secondary tools or inspiration.
- ❌ **Discarded:** Violates hard requirements, empty wrappers, abandoned toys, or AI-slop.

### Step 5: Parallel Anatomical X-Ray (`xray`) of Top Repositories
Run `xray` on the top 4 to 8 relevant repositories in parallel to dissect their complete internal file trees without cloning:

```powershell
python scripts/pirategit.py xray owner1/repo1 owner2/repo2 owner3/repo3
```

*(Optional)* Inspect specific core algorithm or data files with `peek`:
```powershell
python scripts/pirategit.py peek owner/repo path/to/file.py --max-lines 120
```

### Step 6: Deliver Intelligence Report (in User's Language)
Respond in the user's language (e.g. Spanish if prompted in Spanish) with 4 structured sections:
1. **Marco de Objetivo y Requisitos (Target Frame):** North Star, Hard Requirements, and Discard Criteria.
2. **Resumen de la Flota de Exploración (Fleet Triage Summary):** Repos scanned across all channels and relevance breakdown.
3. **Tabla Comparativa de Botín (Comparative Loot Table):** Ranked by composite score with commercial license traffic light (`🟢/🟡/🔴`) and exact scavengeable assets.
4. **Análisis DAFO (SWOT) Enfocado al Objetivo:** Strengths, Weaknesses, Loot Opportunities, and Threats/Risks evaluated strictly against the Step 1 requirements.
