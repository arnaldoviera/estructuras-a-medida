"""Tipología estructura-libre (madera y/o hierro): muebles y estructuras simples armados como lista de piezas.
La ficha describe secciones, barras (dos puntos) y placas (cajas alineadas a los ejes); de ahí salen el croquis 3D,
planta/frente/lateral, verificaciones genéricas, despiece con plan de corte y pedido sin precios.
Medidas en mm. Ejes: x a lo largo (frente), y hacia el fondo, z arriba; el piso es z = 0."""
import datetime, html, json, math, os
from comun import catalogo_tipologia, catalogo_materiales, num, RAIZ

E = html.escape
G = 9.81
ACERO = {"E": 200000, "fy": 235, "dens": 7850}
TIPOS = ("tubo-rect", "tubo-redondo", "madera", "planchuela")


def mm(v):
    return f"{v:,.0f}".replace(",", ".")


def _tag(origen):
    o = (origen or "").strip().lower()
    return next((t for t in ("fuente", "criterio", "cálculo", "supuesto") if o.startswith(t)), "supuesto")


# ======================================================================
# Revisión de la ficha (la llama correr.py antes de modelar)
# ======================================================================
def revisar(ficha):
    """Errores de coherencia que el chequeo de tipos de correr.py no ve: referencias a secciones y materiales, puntos mal cargados."""
    d, cat = ficha["diseno"], catalogo_materiales()
    err = []
    mad, tab = cat.get("maderas_aserradas", {}), cat.get("tableros", {})
    for k, s in d["secciones"].items():
        t = s.get("tipo")
        if t not in TIPOS:
            err.append(f"diseno.secciones.{k}.tipo tiene que ser uno de {', '.join(TIPOS)} (tiene {t!r})")
            continue
        req = {"tubo-rect": ("b", "h", "esp"), "tubo-redondo": ("diam", "esp"), "madera": ("b", "h", "material"), "planchuela": ("b", "h")}[t]
        for c in req:
            if c not in s:
                err.append(f"falta diseno.secciones.{k}.{c}")
        if t == "madera" and s.get("material") not in mad:
            err.append(f"diseno.secciones.{k}.material {s.get('material')!r} no está en catalogo/materiales.json (maderas_aserradas)")
        if t in ("tubo-rect", "tubo-redondo") and "esp" in s and ("b" in s or "diam" in s):
            if 2 * s["esp"] >= min(s.get("b", s.get("diam", 0)), s.get("h", s.get("diam", 0))):
                err.append(f"diseno.secciones.{k}: el espesor no entra en la sección")
    ids = set()
    for i, b in enumerate(d["barras"]):
        nom = f"diseno.barras[{i}]"
        if b.get("id") in ids:
            err.append(f"{nom}: id repetido {b.get('id')!r}")
        ids.add(b.get("id"))
        if b.get("seccion") not in d["secciones"]:
            err.append(f"{nom}.seccion {b.get('seccion')!r} no está en diseno.secciones")
        for c in ("a", "b"):
            if not (isinstance(b.get(c), list) and len(b[c]) == 3 and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in b[c])):
                err.append(f"{nom}.{c} tiene que ser [x, y, z] en mm")
        if isinstance(b.get("a"), list) and b.get("a") == b.get("b"):
            err.append(f"{nom}: los dos puntos son iguales (largo cero)")
        if "ancho_carga" in b and not (isinstance(b["ancho_carga"], (int, float)) and b["ancho_carga"] > 0):
            err.append(f"{nom}.ancho_carga tiene que ser un número de mm mayor que cero")
        if b.get("rol", "viga") not in ("pata", "viga", "riostra"):
            err.append(f"{nom}.rol tiene que ser pata, viga o riostra")
    for i, p in enumerate(d["placas"]):
        nom = f"diseno.placas[{i}]"
        if p.get("id") in ids:
            err.append(f"{nom}: id repetido {p.get('id')!r}")
        ids.add(p.get("id"))
        if p.get("material") not in tab:
            err.append(f"{nom}.material {p.get('material')!r} no está en catalogo/materiales.json (tableros)")
        for c in ("x", "y", "z"):
            v = p.get(c)
            if not (isinstance(v, list) and len(v) == 2 and all(isinstance(t, (int, float)) for t in v) and v[1] > v[0]):
                err.append(f"{nom}.{c} tiene que ser [desde, hasta] en mm, con hasta > desde")
        if p.get("material") in tab and isinstance(p.get("z"), list) and len(p["z"]) == 2:
            esp = tab[p["material"]]["espesor_mm"]
            if abs((p["z"][1] - p["z"][0]) - esp) > 0.5:
                err.append(f"{nom}: el espesor (z) no coincide con el del tablero {p['material']} ({esp} mm)")
    cu = catalogo_tipologia("estructura-libre")["criterios"]["cargas_por_uso"]
    faltan = [k for k in ("distribuida_kg_m2", "puntual_kg", "empuje_lateral_kg", "carga_borde_kg") if k not in ficha["requisitos"].get("cargas", {})]
    if ficha["requisitos"]["tipo_uso"] not in cu and faltan:
        err.append(f"requisitos.tipo_uso {ficha['requisitos']['tipo_uso']!r} no tiene cargas en el catálogo "
                   f"({', '.join(k for k in cu if not k.startswith('_') and k != 'origen')}): cargá requisitos.cargas con {', '.join(faltan)}")
    if not any(b.get("rol") == "pata" for b in d["barras"]):
        err.append("diseno.barras: ninguna barra tiene rol 'pata' (la estructura tiene que apoyar en el piso)")
    return err


# ======================================================================
# Secciones y materiales
# ======================================================================
def _prop(s):
    """Área (mm²), inercias (mm⁴) fuerte (alto h vertical) y mínima, módulo resistente, kg/m, módulo E y tensión admisible."""
    t = s["tipo"]
    if t == "tubo-redondo":
        D, e = s["diam"], s["esp"]
        A = math.pi / 4 * (D ** 2 - (D - 2 * e) ** 2)
        I = math.pi / 64 * (D ** 4 - (D - 2 * e) ** 4)
        return {"A": A, "I": I, "I2": I, "Imin": I, "W": 2 * I / D, "h": D, "b": D, "kg_m": A * ACERO["dens"] * 1e-6,
                "E": ACERO["E"], "acero": True, "f": ACERO["fy"]}
    b, h = s["b"], s["h"]
    if t == "tubo-rect":
        e = s["esp"]
        A = b * h - (b - 2 * e) * (h - 2 * e)
        I = (b * h ** 3 - (b - 2 * e) * (h - 2 * e) ** 3) / 12
        I2 = (h * b ** 3 - (h - 2 * e) * (b - 2 * e) ** 3) / 12
    else:
        A, I, I2 = b * h, b * h ** 3 / 12, h * b ** 3 / 12
    if t == "madera":
        m = catalogo_materiales()["maderas_aserradas"][s["material"]]
        return {"A": A, "I": I, "I2": I2, "Imin": min(I, I2), "W": 2 * I / h, "h": h, "b": b, "kg_m": A * m["densidad_kg_m3"] * 1e-6,
                "E": m["E_MPa"], "acero": False, "f": m["tension_flexion_adm_MPa"], "fc": m["tension_compresion_adm_MPa"]}
    return {"A": A, "I": I, "I2": I2, "Imin": min(I, I2), "W": 2 * I / h, "h": h, "b": b, "kg_m": A * ACERO["dens"] * 1e-6,
            "E": ACERO["E"], "acero": True, "f": ACERO["fy"]}


def _fmt(v):
    return num(v, 0) if float(v).is_integer() else num(v, 2).rstrip("0").rstrip(",")


