"""CLI del motor. Uso:
  python correr.py validar   <carpeta_proyecto>   -> validacion.json + resumen corto (sin graficar)
  python correr.py todo      <carpeta_proyecto>   -> salida/: gráficos, despiece, pedido, (obra), propuesta.html
  python correr.py propuesta <carpeta_proyecto>   -> solo rearma salida/propuesta.html (tras precios o auditoría)
La carpeta del proyecto contiene ficha.json (única fuente de verdad) y, si existen, precios.json y auditoria.json.
Multipropósito: cada tipología (madera o hierro) es un módulo con modelo, validar, despiece y salidas.
"""
import os, sys, re, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import leer_json, escribir_json, escribir_txt, catalogo_tipologia
import portico, jaula_cerdas, perspectiva, detalles, croquis3d, obra, propuesta_web

TIPOLOGIAS = {"portico-hamacas": portico, "jaula-cerdas": jaula_cerdas}
CLAVES_VALIDACION = ("checks", "peso_propio_kg", "peso_total_kg", "volumen_madera_m3", "resumen")


def _cargar(dirp):
    ficha = leer_json(os.path.join(dirp, "ficha.json"))
    t = TIPOLOGIAS.get(ficha["tipologia"])
    if not t:
        sys.exit(f"Tipología no soportada: {ficha['tipologia']} (disponibles: {', '.join(TIPOLOGIAS)})")
    return ficha, t


def _opt(dirp, nombre):
    p = os.path.join(dirp, nombre)
    return leer_json(p) if os.path.exists(p) else None


def _val_json(v):
    return {k: v[k] for k in CLAVES_VALIDACION if k in v}


def validar(dirp):
    ficha, t = _cargar(dirp)
    M = t.modelo(ficha)
    v = t.validar(ficha, M)
    escribir_json(os.path.join(dirp, "validacion.json"), _val_json(v))
    print(v["resumen"])
    return v


def _salidas_portico(ficha, M, v, desp, precios, aud):
    """Pórtico de madera (v1): perspectiva por configuración, láminas de detalles, obra y propuesta con presupuesto."""
    ob = obra.obra(ficha, M)
    lam = detalles.laminas(ficha, M)
    persp = {c["id"]: perspectiva.svg(ficha, M, c["id"]) for c in ficha["requisitos"]["configuraciones"]}
    esc = croquis3d.escena(ficha, M)
    archivos = {"despiece.json": desp, "pedido.json": desp["pedido"], "obra.json": ob, "escena3d.json": esc}
    archivos.update({f"perspectiva-{k}.svg": s for k, s in persp.items()})
    archivos.update({f"detalle_{i}.svg": s for i, (tit, txt, s) in enumerate(lam, 1)})
    return {"archivos": archivos,
            "pagina": propuesta_web.pagina(ficha, M, v, desp, ob, lam, persp, esc, precios, aud),
            # el auditor no ve informes anteriores: el texto se arma sin el anexo de auditoría
            "pagina_auditor": propuesta_web.pagina(ficha, M, v, desp, ob, lam, persp, esc, precios, None),
            "presupuesto": propuesta_web.presupuesto(ficha, desp, precios)}


def todo(dirp, solo_propuesta=False):
    ficha, t = _cargar(dirp)
    sal = os.path.join(dirp, "salida")
    M = t.modelo(ficha)
    v = t.validar(ficha, M)
    desp = t.despiece(ficha, M)
    precios, aud = _opt(dirp, "precios.json"), _opt(dirp, "auditoria.json")
    if not catalogo_tipologia(ficha["tipologia"]).get("presupuesto", True):
        precios = None
    out = t.salidas(ficha, M, v, desp, precios, aud) if hasattr(t, "salidas") else _salidas_portico(ficha, M, v, desp, precios, aud)
    if not solo_propuesta:
        escribir_json(os.path.join(dirp, "validacion.json"), _val_json(v))
        for nombre, cont in out["archivos"].items():
            (escribir_json if nombre.endswith(".json") else escribir_txt)(os.path.join(sal, nombre), cont)
    escribir_txt(os.path.join(sal, "propuesta.html"), out["pagina"])
    # versión en texto plano para el auditor (no ve el razonamiento previo, solo lo que lee el cliente)
    txt = re.sub(r"<svg.*?</svg>", "[gráfico]", out["pagina_auditor"], flags=re.S)
    txt = re.sub(r"<script.*?</script>|<style.*?</style>", "", txt, flags=re.S)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", txt))
    escribir_txt(os.path.join(sal, "propuesta.txt"), re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n", txt)))
    print(v["resumen"].splitlines()[0])
    pres = out["presupuesto"]
    if pres is None:
        print(f"Sin presupuesto (la tipología no lo lleva) · auditoría: {aud['estado'] if aud else 'pendiente'}")
    else:
        print(f"Materiales sin IVA: {pres['subtotal_sin_iva']:,.0f} · faltan precios: {pres['faltan'] or 'ninguno'} · auditoría: {aud['estado'] if aud else 'pendiente'}")
    print("Salida:", os.path.abspath(sal))


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("validar", "todo", "propuesta"):
        sys.exit(__doc__)
    {"validar": validar, "todo": todo, "propuesta": lambda d: todo(d, True)}[sys.argv[1]](sys.argv[2])
