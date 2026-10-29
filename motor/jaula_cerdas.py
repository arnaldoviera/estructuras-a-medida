"""Tipología jaula-cerdas (hierro): box de alimentación individual para cerdas gestantes, tipo Gestal 3G.
modelo → validar → despiece → salidas (planta, lateral, croquis 3D y página técnica sin presupuesto).
Medidas en mm. Ejes: x desde la puerta trasera (0) al frente; y transversal con eje al centro; z arriba."""
import datetime, html, json, math, os
from comun import catalogo_tipologia, catalogo_materiales, num, RAIZ

E = html.escape


def mm(v):
    return f"{v:,.0f}".replace(",", ".")


def _tag(origen):
    """Primera palabra del origen: fuente, criterio, cálculo o supuesto (cualquier otra cosa cuenta como supuesto)."""
    o = (origen or "").strip().lower()
    return next((t for t in ("fuente", "criterio", "cálculo", "supuesto") if o.startswith(t)), "supuesto")


def nombre_tubo(t):
    """Nombre comercial armado desde la medida real (no desde el texto de la ficha): Ø exterior × espesor (pulgadas)."""
    cat = catalogo_materiales()["metales"]["tubo-estructural-redondo"]["diametros_mm"]
    pulg = next((k for k, v in cat.items() if abs(v - t["diam"]) < 0.2), None)
    return f"tubo estructural redondo Ø{num(t['diam'], 1)} × {num(t['esp'], 1)}" + (f" ({pulg})" if pulg else " (medida no comercial)")


def _W(D, e):
    return math.pi * (D ** 4 - (D - 2 * e) ** 4) / (32 * D)


def _kg_m(D, e):
    return math.pi * (D - e) * e * 7.85e-3


# ======================================================================
# Modelo
# ======================================================================
def modelo(ficha):
    d, req = ficha["diseno"], ficha["requisitos"]
    T = d["tubos"]
    L, H, AL = d["box"]["largo"], d["box"]["alto"], d["box"]["ancho_libre"]
    RP, RL, RG = T["parante"]["diam"] / 2, T["larguero"]["diam"] / 2, T["puerta"]["diam"] / 2
    YC = (AL + T["parante"]["diam"]) / 2
    D = {"L": L, "H": H, "AL": AL, "RP": RP, "RL": RL, "RG": RG, "RS": T["pasamanos"]["diam"] / 2, "YC": YC,
         "EXT": round(2 * YC + T["parante"]["diam"]), "pie_alto": 9.5 + d["pie"]["pletina"]["esp"],
         "slat": req["galpon"]["slat"], "linea": req["linea_alimento"]}
    return {"d": D, "escena": _escena(d, D)}


def _escena(d, D):
    L, H, YC, RP, RL, RG = D["L"], D["H"], D["YC"], D["RP"], D["RL"], D["RG"]
    T, P, F, PL = d["tubos"], d["puerta"], d["frente"], d["pie"]["pletina"]
    p, c = [], []
    cil = lambda n, a, b, r, m: p.append({"n": n, "a": a, "b": b, "r": r, "m": m})
    caja = lambda n, x, y, z, m: c.append({"n": n, "x": x, "y": y, "z": z, "m": m})
    dz = d["dosificador"]["travesano_z"]
    des = PL["desplazamiento_afuera"]
    for s in (-1, 1):
        y = s * YC
        for x in d["parantes_x"]:
            cil("parante", [x, y, D["pie_alto"]], [x, y, H], RP, "galva")
            yp = y + s * des
            caja("pletina inox", [x - PL["largo"] / 2, x + PL["largo"] / 2], [yp - PL["ancho"] / 2, yp + PL["ancho"] / 2], [0, PL["esp"]], "inox")
            caja("placa base galva", [x - 75, x + 75], [yp - 75, yp + 75], [PL["esp"], D["pie_alto"]], "galva")
            caja("contrapletina inox", [x - 150, x + 150], [yp - 50, yp + 50], [-98, -90], "inox")
        for z in d["largueros_z"]:
            cil("larguero", [0, y, z], [L, y, z], RL, "galva")
        cil("pasamanos", [0, y, H], [L, y, H], D["RS"], "galva")
        cil("soporte dosificador", [L, y, H], [L, y, dz], RL, "galva")
    cil("travesaño trasero superior", [0, -YC, H], [0, YC, H], D["RS"], "galva")
    cil("travesaño frontal superior", [L, -YC, H], [L, YC, H], D["RS"], "galva")
    cil("travesaño dosificador", [L, -YC, dz], [L, YC, dz], RL, "galva")
    g, pz, bz, tz = P["ancho"] / 2, P["pivote_z"], P["borde_inf_z"], P["trinquete_z"]
    for s in (-1, 1):
        ye = s * (YC + RP + 20)  # leva y varilla por fuera del parante
        caja("leva inox", [-30, 30], sorted([s * (YC + RP + 10), s * (YC + RP + 30)]), [pz - 60, pz + 15], "inox")
        cil("varilla de mando (por fuera)", [0, ye, pz - 45], [0, ye, tz + 15], 5, "galva")
        caja("guarda de chapa", [-35, 35], sorted([s * (YC + RP + 32), s * (YC + RP + 36)]), [tz - 40, pz - 20], "galva")
        cil("perno pasante del trinquete", [0, s * (YC - RP - 10), tz], [0, s * (YC + RP + 30), tz], 5, "galva")
        caja("trinquete (diente adentro)", [22, 72], sorted([s * (g + 6), s * (YC - RP)]), [tz - 30, tz + 30], "oscuro")
    cil("eje puerta inox (pasante)", [0, -(YC + RP + 30), pz], [0, YC + RP + 30, pz], P["eje"]["diam"] / 2, "inox")
    for y in (-g, g):
        cil("puerta lateral", [0, y, pz], [0, y, bz], RG, "puerta")
    for z in P["travesanos_z"]:
        cil("puerta travesaño", [0, -g, z], [0, g, z], RG, "puerta")
    pc = P["panel_ciego"]
    caja("panel ciego PEAD", [-5, 5], [-g + RG, g - RG], [pc["z0"], pc["z1"]], "pead")
    rb = T["barrote"]["diam"] / 2
    n = F["barrotes_cant"]
    luz = (D["AL"] - n * 2 * rb) / (n + 1)
    z330 = F["travesanos_z"][1]
    for i in range(n):
        yb = -D["AL"] / 2 + luz * (i + 1) + rb * (2 * i + 1)
        cil("barrote frontal", [L, yb, z330], [L, yb, H], rb, "galva")
    caja("zócalo frontal", [L - 1, L + 1], [-YC + RP, YC - RP], [50, z330], "galva")
    for z in F["travesanos_z"]:
        cil(f"travesaño frontal z {z}", [L, -YC, z], [L, YC, z], RL, "galva")
    co, do, ca = d["comedero"], d["dosificador"], d["caida"]
    cil("apoyo trasero comedero", [co["apoyo_trasero_x"], -YC, F["travesanos_z"][0]], [co["apoyo_trasero_x"], YC, F["travesanos_z"][0]], RL, "galva")
    caja("comedero inox", [co["x0"], co["x1"]], [-co["ancho"] / 2, co["ancho"] / 2], [co["z0"], co["z1"]], "inox")
    caja("pestaña de apoyo del comedero", [co["x1"], L - RL + 6], [-co["ancho"] / 2, co["ancho"] / 2], [co["z0"] - 2, co["z0"]], "inox")
    for s in (-1, 1):
        caja("protección lateral del comedero", [co["x0"], L - RP], sorted([s * (YC - RL - 1), s * (YC - RL - 3)]), [130, 400], "galva")
    caja("dosificador", [do["x0"], do["x1"]], [-do["ancho"] / 2, do["ancho"] / 2], [do["z0"], do["z1"]], "electro")
    xm = (do["x0"] + do["x1"]) / 2
    la = D["linea"]
    cil("bajada a dosificador", [xm, 0, do["z1"]], [xm, 0, la["z"]], 22, "inox")
    cil("caída al comedero", [ca["x"], 0, ca["z1"]], [ca["x"], 0, ca["z0"]], 25, "inox")
    cil("línea de alimento", [xm, -1600, la["z"]], [xm, 1600, la["z"]], la["diam"] / 2, "linea")
    r = d["rfid"]
    caja("antena RFID", [r["x0"], r["x1"]], [r["y_cara"] - 22, r["y_cara"]], [r["z0"], r["z1"]], "rfid")
    zr = min(d["largueros_z"], key=lambda z: abs(z - (r["z0"] + r["z1"]) / 2))  # larguero donde se toma el separador
    caja("separador PEAD", [r["x0"] + 10, r["x1"] - 10], [r["y_cara"], YC - RL], [zr - 15, zr + 15], "pead")
    sl, x = [], -500
    while x < L + 500:
        sl.append([x, x + D["slat"]["ancho"]])
        x += D["slat"]["ancho"] + D["slat"]["ranura"]
    return {"piezas": p, "cajas": c, "slats": sl, "largo": L, "yc": YC}