def nombre_seccion(s):
    """Nombre comercial desde las medidas (lo que se pide en el corralón), con aviso si no es medida de catálogo."""
    cat = catalogo_materiales()
    t = s["tipo"]
    if t == "tubo-rect":
        c = cat["metales"]["tubo-estructural-cuadrado"]
        ok = (f"{_fmt(s['b'])}x{_fmt(s['h'])}" in c["secciones_mm"] or f"{_fmt(s['h'])}x{_fmt(s['b'])}" in c["secciones_mm"]) and s["esp"] in c["espesores_mm"]
        base = f"caño estructural {'cuadrado' if s['b'] == s['h'] else 'rectangular'} {_fmt(s['b'])} × {_fmt(s['h'])} × {num(s['esp'], 1)}"
    elif t == "tubo-redondo":
        c = cat["metales"]["tubo-estructural-redondo"]
        pulg = next((k for k, v in c["diametros_mm"].items() if abs(v - s["diam"]) < 0.2), None)
        ok = bool(pulg) and s["esp"] in c["espesores_mm"]
        base = f"caño estructural redondo Ø{num(s['diam'], 1)} × {num(s['esp'], 1)}" + (f" ({pulg})" if pulg else "")
    elif t == "madera":
        c = cat["maderas_aserradas"]
        pb, ph = _pulgadas(s["b"], c), _pulgadas(s["h"], c)
        ok = bool(pb and ph)
        base = f"{c[s['material']]['nombre'].split(' (')[0].lower()} {_fmt(s['b'])} × {_fmt(s['h'])}" + (f" ({pb} × {ph})" if ok else "")
    else:
        c = cat["metales"]["planchuela-galvanizada"]
        ok = f"{_fmt(s['b'])}x{_fmt(s['h'])}" in c["secciones_mm"]
        base = f"planchuela {_fmt(s['b'])} × {_fmt(s['h'])}"
    return base if ok else base + " (medida no comercial)", ok


def _pulgadas(v, c):
    """Medida nominal en pulgadas que corresponde a una medida real: la nominal o la nominal menos el cepillado."""
    for tabla in (c["espesores_nominales_pulg"], c["anchos_nominales_pulg"]):
        for k, nom in tabla.items():
            if abs(v - nom) <= 1.5 or abs(v - (nom - c["descuento_cepillado_mm"])) <= 3:
                return k
    return None


def _clase(s):
    """Material para el 3D y los planos según la terminación."""
    if s["tipo"] == "madera":
        return "madera"
    a = (s.get("acabado") or "").lower()
    return "galva" if "galva" in a else "inox" if "inox" in a else "acero_claro" if any(k in a for k in ("blanc", "gris", "clar")) else "acero"


def _clase_placa(p, tab):
    a = (p.get("acabado") or "").lower()
    if a:
        return "blanco" if "blanc" in a else "madera_oscura" if "oscur" in a else "acero" if "negr" in a else "madera"
    mat = p["material"]
    return "acero" if mat.startswith("chapa") else "blanco" if mat.startswith("melamina") else "tablero" if mat.startswith(("mdf", "fenol")) else "madera"


# ======================================================================
# Modelo
# ======================================================================
def _eje(b):
    d = [b["b"][i] - b["a"][i] for i in range(3)]
    L = math.sqrt(sum(v * v for v in d))
    ax = [i for i in range(3) if abs(d[i]) > 1e-6]
    return d, L, (ax[0] if len(ax) == 1 else None)


def _caja_barra(b, s, P, eje):
    """Caja alineada a los ejes de una barra recta paralela a un eje: el alto h de la sección va vertical (o en y si la barra es vertical)."""
    a, c = b["a"], b["b"]
    if eje == 2:
        ex = [P["b"] / 2, P["h"] / 2, 0]
    elif eje == 0:
        ex = [0, P["b"] / 2, P["h"] / 2]
    else:
        ex = [P["b"] / 2, 0, P["h"] / 2]
    return [sorted([a[i] - ex[i], c[i] + ex[i]]) if a[i] <= c[i] else sorted([c[i] - ex[i], a[i] + ex[i]]) for i in range(3)]


def modelo(ficha):
    d = ficha["diseno"]
    tab = catalogo_materiales()["tableros"]
    secc = {k: dict(s, **{"_p": _prop(s)}) for k, s in d["secciones"].items()}
    barras, placas, piezas3d, cajas3d = [], [], [], []
    for b in d["barras"]:
        s = secc[b["seccion"]]
        P = s["_p"]
        dv, L, eje = _eje(b)
        cls = _clase(s)
        caja = _caja_barra(b, s, P, eje) if eje is not None and s["tipo"] != "tubo-redondo" else None
        if caja:
            cajas3d.append({"n": b.get("nombre", b["id"]), "x": caja[0], "y": caja[1], "z": caja[2], "m": cls})
        else:
            piezas3d.append({"n": b.get("nombre", b["id"]), "a": b["a"], "b": b["b"], "r": max(P["b"], P["h"]) / 2, "m": cls})
        cen = [(b["a"][i] + b["b"][i]) / 2 for i in range(3)]
        barras.append({"id": b["id"], "nombre": b.get("nombre", b["id"]), "rol": b.get("rol", "viga"), "seccion": b["seccion"], "s": s, "P": P,
                       "L": L, "eje": eje, "caja": caja, "a": b["a"], "b": b["b"], "cen": cen, "kg": P["kg_m"] * L / 1000,
                       "clase": cls, "corte": b.get("corte", "recto"), "grupo": b.get("grupo", "estructura"), "ancho_carga": b.get("ancho_carga")})
    for p in d["placas"]:
        t = tab[p["material"]]
        dims = [p[c][1] - p[c][0] for c in "xyz"]
        kg = dims[0] * dims[1] * dims[2] * 1e-9 * t["densidad_kg_m3"]
        cls = _clase_placa(p, tab)
        cajas3d.append({"n": p.get("nombre", p["id"]), "x": p["x"], "y": p["y"], "z": p["z"], "m": cls})
        placas.append({"id": p["id"], "nombre": p.get("nombre", p["id"]), "mat": p["material"], "t": t, "x": p["x"], "y": p["y"], "z": p["z"],
                       "dims": dims, "kg": kg, "cen": [sum(p[c]) / 2 for c in "xyz"], "clase": cls, "grupo": p.get("grupo", "placas"),
                       "fijacion": p.get("fijacion", "")})
    # caja envolvente
    xs, ys, zs = [], [], []
    for c in cajas3d:
        xs += c["x"]; ys += c["y"]; zs += c["z"]
    for c in piezas3d:  # el radio solo suma en las direcciones perpendiculares al eje del caño
        dv = [c["b"][i] - c["a"][i] for i in range(3)]
        Lc = math.sqrt(sum(v * v for v in dv))
        ex = [c["r"] * math.sqrt(max(0.0, 1 - (dv[i] / Lc) ** 2)) for i in range(3)]
        for q in (c["a"], c["b"]):
            xs += [q[0] - ex[0], q[0] + ex[0]]; ys += [q[1] - ex[1], q[1] + ex[1]]; zs += [q[2] - ex[2], q[2] + ex[2]]
    env = {"x": [min(xs), max(xs)], "y": [min(ys), max(ys)], "z": [min(zs), max(zs)]}
    patas = [b for b in barras if b["rol"] == "pata"]
    pies = [min(b["a"], b["b"], key=lambda q: q[2]) for b in patas]
    huella = {"x": [min(q[0] for q in pies), max(q[0] for q in pies)], "y": [min(q[1] for q in pies), max(q[1] for q in pies)]}
    peso = sum(b["kg"] for b in barras) + sum(p["kg"] for p in placas)
    cg = [sum(e["kg"] * e["cen"][i] for e in barras + placas) / peso for i in range(3)]
    tam = max(env["x"][1] - env["x"][0], env["y"][1] - env["y"][0], env["z"][1] - env["z"][0])
    escena = {"piezas": piezas3d, "cajas": cajas3d, "centro": [sum(env[c]) / 2 for c in "xyz"], "tam": tam,
              "piso": [[env["x"][0] - tam * .4, env["x"][1] + tam * .4], [env["y"][0] - tam * .4, env["y"][1] + tam * .4]]}
    return {"secc": secc, "barras": barras, "placas": placas, "env": env, "patas": patas, "huella": huella,
            "peso": peso, "cg": cg, "escena": escena}


