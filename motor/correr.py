"""CLI del motor. Uso:
  python3 correr.py validar   <carpeta_proyecto>   -> validacion.json + resumen corto (sin graficar)
  python3 correr.py todo      <carpeta_proyecto>   -> salida/: gráficos, despiece, pedido, (obra), propuesta.html
  python3 correr.py propuesta <carpeta_proyecto>   -> solo rearma salida/propuesta.html (tras precios o auditoría)
La carpeta del proyecto contiene ficha.json (única fuente de verdad) y, si existen, precios.json y auditoria.json.
Multipropósito: cada tipología (madera o hierro) es un módulo con modelo, validar, despiece y salidas.
"""
import datetime, hashlib, json, os, sys, re, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import leer_json, escribir_json, escribir_txt, catalogo_tipologia, num
import portico, jaula_cerdas, perspectiva, detalles, croquis3d, obra, propuesta_web

TIPOLOGIAS = {"portico-hamacas": portico, "jaula-cerdas": jaula_cerdas}
CLAVES_VALIDACION = ("checks", "peso_propio_kg", "peso_total_kg", "volumen_madera_m3", "resumen")

# claves mínimas para que la corrida no se rompa (ruta con puntos → tipo esperado)
COMUNES = {"proyecto.marca": str, "proyecto.numero": str, "proyecto.fecha": str, "proyecto.validez_dias": int, "proyecto.titulo": str,
           "cliente.localidad": str, "cliente.provincia": str, "requisitos.uso": str,
           "comercial.mod.texto": str, "comercial.iva_pct": (int, float), "comercial.mostrar_con_iva": bool}
REQUERIDOS = {
    "portico-hamacas": {"requisitos.configuraciones": list, "requisitos.carga_diseno_kg": (int, float), "requisitos.factor_dinamico": (int, float),
                        "requisitos.carga_por_puesto_kg": (int, float), "requisitos.espacio.largo_eje_travesano_m": (int, float),
                        "requisitos.espacio.largo_vaiven_m": (int, float), "diseno.material": str, "diseno.travesano": dict, "diseno.patas": dict,
                        "diseno.tirante": dict, "diseno.cartela": dict, "diseno.varillas": dict, "diseno.cuelgues.puestos_x": list,
                        "diseno.accesorios": dict, "diseno.apoyo": dict},
    "jaula-cerdas": {"requisitos.galpon.slat.ancho": (int, float), "requisitos.galpon.slat.ranura": (int, float),
                     "requisitos.linea_alimento.z": (int, float), "requisitos.linea_alimento.diam": (int, float),
                     "diseno.box.largo": (int, float), "diseno.box.ancho_libre": (int, float), "diseno.box.alto": (int, float),
                     "diseno.tubos": dict, "diseno.largueros_z": list, "diseno.parantes_x": list, "diseno.puerta": dict, "diseno.frente.travesanos_z": list,
                     "diseno.frente.barrotes_cant": int, "diseno.pie.pletina": dict, "diseno.comedero": dict, "diseno.caida": dict,
                     "diseno.dosificador": dict, "diseno.rfid": dict},
}


class ErrorFicha(Exception):
    pass


def _get(d, ruta):
    for k in ruta.split("."):
        if not isinstance(d, dict) or k not in d:
            raise KeyError(ruta)
        d = d[k]
    return d


