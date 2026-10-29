"""Perspectiva cónica acotada del pórtico (SVG), generada desde el modelo de ficha.json.
Refactor de insumos/portico-v3/perspectiva/plano.py: misma cámara, pintado por profundidad y cotas 3D."""
import html
import math
from comun import add, sub, mul, dot, cross, norm, unit, m, num, cm

COL = {
    "madera": ("#c98a55", "#e0a874", "#7a4a26", "#e8c9a2"),
    "acero": ("#8d969e", "#c4cbd1", "#3e464d", "#b7bfc6"),
    "banda": ("#8d969e", "#c4cbd1", "#3e464d", "#b7bfc6"),
    "oscuro": ("#454c53", "#6b737a", "#1e2226", "#5b636a"),
}
BIAS = {"madera": 0, "acero": -30, "banda": -60, "oscuro": -40}


def svg(ficha, M, config_id=None):
    d, D, r = ficha["diseno"], M["d"], M["raw"]
    req = ficha["requisitos"]
    config_id = config_id or req["configuraciones"][0]["id"]
    beamR, beamZ, beamHalf, legR = r["beamR"], r["beamZ"], r["beamHalf"], r["legR"]
    crossX, foot, apex, lap = r["crossX"], r["foot"], D["apex"], r["lap"]
    tieZ, tieR, braceTopX = r["tieZ"], r["tieR"], r["braceTopX"]
    axisX = M["axisX"]
    HANG, SLOTS = D["hang"], D["slots"]
    ac = d["accesorios"]
    legs = {tuple(int(v) for v in k.split(",")): val for k, val in M["legs"].items()}

    EYE = [-7600, -12800, 4600]
    TGT = [250, 150, 1000]
    FOV = 23
    W, H = 1400, 1050
    fwd = unit(sub(TGT, EYE))
    right = unit(cross(fwd, [0, 0, 1]))
    up = cross(right, fwd)
    fpx = (W / 2) / math.tan(math.radians(FOV / 2))
    CX, CY = W * 0.5, H * 0.47

    def P(p):
        dd = sub(p, EYE)
        zc = dot(dd, fwd)
        return (CX + fpx * dot(dd, right) / zc, CY - fpx * dot(dd, up) / zc)

    def depth(p):
        return norm(sub(p, EYE))

    LIGHT = unit([-0.5, -0.6, 0.8])
    items = []

    def fmt(pts):
        return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)

    def cylinder(a, b, rr, kind, bias=0, caps=True):
        ax = sub(b, a)
        L = norm(ax)
        u = unit(ax)
        n_chunks = max(1, int(L / 220))
        base, hi, edge, cap = COL[kind]
        for k in range(n_chunks):
            p0 = add(a, mul(ax, k / n_chunks))
            p1 = add(a, mul(ax, (k + 1) / n_chunks))
            n0, n1 = unit(cross(u, sub(p0, EYE))), unit(cross(u, sub(p1, EYE)))
            sgn = 1 if dot(n0, LIGHT) > 0 else -1
            q = [P(add(p0, mul(n0, rr))), P(add(p1, mul(n1, rr))), P(add(p1, mul(n1, -rr))), P(add(p0, mul(n0, -rr)))]
            h = [P(add(p0, mul(n0, sgn * rr * 0.15))), P(add(p1, mul(n1, sgn * rr * 0.15))), P(add(p1, mul(n1, sgn * rr * 0.7))), P(add(p0, mul(n0, sgn * rr * 0.7)))]
            sw = 1.1 if kind == "madera" else 0.8
            s = (f'<polygon points="{fmt(q)}" fill="{base}" stroke="{base}" stroke-width="0.6"/>'
                 f'<polygon points="{fmt(h)}" fill="{hi}"/>'
                 f'<line x1="{q[0][0]:.1f}" y1="{q[0][1]:.1f}" x2="{q[1][0]:.1f}" y2="{q[1][1]:.1f}" stroke="{edge}" stroke-width="{sw}"/>'
                 f'<line x1="{q[3][0]:.1f}" y1="{q[3][1]:.1f}" x2="{q[2][0]:.1f}" y2="{q[2][1]:.1f}" stroke="{edge}" stroke-width="{sw}"/>')
            items.append((depth(mul(add(p0, p1), 0.5)) + bias, s))
        ref = [0, 0, 1] if abs(u[2]) < 0.9 else [1, 0, 0]
        e1 = unit(cross(u, ref)); e2 = cross(u, e1)
        for p, dirn in ((a, mul(u, -1)), (b, u)):
            if not caps or dot(dirn, sub(EYE, p)) <= 0:
                continue
            ring = [P(add(p, add(mul(e1, rr * math.cos(t)), mul(e2, rr * math.sin(t))))) for t in [i * 2 * math.pi / 28 for i in range(28)]]
            sw = 1.1 if kind == "madera" else 0.8
            s = f'<polygon points="{fmt(ring)}" fill="{cap}" stroke="{edge}" stroke-width="{sw}"/>'
            if kind == "madera":
                ring2 = [P(add(p, add(mul(e1, rr * 0.55 * math.cos(t)), mul(e2, rr * 0.55 * math.sin(t))))) for t in [i * 2 * math.pi / 20 for i in range(20)]]
                s += f'<polygon points="{fmt(ring2)}" fill="none" stroke="#b98c62" stroke-width="0.6"/>'
            items.append((depth(p) - 1 + bias, s))

    def box(xr, yr, zr, cols=("#8a5a34", "#6e4527", "#5c3a20")):
        x0, x1 = xr; y0, y1 = yr; z0, z1 = zr
        faces = [
            ([[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], [0, 0, 1], cols[0]),
            ([[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1]], [0, -1, 0], cols[1]),
            ([[x0, y0, z0], [x0, y1, z0], [x0, y1, z1], [x0, y0, z1]], [-1, 0, 0], cols[2]),
            ([[x1, y0, z0], [x1, y1, z0], [x1, y1, z1], [x1, y0, z1]], [1, 0, 0], cols[2]),
            ([[x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]], [0, 1, 0], cols[1]),
        ]
        for pts, n, col in faces:
            c = mul([sum(p[i] for p in pts) for i in range(3)], 0.25)
            if dot(n, sub(EYE, c)) <= 0:
                continue
            items.append((depth(c), f'<polygon points="{fmt([P(p) for p in pts])}" fill="{col}" stroke="#3a2412" stroke-width="0.8"/>'))

    for p in M["piezas"]:
        kind = p["mat"]
        cylinder(p["a"], p["b"], p["r"], kind, BIAS[kind], caps=(kind != "banda"))
    for c in M["configs"][config_id]:
        if c["tipo"] == "caja":
            cols = ("#d9cbb4", "#b9a88c", "#a39275") if c["nombre"] == "cama" else ("#8a5a34", "#6e4527", "#5c3a20")
            box(c["x"], c["y"], c["z"], cols)
        elif c["tipo"] == "barra":
            cylinder(c["a"], c["b"], c["r"], "acero", 0)
        elif c["tipo"] == "soga":
            pa, pb = P(c["a"]), P(c["b"])
            items.append((depth(mul(add(c["a"], c["b"]), 0.5)), f'<line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" stroke="#9c958a" stroke-width="1.6"/>'))
    items.sort(key=lambda t: -t[0])

    # ---- suelo, muro y área libre ----
    esp = req["espacio"]
    AX = esp["largo_eje_travesano_m"] * 500
    AY = esp["largo_vaiven_m"] * 500
    AX0, AX1 = -AX, AX
    ground = []
    area = [P([AX0, -AY, 0]), P([AX1, -AY, 0]), P([AX1, AY, 0]), P([AX0, AY, 0])]
    ground.append(f'<polygon points="{fmt(area)}" fill="var(--ground)" stroke="var(--dim)" stroke-width="1" stroke-dasharray="7 5"/>')
    m0, m1 = P([AX0, -AY, 0]), P([AX0, AY, 0])
    ground.append(f'<line x1="{m0[0]:.1f}" y1="{m0[1]:.1f}" x2="{m1[0]:.1f}" y2="{m1[1]:.1f}" stroke="var(--wallEdge)" stroke-width="5"/>')
    nh = int(2 * AY / 250) + 1
    for k in range(nh):
        yy = -AY + k * 250
        a, b = P([AX0, yy, 0]), P([AX0 - 180, yy - 120, 0])
        ground.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="var(--wallEdge)" stroke-width="1"/>')
    mt = P([AX0 - 300, -1200, 0])
    ground.append(f'<text x="{mt[0]:.1f}" y="{mt[1]:.1f}" class="lbl soft" text-anchor="end">MURO</text>')
    czp = P([AX1 + 150, -AY + 200, 0])
    ground.append(f'<text x="{czp[0]:.1f}" y="{czp[1]:.1f}" class="lbl soft" text-anchor="start">CÉSPED →</text>')
    al = P([0, -AY, 0])
    ground.append(f'<text x="{al[0]:.1f}" y="{al[1]+22:.1f}" class="lbl soft" text-anchor="middle">ÁREA LIBRE {num(esp["largo_eje_travesano_m"])} × {num(esp["largo_vaiven_m"])} m</text>')
    px_, py_ = d["apoyo"]["pozo"][0] / 2, d["apoyo"]["pozo"][1] / 2
    for (sx, s_), (f, e) in legs.items():
        c = [f[0] + sx * D["pozo_dx"], f[1] + s_ * D["pozo_dy"], 0]
        rect = [P([c[0] + a * px_, c[1] + b * py_, 0]) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        ground.append(f'<polygon points="{fmt(rect)}" fill="var(--hole)" stroke="none"/>')

    # ---- cotas ----
    dims = []

    def dimline(a, b, off, text, side=1, ext_from=None, size=15, gap=None):
        a2, b2 = add(a, off), add(b, off)
        A, B = P(a2), P(b2)
        ea, eb = (ext_from or (a, b))
        o = unit(off) if norm(off) > 0 else [0, 0, 0]
        for p, q in ((ea, a2), (eb, b2)):
            p1, q1 = P(add(p, mul(o, 40))), P(add(q, mul(o, 60)))
            dims.append(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{q1[0]:.1f}" y2="{q1[1]:.1f}" class="ext"/>')
        dims.append(f'<line x1="{A[0]:.1f}" y1="{A[1]:.1f}" x2="{B[0]:.1f}" y2="{B[1]:.1f}" class="dl" marker-start="url(#ar)" marker-end="url(#ar)"/>')
        mx, my = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2
        ang = math.degrees(math.atan2(B[1] - A[1], B[0] - A[0]))
        if ang > 90: ang -= 180
        if ang < -90: ang += 180
        nx, ny = -math.sin(math.radians(ang)), math.cos(math.radians(ang))
        dd = (gap if gap is not None else 11) * side
        tx, ty = mx - nx * dd, my - ny * dd
        dims.append(f'<text x="{tx:.1f}" y="{ty:.1f}" class="dt" font-size="{size}" text-anchor="middle" dominant-baseline="middle" transform="rotate({ang:.1f} {tx:.1f} {ty:.1f})">{text}</text>')

    dimline([-beamHalf, 0, beamZ + beamR], [beamHalf, 0, beamZ + beamR], [0, 0, 520], m(2 * beamHalf), size=16)
    for i in range(len(HANG) - 1):
        a, b = HANG[i], HANG[i + 1]
        dimline([a, 0, beamZ + beamR + 20], [b, 0, beamZ + beamR + 20], [0, 0, 230], num((b - a) / 1000), size=12, gap=9)
    dimline([-beamHalf, 0, 0], [-beamHalf, 0, beamZ], [-650, 0, 0], m(beamZ) + " eje del travesaño", size=15)
    fA, fB = legs[(1, -1)][0], legs[(1, 1)][0]
    dimline([fA[0] + legR, fA[1], 0], [fA[0] + legR, fB[1], 0], [620, 0, 0], m(2 * foot) + " base", size=15)
    fL, fR = legs[(-1, -1)][0], legs[(1, -1)][0]
    dimline([fL[0] - legR, fL[1], 0], [fR[0] + legR, fR[1], 0], [0, -700, 0], m(D["pies_exterior"]) + " pies (exterior)", size=15)
    dimline([crossX, 0, 0], [crossX, 0, apex], [1400, 0, 0], m(apex) + " cruce", size=13, ext_from=([fB[0], 0, 0], [crossX + legR, 0, apex]))
    yT = D["yT"]
    tB = [D["tx"], d["tirante"]["largo"] / 2, tieZ]
    dimline([tB[0], tB[1], 0], tB, [0, 560, 0], m(tieZ) + " tirante", size=13)
    cfg = next(c for c in req["configuraciones"] if c["id"] == config_id)
    if "hamaca" in cfg["puestos"]:
        i = len(cfg["puestos"]) - 1 - cfg["puestos"][::-1].index("hamaca")
        xs = SLOTS[i] + ac["asiento_ancho"] / 2
        dimline([xs, -90, 0], [xs, -90, ac["asiento_z"]], [0, -420, 0], m(ac["asiento_z"]), size=12)
    if "trapecio" in cfg["puestos"]:
        xc = SLOTS[cfg["puestos"].index("trapecio")] - ac["trapecio_ancho"] / 2
        dimline([xc, 0, 0], [xc, 0, ac["trapecio_z"]], [0, 520, 0], m(ac["trapecio_z"]) + " trapecio", size=12)
    if "cama" in cfg["puestos"]:
        cmz = ac["cama"]["z"]
        dimline([ac["cama"]["largo"] / 2, -ac["cama"]["ancho"] / 2, 0], [ac["cama"]["largo"] / 2, -ac["cama"]["ancho"] / 2, cmz], [0, -420, 0], m(cmz), size=12)
    yS = -foot * (1 - ac["asiento_z"] / apex)
    xi = axisX(ac["asiento_z"]) - legR - lap
    dimline([-xi, yS, ac["asiento_z"]], [xi, yS, ac["asiento_z"]], [0, 0, 0], m(2 * xi) + " libres a la altura del asiento", size=13,
            ext_from=([-xi, yS, ac["asiento_z"]], [xi, yS, ac["asiento_z"]]))

    def fmtp(pts):
        return fmt(pts)
    f, e = legs[(-1, -1)]
    pv, pu = P(f), P(add(f, [0, 0, 700]))
    dims.append(f'<line x1="{pv[0]:.1f}" y1="{pv[1]:.1f}" x2="{pu[0]:.1f}" y2="{pu[1]:.1f}" class="ext"/>')
    arc = [P(add(f, mul(add(mul([0, 0, 1], math.cos(t)), mul([0, 1, 0], math.sin(t))), 560))) for t in [math.radians(D["ang_lateral"]) * i / 16 for i in range(17)]]
    dims.append(f'<polyline points="{fmtp(arc)}" class="dl" fill="none"/>')
    am = arc[8]
    dims.append(f'<text x="{am[0]-8:.1f}" y="{am[1]-10:.1f}" class="dt" font-size="13" text-anchor="end">{D["ang_lateral"]:.0f}° lateral</text>')
    f, e = legs[(1, -1)]
    pv, pu = P(f), P(add(f, [0, 0, 800]))
    dims.append(f'<line x1="{pv[0]:.1f}" y1="{pv[1]:.1f}" x2="{pu[0]:.1f}" y2="{pu[1]:.1f}" class="ext"/>')
    arc = [P(add(f, mul(add(mul([0, 0, 1], math.cos(t)), mul([-1, 0, 0], math.sin(t))), 700))) for t in [math.radians(D["ang_frontal"]) * i / 12 for i in range(13)]]
    dims.append(f'<polyline points="{fmtp(arc)}" class="dl" fill="none"/>')
    am = arc[6]
    dims.append(f'<text x="{am[0]-10:.1f}" y="{am[1]-4:.1f}" class="dt" font-size="13" text-anchor="end">{D["ang_frontal"]:.0f}° frontal</text>')

    def tag(p3, dx, dy, text):
        p = P(p3)
        q = (p[0] + dx, p[1] + dy)
        dims.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="2.6" class="dotc"/>')
        dims.append(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" class="ldr"/>')
        anchor = "start" if dx >= 0 else "end"
        dims.append(f'<text x="{q[0] + (4 if dx >= 0 else -4):.1f}" y="{q[1]+4:.1f}" class="tg" text-anchor="{anchor}">{html.escape(str(text), quote=False)}</text>')

    tr, pa, ti, ca = d["travesano"], d["patas"], d["tirante"], d["cartela"]
    tag([-1300, -60, beamZ + 60], -40, -150, f"Travesaño Ø{cm(tr['diametro'])} · {m(tr['largo'])}")
    mid = lambda f, e, t: add(f, mul(sub(e, f), t))
    tag(mid(*legs[(1, 1)], 0.66), 60, -80, f"Pata Ø{cm(pa['diametro'])} · {m(pa['largo'])} ({cm(pa['enterrado'])} enterrados)")
    tAm = [-D["tx"], -(yT + 60), tieZ]
    tag(tAm, 70, 95, f"Tirante Ø{cm(ti['diametro'])} · {m(ti['largo'])}")
    tag(mid([-D["tx"], 0, tieZ + 60], [-braceTopX, 0, beamZ - beamR], 0.55), 50, -40, f"Cartela Ø{cm(ca['diametro'])} · {m(ca['largo'])}")
    tag([axisX(beamZ), -230, beamZ + 10], 60, -70, "Horqueta (ver detalle)")
    tag([HANG[min(3, len(HANG) - 1)], -105, beamZ - 40], 40, 70, f"{len(HANG)} abrazaderas de cuelgue")
    # el lienzo crece si el área libre (y sus rótulos) no entra en el encuadre fijo
    xs = [p[0] for p in area] + [czp[0] + 110, mt[0] - 60]
    ys = [p[1] for p in area] + [al[1] + 40]
    vx0, vy0 = min(0, min(xs) - 40), min(0, min(ys) - 40)
    vx1, vy1 = max(W, max(xs) + 40), max(H, max(ys) + 20)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx0:.0f} {vy0:.0f} {vx1 - vx0:.0f} {vy1 - vy0:.0f}" role="img" aria-label="Perspectiva acotada del pórtico de hamacas">
<defs><marker id="ar" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M0,1.5 L9,5 L0,8.5 z" class="arh"/></marker></defs>
<rect x="{vx0:.0f}" y="{vy0:.0f}" width="{vx1 - vx0:.0f}" height="{vy1 - vy0:.0f}" fill="var(--paper)"/>
{''.join(ground)}
{''.join(s for _, s in items)}
{''.join(dims)}
</svg>'''