# ======================================================================
# Validación (cálculo simplificado de anteproyecto)
# ======================================================================
def _chk(lst, id_, requisito, valor, limite, estado, nota=""):
    if isinstance(estado, bool):
        estado = "cumple" if estado else "no cumple"
    lst.append({"id": id_, "requisito": requisito, "valor": valor, "limite": limite, "estado": estado, "nota": nota})


def cargas(ficha):
    """Cargas de uso: las de la ficha pisan las del catálogo para el tipo de uso."""
    cr = catalogo_tipologia("estructura-libre")["criterios"]
    base = dict(cr["cargas_por_uso"].get(ficha["requisitos"]["tipo_uso"], {}))
    base.update({k: v for k, v in ficha["requisitos"].get("cargas", {}).items() if not k.startswith("_")})
    return base


def _apoyos(M, p):
    """Vigas horizontales sobre las que apoya la placa, agrupadas por dirección: {0: [(coord_y, barra)], 1: [(coord_x, barra)]}."""
    fam = {0: [], 1: []}
    for b in M["barras"]:
        if b["rol"] == "pata" or b["eje"] not in (0, 1):
            continue
        tope = b["a"][2] + b["P"]["h"] / 2
        if abs(tope - p["z"][0]) > 3:
            continue
        dentro = all(p["x"][0] - 5 <= q[0] <= p["x"][1] + 5 and p["y"][0] - 5 <= q[1] <= p["y"][1] + 5 for q in (b["a"], b["b"]))
        if dentro:
            fam[b["eje"]].append((b["a"][1] if b["eje"] == 0 else b["a"][0], b))
    for k in fam:
        fam[k].sort(key=lambda t: t[0])
    return fam


def _tributarias(fam_k, lim):
    """Ancho tributario de cada viga de una familia sobre una placa entre lim[0] y lim[1]."""
    out = []
    cs = [c for c, _ in fam_k]
    for i, (c, b) in enumerate(fam_k):
        izq = (c - cs[i - 1]) / 2 if i else c - lim[0]
        der = (cs[i + 1] - c) / 2 if i + 1 < len(cs) else lim[1] - c
        out.append((b, izq + der))
    return out