# ======================================================================
# Validación (mismos cálculos que el auditor; cálculo simplificado de anteproyecto)
# ======================================================================
def _chk(lst, id_, requisito, valor, limite, ok, nota=""):
    lst.append({"id": id_, "requisito": requisito, "valor": valor, "limite": limite,
                "estado": "cumple" if ok else "no cumple", "nota": nota})


def validar(ficha, M=None):
    M = M or modelo(ficha)
    d, D, req = ficha["diseno"], M["d"], ficha["requisitos"]
    cr = catalogo_tipologia(ficha["tipologia"])["criterios"]
    cat = catalogo_materiales()["metales"]["tubo-estructural-redondo"]
    T, P, F, PL = d["tubos"], d["puerta"], d["frente"], d["pie"]["pletina"]
    fy, fs_min = cat["fy_MPa"], cr["fs_min"]["valor"]
    F_emp = cr["empuje_lateral_kN"]["valor"] * 1000
    out = []

    def fs(tubo, M_Nmm):
        t = T[tubo]
        return fy / (M_Nmm / _W(t["diam"], t["esp"]))

    a = cr["ancho_libre_mm"]
    _chk(out, "dim.ancho", "Ancho libre interior dentro del rango de las fuentes", f"{D['AL']} mm", f"{a['min']}–{a['max']} mm",
         a["min"] <= D["AL"] <= a["max"], a["origen"])
    util = D["L"] - 2 * D["RP"]
    _chk(out, "dim.largo", "Largo útil entre parantes trasero y delantero", f"{mm(util)} mm", f"≥ {mm(cr['largo_min_mm']['valor'])} mm",
         util >= cr["largo_min_mm"]["valor"], cr["largo_min_mm"]["origen"])
    zs = sorted(d["largueros_z"]) + [D["H"]]
    luces = [round(zs[i + 1] - zs[i] - (D["RL"] + (D["RS"] if zs[i + 1] == D["H"] else D["RL"]))) for i in range(len(zs) - 1)]
    _chk(out, "bien.luz_lateral", "Luz entre largueros (no pasa pata ni cabeza)", f"{min(luces)}–{max(luces)} mm", f"≤ {cr['luz_lateral_max_mm']['valor']} mm",
         max(luces) <= cr["luz_lateral_max_mm"]["valor"], cr["luz_lateral_max_mm"]["origen"])
    lp = min(d["largueros_z"]) - D["RL"]
    _chk(out, "bien.luz_piso", "Luz entre el piso y el primer larguero", f"{lp:.0f} mm", f"≤ {cr['luz_piso_max_mm']['valor']} mm",
         lp <= cr["luz_piso_max_mm"]["valor"], cr["luz_piso_max_mm"]["origen"])
    rb, n = T["barrote"]["diam"] / 2, F["barrotes_cant"]
    luz_f = (D["AL"] - n * 2 * rb) / (n + 1)
    _chk(out, "bien.luz_frontal", "Luz entre barrotes del frente", f"{luz_f:.0f} mm", f"≤ {cr['luz_frontal_max_mm']['valor']} mm",
         luz_f <= cr["luz_frontal_max_mm"]["valor"], cr["luz_frontal_max_mm"]["origen"])
    hol = (D["YC"] - D["RP"]) - (P["ancho"] / 2 + D["RG"])
    lo, hi = cr["pellizco_mm"]["prohibido"]
    _chk(out, "bien.pellizco", "Holgura puerta–parante: la puerta entra y queda fuera de la franja de pellizco", f"{num(hol, 1)} mm", f"0 < h < {lo} o > {hi} mm",
         0 < hol and not (lo <= hol <= hi), cr["pellizco_mm"]["origen"] + ("; con holgura ≤ 0 la puerta choca con el parante" if hol <= 0 else ""))
    pc = P["panel_ciego"]
    _chk(out, "bien.vulva", "Panel ciego de la puerta a la altura de la vulva", f"z {pc['z0']}–{pc['z1']}", "cubre z 550–750",
         pc["z0"] <= 550 and pc["z1"] >= 750, "criterio: la cerda que espera afuera no alcanza la vulva")
    lomo = cr["lomo_mm"]["rango"][1] + cr["lomo_mm"]["margen"]
    _chk(out, "mec.arco", "La puerta abierta a 90° pasa sobre el lomo", f"pivote a {mm(P['pivote_z'])} mm", f"≥ {mm(lomo)} mm",
         P["pivote_z"] >= lomo and P.get("apertura_max_grados", 90) >= 90, cr["lomo_mm"]["origen"])
    hueco = (D["H"] - D["RS"]) - (P["pivote_z"] + 25)
    _chk(out, "mec.eje", "Lugar para la oreja del eje bajo el travesaño trasero", f"{num(hueco, 1)} mm libres", "> 0 mm", hueco > 0,
         "oreja de 50 mm centrada en el pivote")
    reac = F_emp * (P["pivote_z"] - P["borde_inf_z"]) / (P["pivote_z"] - P["trinquete_z"]) / 2
    _chk(out, "mec.traba", "Reacción por trinquete con el empuje de la cerda de afuera", f"{num(reac / 1000, 2)} kN", "≤ 1,0 kN",
         reac <= 1000, "dos trinquetes bajos, uno por lado")
    vano = max(d["parantes_x"][i + 1] - d["parantes_x"][i] for i in range(len(d["parantes_x"]) - 1))
    f1 = fs("larguero", F_emp * vano / 4)
    _chk(out, "res.larguero", f"Larguero: {num(F_emp / 1000, 1)} kN a media luz del vano de {mm(vano)} (apoyado)", f"FS {num(f1, 2)}",
         f"≥ {num(fs_min, 2)}", f1 >= fs_min, cr["empuje_lateral_kN"]["origen"])
    zf = sorted(F["travesanos_z"][1:] + [D["H"]])
    vb = max(zf[i + 1] - zf[i] for i in range(len(zf) - 1))
    f2 = fs("barrote", F_emp * vb / 4)
    _chk(out, "res.barrote", f"Barrote frontal: empuje a media luz del vano de {mm(vb)} (apoyado)", f"FS {num(f2, 2)}", f"≥ {num(fs_min, 2)}",
         f2 >= fs_min, "criterio: la barra de cabeza parte el vano")
    f3 = fs("puerta", F_emp * P["ancho"] / 4)
    _chk(out, "res.puerta", "Travesaño de puerta: empuje a media luz", f"FS {num(f3, 2)}", f"≥ {num(fs_min, 2)}", f3 >= fs_min)
    f4 = fs("pasamanos", F_emp * vano / 4)
    _chk(out, "res.pasamanos", "Pasamanos: empuje a media luz", f"FS {num(f4, 2)}", f"≥ {num(fs_min, 2)}", f4 >= fs_min)
    f5 = fs("parante", cr["momento_base_kNm"]["valor"] * 1e6)
    _chk(out, "res.parante", f"Parante en la base: {num(cr['momento_base_kNm']['valor'], 1)} kN·m", f"FS {num(f5, 2)}", f"≥ {num(fs_min, 2)}",
         f5 >= fs_min, cr["momento_base_kNm"]["origen"])
    q = cr["dosificador_kg"]
    f6 = fs("larguero", q["valor"] * q["factor"] * 9.81 * 2 * D["YC"] / 4)
    _chk(out, "res.dosificador", f"Travesaño del dosificador: {q['valor']} kg × {q['factor']}", f"FS {num(f6, 2)}", f"≥ {num(fs_min, 2)}",
         f6 >= fs_min, q["origen"])
    inv = D["AL"] / 2 - (D["YC"] + PL["desplazamiento_afuera"] - PL["ancho"] / 2)
    _chk(out, "pie.invasion", "El pie no achica el ancho libre a ras del piso", f"{num(inv, 1)} mm por lado",
         f"≤ {cr['invasion_pie_max_mm']['valor']} mm", inv <= cr["invasion_pie_max_mm"]["valor"], cr["invasion_pie_max_mm"]["origen"])
    s = D["slat"]
    _chk(out, "pie.vigas", "La pletina abraza al menos 2 vigas del slat", f"{PL['largo']} mm", f"≥ {2 * s['ancho'] + s['ranura']} mm",
         PL["largo"] >= 2 * s["ancho"] + s["ranura"])
    sb = abs(d["pie"]["m10_y"] - d["pie"]["m12_y"])
    _chk(out, "pie.bulones", f"Separación entre bulones M10 (y ±{d['pie']['m10_y']}) y M12 (y ±{d['pie']['m12_y']}) del pie", f"{sb} mm", "≥ 19,5 mm (arandelas)", sb >= 19.5,
         "con los M12 en colisos sobre esas rectas no chocan en ninguna posición de la ranura")
    sep = D["YC"] - D["RL"] - d["rfid"]["y_cara"]
    _chk(out, "elec.antena", "Antena RFID separada del metal", f"{num(sep, 1)} mm", "≥ 50 mm", sep >= 50,
         "fuente: separar de masas metálicas; mínimo a confirmar con el proveedor")
    la, lf, do = D["linea"], cr["linea_alimento"], d["dosificador"]
    _chk(out, "elec.linea", "La línea de alimento del galpón pasa por encima del dosificador", f"Ø{la['diam']} a {mm(la['z'])} mm",
         f"≥ {mm(do['z1'] + 100)} mm", la["z"] >= do["z1"] + 100, f"dato del galpón; referencia Gestal 3G: Ø{lf['diam_mm']} a {mm(lf['z_mm'])} mm")
    # coherencia de posiciones: lo que cuelga del frente tiene que acompañar al largo del box
    L, co, ca, px = D["L"], d["comedero"], d["caida"], d["parantes_x"]
    _chk(out, "geo.parantes", "Los parantes van de la puerta (x 0) al frente (x = largo)", f"x {mm(px[0])} … {mm(px[-1])}", f"0 … {mm(L)}",
         px[0] == 0 and px[-1] == L and px == sorted(px))
    _chk(out, "geo.comedero", "El comedero apoya contra el frente", f"x {mm(co['x0'])}–{mm(co['x1'])}", f"termina entre {mm(L - D['RP'] - 60)} y {mm(L)} (zócalo)",
         L - D["RP"] - 60 <= co["x1"] <= L and co["x0"] < co["apoyo_trasero_x"] < co["x1"])
    _chk(out, "geo.dosificador", "El dosificador queda sobre el travesaño del frente", f"x {mm(do['x0'])}–{mm(do['x1'])}", f"contiene x {mm(L - D['RL'])}",
         do["x0"] <= L - D["RL"] <= do["x1"] + D["RL"])
    _chk(out, "geo.caida", "La caída descarga dentro del comedero y baja desde el dosificador", f"x {mm(ca['x'])}", f"{mm(co['x0'])}–{mm(co['x1'])}",
         co["x0"] + 25 <= ca["x"] <= co["x1"] - 25 and do["x0"] <= ca["x"] <= do["x1"])
    dias, esps = list(cat["diametros_mm"].values()), cat["espesores_mm"]
    malos = [k for k, t in T.items() if not (any(abs(t["diam"] - x) < 0.2 for x in dias) and t["esp"] in esps)]
    _chk(out, "fab.tubos", "Todos los tubos son medidas comerciales de tubo estructural", "ninguno fuera" if not malos else ", ".join(malos),
         "catálogo", not malos, cat["nota"])
    desp = despiece(ficha, M)
    pl = desp["peso"]["lateral_kg"]
    _chk(out, "fab.peso", "Peso del subconjunto más pesado (lateral) para 2 personas", f"{num(pl, 0)} kg", "≤ 80 kg", pl <= 80)
    return {"checks": out, "peso_propio_kg": desp["peso"]["total_kg"], "peso_total_kg": desp["peso"]["total_kg"],
            "resumen": _resumen(out)}


