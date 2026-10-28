"""Tipología pórtico de hamacas: geometría, validación rápida y despiece, todo desde ficha.json.

Convención (mm): x a lo largo del travesaño (muro -> césped), y = vaivén, z = arriba.
"""
import math
from comun import add, sub, mul, unit, norm, m, cm, num, catalogo_materiales, catalogo_tipologia

G = 9.81
PULG = {10: '3/8"', 12: '1/2"', 16: '5/8"', 20: '3/4"'}  # la varilla roscada se vende en pulgadas: tuercas y arandelas de la misma rosca


# ======================================================================
# Geometría
# ======================================================================
def modelo(ficha):
    d = ficha["diseno"]
    tr, pa, ti, ca = d["travesano"], d["patas"], d["tirante"], d["cartela"]
    cu, ac, va = d["cuelgues"], d["accesorios"], d["varillas"]
    beamR, beamZ, beamHalf = tr["diametro"] / 2, tr["z_eje"], tr["largo"] / 2
    legR, footX, crossX, foot, ext = pa["diametro"] / 2, pa["pie_x"], pa["cruce_x"], pa["semibase"], pa["prolongacion"]
    lap = pa["desfase_media_madera"]
    # cruce: el travesaño apoya tangente a las dos patas de la V
    apex = beamZ - 400
    for _ in range(80):
        apex = beamZ - (beamR + legR) / math.sin(math.atan(foot / apex))
    lean = (footX - crossX) / apex
    axisX = lambda z: footX - lean * z
    legDeg = math.degrees(math.atan(foot / apex))
    frontDeg = math.degrees(math.atan(lean))
    tieZ, tieR = ti["z"], ti["diametro"] / 2
    braceR, braceTopX = ca["diametro"] / 2, ca["x_sup"]
    slots = cu["puestos_x"]
    hang = [c + s * cu["separacion_par"] / 2 for c in slots for s in (-1, 1)]
    pivotZ = cu["z_giro"]

    def at(sx, s, z):
        return [sx * axisX(z) + s * lap, s * foot * (1 - z / apex), z]

    piezas = []  # dict(nombre, tipo, a, b, r, material)

    def cil(nombre, a, b, r, mat="madera", grupo="estructura"):
        piezas.append({"nombre": nombre, "a": a, "b": b, "r": r, "mat": mat, "grupo": grupo})

    cil("travesano", [-beamHalf, 0, beamZ], [beamHalf, 0, beamZ], beamR)
    legs = {}
    yTop = foot * (beamZ / apex - 1)
    yT = foot * (1 - tieZ / apex)
    for sx in (-1, 1):
        lado = "muro" if sx < 0 else "cesped"
        for s in (-1, 1):
            f = at(sx, s, 0)
            c = [sx * crossX + s * lap, 0, apex]
            e = add(c, mul(unit(sub(c, f)), ext))
            cil(f"pata.{lado}.{'frente' if s < 0 else 'atras'}", f, e, legR)
            legs[(sx, s)] = (f, e)
        Lc = va["cruce"]["largo"]
        cil(f"varilla.cruce.{lado}", [sx * crossX - Lc / 2, 0, apex], [sx * crossX + Lc / 2, 0, apex], va["cruce"]["d"] / 2, "acero")
        xTop = sx * axisX(beamZ)
        Lh = va["horqueta"]["largo"]
        cil(f"varilla.horqueta.{lado}", [xTop, -Lh / 2, beamZ], [xTop, Lh / 2, beamZ], va["horqueta"]["d"] / 2, "acero")
        tx = sx * (axisX(tieZ) - legR - tieR + ti["rebaje"] * 2)
        # las dos patas de cada A quedan desfasadas ±lap (media madera): el tirante va levemente oblicuo en planta
        dxt = lap * (ti["largo"] / 2) / yT
        cil(f"tirante.{lado}", [tx - dxt, -ti["largo"] / 2, tieZ], [tx + dxt, ti["largo"] / 2, tieZ], tieR)
        Lt = va["tirante"]["largo"]
        for s in (-1, 1):
            xa = sx * (axisX(tieZ) + legR + 25)
            cil(f"varilla.tirante.{lado}.{s}", [xa - sx * Lt + s * lap, s * yT, tieZ], [xa + s * lap, s * yT, tieZ], va["tirante"]["d"] / 2, "acero")
        cil(f"cartela.{lado}", [tx, 0, tieZ + tieR - ca["rebaje"]], [sx * braceTopX, 0, beamZ - beamR + ca["rebaje"]], braceR)
        Li, Ls = va["cartela_inf"]["largo"], va["cartela_sup"]["largo"]
        cil(f"varilla.cartela_inf.{lado}", [tx, 0, tieZ - tieR - 25], [tx, 0, tieZ - tieR - 25 + Li], va["cartela_inf"]["d"] / 2, "acero")
        cil(f"varilla.cartela_sup.{lado}", [sx * braceTopX, 0, beamZ + beamR + 25 - Ls], [sx * braceTopX, 0, beamZ + beamR + 25], va["cartela_sup"]["d"] / 2, "acero")
    for j, hx in enumerate(hang):
        cil(f"abrazadera.{j+1}", [hx - 20, 0, beamZ], [hx + 20, 0, beamZ], beamR + 7, "banda", "cuelgue")
        cil(f"grillete.{j+1}", [hx, 0, beamZ - beamR - 5], [hx, 0, pivotZ], 12, "oscuro", "cuelgue")

    # Accesorios por configuración (cuerpos: asientos, sogas, barras, cama)
    configs = {}
    for cfg in ficha["requisitos"]["configuraciones"]:
        cuerpos = []
        if cfg["puestos"] == ["cama"]:
            cm_ = ac["cama"]
            z = cm_["z"]
            cuerpos.append({"tipo": "caja", "nombre": "cama", "x": [-cm_["largo"] / 2, cm_["largo"] / 2], "y": [-cm_["ancho"] / 2, cm_["ancho"] / 2], "z": [z - 60, z + 100]})
            for sx in (-1, 1):
                for sy in (-1, 1):
                    cuerpos.append({"tipo": "soga", "a": [sx * (cm_["largo"] / 2 - 10), sy * (cm_["ancho"] / 2 - 10), z], "b": [sx * abs(hang[0]), 0, pivotZ]})
        else:
            for c, p in zip(slots, cfg["puestos"]):
                if p == "hamaca":
                    w = ac["asiento_ancho"] / 2
                    cuerpos.append({"tipo": "caja", "nombre": "asiento", "x": [c - w, c + w], "y": [-ac["asiento_prof"] / 2, ac["asiento_prof"] / 2], "z": [ac["asiento_z"] - 30, ac["asiento_z"]]})
                    for s in (-1, 1):
                        cuerpos.append({"tipo": "soga", "a": [c + s * (w + 20), 0, ac["asiento_z"]], "b": [c + s * cu["separacion_par"] / 2, 0, pivotZ]})
                elif p == "trapecio":
                    w = ac["trapecio_ancho"] / 2
                    cuerpos.append({"tipo": "barra", "a": [c - w, 0, ac["trapecio_z"]], "b": [c + w, 0, ac["trapecio_z"]], "r": 16})
                    for s in (-1, 1):
                        cuerpos.append({"tipo": "soga", "a": [c + s * (w + 10), 0, ac["trapecio_z"] + 16], "b": [c + s * cu["separacion_par"] / 2, 0, pivotZ]})
                elif p == "escalera":
                    for k in range(5):
                        z = 350 + k * 280
                        cuerpos.append({"tipo": "barra", "a": [c - 200, 0, z], "b": [c + 200, 0, z], "r": 15})
                    for s in (-1, 1):
                        cuerpos.append({"tipo": "soga", "a": [c + s * 210, 0, 350], "b": [c + s * cu["separacion_par"] / 2, 0, pivotZ]})
        configs[cfg["id"]] = cuerpos

    cos_v = apex / norm(sub([crossX, 0, apex], [footX, foot, 0]))  # coseno del ángulo de la pata con la vertical
    ang_real = math.degrees(math.acos(cos_v))
    # pie cortado horizontal: la fibra más larga suma R·tan(ángulo real)
    largo_pata = norm(sub(*legs[(1, 1)])) + pa["enterrado"] / cos_v + legR * math.tan(math.radians(ang_real))
    sobre_pata = lambda z: (z + pa["enterrado"]) / cos_v  # distancia sobre el eje de la pata, medida desde el pie
    deriv = {
        "apex": apex, "lean": lean, "ang_lateral": legDeg, "ang_frontal": frontDeg,
        "yTop": yTop, "yT": yT, "hang": hang, "slots": slots,
        # huella real en el piso: pata desfasada ±lap y corte elíptico del cilindro inclinado en vista frontal
        "pies_exterior": 2 * (footX + lap) + 2 * legR / math.cos(math.atan(lean)), "base_A": 2 * foot,
        "pozos_exterior": 2 * (footX + lap) + d["apoyo"]["pozo"][0],
        "libre_asiento": 2 * (axisX(ac["asiento_z"]) - legR - lap),
        "cara_inf_travesano": beamZ - beamR,
        "largo_pata_calc": largo_pata,
        "luz_travesano": 2 * axisX(beamZ),
        "ang_real": ang_real, "cos_v": cos_v,
        "marca_cruce": sobre_pata(apex), "marca_tirante": sobre_pata(tieZ), "marca_horqueta": sobre_pata(beamZ),
        "tirante_oblicuo_grados": math.degrees(math.atan(2 * lap / (2 * yT))),
        "tx": axisX(tieZ) - legR - tieR + ti["rebaje"] * 2,
        "largo_cartela_calc": norm(sub([axisX(tieZ) - legR - tieR + ti["rebaje"] * 2, 0, tieZ + tieR - ca["rebaje"]], [braceTopX, 0, beamZ - beamR + ca["rebaje"]])),
    }
    return {"piezas": piezas, "legs": {f"{k[0]},{k[1]}": v for k, v in legs.items()}, "configs": configs, "d": deriv,
            "axisX": axisX, "raw": {"beamR": beamR, "beamZ": beamZ, "beamHalf": beamHalf, "legR": legR, "footX": footX,
                                     "crossX": crossX, "foot": foot, "lap": lap, "tieZ": tieZ, "tieR": tieR,
                                     "braceR": braceR, "braceTopX": braceTopX, "pivotZ": pivotZ}}