def validar(ficha, M=None):
    M = M or modelo(ficha)
    cr = catalogo_tipologia("estructura-libre")["criterios"]
    Q = cargas(ficha)
    gf, gm = cr["factor_carga"]["valor"], cr["gamma_acero"]["valor"]
    div, bp = cr["flecha_max"]["divisor"], cr["ancho_puntual_mm"]["valor"]
    out = []
    q_uso = Q["distribuida_kg_m2"] * G * 1e-6  # N/mm²
    P_p = Q["puntual_kg"] * G
    env = M["env"]
    largo, ancho, alto = env["x"][1] - env["x"][0], env["y"][1] - env["y"][0], env["z"][1] - env["z"][0]
    med = ficha["requisitos"].get("medidas", {})
    for k, v, nom in (("largo", largo, "Largo total"), ("ancho", ancho, "Ancho total"), ("alto", alto, "Alto total")):
        if k in med:
            _chk(out, f"dim.{k}", f"{nom} igual al pedido", f"{mm(v)} mm", f"{mm(med[k])} ± 5 mm", abs(v - med[k]) <= 5)

    # secciones comerciales y largos
    cat = catalogo_materiales()
    nc = [f"{k}: {nombre_seccion(s)[0]}" for k, s in M["secc"].items() if not nombre_seccion(s)[1]]
    _chk(out, "mat.secciones", "Secciones en medidas comerciales (caño estructural, madera en pulgadas)",
         "todas de catálogo" if not nc else "; ".join(nc), "medidas de catálogo", "cumple" if not nc else "dudoso",
         "" if not nc else "Confirmar con el proveedor o cambiar a la medida comercial más cercana.")
    largos = []
    for b in M["barras"]:
        maxl = (cat["metales"]["tubo-estructural-cuadrado" if b["s"]["tipo"] == "tubo-rect" else "tubo-estructural-redondo"]["largo_barra_mm"]
                if b["s"]["tipo"] != "madera" else max(cat["maderas_aserradas"]["largos_comerciales_m"]) * 1000)
        if b["L"] > maxl:
            largos.append(f"{b['id']} {mm(b['L'])} > {mm(maxl)}")
    _chk(out, "mat.largos", "Cada barra sale de una barra o tirante comercial sin empalmes", "todas entran" if not largos else "; ".join(largos),
         "≤ largo comercial", not largos)
    no_entra = []
    for p in M["placas"]:
        hx, hy = p["t"]["hoja_mm"]
        a, b = sorted(p["dims"][:2], reverse=True)
        if not (a <= max(hx, hy) and b <= min(hx, hy)):
            no_entra.append(f"{p['id']} {mm(a)} × {mm(b)} > hoja {mm(hx)} × {mm(hy)}")
    if M["placas"]:
        _chk(out, "mat.placas", "Cada placa sale de una hoja entera sin empalmes", "todas entran" if not no_entra else "; ".join(no_entra),
             "≤ medida de hoja", not no_entra)

    # placas: flexión y flecha en una dirección entre apoyos
    carga_viga = {}
    for p in M["placas"]:
        fam = _apoyos(M, p)
        t = p["t"]
        q_pp = p["dims"][2] * t["densidad_kg_m3"] * G * 1e-9  # N/mm² de peso propio
        luces = {}
        for k in (0, 1):
            cs = [c for c, _ in fam[k]]
            if len(cs) >= 2:
                luces[k] = max(cs[i + 1] - cs[i] for i in range(len(cs) - 1))
        if not luces:
            _chk(out, f"res.placa.{p['id']}", f"Placa «{p['nombre']}» apoyada en al menos dos vigas paralelas", "sin apoyos detectados",
                 "≥ 2 vigas debajo", False, "El motor busca vigas horizontales cuya cara superior toca la cara inferior de la placa.")
            continue
        k = min(luces, key=luces.get)
        Lp, tt = luces[k], p["dims"][2]
        lim = p["y"] if k == 0 else p["x"]
        cs = [c for c, _ in fam[k]]
        vol = max(cs[0] - lim[0], lim[1] - cs[-1], 0)
        Wm = tt ** 2 / 6  # por mm de ancho
        Mq = (q_uso + q_pp) * Lp ** 2 / 8
        Mp = P_p * Lp / 4 / bp
        Mv = max((q_uso + q_pp) * vol ** 2 / 2, Q["carga_borde_kg"] * G * vol / bp)
        sig = max(Mq, Mp, Mv) / Wm
        fadm = t["tension_flexion_adm_MPa"]
        Ip = tt ** 3 / 12
        fl = max(5 * (q_uso + q_pp) * Lp ** 4, 5 * q_pp * Lp ** 4 + 8 * P_p / bp * Lp ** 3) / (384 * t["E_MPa"] * Ip)  # la misma carga que manda en la tensión
        _chk(out, f"res.placa.{p['id']}", f"Placa «{p['nombre']}»: tensión por flexión entre apoyos y en el voladizo",
             f"{num(sig, 1)} MPa (luz {mm(Lp)}, voladizo {mm(vol)})", f"≤ {num(fadm, 0)} MPa", sig <= fadm,
             f"Carga de uso {Q['distribuida_kg_m2']} kg/m² o {Q['puntual_kg']} kg en una franja de {bp} mm; {Q['carga_borde_kg']} kg en el borde del voladizo.")
        _chk(out, f"def.placa.{p['id']}", f"Placa «{p['nombre']}»: flecha con carga de uso (repartida o puntual)", f"{num(fl, 1)} mm", f"≤ L/{div} = {num(Lp / div, 1)} mm", fl <= Lp / div)
        for kk in (0, 1):
            limk = p["y"] if kk == 0 else p["x"]
            for b, trib in _tributarias(fam[kk], limk):
                c = carga_viga.setdefault(b["id"], {"w_uso": 0, "w_pp": 0})
                c["w_uso"] += q_uso * trib
                c["w_pp"] += q_pp * trib

    # barras que reciben la carga directo (tablas de un asiento, listones de un estante): ancho de carga declarado
    for b in M["barras"]:
        if b["ancho_carga"] and b["rol"] == "viga":
            c = carga_viga.setdefault(b["id"], {"w_uso": 0, "w_pp": 0})
            c["w_uso"] += q_uso * b["ancho_carga"]
    sin = [b["id"] for b in M["barras"] if b["rol"] == "viga" and b["id"] not in carga_viga]
    if sin:
        _chk(out, "res.vigas_sin_carga", "Vigas sin carga directa (no tienen placa encima ni ancho de carga): no se verifican a flexión",
             ", ".join(sin), "informativo", "informativo", "Si alguna recibe carga, declarar su ancho_carga en la ficha.")
    # vigas: flexión y flecha, cada familia tomando toda la carga de la placa (conservador)
    for b in M["barras"]:
        if b["id"] not in carga_viga:
            continue
        P, L, c = b["P"], b["L"], carga_viga[b["id"]]
        w_pp = c["w_pp"] + P["kg_m"] * G / 1000
        if P["acero"]:
            Md = max(gf * (c["w_uso"] + w_pp) * L ** 2 / 8, gf * (w_pp * L ** 2 / 8 + P_p * L / 4))
            lim_s, nota = P["f"] / gm, f"fy {P['f']} / {gm} con carga × {gf}"
        else:
            Md = max((c["w_uso"] + w_pp) * L ** 2 / 8, w_pp * L ** 2 / 8 + P_p * L / 4)
            lim_s, nota = P["f"], "tensión admisible de la madera con carga de uso"
        sig = Md / P["W"]
        fl = max(5 * (c["w_uso"] + w_pp) * L ** 4, 5 * w_pp * L ** 4 + 8 * P_p * L ** 3) / (384 * P["E"] * P["I"])
        _chk(out, f"res.viga.{b['id']}", f"Viga «{b['nombre']}» ({b['id']}, {mm(L)}): tensión por flexión", f"{num(sig, 0)} MPa", f"≤ {num(lim_s, 0)} MPa", sig <= lim_s,
             f"Simplemente apoyada en sus puntas; toma la carga de su ancho de influencia o {Q['puntual_kg']} kg en el medio; {nota}.")
        _chk(out, f"def.viga.{b['id']}", f"Viga «{b['nombre']}» ({b['id']}): flecha con carga de uso (repartida o {Q['puntual_kg']} kg en el medio)", f"{num(fl, 1)} mm", f"≤ L/{div} = {num(L / div, 1)} mm", fl <= L / div)

    # patas: pandeo con la carga total repartida y corrimiento por empuje lateral
    patas = M["patas"]
    area = sum(p["dims"][0] * p["dims"][1] for p in M["placas"])
    Wtot = q_uso * area + M["peso"] * G
    N = Wtot / len(patas)
    H = Q["empuje_lateral_kg"] * G
    fsp, dmax = cr["fs_pandeo"]["valor"], cr["desplome_max"]["divisor"]
    for sec in sorted({b["seccion"] for b in patas}):
        grupo = [b for b in patas if b["seccion"] == sec]
        b = max(grupo, key=lambda x: x["L"])
        P, L = b["P"], b["L"]
        Pcr = math.pi ** 2 * P["E"] * P["Imin"] / (2 * L) ** 2
        fs = min(Pcr, (P["f"] if P["acero"] else P["fc"]) * P["A"]) / N
        _chk(out, f"res.pata.{sec}", f"Patas «{sec}» ({len(grupo)}): pandeo con la carga total repartida", f"FS {num(fs, 1)}", f"≥ {num(fsp, 1)}", fs >= fsp,
             f"{num(N / G, 0)} kg por pata; longitud efectiva 2 × {mm(L)}.")
    _meneo(out, M, H, Q, gf, gm, dmax)

    # vuelco: empuje arriba y carga en el borde del voladizo
    hu, cg, peso = M["huella"], M["cg"], M["peso"] * G
    zt = env["z"][1]
    fsv = cr["fs_vuelco"]["valor"]
    casos = []
    for k, eje in ((0, "x"), (1, "y")):
        dmin = min(cg[k] - hu[eje][0], hu[eje][1] - cg[k])
        if Q.get("empuje_vuelco_kg"):
            casos.append((peso * dmin / (Q["empuje_vuelco_kg"] * G * zt), f"empuje de {Q['empuje_vuelco_kg']} kg arriba, en {eje}"))
        if not M["placas"] or Q["carga_borde_kg"] <= 0:
            continue
        bordes = (min(p[eje][0] for p in M["placas"]), max(p[eje][1] for p in M["placas"]))  # se apoyan sobre la tapa, no sobre el hierro
        for lado, borde, apoyo in ((0, bordes[0], hu[eje][0]), (1, bordes[1], hu[eje][1])):
            vol = abs(borde - apoyo) if (borde < apoyo if lado == 0 else borde > apoyo) else 0
            if vol > 0:
                casos.append((peso * abs(cg[k] - apoyo) / (Q["carga_borde_kg"] * G * vol), f"{Q['carga_borde_kg']} kg en el borde, voladizo de {mm(vol)}"))
    if casos:
        fs, caso = min(casos)
        _chk(out, "est.vuelco", "Estabilidad al vuelco (peso propio contra carga en el borde o empuje arriba)", f"FS {num(fs, 1)} ({caso})", f"≥ {num(fsv, 1)}", fs >= fsv,
             "Sin anclar al piso ni contar la carga de uso a favor.")
    else:
        _chk(out, "est.vuelco", "Estabilidad al vuelco", "la tapa no vuela fuera de las patas", "informativo", "informativo")

    # fabricación
    pmax = max([(b["kg"], b["nombre"]) for b in M["barras"]] + [(p["kg"], p["nombre"]) for p in M["placas"]])
    lim_p = cr["peso_pieza_max_kg"]["valor"]
    _chk(out, "fab.pieza", "Pieza más pesada manejable por una persona", f"{num(pmax[0], 1)} kg ({pmax[1]})", f"≤ {lim_p} kg", pmax[0] <= lim_p)
    _chk(out, "fab.peso", "Peso total", f"{num(M['peso'], 0)} kg", "informativo", "informativo")
    if ficha["requisitos"].get("exterior"):
        sin = [k for k, s in M["secc"].items() if s["tipo"] != "madera" and _clase(s) == "acero" and "epoxi" not in (s.get("acabado") or "").lower()]
        _chk(out, "dur.exterior", "Hierro protegido para exterior (galvanizado o epoxi)", "todo protegido" if not sin else ", ".join(sin), "galvanizado o epoxi",
             "cumple" if not sin else "dudoso")
    return {"checks": out, "peso_propio_kg": round(M["peso"], 1), "peso_total_kg": round(M["peso"], 1), "resumen": _resumen(out)}


def _portales(M, d):
    """Pórticos que resisten un empuje en la dirección d: filas de patas unidas arriba por una viga paralela a d.
    Devuelve [(patas, luz entre ejes, viga)]."""
    o = 1 - d
    filas = {}
    for b in M["patas"]:
        filas.setdefault(round(b["a"][o]), []).append(b)
    out = []
    for co, ps in filas.items():
        if len(ps) < 2:
            continue
        tope = max(max(b["a"][2], b["b"][2]) for b in ps)
        vigas = [v for v in M["barras"] if v["rol"] == "viga" and v["eje"] == d and abs(v["a"][o] - co) <= max(v["P"]["b"], v["P"]["h"]) / 2 + 1
                 and abs(v["a"][2] + v["P"]["h"] / 2 - tope) <= v["P"]["h"] + 5]
        if vigas:
            xs = [b["a"][d] for b in ps]
            out.append((ps, max(xs) - min(xs), min(vigas, key=lambda v: v["P"]["I"])))
    return out


