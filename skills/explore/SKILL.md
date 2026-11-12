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
- `/explore` *(Zero-args mode: automatically inspects the current workspace/repository [README.md, manifests, core files], synthesizes the North Star, and scouts similar projects)*
- `/explore <goal, feature, or project description>` *(Default scope: **100 repositories**)*
- `/explore [goal] --150repos` *(or `--50repos`, `--200repos`, etc. to override scope)*

---

## 6-Step Execution Protocol with Parallel Scouts

### Step 1: Goal Synthesis & Technical Requirements Framing (The North Star)
- **Automatic Workspace Inspection (if invoked as `/explore` with no args):**  
  First read the local workspace's `README.md`, package manifests (`pyproject.toml`, `package.json`, `requirements.txt`, etc.), and core source files. Synthesize what this project does, its core domains, and technical requirements.
- **Explicit Goal (if prompt provided):** Analyze the user's prompt.

Explicitly define the **Objective & Requirements Frame**:
1. **Target Objective (North Star):** 1–2 sentences on what tangible system is being built and what "done" looks like.
2. **Hard Requirements (Must-Haves):** Target runtime/language, input/output data formats, and permissive licensing (`🟢 MIT`, `Apache-2.0`, `BSD`).
3. **Anti-Patterns & Red Lines (Discard Criteria):** Proprietary lock-in, GPU-only training when seeking lightweight heuristics, or incompatible copyleft (`🟡 GPL`).

### Step 2: Multi-Angle Keyword & Topic Expansion (Direct, Lateral & Subsystem)
Do not limit queries to the literal prompt. Generate **10 to 16 short, focused search queries** (1 to 3 words each) and **4 to 6 canonical GitHub Topic slugs**, exploring three distinct conceptual angles:
1. **Ángulo 1: Directo & Sinónimos Core:** Nombres técnicos principales, acrónimos y términos en inglés (ej. si el objetivo es un coche: `car`, `automobile`, `vehicle`; si es un parser: `markdown parser`, `ast`).
2. **Ángulo 2: Dominios Laterales / Horizontales:** Conceptos adyacentes, ecosistema y propósito amplio (ej. para un coche: `mobility`, `transportation`, `telemetry`; para PCB: `eda`, `cad`, `hardware design`).
3. **Ángulo 3: Subsistemas Internos & Piezas Anatómicas:** Componentes específicos de dentro que resuelven subproblemas críticos (ej. para un coche: `steering`, `powertrain`, `wheels`, `brakes`; para PCB: `autorouter`, `component library`, `footprints`, `drc`).

### Step 3: Dispatch Parallel Pirate Scouts (Subagent Search Fleet)
Run the self-contained explore script (installed globally or relative to project):
```powershell
# Windows (Antigravity / Gemini):
python "$env:USERPROFILE\.gemini\config\skills\explore\scripts\explore.py" "query 1" "query 2" "query 3" "query 4" --topics topic-one topic-two --100repos

# (Or Claude Code: python "$env:USERPROFILE\.claude\skills\explore\scripts\explore.py" ... | Linux/macOS: python "$HOME/.gemini/config/skills/explore/scripts/explore.py" ... | Local repo: python skills/explore/scripts/explore.py ...)
```

This searches **GitHub Search + GitHub Topics + Hacker News (Algolia) + Reddit (Public JSON & PullPush archive)** in parallel, downloads clean `README.md` extracts via `raw.githubusercontent.com` (0 API quota), and scores candidates using the DeepGit composite signal formula (`relevance`, `maintenance`, `popularity`, `health`). Scope defaults to **100 repositories**.

*Tip:* Read the untruncated digest saved at `.../agy_github_scout_cache/last_explore_digest.md` to ensure zero lost context.

