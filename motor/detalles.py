"""Detalles constructivos del pórtico: 6 láminas 2D con agujeros (trazos), rebajes y varillas
con arandela + tuerca + contratuerca. Todo sale de ficha.json + modelo."""
import math
from _fig import Fig, WOOD, WOODHI, WOODEDGE, CAP, STEEL, STEELD
from comun import m, cm, num, ag


def laminas(ficha, M):
    d, D, r = ficha["diseno"], M["d"], M["raw"]
    tr, pa, ti, ca, va, cu, ap = d["travesano"], d["patas"], d["tirante"], d["cartela"], d["varillas"], d["cuelgues"], d["apoyo"]
    beamZ, beamR, legR, foot = r["beamZ"], r["beamR"], r["legR"], r["foot"]
    cz, lean, A = D["apex"], D["lean"], D["ang_lateral"]
    hol = va["holgura_agujero"]
    dh, dc, dt, dca, dab = va["horqueta"]["d"], va["cruce"]["d"], va["tirante"]["d"], va["cartela_inf"]["d"], va["abrazadera"]["d"]
    wash = d["arandela_ancha_mm"]
    out = []

    # ===== 1. Horqueta: vista lateral =====
    z0 = cz - 280
    f = Fig(-560, 560, z0, max(beamZ + 230, D["z_punta"] + 60))
    ext = D["prolongacion"]
    for s in (-1, 1):
        a = (s * foot * (1 - z0 / cz), z0)
        u = (-s * foot, cz); L = math.hypot(*u); u = (u[0] / L, u[1] / L)
        if pa.get("punta") == "horizontal":
            # recortar cada cara en el plano horizontal de la punta
            nrm = (-u[1], u[0])
            zt = D["z_punta"]
            caras = []
            for k in (1, -1):
                p0 = (a[0] + nrm[0] * legR * k, a[1] + nrm[1] * legR * k)
                t = (zt - p0[1]) / u[1]
                caras.append((p0, (p0[0] + u[0] * t, zt)))
            (pa0, pa1), (pb0, pb1) = caras
            f.poly([pa0, pa1, pb1, pb0], WOOD, "none", 0)
            f.line(pa0, pa1); f.line(pb0, pb1)
            f.line(pa1, pb1, WOODEDGE, 2)
        else:
            b = (u[0] * ext, cz + u[1] * ext)
            q = f.log_side(a, b, pa["diametro"])
            f.poly([q[1], q[2], (q[2][0] - u[0] * 4, q[2][1] - u[1] * 4), (q[1][0] - u[0] * 4, q[1][1] - u[1] * 4)], CAP, WOODEDGE, 1.2)
    f.section((0, beamZ), beamR)
    yTop = D["yTop"]
    Lh = va["horqueta"]["largo"]
    f.hole((-(yTop + legR), beamZ), (yTop + legR, beamZ), ag(dh))
    f.rod((-Lh / 2 + 30, beamZ), (Lh / 2 - 30, beamZ), dh, wash=wash)
    f.circle((0, cz), 25, "#c4cbd1", STEELD, 0.9)
    f.circle((0, cz), dc / 2, STEEL, STEELD, 0.9)
    f.dim((-Lh / 2 + 30, beamZ), (Lh / 2 - 30, beamZ), 150, f"varilla {dh} mm × {m(Lh)}", 12)
    f.tag((0, beamZ + 60), 150, -20, f"Travesaño Ø{cm(tr['diametro'])}|apoya en la V (asiento|rebajado {cm(pa['asiento_horqueta'], 1)} en cada pata)")
    f.tag((-yTop + 40, beamZ - 20), -150, 70, f"Agujero Ø{ag(dh)} pasante:|pata – travesaño – pata", "end")
    f.tag((0, cz), 150, 30, f"Cruce a media madera|varilla {dc} mm a lo largo|del travesaño (ver vista B)")
    f.dim((0, beamZ), (0, cz), -330, cm(beamZ - cz), 12)
    if pa.get("punta") == "horizontal":
        f.tag((foot * 0 + (D["z_punta"] - cz) * math.tan(math.radians(A)), D["z_punta"]), 60, -25, f"Punta cortada horizontal|a {m(D['z_punta'])} (varilla a {cm(D['dist_punta'], 1)} del extremo)")
    f.text((0, z0 + 20), f"{A:.0f}° en esta vista ({num(D['ang_real'], 1)}° real)", "vw2")
    f.title_txt = "A · VISTA LATERAL"
    out.append(("Horqueta y apoyo del travesaño",
                f"El travesaño apoya en la V que forman las patas arriba del cruce. En cada pata se rebaja un asiento de {cm(pa['asiento_horqueta'], 1)} donde toca el travesaño. Una varilla de {dh} mm atraviesa pata, travesaño y pata a la altura del eje.",
                f.svg("Detalle de la horqueta")))

    # ===== 1B. Cruce a media madera: vista frontal =====
    lap = r["lap"]
    zb0, zb1 = cz - 262, cz + 278
    f = Fig(-330, 330, zb0, zb1, W=640)
    for s in (-1, 1):
        f.log_side((s * lap, zb0), (s * lap - lean * (zb1 - zb0), zb1), pa["diametro"])
    cx = -lean * (cz - zb0)
    reb = pa["diametro"] * pa["rebaje_cruce_frac"]
    f.poly([(cx - reb, cz - 90), (cx + reb, cz - 90), (cx + reb, cz + 90), (cx - reb, cz + 90)], "#b77a48", WOODEDGE, 1, 'stroke-dasharray="4 3"')
    grip = 2 * pa["diametro"] - 2 * reb
    Lc = va["cruce"]["largo"]
    f.hole((cx - grip / 2 - 10, cz), (cx + grip / 2 + 10, cz), ag(dc))
    f.rod((cx - Lc / 2, cz), (cx + Lc / 2, cz), dc, wash=wash)
    f.dim((cx - grip / 2, cz - 120), (cx + grip / 2, cz - 120), -40, f"{cm(grip)} (2 × Ø{cm(pa['diametro'])} − 2 rebajes)", 11)
    f.tag((cx, cz + 60), 120, -60, f"Rebaje de 1/3 del diámetro|(≈ {cm(reb, 1)}) en cada pata;|quedan encastradas")
    f.tag((cx + Lc / 2 - 25, cz), 40, 90, f"Varilla {dc} mm, arandela {wash} mm,|tuerca y contratuerca")
    f.text((cx - 20, zb0 + 30), f"{D['ang_frontal']:.0f}° vista frontal", "vw2")
    f.title_txt = "B · VISTA FRONTAL DEL CRUCE"
    out.append(("Cruce de patas a media madera",
                f"Las dos patas de cada A se cruzan a {m(cz)}. Cada una lleva un rebaje de 1/3 del diámetro para encastrar, y una varilla de {dc} mm las une a lo largo del travesaño.",
                f.svg("Detalle del cruce de patas")))

    # ===== 2. Tirante – pata: corte horizontal =====
    tieZ, tieR = r["tieZ"], r["tieR"]
    ax = M["axisX"](tieZ)
    yT = D["yT"]
    flat = ax - legR + ti["rebaje"]
    tx = flat - tieR + ti["rebaje"]
    f = Fig(tx - tieR - 160, ax + legR + 100, yT - 310, yT + 330)
    y0, y1 = yT - 290, yT + 310
    f.poly([(tx - tieR, y0), (flat, y0), (flat, y1), (tx - tieR, y1)], WOOD, WOODEDGE, 1.3)
    f.poly([(tx - tieR + 20, y0), (tx - 20, y0), (tx - 20, y1), (tx - tieR + 20, y1)], WOODHI, "none", 0)
    pts = []
    for i in range(73):
        t = 2 * math.pi * i / 72
        x, y = ax + legR * math.cos(t), yT + legR * math.sin(t)
        pts.append((max(x, flat), y))
    f.poly(pts, CAP, WOODEDGE, 1.3)
    f.circle((ax + 10, yT), legR * 0.55, "none", "#b98c62", 0.7)
    Lt = va["tirante"]["largo"]
    xa = ax + legR + 25
    f.hole((tx - tieR - 5, yT), (ax + legR + 5, yT), ag(dt))
    f.rod((xa - Lt, yT), (xa + 30, yT), dt, wash=wash)
    f.dim((tx - tieR, y0), (flat, y0), -30, f"Ø{cm(ti['diametro'])} − {cm(ti['rebaje'], 1)}", 11)
    f.tag((flat, yT + 120), 70, -40, f"Rebaje plano {cm(ti['rebaje'], 1)}|en tirante y en pata")
    f.tag((ax, yT - 40), 40, 70, f"Pata Ø{cm(pa['diametro'])} (corte)")
    f.tag((tx - tieR - 40, yT), -10, -80, f"Varilla {dt} mm|agujero Ø{ag(dt)}", "end")
    f.text((tx - 40, y1 - 40), "TIRANTE", "vw2")
    f.title_txt = f"CORTE HORIZONTAL A {m(tieZ)}"
    f.text((ax + legR + 95, y0 + 10), "← interior del pórtico", "vw2", "end")
    out.append(("Tirante contra la pata",
                f"El tirante va por la cara {ti['cara']} de las patas, a {m(tieZ)}. Se rebaja {cm(ti['rebaje'], 1)} en tirante y pata para que apoyen plano, y se unen con varilla de {dt} mm.",
                f.svg("Detalle del tirante y la pata")))

    # ===== 3. Cartela: vista frontal =====
    bx = r["braceTopX"]
    txc = D["tx"]
    f = Fig(bx - 200, txc + 215, tieZ - 120, beamZ + 160)
    xl, xr = bx - 200, txc + 215
    f.poly([(xl, beamZ - beamR + 20), (xr, beamZ - beamR + 20), (xr, beamZ + beamR), (xl, beamZ + beamR)], WOOD, WOODEDGE, 1.3)
    f.poly([(xl, beamZ + 20), (xr, beamZ + 20), (xr, beamZ + 70), (xl, beamZ + 70)], WOODHI, "none", 0)
    f.line((xl, beamZ - beamR), (xr, beamZ - beamR), "#7a4a26", 0.8, 'stroke-dasharray="4 3"')
    zt = tieZ + tieR - ca["rebaje"]
    pts = []
    for i in range(73):
        t = 2 * math.pi * i / 72
        pts.append((txc + tieR * math.cos(t), min(tieZ + tieR * math.sin(t), zt)))
    f.poly(pts, CAP, WOODEDGE, 1.3)
    a, b = (txc, zt), (bx, beamZ - beamR + ca["rebaje"])
    ux, uy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(ux, uy)
    w = r["braceR"] / (abs(uy) / L)
    f.poly([(a[0] - w, a[1]), (a[0] + w, a[1]), (b[0] + w, b[1]), (b[0] - w, b[1])], WOOD, WOODEDGE, 1.3)
    f.poly([(a[0] - w * 0.65, a[1]), (a[0] - w * 0.15, a[1]), (b[0] - w * 0.15, b[1]), (b[0] - w * 0.65, b[1])], WOODHI, "none", 0)
    Li, Ls = va["cartela_inf"]["largo"], va["cartela_sup"]["largo"]
    f.hole((txc, tieZ - tieR), (txc, zt + 165), ag(dca))
    f.rod((txc, tieZ - tieR - 25), (txc, tieZ - tieR - 25 + Li), dca, wash=wash)
    f.hole((bx, beamZ + beamR), (bx, b[1] - 165), ag(dca))
    f.rod((bx, beamZ + beamR + 30), (bx, beamZ + beamR + 30 - Ls), dca, wash=wash)
    f.tag((bx + 20, b[1] - 10), 120, 30, f"Rebaje plano {cm(ca['rebaje'])}|bajo el travesaño")
    f.tag((txc + 20, zt + 5), 80, -10, f"Rebaje plano {cm(ca['rebaje'])}|sobre el tirante")
    f.tag((bx, b[1] - 140), -40, -80, f"Varilla {dca} mm vertical;|sale por el costado de la|cartela: asiento plano", "end")
    f.tag((txc, zt + 105), -80, 40, f"Varilla {dca} mm atraviesa|tirante y pie de cartela", "end")
    f.dim(a, b, -110, f"≈ {m(L)}", 12)
    f.title_txt = "VISTA FRONTAL"
    out.append(("Cartela entre tirante y travesaño",
                f"La cartela apoya arriba del tirante y abajo del travesaño (a {m(bx)} del centro), con las puntas cortadas horizontales y rebajes planos de {cm(ca['rebaje'])}. En cada punta, una varilla vertical de {dca} mm; donde sale por el costado de la cartela se talla un asiento plano para la arandela.",
                f.svg("Detalle de la cartela")))

    # ===== 4. Abrazadera de cuelgue =====
    ab = cu["abrazadera"]
    f = Fig(-260, 260, beamZ - 340, beamZ + 190)
    f.section((0, beamZ), beamR)
    f.circle((0, beamZ), beamR + ab["goma_mm"], "none", "#2b2b2b", ab["goma_mm"] * f.k)
    ring_r = ab["radio_interior"] + ab["goma_mm"] + 2
    f.circle((0, beamZ), ring_r, "none", "#7d868e", 5 * f.k)
    for s in (-1, 1):
        f.poly([(s * 6, beamZ - ring_r - 2), (s * 11, beamZ - ring_r - 2), (s * 11, beamZ - ring_r - ab["oreja"]), (s * 6, beamZ - ring_r - ab["oreja"])], "#7d868e", STEELD, 0.9)
    osup = ab.get("oreja_sup", 0)
    if osup:  # junta de arriba: orejas y una varilla
        for s in (-1, 1):
            f.poly([(s * 6, beamZ + ring_r + 2), (s * 11, beamZ + ring_r + 2), (s * 11, beamZ + ring_r + osup), (s * 6, beamZ + ring_r + osup)], "#7d868e", STEELD, 0.9)
        zz = beamZ + ring_r + osup / 2
        f.line((-30, zz), (30, zz), STEELD, 4)
        f.poly([(14, zz - 7), (24, zz - 7), (24, zz + 7), (14, zz + 7)], "#5b636a", STEELD, 0.8)
        f.poly([(-24, zz - 7), (-14, zz - 7), (-14, zz + 7), (-24, zz + 7)], "#5b636a", STEELD, 0.8)
    for zz in ((beamZ - ring_r - 35,) if osup else (beamZ - ring_r - 25, beamZ - ring_r - 55)):
        f.line((-30, zz), (30, zz), STEELD, 4)
        f.poly([(14, zz - 7), (24, zz - 7), (24, zz + 7), (14, zz + 7)], "#5b636a", STEELD, 0.8)
        f.poly([(-24, zz - 7), (-14, zz - 7), (-14, zz + 7), (-24, zz + 7)], "#5b636a", STEELD, 0.8)
    gz = beamZ - ring_r - 80
    pts = [(18 * math.cos(t), gz - 30 - 30 * math.sin(t)) for t in [math.pi * i / 20 for i in range(21)]]
    f.g.append(f'<polyline points="{f.pts([(-18, gz)] + pts[::-1] + [(18, gz)])}" fill="none" stroke="#454c53" stroke-width="{10*f.k:.1f}" stroke-linecap="round"/>')
    f.line((0, gz - 60), (0, beamZ - 330), "#9c958a", 6 * f.k)
    f.tag((70, beamZ + 75), 70, -30, f"Planchuela {ab['planchuela'].replace('x', ' × ')} mm galvanizada|(o hierro negro + galvanizado|en frío), en dos medias cañas")
    f.tag((-100, beamZ - 20), -50, -90, f"Banda de goma {ab['goma_mm']} mm|(no marca ni resbala)", "end")
    f.tag((24, beamZ - ring_r - 35), 80, -5, (f"Cierre: 1 varilla {dab} mm arriba|y 1 abajo, con tuerca y contratuerca" if osup else f"Cierre: {va['abrazadera']['cant_por_abrazadera']} varillas {dab} mm|con tuerca y contratuerca"))
    f.tag((18, gz - 20), 80, 30, f"{ab['accesorio'][0].upper() + ab['accesorio'][1:]}|para la soga")
    f.text((0, beamZ - 325), "soga / cadena", "vw2")
    f.title_txt = "CORTE TRANSVERSAL"
    n = len(D["hang"])
    out.append((f"Abrazadera de cuelgue (×{n})",
                f"{n} abrazaderas de planchuela en dos medias cañas, con goma, sin perforar el travesaño. Cada media caña tiene oreja arriba y abajo; las juntas se cierran con una varilla de {dab} mm cada una, y abajo llevan un grillete o gancho giratorio. Al sacar los accesorios, la abrazadera queda o se afloja y se corre.",
                f.svg("Detalle de la abrazadera de cuelgue")))

    # ===== 5. Apoyo (vista lateral: sentido del vaivén) =====
    px, py, pz = ap["pozo"]
    ent = pa["enterrado"]
    ang = math.radians(A)
    u = (math.sin(ang), math.cos(ang))
    cxp = ent * math.tan(ang) / 2  # el pozo se centra en el tramo enterrado
    f = Fig(-520, 620, -pz - 120, 460)
    f.poly([(-520, -pz - 120), (620, -pz - 120), (620, 0), (-520, 0)], "var(--soil)", "none", 0)
    f.line((-520, 0), (620, 0), "#7a6a55", 1.5)
    x0, x1 = cxp - py / 2, cxp + py / 2
    f.poly([(x0, -pz), (x1, -pz), (x1, 0), (x0, 0)], "var(--gravel)", "#7a6a55", 1)
    for i in range(90):
        x = x0 + 10 + (i * 37) % (py - 20); y = -pz + 10 + (i * 53) % (pz - 20)
        f.circle((x, y), 7, "#b3a58f", "#8d7f69", 0.5)
    # ladrillos acostados bajo el pie (en esta vista se ve su largo, 25 cm)
    f.poly([(-125, -ent - 55), (125, -ent - 55), (125, -ent), (-125, -ent)], "#b0574a", "#6e3027", 1)
    base = (0, -ent)
    top = (base[0] + u[0] * (ent / u[1] + 520), base[1] + u[1] * (ent / u[1] + 520))
    rr = legR
    nx, ny = -u[1], u[0]
    p1 = (base[0] - rr / u[1], base[1]); p2 = (base[0] + rr / u[1], base[1])
    q1 = (top[0] + nx * rr, top[1] + ny * rr); q2 = (top[0] - nx * rr, top[1] - ny * rr)
    f.poly([p1, p2, q2, q1], WOOD, WOODEDGE, 1.3)
    f.line(p1, p2, WOODEDGE, 2)
    pl = ap["proteccion_largo"]
    f.poly([p1, p2, (p2[0] + u[0] * pl, p2[1] + u[1] * pl), (p1[0] + u[0] * pl, p1[1] + u[1] * pl)], "#3b2a1c", "none", 0, 'opacity=".35"')
    f.dim((x0, -pz), (x1, -pz), -40, cm(py), 12)
    f.dim((x1, -pz), (x1, 0), -50, cm(pz), 12)
    f.dim((-160, -ent), (-160, 0), 60, f"{cm(ent)} enterrado", 11)
    f.tag((p2[0] + 10, -ent + 10), 170, 40, "Pie cortado horizontal|(apoya plano)")
    f.tag((-60, -ent - 30), -110, 50, ap["base"][0].upper() + ap["base"][1:], "end")
    f.tag((x1 - 40, -pz + 30), 110, 10, ap["relleno"][0].upper() + ap["relleno"][1:] + "|también debajo de los ladrillos")
    f.tag((p1[0] + u[0] * 300, p1[1] + u[1] * 300), -150, -60, f"Últimos {cm(pl)} con|{ap['proteccion']}", "end")
    f.title_txt = "APOYO DE CADA PATA · VISTA LATERAL"
    out.append(("Apoyo de cada pata",
                f"Cada pata apoya sola en un pozo de {cm(px)} (a lo largo del travesaño) × {cm(py)} (sentido del vaivén) × {cm(pz)} de profundidad, centrado en el tramo enterrado: algo corrido hacia afuera del pie. Abajo, {ap['relleno']}; encima, {ap['base']} a {cm(ent)} de profundidad. El pie se corta horizontal para que apoye plano. Los últimos {cm(pl)} llevan {ap['proteccion']}.",
                f.svg("Detalle del apoyo de la pata")))
    return out