def _meneo(out, M, H, Q, gf, gm, dmax):
    """Corrimiento arriba y tensión en el nudo por empuje lateral, con pórticos de base articulada (pata apoyada en el piso):
    δ = Hp·h²/(12·E)·(2h/Ic + L/Ib) por pórtico de dos patas; momento en el nudo Hp·h/2."""
    peor = None
    for d, eje in ((0, "x"), (1, "y")):
        port = _portales(M, d)
        if not port:
            _chk(out, f"def.meneo.{eje}", f"Patas unidas arriba por una viga en {eje} (resisten un empuje lateral)", "sin viga que una las patas", "≥ 1 pórtico", False,
                 "Sin un bastidor que una las patas arriba la estructura no resiste el empuje: agregar la viga o una riostra.")
            continue
        Hp = H / len(port)
        for ps, Lb, viga in port:
            c = max(ps, key=lambda b: b["L"])
            P, h = c["P"], c["L"]
            Ic = P["I2"] if d == 0 else P["I"]  # la pata vertical tiene b en x y h en y
            Ib, E = viga["P"]["I"], P["E"]
            dl = Hp * h ** 2 / (12 * E) * (2 * h / Ic + Lb * E / (viga["P"]["E"] * Ib))
            prof = (P["b"] if d == 0 else P["h"]) / 2
            sig = Hp * h / 2 * (gf if P["acero"] else 1) * prof / Ic
            lim_s = P["f"] / gm if P["acero"] else P["f"]
            caso = (dl / (h / dmax), dl, sig, lim_s, h, eje, c["seccion"], viga["id"])
            if peor is None or caso[0] > peor[0]:
                peor = caso
    if peor:
        _, dl, sig, lim_s, h, eje, sec, vid = peor
        _chk(out, "def.meneo", f"Corrimiento arriba con {Q['empuje_lateral_kg']} kg de empuje lateral (peor dirección: {eje})", f"{num(dl, 1)} mm",
             f"≤ alto/{dmax} = {num(h / dmax, 1)} mm", dl <= h / dmax,
             f"Pórtico de patas «{sec}» con la viga {vid}, nudos rígidos (soldadura completa) y pata apoyada en el piso; cuenta la flexión de la pata y de la viga.")
        _chk(out, "res.nudo", "Tensión en el nudo pata-bastidor por el empuje lateral", f"{num(sig, 0)} MPa", f"≤ {num(lim_s, 0)} MPa", sig <= lim_s)


def _resumen(checks):
    ver = [c for c in checks if c["estado"] != "informativo"]
    ok = sum(c["estado"] == "cumple" for c in ver)
    lin = [f"{ok}/{len(ver)} verificaciones cumplen."]
    lin += [f"- {c['estado'].upper()}: {c['requisito']} → {c['valor']} (límite {c['limite']})" for c in ver if c["estado"] != "cumple"]
    return "\n".join(lin)


# ======================================================================
# Despiece, plan de corte y pedido (sin precios)
# ======================================================================
def _ffd(largos, barra, corte):
    """Primer ajuste decreciente: [{"cortes": [...], "libre": mm}]"""
    bins = []
    for L in sorted(largos, reverse=True):
        for b in bins:
            if b["libre"] >= L + corte:
                b["cortes"].append(L)
                b["libre"] -= L + corte
                break
        else:
            bins.append({"cortes": [L], "libre": barra - L - corte})
    for b in bins:
        b["libre"] = max(round(b["libre"]), 0)
    return bins


def _hojas(piezas, hoja, corte=4):
    """Acomodo en estantes: devuelve la lista de hojas con sus piezas [(id, a, b)]."""
    H1, H2 = max(hoja), min(hoja)
    pz = sorted(((i, max(a, b), min(a, b)) for i, a, b in piezas), key=lambda t: -t[2])
    hojas = []
    for i, a, b in pz:
        puesto = False
        for h in hojas:
            for est in h["estantes"]:
                if est["alto"] >= b and est["libre"] >= a + corte:
                    est["libre"] -= a + corte
                    h["piezas"].append((i, a, b))
                    puesto = True
                    break
            if not puesto and h["libre_alto"] >= b + corte:
                h["estantes"].append({"alto": b, "libre": H1 - a - corte})
                h["libre_alto"] -= b + corte
                h["piezas"].append((i, a, b))
                puesto = True
            if puesto:
                break
        if not puesto:
            hojas.append({"estantes": [{"alto": b, "libre": H1 - a - corte}], "libre_alto": H2 - b - corte, "piezas": [(i, a, b)]})
    return hojas


def despiece(ficha, M=None):
    M = M or modelo(ficha)
    cat = catalogo_materiales()
    n = ficha["requisitos"].get("cantidad", 1)
    piezas, grupos = [], {}
    for b in M["barras"]:
        clave = (b["grupo"], b["nombre"], b["seccion"], round(b["L"]), b["corte"])
        grupos.setdefault(clave, []).append(b)
    for (grupo, nombre, sec, L, corte), bs in grupos.items():
        s = M["secc"][sec]
        ops = "corte recto" if corte == "recto" else f"corte {corte}"
        if s["tipo"] != "madera":
            ops += "; soldar completo, amolar la soldadura vista" + ("" if "galva" in (s.get("acabado") or "") else "; antióxido y terminación")
        else:
            ops += "; cepillar y lijar; sellador o impregnante"
        piezas.append({"id": ", ".join(b["id"] for b in bs), "pieza": nombre, "cant": len(bs) * n, "subconjunto": grupo, "seccion_id": sec,
                       "seccion": nombre_seccion(s)[0], "largo": L, "material": s.get("acabado", ""), "operaciones": ops,
                       "kg": round(sum(b["kg"] for b in bs) * n, 1)})
    for p in M["placas"]:
        a, b = sorted(p["dims"][:2], reverse=True)
        piezas.append({"id": p["id"], "pieza": p["nombre"], "cant": n, "subconjunto": p["grupo"], "seccion_id": p["mat"], "seccion": p["t"]["nombre"],
                       "largo": None, "medida": f"{mm(a)} × {mm(b)} × {num(p['dims'][2], 0)}", "material": p.get("acabado", ""),
                       "operaciones": p["fijacion"] or "cortar a medida y cantear", "kg": round(p["kg"] * n, 1)})
    piezas.sort(key=lambda r: (r["subconjunto"], r["pieza"]))
    # plan de corte por sección
    cortes, pedido = {}, {"barras": [], "tableros": [], "insumos": []}
    for sec, s in M["secc"].items():
        largos = [round(b["L"]) for b in M["barras"] if b["seccion"] == sec for _ in range(n)]
        if not largos:
            continue
        if s["tipo"] == "madera":
            mad = cat["maderas_aserradas"]
            disp = sorted(int(v * 1000) for v in mad["largos_comerciales_m"])
            bins = _ffd(largos, disp[-1], 3)
            for b in bins:
                usado = disp[-1] - b["libre"]
                b["barra"] = next(v for v in disp if v >= usado)
                b["libre"] = b["barra"] - usado
            cuenta = {}
            for b in bins:
                cuenta[b["barra"]] = cuenta.get(b["barra"], 0) + 1
            for Lb, c in sorted(cuenta.items()):
                pedido["barras"].append({"descripcion": f"{nombre_seccion(s)[0]}, tirante de {num(Lb / 1000, 2)} m", "cant": c, "unidad": "tirante",
                                         "uso": sec, "seccion_id": sec})
        else:
            cm_ = cat["metales"]["tubo-estructural-cuadrado" if s["tipo"] == "tubo-rect" else "planchuela-galvanizada" if s["tipo"] == "planchuela" else "tubo-estructural-redondo"]
            barra, kerf = cm_.get("largo_barra_mm", 6000), cm_.get("corte_mm", 3)
            bins = _ffd(largos, barra, kerf)
            for b in bins:
                b["barra"] = barra
            tot = sum(largos) + kerf * len(largos)
            pedido["barras"].append({"descripcion": f"{nombre_seccion(s)[0]}, barra de {num(barra / 1000, 0)} m", "cant": len(bins), "unidad": "barra",
                                     "uso": sec, "seccion_id": sec, "desperdicio_pct": round(100 * (1 - tot / (barra * len(bins))), 1)})
        cortes[sec] = bins
    hojas_plan = {}
    for mat in sorted({p["mat"] for p in M["placas"]}):
        t = cat["tableros"][mat]
        pz = [(p["id"], p["dims"][0], p["dims"][1]) for p in M["placas"] if p["mat"] == mat for _ in range(n)]
        hojas = _hojas(pz, t["hoja_mm"])
        hojas_plan[mat] = hojas
        area = sum(a * b for _, a, b in pz)
        pedido["tableros"].append({"descripcion": f"{t['nombre']}, hoja de {mm(t['hoja_mm'][0])} × {mm(t['hoja_mm'][1])}", "cant": len(hojas), "unidad": "hoja",
                                   "uso": mat, "desperdicio_pct": round(100 * (1 - area / (len(hojas) * t["hoja_mm"][0] * t["hoja_mm"][1])), 1)})
    for i in ficha["diseno"].get("insumos", []):
        pedido["insumos"].append({"descripcion": i["descripcion"], "cant": i["cant"] * (n if i.get("por_unidad", True) else 1), "unidad": i["unidad"], "uso": i.get("uso", "")})
    kg_m = sum(b["kg"] for b in M["barras"] if b["s"]["tipo"] != "madera") * n
    kg_w = (sum(b["kg"] for b in M["barras"] if b["s"]["tipo"] == "madera") + sum(p["kg"] for p in M["placas"])) * n
    return {"piezas": piezas, "barras_corte": cortes, "hojas": hojas_plan, "pedido": pedido, "cantidad": n,
            "peso": {"total_kg": round(kg_m + kg_w, 1), "hierro_kg": round(kg_m, 1), "madera_kg": round(kg_w, 1), "por_unidad_kg": round(M["peso"], 1)},
            "nota": "Largos de corte al eje de cada pieza según la ficha; el herrero o carpintero ajusta los descuentos de cada unión."}


