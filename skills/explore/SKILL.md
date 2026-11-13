---
name: explore
description: >-
  Use this skill whenever the user triggers `/explore` (e.g. `/explore pcb placement --50repos`),
  or wants to scout GitHub, Hacker News, and Reddit to find similar repositories, inspect READMEs,
  run anatomical X-rays, and get a ranked unified Loot Table with SWOT (DAFO) analysis before coding.
---

# PirateGit: `/explore` — Multi-Agent Open-Source Radar & Forensic Scout

The `/explore` skill is the intelligence, intent-framing, and reconnaissance fleet of PirateGit. It formalizes the user's ultimate goal and technical requirements upfront, then dispatches **parallel scouting subagents ("Pirate Scouts")** to sweep public platforms, culls candidate READMEs against criteria, runs anatomical zero-clone `xray` inspections, and delivers a **Unified Loot & SWOT (DAFO) Table** followed by an **Architectural Reference Strategy** to feed into `/loot`.

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

## Core Rules & Non-Negotiable Directives

> [!IMPORTANT]
> ### 1. REGLA FUNDAMENTAL DE LICENCIAS (CERO DESCARTES POR COPYLEFT O SIN LICENCIA)
> **ESTO NO PUEDE PASAR NUNCA:** No descartar, rechazar ni catalogar jamás como "Línea Roja" o "Criterio de Descarte" repositorios con licencias copyleft (`GPL-2.0`, `GPL-3.0`, `AGPL-3.0`, `MPL-2.0`, etc.) o repositorios sin licencia explícita.
> - **Se puede usar y saquear TODO el código sin importar su licencia** para prototipos rápidos, experimentación y validación de arquitectura.
> - Ninguna licencia puntúa negativo ni descalifica un repositorio.
> - El único requisito es que cada clase, función o archivo que se extraiga conserve su trazabilidad con el docstring `[PIRATEGIT LOOT PROVENANCE]`, indicando la licencia de origen para que el equipo sepa qué partes deberán reimplementarse (mediante Clean-Room) si en el futuro se comercializa o monetiza el software.
>
> ### 2. REUTILIZACIÓN REAL vs. FAMA / ESTRELLAS
> **No importa cuán famoso sea un repositorio, ni cuántas estrellas o forks tenga.**
> - Lo verdaderamente determinante es **lo que tiene dentro que podamos reutilizar**: algoritmos específicos, parsers, motores de cálculo, esquemas o datasets.
> - Un repositorio pequeño o desconocido de 2 estrellas que resuelva con precisión matemática o técnica el problema vale infinitamente más que un repositorio mediático de 40.000 estrellas que sea un simple envoltorio o interfaz web.
> - Los repositorios grandes son bienvenidos si tienen buen código, pero los pequeños también se evalúan con el mismo rigor y prioridad técnica.

---

## 6-Step Execution Protocol with Parallel Scouts

### Step 1: Goal Synthesis & Technical Requirements Framing (The Target Frame)
- **Automatic Workspace Inspection (if invoked as `/explore` with no args):**  
  Read local workspace `README.md`, package manifests (`pyproject.toml`, `package.json`, `requirements.txt`, etc.), and existing source files. Synthesize domain, stack, and active modules.
- **Explicit Goal (if prompt provided):** Analyze user objectives and specific subproblems.

Synthesize the **Target Frame** strictly under these guidelines:
1. **Objetivo Primario (North Star):** 1–2 oraciones claras sobre el sistema concreto que se construye y qué define el estado de "terminado".
2. **Requisitos Técnicos Críticos (Must-Haves):** Runtime, stack de librerías base, pipeline headless/modular, formatos de datos de entrada/salida.
3. **Líneas Rojas & Antipatrones Técnicos (Discard Criteria):** ÚNICAMENTE bloqueos técnicos insalvables (ej. acoplamiento inseparable a UIs propietarias no desacoplables, APIs de pago obligatorio sin alternativa, o dependencias de hardware inexistentes). **NUNCA incluir licencias Copyleft ni repositorios sin licencia aquí.**

### Step 2: Multi-Angle Keyword & Topic Expansion (Direct, Lateral & Subsystem)
Do not limit queries to the literal prompt. Generate **10 to 16 short, focused search queries** (1 to 3 words each) and **4 to 6 canonical GitHub Topic slugs**, exploring three distinct conceptual angles:
1. **Ángulo 1: Directo & Sinónimos Core:** Nombres técnicos principales, acrónimos y términos en inglés.
2. **Ángulo 2: Dominios Laterales / Horizontales:** Conceptos adyacentes, ecosistema y propósito amplio.
3. **Ángulo 3: Subsistemas Internos & Piezas Anatómicas:** Componentes específicos de dentro que resuelven subproblemas críticos (ej. algoritmos, animaciones, filtros, sincronización, layouts).

### Step 3: Dispatch Parallel Pirate Scouts (Subagent Search Fleet)
Run the self-contained explore script:
```powershell
# Windows (Antigravity / Gemini):
python "$env:USERPROFILE\.gemini\config\skills\explore\scripts\explore.py" "query 1" "query 2" "query 3" "query 4" --topics topic-one topic-two --limit 25 --max-total 100
```
This searches **GitHub Search + GitHub Topics + Hacker News (Algolia) + Reddit (Public JSON & PullPush archive)** in parallel, downloads clean `README.md` extracts via `raw.githubusercontent.com` (0 API quota), and scores candidates prioritizing technical fit and relevance over popularity. Scope defaults to **100 repositories**.

