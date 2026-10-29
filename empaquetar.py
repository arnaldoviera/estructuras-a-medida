"""Empaqueta el plugin: dist/estructuras-a-medida.plugin = zip del directorio, sin archivos de sesión.
Antes revisa que el motor compile con Python 3.10 y 3.11 si están instalados (el plugin promete 3.10+)."""
import glob, os, shutil, subprocess, sys, tempfile, zipfile

RAIZ = os.path.dirname(os.path.abspath(__file__))
FUERA_DIRS = {".git", ".claude", "dist", "__pycache__", "proyectos"}
FUERA_ARCH = {"memoria.md", "CLAUDE.md", "empaquetar.py", ".gitignore"}

fuentes = sorted(glob.glob(os.path.join(RAIZ, "motor", "*.py")))
probados = []
for exe in ("python3.10", "python3.11"):
    if shutil.which(exe):
        with tempfile.TemporaryDirectory() as tmp:  # los .pyc van a una carpeta temporal, no al repo
            r = subprocess.run([exe, "-c", "import py_compile,sys\nfor f in sys.argv[2:]: py_compile.compile(f, cfile=sys.argv[1] + '/x.pyc', doraise=True)",
                                tmp, *fuentes], capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"El motor no compila con {exe}:\n{r.stderr.strip()}")
        probados.append(exe)

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
print(f"{dest} · {n} archivos · {os.path.getsize(dest) / 1024:.0f} KB · compila en: {', '.join(probados) or 'sin intérpretes 3.10/3.11 para probar'}")