# ======================================================================
# Vistas (proyecciones ortogonales con cotas)
# ======================================================================
DEFS = ('<defs><marker id="fl" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0,1 L9,5 L0,9 z" class="flecha"/></marker></defs>')
VISTAS = {"planta": (0, 1, 2, "Planta"), "frente": (0, 2, 1, "Frente"), "lateral": (1, 2, 0, "Lateral")}


def _cajas_vista(M):
    """Todo como cajas alineadas (las barras inclinadas o redondas se aproximan por su envolvente)."""
    out = []
    for b in M["barras"]:
        if b["caja"]:
            out.append((b["caja"], b["clase"], False))
        else:
            r = max(b["P"]["b"], b["P"]["h"]) / 2
            if b["eje"] is not None:
                out.append(([sorted([b["a"][i], b["b"][i]]) if i == b["eje"] else [b["a"][i] - r, b["a"][i] + r] for i in range(3)], b["clase"], False))
            else:
                out.append(("linea", b, False))
    for p in M["placas"]:
        out.append(([p["x"], p["y"], p["z"]], p["clase"], True))
    return out


def vista(M, cual):
    """Proyección ortogonal; en planta las placas van semitransparentes para que se vea la estructura de abajo."""
    u, v, w, titulo = VISTAS[cual]
    env = M["env"]
    U, V = env["xyz"[u]], env["xyz"[v]]
    du, dv = U[1] - U[0], V[1] - V[0]
    k = max(du, dv) / 1800  # escala de textos y cotas
    pad = 260 * k
    fs = 70 * k
    ox, oy = pad - U[0], pad + V[1]
    X = lambda a: ox + a
    Y = lambda b: oy - b
    W, Hh = du + 2 * pad, dv + 2 * pad + (60 * k if cual != "planta" else 0)
    s = [f'<svg viewBox="0 0 {W:.0f} {Hh:.0f}" role="img" aria-label="{titulo}">', DEFS]
    if cual != "planta":
        s.append(f'<line class="piso" x1="{X(U[0]) - pad * .6:.0f}" y1="{Y(0):.0f}" x2="{X(U[1]) + pad * .6:.0f}" y2="{Y(0):.0f}" style="stroke-width:{6 * k:.1f}"/>')
    # de atrás hacia adelante: en planta lo más bajo primero; en frente lo de atrás (y alto) primero; en lateral lo de atrás (x bajo) primero
    orden = (lambda c: c[0][2][1]) if cual == "planta" else (lambda c: -c[0][1][1]) if cual == "frente" else (lambda c: c[0][0][0])
    cajas = [c for c in _cajas_vista(M) if c[0] != "linea"]
    if cual == "planta":  # placas al final y transparentes
        orden = lambda c: (c[2], c[0][2][1])
    for caja, cls, es_placa in sorted(cajas, key=orden):
        a0, a1 = caja[u]
        b0, b1 = caja[v]
        y0 = min(Y(b0), Y(b1))
        tr = " transp" if cual == "planta" and es_placa else ""
        s.append(f'<rect class="m-{cls}{tr}" x="{X(a0):.1f}" y="{y0:.1f}" width="{a1 - a0:.1f}" height="{abs(Y(b1) - Y(b0)):.1f}" style="stroke-width:{2.5 * k:.1f}"/>')
    for c, b, _ in [c for c in _cajas_vista(M) if c[0] == "linea"]:
        s.append(f'<line class="m-{b["clase"]} lin" x1="{X(b["a"][u]):.1f}" y1="{Y(b["a"][v]):.1f}" x2="{X(b["b"][u]):.1f}" y2="{Y(b["b"][v]):.1f}" '
                 f'style="stroke-width:{max(b["P"]["b"], b["P"]["h"]):.0f}"/>')
    st = f'style="font-size:calc(var(--fx, 1) * {fs:.0f}px)"'  # la plantilla achica la vista que va a todo el ancho
    sw = f'style="stroke-width:{4 * k:.1f}"'
    # cota horizontal total
    yb = Y(V[0]) + pad * .55
    s.append(f'<line class="cota" {sw} x1="{X(U[0]):.0f}" y1="{yb:.0f}" x2="{X(U[1]):.0f}" y2="{yb:.0f}" marker-start="url(#fl)" marker-end="url(#fl)"/>'
             f'<text class="ct" {st} x="{X((U[0] + U[1]) / 2):.0f}" y="{yb + fs * 1.15:.0f}" text-anchor="middle">{mm(du)}</text>')
    # cota vertical total
    xr = X(U[1]) + pad * .45
    yt, yb2 = Y(V[1]), Y(V[0])
    s.append(f'<line class="cota" {sw} x1="{xr:.0f}" y1="{yt:.0f}" x2="{xr:.0f}" y2="{yb2:.0f}" marker-start="url(#fl)" marker-end="url(#fl)"/>'
             f'<text class="ct" {st} x="{xr + fs * .3:.0f}" y="{(yt + yb2) / 2 + fs * .35:.0f}" text-anchor="start" '
             f'transform="rotate(-90 {xr + fs * .3:.0f} {(yt + yb2) / 2:.0f})">{mm(dv)}</text>')
    # separación de patas (eje a eje) arriba de la vista
    ejes = sorted({round(b["a"][u]) for b in M["patas"]})
    if len(ejes) >= 2:
        yc = Y(V[1]) - pad * .45
        s.append(f'<line class="cota" {sw} x1="{X(ejes[0]):.0f}" y1="{yc:.0f}" x2="{X(ejes[-1]):.0f}" y2="{yc:.0f}" marker-start="url(#fl)" marker-end="url(#fl)"/>'
                 f'<text class="ct" {st} x="{X((ejes[0] + ejes[-1]) / 2):.0f}" y="{yc - fs * .35:.0f}" text-anchor="middle">{mm(ejes[-1] - ejes[0])} entre ejes de patas</text>')
    s.append("</svg>")
    return "".join(s)


# ======================================================================
# Página técnica (sin presupuesto)
# ======================================================================
LEYENDA = {"acero": ("#2f3539", "hierro pintado"), "acero_claro": ("#c9ced1", "hierro pintado claro"), "galva": ("#a3b0b8", "hierro galvanizado"),
           "inox": ("#e4e9ec", "acero inoxidable"), "madera": ("#c8925a", "madera"), "madera_oscura": ("#8a5a35", "madera oscura"),
           "tablero": ("#d9c7a5", "tablero"), "blanco": ("#f1f0ec", "melamina blanca")}


