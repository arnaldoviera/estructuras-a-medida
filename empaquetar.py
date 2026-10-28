"""Empaqueta el plugin: dist/estructuras-a-medida.plugin = zip del directorio, sin insumos ni archivos de sesión."""
import os, zipfile

RAIZ = os.path.dirname(os.path.abspath(__file__))
FUERA_DIRS = {".git", ".claude", "dist", "insumos", "__pycache__", "proyectos"}
FUERA_ARCH = {"memoria.md", "CLAUDE.md", "insumos-portico.zip", "empaquetar.py"}

os.makedirs(os.path.join(RAIZ, "dist"), exist_ok=True)
dest = os.path.join(RAIZ, "dist", "estructuras-a-medida.plugin")
n = 0
with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
    for base, dirs, files in os.walk(RAIZ):
        dirs[:] = sorted(d for d in dirs if d not in FUERA_DIRS)
        for f in sorted(files):
            if f in FUERA_ARCH or f.endswith(".pyc"):
                continue
            p = os.path.join(base, f)
            z.write(p, os.path.relpath(p, RAIZ).replace(os.sep, "/"))
            n += 1
print(f"{dest} · {n} archivos · {os.path.getsize(dest) / 1024:.0f} KB")