def _resumen(checks):
    ok = sum(c["estado"] == "cumple" for c in checks)
    lin = [f"{ok}/{len(checks)} verificaciones cumplen."]
    lin += [f"- {c['estado'].upper()}: {c['requisito']} → {c['valor']} (límite {c['limite']})" for c in checks if c["estado"] != "cumple"]
    return "\n".join(lin)


# ======================================================================
# Despiece, plan de corte y pedido (sin precios)
# ======================================================================
def despiece(ficha, M=None):
    M = M or modelo(ficha)
    d, D = ficha["diseno"], M["d"]
    cat = catalogo_materiales()["metales"]["tubo-estructural-redondo"]
    BARRA, CORTE = cat["largo_barra_mm"], cat["corte_mm"]
    T, P, F, PL = d["tubos"], d["puerta"], d["frente"], d["pie"]["pletina"]
    L, H, AL, YC = D["L"], D["H"], D["AL"], D["YC"]
    dP, dS, dL = T["parante"]["diam"], T["pasamanos"]["diam"], T["larguero"]["diam"]
    PX = d["parantes_x"]
    luz_trav = round(2 * YC - dP)
    luz_lar = round(2 * (YC - dL / 2))
    vanos = [round(PX[i + 1] - PX[i] - dP) for i in range(len(PX) - 1)]
    z_tr = F["travesanos_z"]
    dz = d["dosificador"]["travesano_z"]
    piezas = []

    def pz(id_, pieza, cant, tubo, largo, sub, ops):
        t = T[tubo]
        piezas.append({"id": id_, "pieza": pieza, "cant": cant, "subconjunto": sub, "material": nombre_tubo(t), "tubo": tubo,
                       "seccion": f"Ø{num(t['diam'], 1)} × {num(t['esp'], 1)}", "largo": largo, "operaciones": ops})

    def otra(id_, pieza, cant, material, medida, sub, ops, kg_u=0.0):
        piezas.append({"id": id_, "pieza": pieza, "cant": cant, "subconjunto": sub, "material": material, "tubo": None,
                       "seccion": medida, "largo": None, "operaciones": ops, "kg_u": kg_u})

    n_lat, n_pies = 2, 2 * len(PX)
    pz("L1", "Parante", n_lat * len(PX), "parante", round(H - D["pie_alto"] - dS / 2), "Lateral",
       "Pie a escuadra con tapa soldada; cabeza con boca de pescado contra el pasamanos; venteo Ø10 cerca de cada punta, en la cara ±x (adelante o atrás) y por encima de las cartelas: fuera de la fibra más cargada")
    pz("L2", "Pasamanos", n_lat, "pasamanos", round(L + dP), "Lateral", "Puntas a escuadra con tapa soldada; venteos Ø10; oreja para actuador (un lateral)")
    for i, v in enumerate(vanos):
        pz(f"L3.{i + 1}", f"Larguero, vano {i + 1}", n_lat * len(d["largueros_z"]), "larguero", v, "Lateral",
           "Boca de pescado en las dos puntas; a z " + " · ".join(mm(z) for z in d["largueros_z"]) + "; venteo Ø10 por tramo, cara exterior")
    pz("L4", "Soporte de dosificador", n_lat, "larguero", round(dz - H - dS / 2 - dL / 2), "Lateral",
       f"Sobre el pasamanos en x {mm(L)}; boca de pescado en las dos puntas")
    nombres = {z_tr[0]: "Travesaño inferior frontal (apoyo comedero)", z_tr[1]: f"Travesaño frontal z {z_tr[1]}", z_tr[2]: f"Barra de cabeza z {z_tr[2]}"}
    for i, z in enumerate(z_tr, 1):
        pz(f"F{i}", nombres[z], 1, "larguero", luz_trav, "Frente", f"z {z}; boca de pescado; se une a los parantes delanteros con planchuela y 2 M10")
    pz("F4", "Travesaño frontal superior", 1, "pasamanos", luz_trav, "Frente", f"z {mm(H)}; boca de pescado; planchuela y 2 M10")
    nb = F["barrotes_cant"]
    pz("F5", "Barrote frontal, tramo inferior", nb, "barrote", round(z_tr[2] - z_tr[1] - dL), "Frente", f"Entre z {z_tr[1]} y {z_tr[2]}; boca de pescado")
    pz("F6", "Barrote frontal, tramo superior", nb, "barrote", round(H - z_tr[2] - dL / 2 - dS / 2), "Frente", f"Entre z {z_tr[2]} y {mm(H)}; boca de pescado")
    pz("F7", "Travesaño del dosificador", 1, "larguero", round(2 * YC - dL), "Frente", f"z {mm(dz)}; boca de pescado; 2 planchuelas para el dosificador")
    pz("F8", "Apoyo trasero del comedero", 1, "larguero", luz_lar, "Frente",
       f"x {mm(d['comedero']['apoyo_trasero_x'])}, z {z_tr[0]}; se cuelga del larguero inferior de cada lateral con planchuela y 2 M10")
    otra("F9", "Zócalo frontal", 1, "Chapa galvanizada 2 mm", f"{AL} × {z_tr[1] - 50}", "Frente", "Abulonado a parantes y travesaños; cantos protegidos",
         AL * (z_tr[1] - 50) * 2 * 7.85e-6)
    pz("R1", "Travesaño trasero superior", 1, "pasamanos", luz_trav, "Trasero", f"z {mm(H)}; boca de pescado; planchuela y 2 M10")
    alto_p = P["pivote_z"] - P["borde_inf_z"]
    pz("P1", "Lateral de puerta", 2, "puerta", alto_p, "Puerta", "Arriba planchuela con agujero Ø21 para el eje y pasador")
    pz("P2", "Travesaño de puerta", len(P["travesanos_z"]), "puerta", round(P["ancho"] - T["puerta"]["diam"]), "Puerta",
       "z " + " · ".join(str(z) for z in P["travesanos_z"]) + "; boca de pescado")
    pcz = P["panel_ciego"]
    pw, ph = round(P["ancho"] - T["puerta"]["diam"]), pcz["z1"] - pcz["z0"]
    otra("P3", "Panel ciego", 1, "PEAD 10 mm", f"{pw} × {ph}", "Puerta", "6 M8 inox con arandelas grandes; cantos redondeados", pw * ph * 10 * 0.95e-6)
    ej = d["puerta"]["eje"]["diam"]
    le = round(2 * YC + dP + 60)  # pasante por los dos parantes traseros + leva por fuera
    otra("P4", "Eje de puerta (pasante)", 1, "Barra inox 304 maciza", f"Ø{ej} × {le}", "Puerta",
         "Atraviesa los dos parantes traseros por bujes de PEAD; leva soldada en una punta, por fuera; agujero Ø6 para el pasador de la puerta",
         math.pi * (ej / 2) ** 2 * le * 7.9e-6)
    otra("P5", "Refuerzo del agujero del eje", 2, "Planchuela 2\" × ¼\" galvanizada", "50,8 × 6,35 × 100", "Trasero",
         "Soldada por fuera del parante trasero, alineada con el agujero Ø30 del parante para el buje", 0.25)
    otra("P6", "Buje", 4, "PEAD", "Ø30 × Ø20 × 15", "Puerta",
         "2 en los parantes traseros y 2 en las planchuelas de la puerta (agujero Ø30): aíslan el eje inox del galvanizado")
    ltr = round(2 * D["RP"] + 30)  # buje del trinquete: atraviesa el parante y sobresale 15 por lado
    otra("P7", "Trinquete (diente + brazo + buje)", 2, "Planchuela 2\" × ¼\" galvanizada + tubo Ø17,2 × 2,3", f"diente 80, brazo 60, buje {ltr}", "Trasero",
         f"A z {P['trinquete_z']}: diente (adentro, traba la puerta) y brazo (afuera, lo mueve la varilla) soldados a un buje de tubo que gira dentro de un agujero Ø20 del parante; tope de goma y taco plano de apoyo", 0.55)
    otra("P7b", "Perno del trinquete", 2, "Bulón M10 × 100 galvanizado con tuerca autofrenante", f"M10 × 100", "Trasero",
         f"Atraviesa el buje del trinquete ({ltr} mm) con arandelas a los dos lados")
    otra("P12", "Leva", 2, "Chapa inox 304 6 mm", "60 × 75 × 6", "Puerta", "Soldada al eje inox, una por punta, por fuera del parante; ojal para la varilla", 0.2)
    vl = P["pivote_z"] - 20 - P["trinquete_z"] - 30
    otra("P8", "Varilla de mando", 2, "Barra redonda maciza galvanizada", f"Ø10 × {vl}", "Trasero", "Por fuera del parante, de la leva al brazo del trinquete; ojal en cada punta", 0.617 * vl / 1000)
    lg = (P["pivote_z"] - 20) - (P["trinquete_z"] - 40)
    otra("P9", "Guarda de la varilla", 2, "Chapa galvanizada 2 mm", f"100 × {lg}", "Trasero", "Doblada en U, abulonada al parante con 2 M8; cubre leva, varilla y brazo", 100 * lg * 2 * 7.85e-6)
    otra("P11", "Gatillo y palanca de destrabe", 1, "Planchuela 2\" × ¼\" galvanizada", "juego (≈ 0,3 m)", "Trasero",
         "Gatillo a 70° hacia adentro (arma la traba) y palanca de destrabe manual desde el pasillo; pernos de ojal M8", 0.8)
    lc = round(L - D["RP"] - d["comedero"]["x0"])
    otra("C4", "Protección lateral del comedero", 2, "Chapa galvanizada 2 mm", f"{lc} × 270", "Lateral",
         f"x {mm(d['comedero']['x0'])} a la cara del parante delantero, z 130 a 400 (por encima del apoyo trasero), cantos doblados 15 mm; "
         "abulonada por dentro de los largueros con 4 M8: la cerda de al lado no alcanza el comedero", lc * 300 * 2 * 7.85e-6)
    otra("P10", "Resorte regulable y topes de goma", 1, "Juego", "1 resorte + 4 topes", "Puerta", "Topes en parantes traseros y en el pasamanos (90°)")
    co = d["comedero"]
    cl, ca_, ch = co["x1"] - co["x0"], co["ancho"], co["z1"] - co["z0"]
    otra("C1", "Comedero", 1, "Inox 304 1,5 mm", f"{cl} × {ca_} × {ch}", "Frente", "Sin bordes filosos; M8 inox con bujes de nylon; nunca soldado",
         (cl * ca_ + 2 * ch * (cl + ca_)) * 1.5 * 7.9e-6)
    cz = d["caida"]["z1"] - d["caida"]["z0"]
    otra("C2", "Caída de alimento", 1, "Caño inox 304 Ø50 × 1,5", f"{cz}", "Frente", "Abrazadera inox con buje de nylon al travesaño frontal superior",
         math.pi * 48.5 * 1.5 * cz * 7.9e-6)
    r_ = d["rfid"]
    zr = min(d["largueros_z"], key=lambda z: abs(z - (r_["z0"] + r_["z1"]) / 2))
    otra("C3", "Separador de antena", 1, "PEAD", f"{r_['x1'] - r_['x0'] - 20} × {round(YC - dL / 2 - r_['y_cara'])} × 30", "Lateral",
         f"2 agujeros Ø9 al larguero z {mm(zr)}")
    otra("B1", "Placa base", n_pies, "Chapa 9,5 mm galvanizada", "150 × 150 × 9,5", "Lateral",
         "Concéntrica con la pletina; parante corrido 25 mm hacia adentro; 4 agujeros Ø14 a ±55 (lugar para la vaina aislante del M10)", 150 * 150 * 9.5 * 7.85e-6)
    otra("B2", "Cartela", 3 * n_pies, "Chapa 6 mm galvanizada", "45 × 45 × 6 (±x) y 60 × 60 × 6 (afuera)", "Lateral",
         "3 por parante: hacia adelante, hacia atrás y hacia afuera; ninguna hacia adentro (no invade el ancho libre)", 0.5 * 50 * 50 * 6 * 7.85e-6)
    otra("B3", "Tapa de caño", n_pies + 2 * n_lat, "Chapa 3 mm galvanizada", "Ø50,8 × 3", "Lateral", "Pie de cada parante y puntas de pasamanos",
         math.pi * 25.4 ** 2 * 3 * 7.85e-6)
    otra("B4", "Pletina de apoyo", n_pies, "Inox 304 10 mm", f"{PL['largo']} × {PL['ancho']} × {PL['esp']}", "Pie",
         f"Chaflanes 2 × 45°, esquinas R15; 4 agujeros roscados M10 a ±{d['pie']['m10_y']} (abajo está el slat: sin tuerca); 2 colisos avellanados para M12 en y ±{d['pie']['m12_y']}", PL["largo"] * PL["ancho"] * PL["esp"] * 7.9e-6)
    otra("B5", "Contrapletina", n_pies, "Inox 304 8 mm", "300 × 100 × 8", "Pie", f"Abraza 2 vigas del slat; 2 colisos Ø13 en y ±{d['pie']['m12_y']}", 300 * 100 * 8 * 7.9e-6)
    otra("B6", "Junta aislante", n_pies, "Fenólico 3 mm", "155 × 160 × 3", "Pie", "Entre placa base y pletina; al ras del lado interior y sobresale 5 mm hacia los otros tres lados")
    n_abul = len(z_tr) + 4  # travesaños frontales + superior frontal + del dosificador + trasero superior + apoyo del comedero: una planchuela por punta
    otra("U1", "Planchuela de unión", 2 * n_abul, "Planchuela 2\" × ¼\" galvanizada", "50,8 × 6,35 × 80", "Uniones",
         "2 agujeros Ø11; una por punta de cada travesaño abulonado (frente, dosificador, trasero y apoyo del comedero)", 0.2)
    otra("U2", "Planchuela del dosificador", 2, "Planchuela 2\" × ¼\" galvanizada", "50,8 × 6,35 × 120", "Frente", "2 agujeros Ø13 a 100 mm", 0.3)
    otra("U3", "Oreja del actuador", 1, "Planchuela 2\" × ¼\" galvanizada", "50,8 × 6,35 × 80", "Lateral", "Agujero Ø13; previsión etapa 4", 0.2)

    # cantidad de boxes: el despiece y el pedido salen para todos; los pesos se informan también por box
    nb = int(ficha["requisitos"].get("cantidad_boxes", 1) or 1)
    for p in piezas:
        p["cant"] *= nb

    # plan de corte por sección (mismo tubo, misma barra), primer ajuste decreciente
    cortes, clave = {}, {}
    for p in piezas:
        if p["tubo"]:
            t = T[p["tubo"]]
            k = clave.setdefault((t["diam"], t["esp"]), p["tubo"])
            cortes.setdefault(k, []).extend([p["largo"]] * p["cant"])
    barras = {}
    for tubo, lst in cortes.items():
        bs = []
        for c_ in sorted(lst, reverse=True):
            for b in bs:
                if b["libre"] >= c_ + CORTE:
                    b["cortes"].append(c_)
                    b["libre"] -= c_ + CORTE
                    break
            else:
                bs.append({"cortes": [c_], "libre": BARRA - c_ - CORTE})
        barras[tubo] = bs

    # pesos (con 5 % de zinc en lo galvanizado)
    kg_tubo = sum(p["cant"] * p["largo"] / 1000 * _kg_m(T[p["tubo"]]["diam"], T[p["tubo"]]["esp"]) for p in piezas if p["tubo"])
    kg_galv_otros = sum(p["cant"] * p.get("kg_u", 0) for p in piezas if not p["tubo"] and "galvaniz" in (p["material"] or "").lower())
    kg_resto = sum(p["cant"] * p.get("kg_u", 0) for p in piezas if not p["tubo"] and "galvaniz" not in (p["material"] or "").lower())
    kg_galv = (kg_tubo + kg_galv_otros) * 1.05
    lat = [p for p in piezas if p["subconjunto"] == "Lateral" and p["id"] not in ("U3", "C3")]
    kg_lat = (sum(p["cant"] * (p["largo"] / 1000 * _kg_m(T[p["tubo"]]["diam"], T[p["tubo"]]["esp"]) if p["tubo"] else p.get("kg_u", 0)) for p in lat) / (n_lat * nb)) * 1.05
    peso = {"total_kg": round(kg_galv + kg_resto, 1), "galvanizado_kg": round(kg_galv, 1), "otros_kg": round(kg_resto, 1),
            "tubo_kg": round(kg_tubo, 1), "lateral_kg": round(kg_lat, 1), "por_box_kg": round((kg_galv + kg_resto) / nb, 1), "boxes": nb}

    pedido = {"tubo": [], "chapa_y_planchuela": [], "inox": [], "bulones_y_aislacion": [], "otros": []}
    for tubo, bs in barras.items():
        util = sum(sum(b["cortes"]) for b in bs)
        pedido["tubo"].append({"id": f"tubo_{tubo}", "descripcion": nombre_tubo(T[tubo]) + f", barra de {num(BARRA / 1000, 0)} m", "cant": len(bs),
                               "unidad": "barra", "uso": f"{mm(util)} mm útiles", "desperdicio_pct": round(100 * (1 - util / (len(bs) * BARRA)), 1)})
    pedido["chapa_y_planchuela"] += [
        {"id": "planch_2x14", "descripcion": "Planchuela 2\" × ¼\" (50,8 × 6,35)", "cant": 1, "unidad": "barra de 6 m", "uso": "orejas, trinquetes, uniones, dosificador, actuador"},
        {"id": "chapa_95", "descripcion": "Chapa 9,5 mm, placas base 150 × 150", "cant": n_pies, "unidad": "u", "uso": "B1"},
        {"id": "chapa_6", "descripcion": "Chapa 6 mm, cartelas (2 de 45 × 45 y 1 de 60 × 60 por pie)", "cant": 3 * n_pies, "unidad": "u", "uso": "B2"},
        {"id": "chapa_3", "descripcion": "Chapa 3 mm, tapas Ø50,8", "cant": n_pies + 2 * n_lat, "unidad": "u", "uso": "B3"},
        {"id": "chapa_2", "descripcion": f"Chapa galvanizada 2 mm: zócalo {AL} × {z_tr[1] - 50}, 2 guardas 100 × {lg} y 2 protecciones {lc} × 300", "cant": 1, "unidad": "juego", "uso": "F9, P9, C4"},
        {"id": "barra_10", "descripcion": f"Barra redonda maciza Ø10, 2 × {vl} mm", "cant": 1, "unidad": "juego", "uso": "P8"}]
    pedido["inox"] += [
        {"id": "inox_leva", "descripcion": "Chapa inox 304 6 mm, 2 levas 60 × 75", "cant": 1, "unidad": "juego", "uso": "P12"},
        {"id": "inox_pletina", "descripcion": f"Pletina inox 304 {PL['largo']} × {PL['ancho']} × {PL['esp']}, corte láser", "cant": n_pies, "unidad": "u", "uso": "B4"},
        {"id": "inox_contra", "descripcion": "Contrapletina inox 304 300 × 100 × 8", "cant": n_pies, "unidad": "u", "uso": "B5"},
        {"id": "inox_eje", "descripcion": f"Barra inox 304 maciza Ø{ej} × {le}", "cant": 1, "unidad": "u", "uso": "P4"},
        {"id": "inox_comedero", "descripcion": f"Comedero inox 304 {cl} × {ca_} × {ch} (a medida)", "cant": 1, "unidad": "u", "uso": "C1"},
        {"id": "inox_caida", "descripcion": f"Caño inox 304 Ø50 × 1,5 × {cz} + abrazadera", "cant": 1, "unidad": "juego", "uso": "C2"}]
    pedido["bulones_y_aislacion"] += [
        {"id": "m12_avell", "descripcion": "Bulón M12 × 140 inox, cabeza avellanada DIN 7991, tuerca autofrenante y arandela", "cant": 4 * n_pies, "unidad": "u",
         "uso": "anclaje al slat (largo según el espesor real del slat)"},
        {"id": "m10_inox_pie", "descripcion": "Bulón M10 × 25 inox (rosca en la pletina, no sobresale hacia el slat) con vaina y arandela aislantes", "cant": 4 * n_pies, "unidad": "juego", "uso": "pie"},
        {"id": "fenolico", "descripcion": "Junta fenólica 155 × 160 × 3", "cant": n_pies, "unidad": "u", "uso": "B6"},
        {"id": "m10_galv", "descripcion": "Bulón M10 × 70 galvanizado con tuerca autofrenante y 2 arandelas", "cant": 4 * n_abul, "unidad": "u",
         "uso": "uniones de subconjuntos (2 por planchuela)"},
        {"id": "m10x100_galv", "descripcion": "Bulón M10 × 100 galvanizado con tuerca autofrenante y 2 arandelas", "cant": 2, "unidad": "u", "uso": "perno de cada trinquete (P7b)"},
        {"id": "m8_inox", "descripcion": "Bulón M8 inox con buje y arandelas de nylon", "cant": 12, "unidad": "juego", "uso": "comedero (6) y panel ciego (6)"},
        {"id": "m8_galv", "descripcion": "Bulón M8 galvanizado con arandela", "cant": 24, "unidad": "u",
         "uso": "zócalo (6), separador de antena (2), guardas (4), protecciones del comedero (8) y ojales de la varilla (4)"},
        {"id": "pasador", "descripcion": "Pasador elástico Ø6 galvanizado con vaina aislante", "cant": 2, "unidad": "u", "uso": "puerta–eje"}]
    pedido["otros"] += [
        {"id": "pead_10", "descripcion": f"Placa PEAD 10 mm {pw} × {ph}", "cant": 1, "unidad": "u", "uso": "P3"},
        {"id": "pead_buje", "descripcion": "Barra PEAD Ø30 (4 bujes) y taco de PEAD 30 mm de espesor (separador de antena)", "cant": 1, "unidad": "juego", "uso": "P6, C3"},
        {"id": "resorte", "descripcion": "Resorte de tracción regulable + 4 topes de goma", "cant": 1, "unidad": "juego", "uso": "P10"},
        {"id": "galvanizado", "descripcion": "Servicio de galvanizado por inmersión en caliente (subconjuntos ya soldados)", "cant": round(kg_tubo + kg_galv_otros),
         "unidad": "kg aprox.", "uso": "laterales, frente, trasero, puerta, chapas y planchuelas"}]
    for grupo in ("chapa_y_planchuela", "inox", "bulones_y_aislacion", "otros"):
        for r in pedido[grupo]:
            if r["id"] == "planch_2x14":
                r["cant"] = math.ceil(2.4 * nb / 6)  # ≈ 2,4 m de planchuela por box
            elif r["id"] != "galvanizado":
                r["cant"] *= nb
    return {"piezas": piezas, "barras_corte": barras, "pedido": pedido, "peso": peso, "barra_comercial_mm": BARRA, "corte_mm": CORTE,
            "nota": "Largos entre caras para uniones a tope con boca de pescado; verificar en el plano de taller. Sin precios ni presupuesto."}


