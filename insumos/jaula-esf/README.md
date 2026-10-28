# Jaula de alimentación para cerdas gestantes — insumos (referencia)

Material con el que se diseñó y auditó la tipología `jaula-cerdas` antes de pasarla al plugin. El plugin no lo ejecuta: `motor/jaula_cerdas.py` es el refactor que lee `ficha.json` (ejemplo en `ejemplos/jaula-cerdas/`).

- `cuaderno/`: consultas y respuestas del cuaderno NotebookLM «ESF — Jaulas mecánicas y estructuras tubulares de estaciones de alimentación de cerdas» (https://notebooklm.google.com/notebook/a543a6b6-bcf8-4c34-b602-5330eda9cbfb, unas 50 fuentes: manuales, patentes, guías de extensión y videos del Gestal 3G). Es la evidencia que respalda lo marcado «fuente».
- `medidas.json` → `ejemplos/jaula-cerdas/ficha.json` (bloque `diseno`).
- `genera.py` + `plantilla.html` → `motor/jaula_cerdas.py` (planta, lateral, 3D) + `skills/propuesta-web/assets/plantilla-jaula.html`.
- `despiece.py` → `motor/jaula_cerdas.py` (`despiece`).
- `auditoria.json`: vuelta 5 de la auditoría independiente (10/34 → 23/39 → 27/39 → 35/40 → 35/37), copiada también en el ejemplo.
- `jaula.html`: anteproyecto publicado en https://claude.ai/artifact/WFimpCdmgAyx1dkKdxoqV1 antes de pasar al plugin.

Uso suelto (opcional): `python3 genera.py` desde esta carpeta regenera `jaula.html` y `despiece.json`.