# ======================================================================
# Validación rápida
# ======================================================================
def _chk(lst, id_, requisito, valor, limite, ok, nota="", dudoso=False):
    lst.append({"id": id_, "requisito": requisito, "valor": valor, "limite": limite,
                "estado": "dudoso" if dudoso else ("cumple" if ok else "no cumple"), "nota": nota})


def validar(ficha, M=None):
    M = M or modelo(ficha)
    d, D, r = ficha["diseno"], M["d"], M["raw"]
    req = ficha["requisitos"]
    tip = catalogo_tipologia(ficha["tipologia"])
    mat = catalogo_materiales()["maderas"][d["material"]]
    cu, ac, pa = d["cuelgues"], d["accesorios"], d["patas"]
    out = []

    # --- espacio ---
    esp = req["espacio"]
    _chk(out, "espacio.eje", "Entra en el largo disponible a lo largo del travesaño",
         m(D["pies_exterior"]) + " de pie a pie por fuera", m(esp["largo_eje_travesano_m"] * 1000),
         D["pies_exterior"] <= esp["largo_eje_travesano_m"] * 1000)
    _chk(out, "espacio.pozos", "Los pozos (centrados en cada pie) entran en el largo disponible",
         m(D["pozos_exterior"]) + " de pozo a pozo por fuera", m(esp["largo_eje_travesano_m"] * 1000),
         D["pozos_exterior"] <= esp["largo_eje_travesano_m"] * 1000)
    L = cu["z_giro"] - ac["asiento_z"]
    zl = (L * 0.867 + 1500)
    _chk(out, "norma.zona_libre", "Zona libre de vaivén (EN 1176-2): (giro − asiento)·0,867 + 1,50 m por lado",
         m(zl) + " por lado = " + m(2 * zl), m(esp["largo_vaiven_m"] * 1000),
         2 * zl <= esp["largo_vaiven_m"] * 1000 + 5,
         "Entra justo" if abs(2 * zl - esp["largo_vaiven_m"] * 1000) < 30 else "")
    for cfg in req["configuraciones"]:
        if "cama" in cfg["puestos"]:
            zlc = (cu["z_giro"] - ac["cama"]["z"]) * 0.867 + 1500
            _chk(out, "norma.zona_libre_cama", "Zona libre de vaivén de la hamaca-cama (misma fórmula, cama a " + m(ac["cama"]["z"]) + ")",
                 m(zlc) + " por lado = " + m(2 * zlc), m(esp["largo_vaiven_m"] * 1000), 2 * zlc <= esp["largo_vaiven_m"] * 1000 + 5)
    # --- separaciones ---
    s_min = 0.2 * L + 200
    tiene_ham = any("hamaca" in c["puestos"] for c in req["configuraciones"])
    if tiene_ham:
        anchos = {"hamaca": ac["asiento_ancho"], "trapecio": ac["trapecio_ancho"], "escalera": 400}
        paso = cu["puestos_x"][1] - cu["puestos_x"][0]
        gap = min(paso - (anchos[a] + anchos[b]) / 2 for c in req["configuraciones"] if "cama" not in c["puestos"]
                  for a, b in zip(c["puestos"], c["puestos"][1:]))
        _chk(out, "norma.sep_asientos", "Separación entre accesorios vecinos (0,20·L + 0,20 m)", m(gap, 3), "≥ " + m(s_min, 3), gap >= s_min)
        sp_min = 0.2 * L + 300
        x_ext = max(abs(x) for x in cu["puestos_x"]) + ac["asiento_ancho"] / 2
        gap_p = D["libre_asiento"] / 2 - x_ext
        _chk(out, "norma.sep_pata", "Separación asiento–pata (0,20·L + 0,30 m)", m(gap_p), "≥ " + m(sp_min), gap_p >= sp_min)
        h0, h1 = tip["norma"]["altura_asiento_m"]
        _chk(out, "norma.altura_asiento", "Altura del asiento", m(ac["asiento_z"]), f"{num(h0)}–{num(h1)} m",
             h0 * 1000 <= ac["asiento_z"] <= h1 * 1000)
    if any("trapecio" in c["puestos"] for c in req["configuraciones"]):
        lim = tip["norma"]["caida_max_trapecio_m"] * 1000
        _chk(out, "norma.trapecio", "Altura de caída del trapecio", m(ac["trapecio_z"]), "≤ " + m(lim), ac["trapecio_z"] <= lim)

    # --- geometría cerrada ---
    zc_formula = D["apex"]
    _chk(out, "geo.cruce", "Altura del cruce: zc = z_eje − (R_trav + R_pata)/sin(atan(semibase/zc))", m(zc_formula, 3),
         "tangencia del travesaño en la V", True)
    _chk(out, "geo.angulos", "Ángulos de las patas", f"{num(D['ang_lateral'], 0)}° lateral · {num(D['ang_frontal'], 0)}° frontal", "—", True)
    _chk(out, "geo.largo_pata", "Largo de pata (enterrado + pie cortado horizontal) vs. rollizo comercial",
         m(D["largo_pata_calc"], 3), "≤ " + m(pa["largo_comercial"], 3), D["largo_pata_calc"] <= pa["largo_comercial"])
    _chk(out, "geo.prolongacion", "Prolongación de la pata sobre el cruce cubre el travesaño",
         cm(pa["prolongacion"]), "≥ " + cm(2 * r["beamR"] + 100), pa["prolongacion"] >= 2 * r["beamR"] + 100)
    _chk(out, "geo.voladizo", "El travesaño sobresale de la horqueta en ambos extremos",
         m(d["travesano"]["largo"] / 2 - M["axisX"](r["beamZ"])), "≥ 0,15 m", d["travesano"]["largo"] / 2 - M["axisX"](r["beamZ"]) >= 150)
    _chk(out, "geo.cartela", "Largo de la cartela entre apoyos vs. pieza", m(D["largo_cartela_calc"]), "≤ " + m(d["cartela"]["largo"]),
         D["largo_cartela_calc"] <= d["cartela"]["largo"])

    ap = d["apoyo"]
    huella = pa["diametro"] / D["cos_v"]
    _chk(out, "geo.pozo", "El pozo contiene la huella del pie inclinado (elipse de " + cm(huella) + ")",
         cm(ap["pozo"][0]) + " de lado", "≥ huella + 5 cm", ap["pozo"][0] >= huella + 50)
    # --- cargas y flexión del travesaño ---
    luz = D["luz_travesano"]
    E, fadm = mat["E_MPa"], mat["tension_flexion_adm_MPa"]
    dm = d["travesano"]["diametro"]
    W = math.pi * dm ** 3 / 32  # mm3
    I = math.pi * dm ** 4 / 64
    fd = req["factor_dinamico"]
    casos = []
    # caso A: carga de diseño (cama) repartida en las 2 abrazaderas exteriores
    P = req["carga_diseno_kg"] * G * fd
    a = luz / 2 - abs(D["hang"][0])
    casos.append(("Carga de diseño en las abrazaderas exteriores (cama)", (P / 2) * a, P / 2 * a * (3 * luz ** 2 - 4 * a ** 2) / (24 * E * I)))
    # caso B: un adulto por puesto en los 3 puestos
    Pp = req["carga_por_puesto_kg"] * G * fd
    xs = [x + luz / 2 for x in cu["puestos_x"]]
    Ra = sum(Pp * (luz - xi) for xi in xs) / luz
    Mc = Ra * luz / 2 - sum(Pp * (luz / 2 - xi) for xi in xs if xi < luz / 2)
    casos.append(("Un adulto por puesto en los 3 puestos", Mc, None))
    # caso C (envolvente conservadora): toda la carga de diseño en el puesto central
    casos.append(("Toda la carga de diseño en el puesto central (envolvente)", P * luz / 4, P * luz ** 3 / (48 * E * I)))
    for nombre, Mmax, flecha in casos:
        sig = Mmax / W
        _chk(out, "calc.flexion", f"Flexión del travesaño — {nombre}", f"σ = {num(sig, 1)} MPa (M = {num(Mmax / 1e6, 2)} kN·m)",
             f"≤ {num(fadm, 0)} MPa", sig <= fadm)
        if flecha is not None:
            _chk(out, "calc.flecha", f"Flecha del travesaño — {nombre}", f"{num(flecha, 1)} mm", f"≤ L/300 = {num(luz / 300, 1)} mm", flecha <= luz / 300)

    # --- peso propio ---
    vol = 0
    for p in M["piezas"]:
        if p["mat"] == "madera":
            vol += math.pi * p["r"] ** 2 * norm(sub(p["b"], p["a"]))
    vol_m3 = vol / 1e9
    Gp = vol_m3 * mat["densidad_kg_m3"] * G  # N

    # --- vuelco (sin anclaje), en el sentido del vaivén ---
    amp = tip["calculo"]["amplitud_max_grados"]
    fs_min = tip["calculo"]["fs_vuelco_min"]
    zg = cu["z_giro"]
    for cfg in req["configuraciones"]:
        H = V = 0
        for p in cfg["puestos"]:
            masa = req["carga_diseno_kg"] if p == "cama" else req["carga_por_puesto_kg"]
            t0 = math.radians(amp.get(p, 45))
            best = (0, 0)
            for k in range(1, 900):
                t = t0 * k / 900
                T = masa * G * (3 * math.cos(t) - 2 * math.cos(t0))
                if T * math.sin(t) > best[0]:
                    best = (T * math.sin(t), T * math.cos(t))
            H += best[0]
            V += best[1]
        Mv = H * zg
        Ms = (Gp + V) * r["foot"]
        fs = Ms / Mv
        _chk(out, "calc.vuelco", f"Vuelco sin anclaje — {cfg['nombre']} (todos en fase)",
             f"FS = {num(fs, 2)} (H = {num(H / 1000, 2)} kN a {m(zg)})", f"≥ {num(fs_min, 1)}", fs >= fs_min)

    # --- compresión / pandeo de patas ---
    Ntot = req["carga_diseno_kg"] * G * fd + Gp
    f, e = M["legs"]["1,1"]
    cosv = (sub([r["crossX"], 0, M["d"]["apex"]], [r["footX"], r["foot"], 0])[2]) / norm(sub([r["crossX"], 0, M["d"]["apex"]], [r["footX"], r["foot"], 0]))
    N = Ntot / 4 / cosv
    Il = math.pi * pa["diametro"] ** 4 / 64
    Lp = norm(sub([r["crossX"], 0, M["d"]["apex"]], [r["footX"], r["foot"], 0]))
    Pcr = math.pi ** 2 * E * Il / Lp ** 2
    _chk(out, "calc.pandeo", "Pandeo de pata (Euler, pie–cruce)", f"N = {num(N / 1000, 2)} kN; FS = {num(Pcr / N, 0)}", "FS ≥ 3", Pcr / N >= 3)

    # --- varillas: largo suficiente (agarre + arandela, tuerca y contratuerca) ---
    va = d["varillas"]
    grips = {
        "horqueta": 2 * (D["yTop"] + r["legR"] / math.cos(math.radians(D["ang_lateral"]))),
        "cruce": 2 * pa["diametro"] - 2 * pa["diametro"] * pa["rebaje_cruce_frac"],
        "tirante": d["tirante"]["diametro"] + pa["diametro"] - 2 * d["tirante"]["rebaje"],
        "cartela_inf": d["tirante"]["diametro"] + d["cartela"]["diametro"] * 0.9,
        "cartela_sup": d["travesano"]["diametro"] + d["cartela"]["diametro"] * 0.9,
    }
    for k, g in grips.items():
        need = g + 2 * 30
        _chk(out, "varilla." + k, f"Varilla {k.replace('_', ' ')} ({va[k]['d']} mm): agarre + 2 × (arandela + tuerca + contratuerca)",
             m(va[k]["largo"]), "≥ " + m(need), va[k]["largo"] >= need)

    vol_ent = pa["cantidad"] * math.pi * (pa["diametro"] / 2) ** 2 * (D["largo_pata_calc"] - norm(sub(*M["legs"]["1,1"]))) / 1e9
    return {"checks": out, "peso_propio_kg": vol_m3 * mat["densidad_kg_m3"], "peso_total_kg": (vol_m3 + vol_ent) * mat["densidad_kg_m3"],
            "volumen_madera_m3": vol_m3,
            "resumen": resumen_validacion(out)}