def _html_despiece(desp):
    filas, sub_ant = [], None
    for p in desp["piezas"]:
        if p["subconjunto"] != sub_ant:
            filas.append(f'<tr class="grupo"><th colspan="5">{E(p["subconjunto"])}</th></tr>')
            sub_ant = p["subconjunto"]
        medida = p.get("medida") or f'{mm(p["largo"])}'
        filas.append(f'<tr><td class="v">{E(p["id"])}</td><td>{E(p["pieza"])}</td><td class="v">{p["cant"]}</td>'
                     f'<td class="v">{E(medida)}</td><td>{E(p["operaciones"])}<br><small>{E(p["seccion"])}{" · " + E(p["material"]) if p["material"] else ""}</small></td></tr>')
    corte = []
    for sec, bs in desp["barras_corte"].items():
        nom = next(r["descripcion"].rsplit(", ", 1)[0] for r in desp["pedido"]["barras"] if r["seccion_id"] == sec)
        bars = "".join(
            f'<div class="barra"><b>{i}</b><div class="tira">'
            + "".join(f'<span class="seg" style="flex:{c}" title="{c}">{mm(c)}</span>' for c in b["cortes"])
            + f'<span class="sobra" style="flex:{max(b["libre"], 1)}">{mm(b["libre"])}</span></div></div>' for i, b in enumerate(bs, 1))
        largo = sorted({b["barra"] for b in bs})
        corte.append(f'<div class="corte"><h3>{E(nom)} · {len(bs)} × {" / ".join(num(v / 1000, 2) for v in largo)} m</h3>{bars}</div>')
    for mat, hojas in desp["hojas"].items():
        t = catalogo_materiales()["tableros"][mat]
        bars = "".join(f'<div class="barra"><b>{i}</b><div class="tira">'
                       + "".join(f'<span class="seg" style="flex:{a * b}" title="{E(pid)}">{E(pid)} {mm(a)}×{mm(b)}</span>' for pid, a, b in h["piezas"])
                       + f'<span class="sobra" style="flex:{max(t["hoja_mm"][0] * t["hoja_mm"][1] - sum(a * b for _, a, b in h["piezas"]), 1)}">resto</span></div></div>'
                       for i, h in enumerate(hojas, 1))
        corte.append(f'<div class="corte"><h3>{E(t["nombre"])} · {len(hojas)} hoja{"s" if len(hojas) > 1 else ""} de {mm(t["hoja_mm"][0])} × {mm(t["hoja_mm"][1])}</h3>{bars}</div>')
    nom = {"barras": "Caños y madera", "tableros": "Tableros", "insumos": "Insumos y herrajes"}
    ped = []
    for k, lst in desp["pedido"].items():
        if not lst:
            continue
        ped.append(f'<tr class="grupo"><th colspan="3">{nom[k]}</th></tr>')
        for r in lst:
            extra = f' · desperdicio {num(r["desperdicio_pct"], 1)} %' if "desperdicio_pct" in r else ""
            ped.append(f'<tr><td>{E(r["descripcion"])}<br><small>{E(r.get("uso", ""))}{extra}</small></td><td class="v">{r["cant"]}</td><td>{E(r["unidad"])}</td></tr>')
    pe = desp["peso"]
    return (f'<div class="tabla"><table class="desp"><thead><tr><th>Id</th><th>Pieza</th><th>Cant.</th><th>Medida (mm)</th><th>Operaciones</th></tr></thead>'
            f'<tbody>{"".join(filas)}</tbody></table></div>'
            f'<div class="cortes"><h3 class="sub">Plan de corte</h3><p class="hint">Caño en barras de 6 m con 3 mm por corte; madera en el tirante comercial más corto que alcanza; '
            f'tableros por hoja (las proporciones de la tira son por área). Gris: sobrante.</p>{"".join(corte)}</div>'
            f'<div class="tabla"><h3 class="sub">Pedido de materiales (sin precios)</h3><table><thead><tr><th>Material</th><th>Cant.</th><th>Unidad</th></tr></thead>'
            f'<tbody>{"".join(ped)}</tbody></table></div>'
            + (f'<p class="hint" style="padding:12px 16px 0">Despiece y pedido para {desp["cantidad"]} unidades (≈ {num(pe["por_unidad_kg"], 0)} kg cada una).</p>' if desp["cantidad"] > 1 else "")
            + f'<p class="hint" style="padding:12px 16px">Peso ≈ {num(pe["total_kg"], 0)} kg (hierro ≈ {num(pe["hierro_kg"], 0)} kg, madera y tableros ≈ {num(pe["madera_kg"], 0)} kg). {E(desp["nota"])}</p>')


def _filas_medidas(ficha, M, Q):
    d, env = ficha["diseno"], M["env"]
    rows = [("Medidas totales", f"{mm(env['x'][1] - env['x'][0])} × {mm(env['y'][1] - env['y'][0])} × {mm(env['z'][1] - env['z'][0])}",
             ficha["requisitos"].get("_origen_medidas", "supuesto: medidas del pedido"))]
    for k, s in d["secciones"].items():
        usos = sorted({b["nombre"] for b in M["barras"] if b["seccion"] == k})
        rows.append((f"{k} ({', '.join(usos)})" if usos else k, nombre_seccion(s)[0] + (f" · {s['acabado']}" if s.get("acabado") else ""), s.get("_origen", "supuesto: sección propuesta")))
    for p in M["placas"]:
        rows.append((p["nombre"], f"{p['t']['nombre']} · {mm(p['dims'][0])} × {mm(p['dims'][1])}", d["placas"][[q["id"] for q in d["placas"]].index(p["id"])].get("_origen", "supuesto: placa propuesta")))
    for clave, titulo in (("uniones", "Uniones"), ("terminacion", "Terminación")):
        if d.get(clave):
            rows.append((titulo, d[clave], d.get(f"_origen_{clave}", "criterio: práctica de taller")))
    rows.append(("Cargas de uso", f"{Q['distribuida_kg_m2']} kg/m² · {Q['puntual_kg']} kg puntual · {Q['empuje_lateral_kg']} kg lateral · {Q['carga_borde_kg']} kg en el borde",
                 "criterio: " + ("valores de la ficha" if ficha["requisitos"].get("cargas") else f"cargas por uso «{ficha['requisitos']['tipo_uso']}» del catálogo")))
    rows.append(("Peso", f"≈ {num(M['peso'], 0)} kg", "cálculo: suma de las piezas"))
    out = []
    for el, val, origen in rows:
        t = _tag(origen)
        cls = "f" if t == "fuente" else "s"
        resp = origen.split(":", 1)[1].strip() if origen.lower().startswith(t) and ":" in origen[:12] else origen
        out.append(f'<tr><td>{E(el)}</td><td>{E(val)}</td><td><span class="tag {cls}">{t}</span></td><td>{E(resp)}</td></tr>')
    return "".join(out)


def _estado(e):
    return f'<span class="st {"ok" if e == "cumple" else "bad" if e == "no cumple" else "info" if e == "informativo" else "warn"}">{E(e)}</span>'


