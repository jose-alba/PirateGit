# 🏴‍☠️ PirateGit: Provenance & Scavenged Assets Log (`projects.md`)

This file is maintained automatically by `/loot` to record every external algorithm, dataset, schema, or utility scavenged into the codebase, preserving full license traceability and intellectual provenance.

---

## 📜 Scavenged Assets Manifest

| Component / Function | Destination File | Origin Repository | Original License | Usage Status | Production Notes |
|---|---|---|---|---|---|
| `smart_truncate_output()` | `skills/common/utils.py` | [rtk-ai/rtk](https://github.com/rtk-ai/rtk) | 🟢 Apache-2.0 | ⚠️ PoC / Prototipo Experimental | Adaptación en Python stdlib de las heurísticas de colapso de outputs CLI para ahorro de tokens. Licencia permisiva; integrable comercialmente manteniendo atribución. |
| `skillgen` multi-agent packaging | `others/graphify/tools/skillgen/gen.py` | [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | 🟢 Apache-2.0 | ⚠️ PoC / En cuarentena en `others/` | Utilidad de referencia para generar artefactos de skills compatibles con 15+ clientes de IA. |

---

## 🏷️ Standard In-Code Provenance Tag

Every looted asset in source code must carry this header block:

```python
"""
[PIRATEGIT LOOT PROVENANCE]
- Origin: https://github.com/<owner>/<repo> (path: <original/file/path>)
- Original License: <License SPDX> (e.g. Apache-2.0, MIT, GPL-3.0, None)
- Usage Status: ⚠️ PoC / Prototipo Experimental
- Production Note: Si este proyecto pasa a producción comercial, revisar la licencia.
                   (Permisiva = uso directo | Copyleft/Privativa = reescribir con Clean-Room).
"""
```
