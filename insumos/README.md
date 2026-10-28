# Insumos (referencia)

Material del pórtico cerrado con el usuario antes del plugin (portico-v3). El plugin no los ejecuta: `motor/` es el refactor que lee ficha.json.

- `perspectiva/plano.py` → `motor/perspectiva.py`
- `detalles/detalles.py` → `motor/detalles.py` + `motor/_fig.py`
- `pagina/index.html` → base de `skills/propuesta-web/assets/plantilla.html`
- `croquis-3d/`: adaptación de la skill "anatomy-reveal" (repo annnguyentt/anatomy-reveal-skill, commit dd01e1c, licencia MIT; kit Anatomy de wheresryan22, MIT). Requería Node 20+, Chrome headless, ffmpeg e ImageMagick; en el plugin se reemplazó por un visor Three.js.