def pagina(ficha, M, val, desp, auditoria=None):
    pr, cl, req, d = ficha["proyecto"], ficha["cliente"], ficha["requisitos"], ficha["diseno"]
    tip = catalogo_tipologia("estructura-libre")
    Q = cargas(ficha)
    tpl = open(os.path.join(RAIZ, "skills", "propuesta-web", "assets", "plantilla-libre.html"), encoding="utf-8").read()
    fecha = datetime.date.fromisoformat(pr["fecha"])
    vence = fecha + datetime.timedelta(days=pr["validez_dias"])
    f_ = lambda x: x.strftime("%d/%m/%Y")
    falta = '<span class="tbd">a completar</span>'
    v_ = lambda x: E(x) if x else falta
    ver = [c for c in val["checks"] if c["estado"] != "informativo"]
    ok = sum(c["estado"] == "cumple" for c in ver)
    env = M["env"]
    cifras = "".join(f"<span>{a} <em>{b}</em></span>" for a, b in (
        (mm(env["x"][1] - env["x"][0]), "largo"), (mm(env["y"][1] - env["y"][0]), "ancho"), (mm(env["z"][1] - env["z"][0]), "alto"),
        (f"≈ {num(M['peso'], 0)} kg", "peso"), (str(len(M["barras"]) + len(M["placas"])), "piezas")))
    mats = sorted({b["s"]["tipo"] == "madera" for b in M["barras"]} | ({True} if M["placas"] and any(not p["mat"].startswith("chapa") for p in M["placas"]) else set()))
    material = "hierro + madera" if mats == [False, True] else "madera" if mats == [True] else "hierro"
    vu = (auditoria or {}).get("vueltas", "?")
    aud_estado = (f"auditoría vuelta {vu}: {auditoria.get('estado')}" + (" (desactualizada)" if auditoria.get("_aviso") else "")) if auditoria else "auditoría pendiente"
    der = "".join(f"<span>{a} <b>{E(b)}</b></span>" for a, b in (
        ("Medidas", "mm"), ("Material", material), ("Uso", req["tipo_uso"]), ("Verificaciones", f"{ok}/{len(ver)}"), ("Estado", aud_estado)))
    datos = ('<dl class="datos">' + "".join(f"<dt>{a}</dt><dd>{b}</dd>" for a, b in (
        ("Propuesta", E(pr["numero"])), ("Fecha", f_(fecha)), ("Validez", f"{pr['validez_dias']} días (hasta el {f_(vence)})"),
        ("Cliente", v_(cl.get("nombre"))), ("Contacto", v_(cl.get("contacto"))),
        ("Entrega", f"{v_(cl.get('direccion_obra'))} — {E(cl['localidad'])}, {E(cl['provincia'])}"),
        ("Cantidad", f"{req.get('cantidad', 1)}"), ("Uso", E(req["uso"])))) + "</dl>")
    ref = req.get("referencia", {})
    referencia = ""
    if ref:
        tomado = "".join(f"<li>{E(x)}</li>" for x in ref.get("tomado", []))
        cambiado = "".join(f"<li>{E(x)}</li>" for x in ref.get("cambiado", []))
        referencia = (f'<section class="lamina"><header><h2>Referencia</h2><small>{E(ref.get("origen", "pedido del cliente"))}</small></header><div class="texto">'
                      f'<p>{E(ref.get("descripcion", ""))}</p>'
                      + (f'<h3>Lo que se tomó de la referencia</h3><ul>{tomado}</ul>' if tomado else "")
                      + (f'<h3>Lo que se cambió y por qué</h3><ul>{cambiado}</ul>' if cambiado else "") + '</div></section>')
    clases = sorted({c["m"] for c in M["escena"]["cajas"] + M["escena"]["piezas"]})
    leyenda = "".join(f'<span><i style="background:{LEYENDA[c][0]}"></i>{LEYENDA[c][1]}</span>' for c in clases if c in LEYENDA)
    verif = "".join(f'<tr><td>{E(c["requisito"])}<br><small>{E(c.get("nota", ""))}</small></td><td class="v">{E(c["valor"])}</td>'
                    f'<td class="v">{E(c["limite"])}</td><td>{_estado(c["estado"])}</td></tr>' for c in val["checks"])
    princ = ""
    for p in tip["principios"]:
        cita = (f'<blockquote>“{E(p["cita"]["texto"])}”<cite>{E(p["cita"]["fuente"])}</cite></blockquote>' if p.get("cita") else "")
        princ += f'<article><h3>{E(p["titulo"])}</h3><ul>{"".join(f"<li>{E(i)}</li>" for i in p["items"])}</ul>{cita}</article>'
    pend = list(d.get("pendientes", [])) + [
        "Secciones, cargas y uniones son propuesta del anteproyecto, verificadas con cálculo simplificado: no reemplazan el cálculo de un ingeniero matriculado.",
        "El plano de taller y los descuentos de cada unión los resuelve quien fabrica.",
        "Armar un prototipo y probar el meneo y el vuelco antes de fabricar en serie."]
    if ficha.get("estado", {}).get("nota_auditoria"):
        pend.insert(0, ficha["estado"]["nota_auditoria"])
    if auditoria:
        pend.insert(0, f"Auditoría independiente: vuelta {vu}, estado «{auditoria.get('estado')}». El detalle está en el anexo." + (" " + auditoria["_aviso"] if auditoria.get("_aviso") else ""))
    cond = "".join(f"<p>{x}</p>" for x in (
        "Propuesta técnica: diseño, verificaciones, despiece y pedido de materiales <b>sin precios</b>.",
        E(ficha["comercial"]["mod"]["texto"]),
        f"Plazo de entrega: {v_(ficha['comercial'].get('plazo_entrega'))}. Garantía: {v_(ficha['comercial'].get('garantia'))}.",
        "Anteproyecto con cálculo simplificado: no reemplaza el cálculo de un ingeniero matriculado."))
    aud = ""
    if auditoria:
        it = auditoria.get("items", [])
        okn = sum(i["estado"] == "cumple" for i in it)
        filas = "".join(f'<tr><td>{E(i["requisito"])}</td><td>{_estado(i["estado"])}</td><td>{E(i.get("evidencia", ""))}</td></tr>' for i in it)
        aviso = f'<p class="hint" style="padding:12px 16px"><b>{E(auditoria["_aviso"])}</b></p>' if auditoria.get("_aviso") else ""
        aud = (f'<section class="lamina"><header><h2>Anexo: auditoría independiente</h2><small>vuelta {vu} · {okn}/{len(it)} cumple · {E(auditoria.get("estado", ""))}</small></header>{aviso}'
               f'<div class="tabla"><table><thead><tr><th>Requisito</th><th>Estado</th><th>Evidencia</th></tr></thead><tbody>{filas}</tbody></table></div></section>')
    rep = {
        "{{TITULO_CORTO}}": E(pr.get("titulo_corto", pr["titulo"]))[:60], "{{EYEBROW}}": f"Propuesta técnica {E(pr['numero'])} · {f_(fecha)}",
        "{{TITULO}}": E(pr["titulo"]), "{{BAJADA}}": E(pr.get("bajada", req["uso"])),
        "{{CIFRAS}}": cifras, "{{ROTULO_DER}}": der, "{{MARCA}}": E(pr["marca"]), "{{DATOS}}": datos, "{{REFERENCIA}}": referencia,
        "{{LEYENDA}}": leyenda, "{{FRENTE}}": vista(M, "frente"), "{{PLANTA}}": vista(M, "planta"), "{{LATERAL}}": vista(M, "lateral"),
        "{{FILAS_MEDIDAS}}": _filas_medidas(ficha, M, Q),
        "{{RESUMEN_VALIDACION}}": f"{ok} de {len(ver)} cumplen", "{{VERIFICACIONES}}": verif,
        "{{DESPIECE}}": _html_despiece(desp), "{{PRINCIPIOS}}": princ,
        "{{PENDIENTES}}": "".join(f"<li>{E(x)}</li>" for x in pend), "{{CONDICIONES}}": cond, "{{AUDITORIA}}": aud,
        "{{FUENTES}}": E(tip["fuentes"]) + " Generado con el plugin «estructuras-a-medida».", "{{ESCENA}}": json.dumps(M["escena"]),
    }
    import re
    return re.sub(r"\{\{[A-Z_]+\}\}", lambda m_: rep.get(m_.group(0), m_.group(0)), tpl)


def salidas(ficha, M, val, desp, precios=None, auditoria=None):
    """Devuelve {archivo: contenido} para salida/ y las páginas (con y sin anexo de auditoría)."""
    archivos = {f"{k}.svg": vista(M, k) for k in VISTAS}
    archivos.update({"escena3d.json": M["escena"], "despiece.json": desp, "pedido.json": desp["pedido"]})
    return {"archivos": archivos, "pagina": pagina(ficha, M, val, desp, auditoria), "pagina_auditor": pagina(ficha, M, val, desp, None),
            "presupuesto": None}
