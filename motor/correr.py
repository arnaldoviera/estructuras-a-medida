"""CLI del motor. Uso:
  python correr.py validar   <carpeta_proyecto>   -> validacion.json + resumen corto (sin graficar)
  python correr.py todo      <carpeta_proyecto>   -> salida/: gráficos, despiece, pedido, obra, propuesta.html
  python correr.py propuesta <carpeta_proyecto>   -> solo rearma salida/propuesta.html (tras precios o auditoría)
La carpeta del proyecto contiene ficha.json (única fuente de verdad) y, si existen, precios.json y auditoria.json.
"""
import os, sys, re, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import leer_json, escribir_json, escribir_txt
import portico, perspectiva, detalles, croquis3d, obra, propuesta_web

TIPOLOGIAS = {"portico-hamacas": portico}


def _cargar(dirp):
    ficha = leer_json(os.path.join(dirp, "ficha.json"))
    t = TIPOLOGIAS.get(ficha["tipologia"])
    if not t:
        sys.exit(f"Tipología no soportada en v1: {ficha['tipologia']}")
    return ficha, t


def _opt(dirp, nombre):
    p = os.path.join(dirp, nombre)
    return leer_json(p) if os.path.exists(p) else None


def validar(dirp):
    ficha, t = _cargar(dirp)
    M = t.modelo(ficha)
    v = t.validar(ficha, M)
    escribir_json(os.path.join(dirp, "validacion.json"), {k: v[k] for k in ("checks", "peso_propio_kg", "peso_total_kg", "volumen_madera_m3", "resumen")})
    print(v["resumen"])
    return v


def todo(dirp, solo_propuesta=False):
    ficha, t = _cargar(dirp)
    sal = os.path.join(dirp, "salida")
    M = t.modelo(ficha)
    v = t.validar(ficha, M)
    desp = t.despiece(ficha, M)
    ob = obra.obra(ficha, M)
    lam = detalles.laminas(ficha, M)
    persp = {c["id"]: perspectiva.svg(ficha, M, c["id"]) for c in ficha["requisitos"]["configuraciones"]}
    esc = croquis3d.escena(ficha, M)
    if not solo_propuesta:
        escribir_json(os.path.join(dirp, "validacion.json"), {k: v[k] for k in ("checks", "peso_propio_kg", "peso_total_kg", "volumen_madera_m3", "resumen")})
        escribir_json(os.path.join(sal, "despiece.json"), desp)
        escribir_json(os.path.join(sal, "pedido.json"), desp["pedido"])
        escribir_json(os.path.join(sal, "obra.json"), ob)
        escribir_json(os.path.join(sal, "escena3d.json"), esc)
        for k, s in persp.items():
            escribir_txt(os.path.join(sal, f"perspectiva-{k}.svg"), s)
        for i, (tit, txt, s) in enumerate(lam, 1):
            escribir_txt(os.path.join(sal, f"detalle_{i}.svg"), s)
    precios, aud = _opt(dirp, "precios.json"), _opt(dirp, "auditoria.json")
    page = propuesta_web.pagina(ficha, M, v, desp, ob, lam, persp, esc, precios, aud)
    escribir_txt(os.path.join(sal, "propuesta.html"), page)
    # versión en texto plano para el auditor (no ve el razonamiento previo, solo lo que lee el cliente)
    # el auditor no ve informes anteriores: el texto se arma sin el anexo de auditoría
    base = propuesta_web.pagina(ficha, M, v, desp, ob, lam, persp, esc, precios, None)
    txt = re.sub(r"<svg.*?</svg>", "[gráfico]", base, flags=re.S)
    txt = re.sub(r"<script.*?</script>|<style.*?</style>", "", txt, flags=re.S)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", txt))
    escribir_txt(os.path.join(sal, "propuesta.txt"), re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n", txt)))
    pres = propuesta_web.presupuesto(ficha, desp, precios)
    print(v["resumen"].splitlines()[0])
    print(f"Materiales sin IVA: {pres['subtotal_sin_iva']:,.0f} · faltan precios: {pres['faltan'] or 'ninguno'} · auditoría: {aud['estado'] if aud else 'pendiente'}")
    print("Salida:", os.path.abspath(sal))


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("validar", "todo", "propuesta"):
        sys.exit(__doc__)
    {"validar": validar, "todo": todo, "propuesta": lambda d: todo(d, True)}[sys.argv[1]](sys.argv[2])