def _revisar_ficha(ficha):
    """Chequeo mínimo de claves y tipos, con mensajes entendibles (el detalle está en skills/relevamiento/references/ficha-schema.json)."""
    tip = ficha.get("tipologia")
    if tip not in TIPOLOGIAS:
        raise ErrorFicha(f"tipología no soportada: {tip!r} (disponibles: {', '.join(TIPOLOGIAS)})")
    errores = []
    for ruta, tipo in {**COMUNES, **REQUERIDOS[tip]}.items():
        try:
            v = _get(ficha, ruta)
        except KeyError:
            errores.append(f"falta {ruta}")
            continue
        if isinstance(v, bool) and tipo is not bool or not isinstance(v, tipo):
            errores.append(f"{ruta} tiene un valor de tipo {type(v).__name__} ({v!r})")
    try:
        datetime.date.fromisoformat(str(ficha.get("proyecto", {}).get("fecha")))
    except ValueError:
        errores.append("proyecto.fecha tiene que ir como AAAA-MM-DD")
    for ruta in ("diseno.largueros_z", "diseno.parantes_x") if tip == "jaula-cerdas" else ("diseno.cuelgues.puestos_x",):
        try:
            if len(_get(ficha, ruta)) < (2 if "parantes" in ruta else 1):
                errores.append(f"{ruta} no tiene suficientes valores")
        except (KeyError, TypeError):
            pass
    if errores:
        raise ErrorFicha("la ficha tiene problemas:\n  - " + "\n  - ".join(errores))


def _cargar(dirp):
    ruta = os.path.join(dirp, "ficha.json")
    if not os.path.exists(ruta):
        raise ErrorFicha(f"no encuentro {ruta}: la carpeta del proyecto tiene que tener ficha.json")
    try:
        ficha = leer_json(ruta)
    except json.JSONDecodeError as e:
        raise ErrorFicha(f"ficha.json no es JSON válido (línea {e.lineno}, columna {e.colno}): {e.msg}")
    _revisar_ficha(ficha)
    return ficha, TIPOLOGIAS[ficha["tipologia"]]


def _opt(dirp, nombre):
    p = os.path.join(dirp, nombre)
    if not os.path.exists(p):
        return None
    try:
        return leer_json(p)
    except json.JSONDecodeError as e:
        raise ErrorFicha(f"{nombre} no es JSON válido (línea {e.lineno}, columna {e.colno}): {e.msg}")


def huella_ficha(dirp):
    """sha256 de ficha.json: el auditor la copia en auditoria.json para atar el informe a la ficha que revisó."""
    with open(os.path.join(dirp, "ficha.json"), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _auditoria(dirp):
    aud = _opt(dirp, "auditoria.json")
    if aud is None:
        return None
    if "vueltas" not in aud and "vuelta" in aud:  # formato anterior
        aud["vueltas"] = aud["vuelta"]
    h = aud.get("ficha_sha256")
    if h is None:
        aud["_aviso"] = "Este informe no indica qué versión de la ficha revisó: puede no corresponder al diseño actual."
    elif h != huella_ficha(dirp):
        aud["_aviso"] = "La ficha cambió después de esta auditoría: el informe corresponde a una versión anterior del diseño y hay que volver a auditar."
    return aud


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
    """Pórtico de madera: perspectiva por configuración, láminas de detalles, obra y propuesta con presupuesto."""
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
    precios, aud = _opt(dirp, "precios.json"), _auditoria(dirp)
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
    estado_aud = (aud["estado"] + (" (desactualizada)" if aud.get("_aviso") else "")) if aud else "pendiente"
    pres = out["presupuesto"]
    if pres is None:
        print(f"Sin presupuesto (la tipología no lo lleva) · auditoría: {estado_aud}")
    else:
        faltan = "; ".join(pres["faltan"]) or "ninguno"
        print(f"Materiales sin IVA: $ {num(pres['subtotal_sin_iva'], 0)} · faltan precios: {faltan} · auditoría: {estado_aud}")
    print("Salida:", os.path.abspath(sal))
    print("Huella de la ficha (para auditoria.json):", huella_ficha(dirp))


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("validar", "todo", "propuesta"):
        sys.exit(__doc__)
    try:
        {"validar": validar, "todo": todo, "propuesta": lambda d: todo(d, True)}[sys.argv[1]](sys.argv[2])
    except ErrorFicha as e:
        sys.exit(f"Error: {e}")
    except (KeyError, TypeError, ValueError, IndexError) as e:
        sys.exit(f"Error: la ficha tiene un dato faltante o con formato inesperado ({type(e).__name__}: {e}). "
                 "Revisala contra el ejemplo de la tipología en ejemplos/ y contra skills/relevamiento/references/ficha-schema.json.")