### Step 4: README Triage & Criteria Filtering
Review candidate `README.md` digests strictly against the **Objective & Requirements from Step 1**:
- 🔥 **High Relevance:** Direct hits solving the core problem with scavengeable data, engines, or architecture.
- ⚖️ **Medium Relevance:** Secondary tools or inspiration.
- ❌ **Discarded:** Violates hard requirements, empty wrappers, abandoned toys, or AI-slop.

### Step 5: Parallel Anatomical X-Ray (`xray.py`) of Top Repositories
Run `xray.py` on the top relevant candidates (orientativamente los **10 a 20 repositorios** más prometedores que hayan superado el triaje, cubriendo tanto soluciones completas como subsistemas internos) en paralelo para diseccionar sus árboles de archivos sin clonar:

```powershell
python "$env:USERPROFILE\.gemini\config\skills\explore\scripts\xray.py" owner1/repo1 owner2/repo2 owner3/repo3 owner4/repo4
# (Or: python skills/explore/scripts/xray.py ...)
```

*(Optional)* Inspect specific core algorithm or data files with `peek.py`:
```powershell
python "$env:USERPROFILE\.gemini\config\skills\explore\scripts\peek.py" owner/repo path/to/file.py --max-lines 120
# (Or: python skills/explore/scripts/peek.py ...)
```

### Step 6: Deliver Intelligence Report (in User's Language)
Respond in the language used by the user (e.g. Spanish if prompted in Spanish) with 4 structured sections. *(Nota: La cifra de 10 es orientativa; puedes incluir más repositorios si consideras que aportan valor técnico o botín diferencial).*

1. **Marco de Objetivo y Requisitos (Target Frame):** North Star, Hard Requirements, and Discard Criteria.
2. **Resumen de la Flota de Exploración (Fleet Triage Summary):** Repos scanned across all channels and relevance breakdown (100 repos analizados por defecto).
3. **Tabla de Análisis DAFO / SWOT (Top 10+ orientado a valor):**
   Presenta el análisis DAFO en formato de **tabla estructurada y sintética** (antes de la tabla de botín) para evaluar rápidamente la viabilidad técnica y legal de los mejores repositorios (mínimo 10, ampliable según relevancia):
   Columnas:
   - `#`: Posición por puntuación compuesta.
   - `Repositorio`: Enlace markdown al repositorio (`owner/repo`).
   - `Fortalezas (F)`: Calidad de código, tests, CI, modularidad o algoritmos punteros.
   - `Debilidades (D)`: Desactualizado, dependencias pesadas, acoplamiento o falta de docs.
   - `Oportunidades de Saqueo (O)`: Algoritmos clave a portar, datasets, schemas o prompts aprovechables.
   - `Amenazas / Licencia (A)`: Riesgo legal (Copyleft `GPL/AGPL`, licencias ambiguas) o dependencias incompatibles.
4. **Tabla Comparativa de Botín (Comparative Loot Table — Top 10+ orientado a valor):**
   Presenta la tabla comparativa técnica y de recursos reutilizables con los candidatos más destacados:
   Columnas:
   - `#`: Posición.
   - `Repositorio`: Enlace markdown (`owner/repo`).
   - `Puntuación`: Puntuación compuesta (ej. `0.87`).
   - `Licencia`: Semáforo de Licencia (`🟢 Permisiva / 🟡 Copyleft / 🔴 Sin licencia`).
   - `Lenguaje / Tamaño`: Lenguaje principal y tamaño en KB o MB.
   - `Botín Concreto Reutilizable`: Rutas y nombres específicos de archivos de datos, motores, algoritmos o dependencias identificadas durante el `xray`.

> [!NOTE]
> **Aviso de expansión al final del reporte:**
> Incluye siempre al pie del reporte un mensaje claro ofreciendo consultar el resto de repositorios:
> *"💡 **Mostrando los repositorios más destacados.** Si deseas ver la tabla DAFO o de botín ampliada con el resto de los 100 repositorios escaneados, o profundizar en el árbol de archivos de cualquiera de ellos, indícalo y te lo muestro."*