*Tip:* Read the untruncated digest saved at `.../agy_github_scout_cache/last_explore_digest.md` to ensure zero lost context.

### Step 4: README Triage & Anatomical Candidate Selection
Review candidate digests strictly evaluating **reusable logic and internal code quality**:
- 🔥 **Alta Relevancia:** Repositorios (grandes o pequeños, cualquier licencia) que contienen código, motores, esquemas o algoritmos directamente reutilizables.
- ⚖️ **Relevancia Media:** Repositorios de inspiración o soporte secundario.
- ❌ **Descartados:** Únicamente proyectos completamente vacíos, repositorios rotos/abandonados sin código útil, o listas de enlaces sin implementación.

### Step 5: Parallel Anatomical X-Ray (`xray.py`) of Top Repositories
Run `xray.py` on the top relevant candidates (orientativamente los **10 a 20 repositorios** más prometedores) para diseccionar sus árboles de archivos sin clonar:

```powershell
python "$env:USERPROFILE\.gemini\config\skills\explore\scripts\xray.py" owner1/repo1 owner2/repo2 owner3/repo3 owner4/repo4
```

Inspect specific core algorithm or data files with `peek.py`:
```powershell
python "$env:USERPROFILE\.gemini\config\skills\explore\scripts\peek.py" owner/repo path/to/file.py --max-lines 120
```

---

### Step 6: Deliver Intelligence Report (in User's Language)

Respond in the language used by the user with the following clear structure:

#### 1. Marco de Objetivo y Requisitos (Target Frame)
- **Objetivo Primario (North Star)**
- **Requisitos Técnicos Críticos (Must-Haves)**
- **Líneas Rojas & Antipatrones Técnicos** *(Recuerda: sin vetos por licencia ni por bajas estrellas)*

#### 2. Resumen de la Flota de Exploración (Fleet Triage Summary)
- Total de repositorios escaneados en todos los canales y desglose de relevancia.

#### 3. Tabla Unificada de Botín y DAFO (Top 10+ orientado a valor)
Presenta una **única tabla integral** que combina la evaluación técnica, el análisis DAFO y el botín concreto reutilizable con las siguientes columnas exactas:

| Repo | Puntuación y estrellas | Qué hace (idea rápida) | Debilidades | Fortalezas | Oportunidades | Amenazas | Qué vamos a aprovechar (en texto) | Qué vamos a aprovechar (en código) |
|---|---|---|---|---|---|---|---|---|
| [`owner/repo`](https://github.com/owner/repo) | `0.91 \| ⭐ 42` | Motor de cálculo... | Acoplado a CLI... | Algoritmo determinista puro... | Acelera módulo de routing | Licencia GPL (reescribir si se monetiza) | El generador de curvas y el parser de esquemas | `src/math/splines.py`, `models/schema.json` |

*Explicación de las columnas:*
1. **Repo:** Enlace markdown al repositorio (`owner/repo`).
2. **Puntuación y estrellas:** Puntuación compuesta y estrellas en la misma celda (ej. `0.88 | ⭐ 15`).
3. **Qué hace (idea rápida):** Síntesis concisa de qué resuelve el proyecto.
4. **Debilidades:** Carencias técnicas, falta de tests, dependencias pesadas o código desordenado.
5. **Fortalezas:** Calidad de los algoritmos, eficiencia, diseño limpio o robustez.
6. **Oportunidades:** Qué valor diferencial inyecta a nuestro North Star.
7. **Amenazas:** Riesgos técnicos o licencia a sustituir/reescribir en producción comercial.
8. **Qué vamos a aprovechar (en texto):** Explicación funcional y conceptual de los componentes a reutilizar.
9. **Qué vamos a aprovechar (en código):** Rutas exactas de archivos, clases, funciones o módulos descubiertos en el X-ray.

#### 4. Recomendación de Estrategia Arquitectónica de Referencia (Hacia `/loot`)
Cierra el informe analizando cómo conectar con `/loot`:
- **Opción A (Adoptar como Base / Esqueleto):** Si partimos de cero y alguno de los repositorios tiene una arquitectura, jerarquía de carpetas y diseño modular tan sólido que merezca ser adoptado como el esqueleto base (`src/`) sobre el cual podar y construir.
- **Opción B (Arquitectura Propia + Saqueo Quirúrgico):** Si es mejor diseñar nuestra propia arquitectura limpia y únicamente trasvasar piezas específicas (algoritmos, schemas, utilidades) de los repositorios analizados.
- **Opción C (Integración en Proyecto Existente):** Si el workspace actual ya cuenta con su propia base y solo incorporaremos los componentes identificados en las carpetas correspondientes.

> [!NOTE]
> *"💡 **Mostrando los repositorios más destacados.** Si deseas ver la tabla ampliada con el resto de los 100 repositorios escaneados, o profundizar en el árbol de archivos (`xray`/`peek`) de cualquiera de ellos, indícalo y te lo muestro."*