# ======================================================================
# Gráficos (SVG con clases que pinta la plantilla)
# ======================================================================
DEFS = ('<defs><marker id="fl" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0,1 L9,5 L0,9 z" class="flecha"/></marker>'
        '<pattern id="hatch" width="24" height="24" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        '<line x1="0" y1="0" x2="0" y2="24" class="hatch"/></pattern></defs>')


def _cota_h(x0, x1, y, txt, arriba=True):
    ty = y - 28 if arriba else y + 78
    return (f'<line class="cota" x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" marker-start="url(#fl)" marker-end="url(#fl)"/>'
            f'<text class="ct" x="{(x0 + x1) / 2}" y="{ty}" text-anchor="middle">{txt}</text>')


def _cota_v(x, y0, y1, txt, izq=True):
    return (f'<line class="cota" x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" marker-start="url(#fl)" marker-end="url(#fl)"/>'
            f'<text class="ct" x="{x - 30 if izq else x + 30}" y="{(y0 + y1) / 2 + 22}" text-anchor="{"end" if izq else "start"}">{txt}</text>')


def planta(ficha, M):
    d, D = ficha["diseno"], M["d"]
    L, YC, RP = D["L"], D["YC"], D["RP"]
    PL = d["pie"]["pletina"]
    W = 2 * YC + 2 * RP
    pad_l, pad_r, pad_t, pad_b = 560, 560, 260, 300
    ox, oy = pad_l, pad_t + W / 2
    X, Y = (lambda x: ox + x), (lambda y: oy - y)
    s = [f'<svg viewBox="0 0 {L + pad_l + pad_r:.0f} {W + pad_t + pad_b:.0f}" role="img" aria-label="Planta">', DEFS]
    co, do, r = d["comedero"], d["dosificador"], d["rfid"]
    s.append(f'<rect class="comedero" x="{X(co["x0"])}" y="{Y(co["ancho"] / 2)}" width="{co["x1"] - co["x0"]}" height="{co["ancho"]}"/>')
    s.append(f'<rect class="dosif" x="{X(do["x0"])}" y="{Y(do["ancho"] / 2)}" width="{do["x1"] - do["x0"]}" height="{do["ancho"]}"/>')
    for sg in (-1, 1):
        y = sg * YC
        s.append(f'<rect class="tubo" x="{X(0)}" y="{Y(y) - RP}" width="{L}" height="{2 * RP}"/>')
        for x in d["parantes_x"]:
            s.append(f'<rect class="pie" x="{X(x) - PL["largo"] / 2}" y="{Y(y + sg * PL["desplazamiento_afuera"]) - PL["ancho"] / 2}" width="{PL["largo"]}" height="{PL["ancho"]}"/>')
            s.append(f'<circle class="parante" cx="{X(x)}" cy="{Y(y)}" r="{RP}"/>')
    s.append(f'<rect class="tubo" x="{X(L) - RP}" y="{Y(YC)}" width="{2 * RP}" height="{2 * YC}"/>')
    s.append(f'<line class="puerta" x1="{X(0)}" y1="{Y(d["puerta"]["ancho"] / 2)}" x2="{X(0)}" y2="{Y(-d["puerta"]["ancho"] / 2)}"/>')
    s.append(f'<line class="caida" x1="{X(d["caida"]["x"])}" y1="{Y(0) - 25}" x2="{X(d["caida"]["x"])}" y2="{Y(0) + 25}"/>')
    s.append(f'<rect class="rfid" x="{X(r["x0"])}" y="{Y(r["y_cara"])}" width="{r["x1"] - r["x0"]}" height="22"/>')
    s.append(f'<text class="rot" x="{X(-60)}" y="{Y(0) + 22}" text-anchor="end">ENTRADA →</text>')
    s.append(f'<text class="rot ac" x="{X(90)}" y="{Y(-YC) + 120}">puerta trasera</text>')
    s.append(f'<text class="rot" x="{X((co["x0"] + co["x1"]) / 2)}" y="{Y(-YC) + 140}" text-anchor="middle">comedero inox</text>')
    s.append(f'<text class="rot" x="{X(r["x0"]) - 40}" y="{Y(YC) - 70}" text-anchor="end">antena RFID</text>')
    x1 = d["parantes_x"][1]
    s.append(f'<text class="rot" x="{X(x1)}" y="{Y(YC) - 110}" text-anchor="middle">pletina de anclaje</text>')
    s.append(_cota_h(X(0), X(L), Y(-YC) + 190, mm(L), arriba=False))
    s.append(_cota_h(X(0), X(x1), Y(YC) - 190, mm(x1)))
    s.append(_cota_v(X(L / 2), Y(YC - RP), Y(-YC + RP), f"{mm(D['AL'])} libre", izq=False))
    s.append(_cota_v(X(L) + 200, Y(YC + RP), Y(-YC - RP), f"{mm(D['EXT'])} ext.", izq=False))
    s.append("</svg>")
    return "".join(s)


def lateral(ficha, M):
    d, D = ficha["diseno"], M["d"]
    L, H, RP, RL, RS = D["L"], D["H"], D["RP"], D["RL"], D["RS"]
    la, sl, F, P = D["linea"], D["slat"], d["frente"], d["puerta"]
    dz = d["dosificador"]["travesano_z"]
    zt = la["z"] + 60
    pad_l, pad_r, pad_t, pad_b = 1000, 980, 120, 420
    ox, oz = pad_l, pad_t + zt
    X, Z = (lambda x: ox + x), (lambda z: oz - z)
    s = [f'<svg viewBox="0 0 {L + pad_l + pad_r:.0f} {zt + pad_t + pad_b:.0f}" role="img" aria-label="Vista lateral">', DEFS]
    x = -500
    while x < L + 400:
        s.append(f'<rect class="slat" x="{X(x)}" y="{Z(0)}" width="{sl["ancho"]}" height="90"/>')
        x += sl["ancho"] + sl["ranura"]
    co, do, ca, r = d["comedero"], d["dosificador"], d["caida"], d["rfid"]
    xm = (do["x0"] + do["x1"]) / 2
    for z in d["largueros_z"]:
        s.append(f'<rect class="tubo" x="{X(0)}" y="{Z(z) - RL}" width="{L}" height="{2 * RL}"/>')
    s.append(f'<rect class="tubo" x="{X(0)}" y="{Z(H) - RS}" width="{L}" height="{2 * RS}"/>')
    for x in d["parantes_x"]:
        s.append(f'<rect class="tubo" x="{X(x) - RP}" y="{Z(H)}" width="{2 * RP}" height="{H}"/>')
        s.append(f'<rect class="pie" x="{X(x) - d["pie"]["pletina"]["largo"] / 2}" y="{Z(D["pie_alto"])}" width="{d["pie"]["pletina"]["largo"]}" height="{D["pie_alto"]}"/>')
    s.append(f'<rect class="tubo" x="{X(L) - RL}" y="{Z(dz)}" width="{2 * RL}" height="{dz - H}"/>')
    s.append(f'<circle class="parante" cx="{X(L)}" cy="{Z(dz)}" r="{RL}"/>')
    s.append(f'<rect class="comedero" x="{X(co["x0"])}" y="{Z(co["z1"])}" width="{co["x1"] - co["x0"]}" height="{co["z1"] - co["z0"]}"/>')
    s.append(f'<rect class="dosif" x="{X(do["x0"])}" y="{Z(do["z1"])}" width="{do["x1"] - do["x0"]}" height="{do["z1"] - do["z0"]}"/>')
    s.append(f'<line class="bajada" x1="{X(xm)}" y1="{Z(la["z"])}" x2="{X(xm)}" y2="{Z(do["z1"])}"/>')
    s.append(f'<line class="bajada" x1="{X(ca["x"])}" y1="{Z(ca["z1"])}" x2="{X(ca["x"])}" y2="{Z(ca["z0"])}"/>')
    z1 = F["travesanos_z"][1]
    s.append(f'<line class="tubo-l" x1="{X(L)}" y1="{Z(z1)}" x2="{X(L)}" y2="{Z(H)}"/>')
    s.append(f'<rect class="zocalo" x="{X(L) - 8}" y="{Z(z1)}" width="16" height="{z1 - 50}"/>')
    for zz in F["travesanos_z"]:
        s.append(f'<circle class="parante" cx="{X(L)}" cy="{Z(zz)}" r="{RL}"/>')
    s.append(f'<circle class="parante" cx="{X(co["apoyo_trasero_x"])}" cy="{Z(F["travesanos_z"][0])}" r="{RL}"/>')
    s.append(f'<circle class="linea" cx="{X(xm)}" cy="{Z(la["z"])}" r="{la["diam"] / 2}"/>')
    s.append(f'<rect class="rfid" x="{X(r["x0"])}" y="{Z(r["z1"])}" width="{r["x1"] - r["x0"]}" height="{r["z1"] - r["z0"]}"/>')
    pz, bz, pc, tz = P["pivote_z"], P["borde_inf_z"], P["panel_ciego"], P["trinquete_z"]
    R = pz - bz
    for sg in (1, -1):
        pts = " ".join(f"{X(sg * R * math.sin(math.radians(t))):.0f},{Z(pz - R * math.cos(math.radians(t))):.0f}" for t in range(0, 91, 5))
        s.append(f'<polyline class="arco" points="{pts}"/>')
    s.append(f'<rect class="panel" x="{X(0) - 22}" y="{Z(pc["z1"])}" width="44" height="{pc["z1"] - pc["z0"]}"/>')
    s.append(f'<line class="puerta" x1="{X(0)}" y1="{Z(pz)}" x2="{X(0)}" y2="{Z(bz)}"/>')
    s.append(f'<circle class="pivote" cx="{X(0)}" cy="{Z(pz)}" r="20"/>')
    s.append(f'<rect class="trinq" x="{X(0) + 22}" y="{Z(tz + 30)}" width="50" height="60"/>')
    s.append(f'<text class="rot ac" x="{X(-60)}" y="{Z(700)}" text-anchor="end">puerta con</text>')
    s.append(f'<text class="rot ac" x="{X(-60)}" y="{Z(700) + 80}" text-anchor="end">panel ciego</text>')
    s.append(f'<text class="rot" x="{X(100)}" y="{Z(tz) + 20}">2 trinquetes z {tz}</text>')
    s.append(f'<text class="rot" x="{X(do["x0"]) - 40}" y="{Z((do["z0"] + do["z1"]) / 2)}" text-anchor="end">dosificador</text>')
    s.append(f'<text class="rot" x="{X(xm) - 60}" y="{Z(la["z"]) + 18}" text-anchor="end">línea Ø{la["diam"]}</text>')
    s.append(f'<text class="rot" x="{X(co["x0"]) - 40}" y="{Z(220)}" text-anchor="end">comedero</text>')
    s.append(f'<text class="rot" x="{X(L / 2)}" y="{Z(0) + 160}" text-anchor="middle">piso de slats</text>')
    s.append(_cota_v(X(L) + 340, Z(H), Z(0), mm(H), izq=False))
    s.append(_cota_v(X(L) + 340, Z(la["z"]), Z(H), mm(la["z"] - H), izq=False))
    s.append(f'<text class="ct" x="{X(L) + 370}" y="{Z(la["z"]) - 20}">{mm(la["z"])} al piso</text>')
    s.append(_cota_v(X(0) - 560, Z(bz), Z(0), str(bz)))
    s.append(_cota_h(X(0), X(L), Z(0) + 240, mm(L), arriba=False))
    for z in d["largueros_z"]:
        s.append(f'<text class="ct ch" x="{X(L / 2)}" y="{Z(z) - 24}" text-anchor="middle">{mm(z)}</text>')
    s.append("</svg>")
    return "".join(s)


# ======================================================================
# Página técnica (sin presupuesto)
# ======================================================================
def _html_despiece(desp, T):
    filas, sub_ant = [], None
    for p in desp["piezas"]:
        if p["subconjunto"] != sub_ant:
            filas.append(f'<tr class="grupo"><th colspan="5">{E(p["subconjunto"])}</th></tr>')
            sub_ant = p["subconjunto"]
        medida = f'{p["seccion"]} × {mm(p["largo"])}' if p["largo"] else p["seccion"]
        mat = p["material"]
        filas.append(f'<tr><td class="v">{p["id"]}</td><td>{E(p["pieza"])}</td><td class="v">{p["cant"]}</td>'
                     f'<td class="v">{E(medida)}</td><td>{E(p["operaciones"])}<br><small>{E(mat)}</small></td></tr>')
    corte = []
    for tubo, bs in desp["barras_corte"].items():
        bars = "".join(
            f'<div class="barra"><b>{i}</b><div class="tira">'
            + "".join(f'<span class="seg" style="flex:{c}" title="{c}">{mm(c)}</span>' for c in b["cortes"])
            + f'<span class="sobra" style="flex:{max(b["libre"], 1)}">{mm(b["libre"])}</span></div></div>' for i, b in enumerate(bs, 1))
        corte.append(f'<div class="corte"><h3>{E(nombre_tubo(T[tubo]))} · {len(bs)} barras</h3>{bars}</div>')
    nom = {"tubo": "Tubo estructural", "chapa_y_planchuela": "Chapa y planchuela", "inox": "Acero inoxidable 304",
           "bulones_y_aislacion": "Bulonería y aislación", "otros": "Otros"}
    ped = []
    for k, lst in desp["pedido"].items():
        ped.append(f'<tr class="grupo"><th colspan="3">{nom[k]}</th></tr>')
        for r in lst:
            extra = f' · desperdicio {num(r["desperdicio_pct"], 1)} %' if "desperdicio_pct" in r else ""
            ped.append(f'<tr><td>{E(r["descripcion"])}<br><small>{E(r.get("uso", ""))}{extra}</small></td><td class="v">{r["cant"]}</td><td>{E(r["unidad"])}</td></tr>')
    pe = desp["peso"]
    return (f'<div class="tabla"><table class="desp"><thead><tr><th>Id</th><th>Pieza</th><th>Cant.</th><th>Medida (mm)</th><th>Operaciones</th></tr></thead>'
            f'<tbody>{"".join(filas)}</tbody></table></div>'
            f'<div class="cortes"><h3 class="sub">Plan de corte</h3><p class="hint">Barras de {num(desp["barra_comercial_mm"] / 1000, 0)} m, {desp["corte_mm"]} mm por corte. Gris: sobrante.</p>{"".join(corte)}</div>'
            f'<div class="tabla"><h3 class="sub">Pedido de materiales (sin precios)</h3><table><thead><tr><th>Material</th><th>Cant.</th><th>Unidad</th></tr></thead>'
            f'<tbody>{"".join(ped)}</tbody></table></div>'
            + (f'<p class="hint" style="padding:12px 16px 0">Despiece y pedido para {pe["boxes"]} boxes (≈ {num(pe["por_box_kg"], 0)} kg cada uno).</p>' if pe["boxes"] > 1 else "")
            + f'<p class="hint" style="padding:12px 16px">Peso ≈ {num(pe["total_kg"], 0)} kg (galvanizado ≈ {num(pe["galvanizado_kg"], 0)} kg, '
            f'inox y otros ≈ {num(pe["otros_kg"], 0)} kg); cada lateral ≈ {num(pe["lateral_kg"], 0)} kg. {E(desp["nota"])}</p>')


def _filas_medidas(ficha, D, desp):
    d, req = ficha["diseno"], ficha["requisitos"]
    T, P, F, PL = d["tubos"], d["puerta"], d["frente"], d["pie"]["pletina"]
    nm = lambda t: E(t.split(" (")[0])
    rows = [
        ("Largo del box", mm(D["L"]), "fuente: Gestal 3G 2.235 mm (Ojefer); Big Dutchman ≈ 2.300 mm; mínimo 2.100 mm (The Pig Site)"),
        ("Ancho libre interior", mm(D["AL"]), "criterio: entre los 520 del Gestal 3G (solo comer) y los 600 recomendados si la cerda también descansa adentro"),
        ("Alto de paneles", mm(D["H"]), "fuente: Gestal 3G 1.132 mm"),
        ("Parantes por lado", f"{len(d['parantes_x'])}, cada {mm(d['parantes_x'][1])}", "criterio: con menos parantes el larguero no resiste el empuje"),
        ("Largueros laterales", " · ".join(mm(z) for z in d["largueros_z"]), "criterio: luces ≤ 100 mm, no pasa una pata ni una cabeza"),
        ("Parantes", f"Ø{num(T['parante']['diam'], 1)} × {num(T['parante']['esp'], 1)}", T["parante"]["_origen"]),
        ("Pasamanos y travesaños superiores", f"Ø{num(T['pasamanos']['diam'], 1)} × {num(T['pasamanos']['esp'], 1)}", T["pasamanos"]["_origen"]),
        ("Largueros", f"Ø{num(T['larguero']['diam'], 1)} × {num(T['larguero']['esp'], 1)}", T["larguero"]["_origen"]),
        ("Puerta trasera", f"{P['ancho']} × {P['pivote_z'] - P['borde_inf_z']}", "supuesto: medidas propias; " + P["_origen"]),
        ("Traba", f"2 trinquetes a z {P['trinquete_z']}", "criterio: " + P["traba"]),
        ("Frente", f"{F['barrotes_cant']} barrotes, luz {round((D['AL'] - F['barrotes_cant'] * T['barrote']['diam']) / (F['barrotes_cant'] + 1))}",
         f"supuesto: barrotes Ø{num(T['barrote']['diam'], 1)} × {num(T['barrote']['esp'], 1)} centrados entre los travesaños z "
         + " · ".join(mm(z) for z in F["travesanos_z"][1:]) + f" y {mm(D['H'])}; " + F["zocalo"]),
        ("Pie", f"placa 150 + pletina {PL['largo']} × {PL['ancho']} × {PL['esp']}", d["pie"]["_origen"]),
        ("Anclaje al slat", "4 M12 pasantes + contrapletina", "supuesto: " + d["bulon_anclaje"]),
        ("Comedero", f"{d['comedero']['x1'] - d['comedero']['x0']} × {d['comedero']['ancho']} × {d['comedero']['z1'] - d['comedero']['z0']}",
         "supuesto: medidas propias; " + d["comedero"]["_origen"] + ". " + d["comedero"]["soportes"]),
        ("Caída de alimento", d["caida"]["cano"], d["caida"]["_origen"]),
        ("Dosificador", f"{d['dosificador']['x1'] - d['dosificador']['x0']} × {d['dosificador']['ancho']} × {d['dosificador']['z1'] - d['dosificador']['z0']}",
         "supuesto: " + d["dosificador"]["_origen"]),
        ("Línea de alimento", f"Ø{req['linea_alimento']['diam']} a {mm(req['linea_alimento']['z'])}", req["linea_alimento"]["_origen"]),
        ("Antena RFID", d["rfid"]["separador"], d["rfid"]["_origen"]),
        ("Peso", f"≈ {num(desp['peso']['total_kg'], 0)} kg", "cálculo: suma del despiece, con 5 % de zinc en lo galvanizado"),
    ]
    out = []
    for el, val, origen in rows:
        t = _tag(origen)
        cls = "f" if t == "fuente" else "s"
        resp = origen.split(":", 1)[1].strip() if origen.lower().startswith(t) and ":" in origen[:12] else origen
        out.append(f'<tr><td>{E(el)}</td><td class="v">{E(val)}</td><td><span class="tag {cls}">{t}</span></td><td>{E(resp)}</td></tr>')
    return "".join(out)


def _estado(e):
    return f'<span class="st {"ok" if e == "cumple" else "bad" if e == "no cumple" else "warn"}">{E(e)}</span>'


def pagina(ficha, M, val, desp, auditoria=None):
    pr, cl, req, d = ficha["proyecto"], ficha["cliente"], ficha["requisitos"], ficha["diseno"]
    D, tip = M["d"], catalogo_tipologia(ficha["tipologia"])
    tpl = open(os.path.join(RAIZ, "skills", "propuesta-web", "assets", "plantilla-jaula.html"), encoding="utf-8").read()
    fecha = datetime.date.fromisoformat(pr["fecha"])
    vence = fecha + datetime.timedelta(days=pr["validez_dias"])
    f_ = lambda x: x.strftime("%d/%m/%Y")
    falta = '<span class="tbd">a completar</span>'
    v_ = lambda x: E(x) if x else falta
    ok = sum(c["estado"] == "cumple" for c in val["checks"])
    cifras = "".join(f"<span>{a} <em>{b}</em></span>" for a, b in (
        (mm(D["L"]), "largo"), (mm(D["AL"]), "ancho libre"), (mm(D["EXT"]), "ancho ext."), (mm(D["H"]), "alto"),
        (mm(req["linea_alimento"]["z"]), "a la línea"), ("1", "cerda por box sin RFID"), ("15–18", "con RFID")))
    vu = (auditoria or {}).get("vueltas", (auditoria or {}).get("vuelta", "?"))
    aud_estado = (f"auditoría vuelta {vu}: {auditoria.get('estado')}" + (" (desactualizada)" if auditoria.get("_aviso") else "")) if auditoria else "auditoría pendiente"
    der = "".join(f"<span>{a} <b>{E(b)}</b></span>" for a, b in (
        ("Medidas", "mm"), ("Material", "hierro galvanizado + inox"), ("Puerta", "mecánica, sin aire"),
        ("Verificaciones", f"{ok}/{len(val['checks'])}"), ("Estado", aud_estado)))
    datos = ('<dl class="datos">' + "".join(f"<dt>{a}</dt><dd>{b}</dd>" for a, b in (
        ("Propuesta", E(pr["numero"])), ("Fecha", f_(fecha)), ("Validez", f"{pr['validez_dias']} días (hasta el {f_(vence)})"),
        ("Cliente", v_(cl.get("nombre"))), ("Contacto", v_(cl.get("contacto"))),
        ("Obra", f"{v_(cl.get('direccion_obra'))} — {E(cl['localidad'])}, {E(cl['provincia'])}"),
        ("Cantidad", f"{req.get('cantidad_boxes', 1)} box"), ("Uso", E(req["uso"])))) + "</dl>")
    verif = "".join(f'<tr><td>{E(c["requisito"])}<br><small>{E(c.get("nota", ""))}</small></td><td class="v">{E(c["valor"])}</td>'
                    f'<td class="v">{E(c["limite"])}</td><td>{_estado(c["estado"])}</td></tr>' for c in val["checks"])
    princ = ""
    for p in tip["principios"]:
        cita = (f'<blockquote>“{E(p["cita"]["texto"])}”<cite>{E(p["cita"]["fuente"])}</cite></blockquote>' if p.get("cita") else "")
        princ += f'<article><h3>{E(p["titulo"])}</h3><ul>{"".join(f"<li>{E(i)}</li>" for i in p["items"])}</ul>{cita}</article>'
    etapas = "".join(f'<li><h3>{E(e["titulo"])}</h3><p>{E(e["texto"])}</p></li>' for e in tip["etapas"])
    pend = [f"Pruebas de prototipo con cerdas: {', '.join(d['puerta'].get('pruebas_prototipo', []))}.",
            "Espesores de caño, luz entre barrotes, métrica de bulones y resortes no están en las fuentes: son propuesta del anteproyecto, verificada con cálculo simplificado.",
            "Validar con un ingeniero matriculado y con un productor antes de fabricar en serie.",
            "Confirmar con el proveedor el largo de barra (6 o 6,40 m) y con el galpón el espesor real del slat (largo del bulón de anclaje)."]
    if ficha.get("estado", {}).get("nota_auditoria"):
        pend.insert(0, ficha["estado"]["nota_auditoria"])
    if auditoria:
        pend.insert(0, f"Auditoría independiente: vuelta {vu}, estado «{auditoria.get('estado')}». El detalle está en el anexo." + (" " + auditoria["_aviso"] if auditoria.get("_aviso") else ""))
    cond = "".join(f"<p>{x}</p>" for x in (
        "Propuesta técnica: diseño, verificaciones, despiece y pedido de materiales <b>sin precios</b>. Esta tipología no lleva presupuesto.",
        E(ficha["comercial"]["mod"]["texto"]),
        f"Plazo de entrega: {v_(ficha['comercial'].get('plazo_entrega'))}. Garantía: {v_(ficha['comercial'].get('garantia'))}.",
        "Mantenimiento: revisar a diario trabas, resortes y picos; limpiar mensualmente la antena; lavar con hidrolavadora; reponer topes de goma.",
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
        "{{TITULO_CORTO}}": "Box de Alimentación Cerdas", "{{EYEBROW}}": f"Propuesta técnica {E(pr['numero'])} · {f_(fecha)}",
        "{{TITULO}}": E(pr["titulo"]),
        "{{BAJADA}}": "Jaula tubular tipo Gestal 3G para fabricar en un taller de herrería argentino y automatizar por etapas.",
        "{{CIFRAS}}": cifras, "{{ROTULO_DER}}": der, "{{MARCA}}": E(pr["marca"]), "{{DATOS}}": datos,
        "{{PLANTA}}": planta(ficha, M), "{{LATERAL}}": lateral(ficha, M), "{{FILAS_MEDIDAS}}": _filas_medidas(ficha, D, desp),
        "{{RESUMEN_VALIDACION}}": f"{ok} de {len(val['checks'])} cumplen", "{{VERIFICACIONES}}": verif,
        "{{DESPIECE}}": _html_despiece(desp, d["tubos"]), "{{PRINCIPIOS}}": princ, "{{ETAPAS}}": etapas,
        "{{PENDIENTES}}": "".join(f"<li>{E(x)}</li>" for x in pend), "{{CONDICIONES}}": cond, "{{AUDITORIA}}": aud,
        "{{FUENTES}}": E(tip["fuentes"]) + " Generado con el plugin «estructuras-a-medida».", "{{ESCENA}}": json.dumps(M["escena"]),
    }
    for k, v in rep.items():
        tpl = tpl.replace(k, v)
    return tpl


# ======================================================================
# Salidas de la corrida completa (las usa correr.py)
# ======================================================================
def salidas(ficha, M, val, desp, precios=None, auditoria=None):
    """Devuelve {archivo: contenido} para salida/ y las páginas (con y sin anexo de auditoría)."""
    archivos = {"planta.svg": planta(ficha, M), "lateral.svg": lateral(ficha, M), "escena3d.json": M["escena"],
                "despiece.json": desp, "pedido.json": desp["pedido"]}
    return {"archivos": archivos, "pagina": pagina(ficha, M, val, desp, auditoria), "pagina_auditor": pagina(ficha, M, val, desp, None),
            "presupuesto": None}