def resumen_validacion(checks):
    n = len(checks)
    ok = sum(c["estado"] == "cumple" for c in checks)
    malos = [c for c in checks if c["estado"] != "cumple"]
    lineas = [f"{ok}/{n} verificaciones cumplen."]
    for c in malos:
        lineas.append(f"- {c['estado'].upper()}: {c['requisito']} → {c['valor']} (límite {c['limite']})")
    return "\n".join(lineas)


# ======================================================================
# Despiece y pedido de materiales
# ======================================================================
def _rollizo_comercial(d_mm, largo_mm, mat):
    dc = d_mm / 10
    for lo, hi in mat["rangos_diametro_cm"]:
        if lo <= dc < hi:
            return lo, hi
    return mat["rangos_diametro_cm"][-1]


def despiece(ficha, M=None):
    M = M or modelo(ficha)
    d, D = ficha["diseno"], M["d"]
    mat = catalogo_materiales()
    mad = mat["maderas"][d["material"]]
    pa, ti, ca, tr, va = d["patas"], d["tirante"], d["cartela"], d["travesano"], d["varillas"]
    hol = va["holgura_agujero"]
    piezas = [
        {"id": "T1", "pieza": "Travesaño", "cant": 1, "material": mad["nombre"], "seccion": f"Ø{cm(tr['diametro'])}", "largo": tr["largo"],
         "angulos": "Puntas a escuadra", "rebajes": f"Plano de {cm(ca['rebaje'])} abajo, a ±{m(ca['x_sup'])} del centro, para apoyar cada cartela",
         "agujeros": f"2 pasantes Ø{va['horqueta']['d'] + hol} mm horizontales (sentido del vaivén) a ±{m(M['axisX'](tr['z_eje']))} del centro, en el eje; 2 pasantes Ø{va['cartela_sup']['d'] + hol} mm verticales a ±{m(ca['x_sup'])} del centro (cartelas)"},
        {"id": "P1–P4", "pieza": "Patas", "cant": pa["cantidad"], "material": mad["nombre"], "seccion": f"Ø{cm(pa['diametro'])}", "largo": pa["largo"],
         "angulos": f"Pie cortado horizontal: la pata forma {num(D['ang_real'], 1)}° con la vertical ({num(D['ang_lateral'], 0)}° en vista lateral y {num(D['ang_frontal'], 0)}° en vista frontal)",
         "rebajes": f"Media madera en el cruce (1/3 Ø ≈ {cm(pa['diametro'] * pa['rebaje_cruce_frac'], 1)}); asiento de {cm(pa['asiento_horqueta'], 1)} para el travesaño; plano de {cm(ti['rebaje'], 1)} para el tirante; asiento plano para la arandela donde sale cada varilla",
         "agujeros": f"Medidas SOBRE la pata desde el pie: cruce Ø{va['cruce']['d'] + hol} a {m(D['marca_cruce'])} (altura {m(D['apex'])}); tirante Ø{va['tirante']['d'] + hol} a {m(D['marca_tirante'])} (altura {m(ti['z'])}); horqueta Ø{va['horqueta']['d'] + hol} a {m(D['marca_horqueta'])} (altura {m(tr['z_eje'])})"},
        {"id": "R1–R2", "pieza": "Tirantes", "cant": 2, "material": mad["nombre"], "seccion": f"Ø{cm(ti['diametro'])}", "largo": ti["largo"],
         "angulos": f"Puntas a escuadra; queda oblicuo {num(D['tirante_oblicuo_grados'], 1)}° en planta (sigue el desfase de la media madera)", "rebajes": f"2 planos de {cm(ti['rebaje'], 1)} contra las patas; plano de {cm(ca['rebaje'], 0)} arriba al centro para la cartela",
         "agujeros": f"2 × Ø{va['tirante']['d'] + hol} horizontales (patas) + 1 × Ø{va['cartela_inf']['d'] + hol} vertical al centro"},
        {"id": "C1–C2", "pieza": "Cartelas", "cant": 2, "material": mad["nombre"], "seccion": f"Ø{cm(ca['diametro'])}", "largo": ca["largo"],
         "angulos": "Puntas cortadas horizontales", "rebajes": f"Planos de {cm(ca['rebaje'], 0)} en las dos puntas; asiento plano para la arandela donde sale la varilla",
         "agujeros": f"1 × Ø{va['cartela_inf']['d'] + hol} vertical en cada punta"},
    ]
    # pedido de madera por medida comercial
    madera = []
    def add_madera(id_, desc, d_mm, largo_mm, cant_piezas, por_rollizo, uso):
        lo, hi = _rollizo_comercial(d_mm, largo_mm, mad)
        Lc = min(x for x in mad["largos_comerciales_m"] if x * 1000 >= largo_mm * por_rollizo + 20 * por_rollizo)
        n = math.ceil(cant_piezas / por_rollizo)
        madera.append({"id": id_, "descripcion": f"{desc} Ø {lo}-{hi} cm × {num(Lc, 1)} m (mín. Ø {num(d_mm / 10, 0)} cm en la punta fina)", "cant": n, "unidad": "u", "uso": uso,
                       "largo_util_mm": largo_mm * cant_piezas, "largo_compra_mm": Lc * 1000 * n})
    add_madera("rollizo_d20_l4", "Rollizo eucalipto impregnado", tr["diametro"], tr["largo"], 1, 1, "Travesaño")
    add_madera("rollizo_d17_l3", "Rollizo eucalipto impregnado", pa["diametro"], pa["largo"], pa["cantidad"], 1, "Patas")
    add_madera("rollizo_d15_l25", "Rollizo eucalipto impregnado", ti["diametro"], ti["largo"], 2, 2, "2 tirantes de un rollizo")
    add_madera("rollizo_d12_l25", "Rollizo eucalipto impregnado", ca["diametro"], ca["largo"], 2, 2, "2 cartelas de un rollizo")

    # varillas: optimización de corte en barras de 1 m
    vr = mat["metales"]["varilla-roscada-galvanizada"]
    cortes = {}
    for k, v in va.items():
        if not isinstance(v, dict):
            continue
        n = v.get("cant", v.get("cant_por_abrazadera", 0) * len(D["hang"]))
        cortes.setdefault(v["d"], []).extend([(v["largo"], k)] * n)
    ferre = []
    barras_det = {}
    for dia, lst in sorted(cortes.items(), reverse=True):
        lst.sort(reverse=True)
        barras = []
        for L, k in lst:
            for b in barras:
                if b["libre"] >= L + vr["corte_mm"]:
                    b["cortes"].append(L); b["libre"] -= L + vr["corte_mm"]; break
            else:
                barras.append({"cortes": [L], "libre": vr["largo_barra_mm"] - L - vr["corte_mm"]})
        barras_det[dia] = barras
        nvar = len(lst)
        ferre.append({"id": f"varilla_{dia}", "descripcion": f"Varilla roscada galvanizada {dia} mm ({PULG[dia]}) × 1 m", "cant": len(barras), "unidad": "u",
                      "uso": f"{nvar} tramos: " + ", ".join(f"{sum(1 for x in lst if x[1] == k)} × {m(L)}" for L, k in sorted(set(lst), reverse=True))})
        ferre.append({"id": f"tuerca_{dia}", "descripcion": f"Tuerca galvanizada {PULG[dia]} (misma rosca que la varilla)", "cant": nvar * 4, "unidad": "u", "uso": "Tuerca + contratuerca en cada punta"})
        if dia >= 12:
            ferre.append({"id": f"arandela_ancha_{dia}", "descripcion": f"Arandela ancha galvanizada {PULG[dia]} (Ø ext. {d['arandela_ancha_mm']}-60 mm)", "cant": nvar * 2, "unidad": "u", "uso": "Una por punta"})
        else:
            ferre.append({"id": f"arandela_{dia}", "descripcion": f"Arandela galvanizada {PULG[dia]}", "cant": nvar * 2, "unidad": "u", "uso": "Una por punta"})
    ab = d["cuelgues"]["abrazadera"]
    nab = len(D["hang"])
    radio = ab["radio_interior"] + ab["goma_mm"]
    tira = 2 * (math.pi * radio + ab["oreja"])
    plan_m = tira * nab * (1 + d["desperdicio_pct"] / 100) / 1000
    ferre.append({"id": "planchuela_40x5", "descripcion": f"Planchuela {ab['planchuela']} mm × 6 m (galvanizada; si es de hierro negro, la herrería la termina con galvanizado en frío)", "cant": math.ceil(plan_m / 6), "unidad": "barra 6 m",
                  "uso": f"{nab} abrazaderas × 2 medias cañas de {m(tira / 2)} = {num(plan_m, 1)} m con desperdicio", "metros": plan_m})
    goma_m = nab * (2 * math.pi * ab["radio_interior"] + 30) / 1000 * (1 + d["desperdicio_pct"] / 100)
    ferre.append({"id": "goma_3mm", "descripcion": "Goma 3 mm, tira de 5 cm de ancho", "cant": round(goma_m, 1), "unidad": "m", "uso": "Banda bajo cada abrazadera", "area_m2": goma_m * 0.05})
    ferre.append({"id": "grillete_10", "descripcion": "Grillete galvanizado 3/8\" (10 mm) o gancho giratorio, carga de trabajo ≥ 0,5 t", "cant": nab, "unidad": "u", "uso": "Uno por abrazadera"})

    # terminación y apoyo
    ins = mat["insumos"]
    area = 0
    for p in M["piezas"]:
        if p["mat"] == "madera":
            area += 2 * math.pi * p["r"] * norm(sub(p["b"], p["a"]))
    area_m2 = area / 1e6
    cet = ins["cetol"]
    litros = area_m2 * cet["manos"] / cet["rendimiento_m2_l_mano"]
    ap = d["apoyo"]
    asf = ins["asfalto-frio"]
    area_asf = pa["cantidad"] * math.pi * pa["diametro"] * ap["proteccion_largo"] / 1e6
    litros_asf = area_asf * asf["manos"] / asf["rendimiento_m2_l_mano"]
    term = [
        {"id": "cetol_4l", "descripcion": "Cetol para madera exterior, 4 L", "cant": math.ceil(litros / cet["envase_l"]), "unidad": "u",
         "uso": f"{num(area_m2, 1)} m² × {cet['manos']} manos ≈ {num(litros, 1)} L"},
        {"id": "asfalto_frio_4l", "descripcion": "Asfalto en frío / pintura asfáltica, 4 L", "cant": math.ceil(litros_asf / asf["envase_l"]), "unidad": "u",
         "uso": f"Últimos {cm(ap['proteccion_largo'])} de cada pata: {num(area_asf, 2)} m² × {asf['manos']} manos"},
        {"id": "ladrillo_macizo", "descripcion": "Ladrillo común macizo", "cant": pa["cantidad"], "unidad": "u", "uso": "Uno en el fondo de cada pozo (o laja)"},
    ]
    px, py, pz = ap["pozo"]
    vol_ripio = pa["cantidad"] * (px * py * pz - math.pi * (pa["diametro"] / 2) ** 2 * pa["enterrado"] - 250 * 120 * 55) / 1e9
    term.append({"id": "ripio_bolsa", "descripcion": "Ripio / piedra partida", "cant": round(vol_ripio * ins["ripio"]["densidad_kg_m3"]), "unidad": "kg",
                 "uso": f"{pa['cantidad']} pozos de {cm(px)} × {cm(py)} × {cm(pz)}: {num(vol_ripio, 3)} m³"})

    # desperdicio de madera
    util = sum(x["largo_util_mm"] for x in madera)
    compra = sum(x["largo_compra_mm"] for x in madera)
    return {"piezas": piezas, "varillas_corte": {str(k): v for k, v in barras_det.items()},
            "pedido": {"madera": madera, "ferreteria": ferre, "terminacion_apoyo": term},
            "desperdicio_madera_pct": 100 * (1 - util / compra),
            "area_madera_m2": area_m2}
