"""Utilidades comunes: lectura de ficha/catálogo, vectores y formato rioplatense."""
import json, math, os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def leer_json(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def escribir_json(ruta, datos):
    os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def escribir_txt(ruta, texto):
    os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)


def catalogo_materiales():
    return leer_json(os.path.join(RAIZ, "catalogo", "materiales.json"))


def catalogo_tipologia(tid):
    return leer_json(os.path.join(RAIZ, "catalogo", "tipologias", f"{tid}.json"))


# ---- formato (coma decimal) ----
def num(v, dec=2):
    s = f"{v:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def m(mm, dec=2):
    """mm -> '2,10 m'"""
    return num(mm / 1000, dec) + " m"


def cm(mm, dec=0):
    return num(mm / 10, dec) + " cm"


def pesos(v):
    return "$ " + num(v, 0)


# ---- varilla roscada (se vende en pulgadas) ----
PULG = {10: '3/8"', 12: '1/2"', 16: '5/8"', 20: '3/4"'}
D_REAL = {10: 9.53, 12: 12.7, 16: 15.88, 20: 19.05}
LLAVE = {10: '9/16" (14 mm)', 12: '3/4" (19 mm)', 16: '15/16" (24 mm)', 20: '1 1/8" (29 mm)'}


def ag(d, holgura=2):
    """Diámetro de mecha (mm entero) = diámetro real de la varilla + holgura, redondeado para arriba."""
    return math.ceil(D_REAL.get(d, d) + holgura - 1e-9)


# ---- vectores ----
def add(a, b): return [a[i] + b[i] for i in range(3)]
def sub(a, b): return [a[i] - b[i] for i in range(3)]
def mul(a, k): return [a[i] * k for i in range(3)]
def dot(a, b): return sum(a[i] * b[i] for i in range(3))
def cross(a, b): return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
def norm(a): return math.sqrt(dot(a, a))
def unit(a):
    n = norm(a)
    return [a[i] / n for i in range(3)]
