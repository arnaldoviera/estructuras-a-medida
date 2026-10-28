"""Perspectiva acotada del pórtico de hamacas (SVG). Unidades: mm. x: muro->césped, y: vaivén, z: arriba."""
import math, sys

OUT = sys.argv[1]

# ---------------- geometría v3 (centro del travesaño a 2,10 m) ----------------
beamR, beamZ, beamHalf = 100, 2100, 1850
legR, footX, crossX, foot, ext = 85, 2065, 1635, 1150, 560
apex = 1760
for _ in range(50):
    apex = beamZ - (beamR + legR) / math.sin(math.atan(foot / apex))
legDeg = math.degrees(math.atan(foot / apex))
lean = (footX - crossX) / apex
frontDeg = math.degrees(math.atan(lean))
axisX = lambda z: footX - lean * z
lap = 30
tieZ, tieR = 1100, 75
braceR, braceTopX = 60, 1350
rodR = 8
SLOTS = [-940, 0, 940]
HANG = [c + d for c in SLOTS for d in (-250, 250)]
pivotZ = 1940
hookZ = pivotZ
seatZ = 500

def add(a, b): return [a[i] + b[i] for i in range(3)]
def sub(a, b): return [a[i] - b[i] for i in range(3)]
def mul(a, k): return [a[i] * k for i in range(3)]
def dot(a, b): return sum(a[i] * b[i] for i in range(3))
def cross(a, b): return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
def norm(a): return math.sqrt(dot(a, a))
def unit(a):
    n = norm(a); return [a[i] / n for i in range(3)]

def at(sx, s, z):
    return [sx * axisX(z) + s * lap, s * foot * (1 - z / apex), z]

cyl = []  # (a, b, r, kind, bias)
cyl.append(([-beamHalf, 0, beamZ], [beamHalf, 0, beamZ], beamR, "wood", 0))
legs = {}
for sx in (-1, 1):
    for s in (-1, 1):
        f = at(sx, s, 0)
        c = [sx * crossX + s * lap, 0, apex]
        e = add(c, mul(unit(sub(c, f)), ext))
        cyl.append((f, e, legR, "wood", 0))
        legs[(sx, s)] = (f, e)
    cyl.append(([sx * crossX - 150, 0, apex], [sx * crossX + 150, 0, apex], rodR, "steel", -30))
    yTop = foot * (beamZ / apex - 1)
    xTop = sx * axisX(beamZ)
    cyl.append(([xTop, -(yTop + 130), beamZ], [xTop, yTop + 130, beamZ], rodR, "steel", -30))
    yT = foot * (1 - tieZ / apex)
    tx = sx * (axisX(tieZ) - legR - tieR + 50)
    cyl.append(([tx, -(yT + 130), tieZ], [tx, yT + 130, tieZ], tieR, "wood", 0))
    for s in (-1, 1):
        cyl.append(([tx - sx * 110, s * yT, tieZ], [sx * (axisX(tieZ) + legR + 25), s * yT, tieZ], rodR, "steel", -30))
    cyl.append(([tx, 0, tieZ + tieR - 15], [sx * braceTopX, 0, beamZ - beamR + 15], braceR, "wood", 0))
    cyl.append(([tx, 0, tieZ - tieR - 25], [tx, 0, tieZ + tieR + 110], 6, "steel", -30))
    cyl.append(([sx * braceTopX, 0, beamZ - beamR - 110], [sx * braceTopX, 0, beamZ + beamR + 25], 6, "steel", -30))
for hx in HANG:
    cyl.append(([hx - 20, 0, beamZ], [hx + 20, 0, beamZ], beamR + 7, "band", -60))
    cyl.append(([hx, 0, beamZ - beamR - 5], [hx, 0, pivotZ], 12, "dark", -40))
ropes = []
boxes = []
for c in (SLOTS[0], SLOTS[2]):
    boxes.append(((c - 215, c + 215), (-90, 90), (seatZ - 30, seatZ)))
    for s in (-1, 1):
        ropes.append(([c + s * 235, 0, seatZ], [c + s * 250, 0, hookZ]))
cyl.append(([-230, 0, 1300], [230, 0, 1300], 16, "steel", 0))
for s in (-1, 1):
    ropes.append(([s * 240, 0, 1316], [s * 250, 0, hookZ]))

# ---------------- cámara en perspectiva ----------------
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
    d = sub(p, EYE)
    zc = dot(d, fwd)
    return (CX + fpx * dot(d, right) / zc, CY - fpx * dot(d, up) / zc)

def depth(p):
    return norm(sub(p, EYE))

LIGHT = unit([-0.5, -0.6, 0.8])
COL = {
    "wood": ("#c98a55", "#e0a874", "#7a4a26", "#e8c9a2"),
    "steel": ("#8d969e", "#c4cbd1", "#3e464d", "#b7bfc6"),
    "dark": ("#454c53", "#6b737a", "#1e2226", "#5b636a"),
}
items = []  # (depth, svg)

def fmt(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)

def cylinder(a, b, r, kind, bias=0, caps=True):
    ax = sub(b, a)
    L = norm(ax)
    u = unit(ax)
    n_chunks = max(1, int(L / 220))
    base, hi, edge, cap = COL[kind]
    for k in range(n_chunks):
        p0 = add(a, mul(ax, k / n_chunks))
        p1 = add(a, mul(ax, (k + 1) / n_chunks))
        def off(p):
            n = unit(cross(u, sub(p, EYE)))
            return n
        n0, n1 = off(p0), off(p1)
        sgn = 1 if dot(n0, LIGHT) > 0 else -1
        q = [P(add(p0, mul(n0, r))), P(add(p1, mul(n1, r))), P(add(p1, mul(n1, -r))), P(add(p0, mul(n0, -r)))]
        h = [P(add(p0, mul(n0, sgn * r * 0.15))), P(add(p1, mul(n1, sgn * r * 0.15))), P(add(p1, mul(n1, sgn * r * 0.7))), P(add(p0, mul(n0, sgn * r * 0.7)))]
        sw = 1.1 if kind == "wood" else 0.8
        svg = (f'<polygon points="{fmt(q)}" fill="{base}" stroke="{base}" stroke-width="0.6"/>'
               f'<polygon points="{fmt(h)}" fill="{hi}"/>'
               f'<line x1="{q[0][0]:.1f}" y1="{q[0][1]:.1f}" x2="{q[1][0]:.1f}" y2="{q[1][1]:.1f}" stroke="{edge}" stroke-width="{sw}"/>'
               f'<line x1="{q[3][0]:.1f}" y1="{q[3][1]:.1f}" x2="{q[2][0]:.1f}" y2="{q[2][1]:.1f}" stroke="{edge}" stroke-width="{sw}"/>')
        items.append((depth(mul(add(p0, p1), 0.5)) + bias, svg))
    # tapas
    ref = [0, 0, 1] if abs(u[2]) < 0.9 else [1, 0, 0]
    e1 = unit(cross(u, ref)); e2 = cross(u, e1)
    for p, dirn in ((a, mul(u, -1)), (b, u)):
        if not caps or dot(dirn, sub(EYE, p)) <= 0:
            continue
        ring = [P(add(p, add(mul(e1, r * math.cos(t)), mul(e2, r * math.sin(t))))) for t in [i * 2 * math.pi / 28 for i in range(28)]]
        sw = 1.1 if kind == "wood" else 0.8
        svg = f'<polygon points="{fmt(ring)}" fill="{cap}" stroke="{edge}" stroke-width="{sw}"/>'
        if kind == "wood":
            ring2 = [P(add(p, add(mul(e1, r * 0.55 * math.cos(t)), mul(e2, r * 0.55 * math.sin(t))))) for t in [i * 2 * math.pi / 20 for i in range(20)]]
            svg += f'<polygon points="{fmt(ring2)}" fill="none" stroke="#b98c62" stroke-width="0.6"/>'
        items.append((depth(p) - 1 + bias, svg))

def box(xr, yr, zr):
    x0, x1 = xr; y0, y1 = yr; z0, z1 = zr
    v = lambda x, y, z: [x, y, z]
    faces = [
        ([v(x0,y0,z1), v(x1,y0,z1), v(x1,y1,z1), v(x0,y1,z1)], [0,0,1], "#8a5a34"),
        ([v(x0,y0,z0), v(x1,y0,z0), v(x1,y0,z1), v(x0,y0,z1)], [0,-1,0], "#6e4527"),
        ([v(x0,y0,z0), v(x0,y1,z0), v(x0,y1,z1), v(x0,y0,z1)], [-1,0,0], "#5c3a20"),
        ([v(x1,y0,z0), v(x1,y1,z0), v(x1,y1,z1), v(x1,y0,z1)], [1,0,0], "#5c3a20"),
        ([v(x0,y1,z0), v(x1,y1,z0), v(x1,y1,z1), v(x0,y1,z1)], [0,1,0], "#6e4527"),
    ]
    for pts, n, col in faces:
        c = mul([sum(p[i] for p in pts) for i in range(3)], 0.25)
        if dot(n, sub(EYE, c)) <= 0:
            continue
        items.append((depth(c), f'<polygon points="{fmt([P(p) for p in pts])}" fill="{col}" stroke="#3a2412" stroke-width="0.8"/>'))

for a, b, r, k, bi in cyl:
    cylinder(a, b, r, 'steel' if k == 'band' else k, bi, caps=(k != 'band'))
for bx in boxes:
    box(*bx)
for a, b in ropes:
    pa, pb = P(a), P(b)
    items.append((depth(mul(add(a, b), 0.5)), f'<line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" stroke="#9c958a" stroke-width="1.6"/>'))

items.sort(key=lambda t: -t[0])

# ---------------- suelo y área ----------------
ground = []
AX0, AX1, AY = -2250, 2250, 2750
area = [P([AX0, -AY, 0]), P([AX1, -AY, 0]), P([AX1, AY, 0]), P([AX0, AY, 0])]
ground.append(f'<polygon points="{fmt(area)}" fill="var(--ground)" stroke="var(--dim)" stroke-width="1" stroke-dasharray="7 5"/>')
# muro: línea gruesa en el piso con rayado hacia afuera
m0, m1 = P([AX0, -AY, 0]), P([AX0, AY, 0])
ground.append(f'<line x1="{m0[0]:.1f}" y1="{m0[1]:.1f}" x2="{m1[0]:.1f}" y2="{m1[1]:.1f}" stroke="var(--wallEdge)" stroke-width="5"/>')
for k in range(23):
    yy = -AY + k * 250
    a, b = P([AX0, yy, 0]), P([AX0 - 180, yy - 120, 0])
    ground.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="var(--wallEdge)" stroke-width="1"/>')
mt = P([AX0 - 300, -1200, 0])
ground.append(f'<text x="{mt[0]:.1f}" y="{mt[1]:.1f}" class="lbl soft" text-anchor="end">MURO</text>')
cz = P([AX1 + 150, -AY + 200, 0])
ground.append(f'<text x="{cz[0]:.1f}" y="{cz[1]:.1f}" class="lbl soft" text-anchor="start">CÉSPED →</text>')
al = P([0, -AY, 0])
ground.append(f'<text x="{al[0]:.1f}" y="{al[1]+22:.1f}" class="lbl soft" text-anchor="middle">ÁREA LIBRE 4,50 × 5,50 m</text>')
# pozos de las patas
for sx in (-1, 1):
    for s in (-1, 1):
        f = legs[(sx, s)][0]
        ring = [P(add(f, [150 * math.cos(t), 150 * math.sin(t), 0])) for t in [i * 2 * math.pi / 24 for i in range(24)]]
        ground.append(f'<polygon points="{fmt(ring)}" fill="var(--hole)" stroke="none"/>')

# ---------------- cotas ----------------
dims = []
TICK = 7

def dimline(a, b, off, text, side=1, ext_from=None, size=15, gap=None):
    """Cota entre a y b, desplazada por el vector 'off' (3D). Líneas de referencia desde a, b."""
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
    d = (gap if gap is not None else 11) * side
    tx, ty = mx - nx * d, my - ny * d
    dims.append(f'<text x="{tx:.1f}" y="{ty:.1f}" class="dt" font-size="{size}" text-anchor="middle" dominant-baseline="middle" transform="rotate({ang:.1f} {tx:.1f} {ty:.1f})">{text}</text>')

def m(v):
    return f"{v/1000:.2f}".replace(".", ",") + " m"

# 1. Largo travesaño y cadena de cuelgues (arriba)
dimline([-beamHalf, 0, beamZ + beamR], [beamHalf, 0, beamZ + beamR], [0, 0, 520], m(2 * beamHalf), size=16)
for i in range(len(HANG) - 1):
    a, b = HANG[i], HANG[i + 1]
    dimline([a, 0, beamZ + beamR + 20], [b, 0, beamZ + beamR + 20], [0, 0, 230], f"{(b-a)/1000:.2f}".replace(".", ","), size=12, gap=9)
# 2. Altura del eje del travesaño
dimline([-beamHalf, 0, 0], [-beamHalf, 0, beamZ], [-650, 0, 0], m(beamZ) + " eje del travesaño", size=15)
# 3. Base de cada A (césped)
fA, fB = legs[(1, -1)][0], legs[(1, 1)][0]
dimline([fA[0] + legR, fA[1], 0], [fA[0] + legR, fB[1], 0], [620, 0, 0], m(2 * foot) + " base", size=15)
# 4. Pies por fuera (frente)
fL, fR = legs[(-1, -1)][0], legs[(1, -1)][0]
dimline([fL[0] - legR, fL[1], 0], [fR[0] + legR, fR[1], 0], [0, -700, 0], m(fR[0] - fL[0] + 2 * legR) + " pies (exterior)", size=15)
# 5. Cruce y tirante (A del césped)
dimline([crossX, 0, 0], [crossX, 0, apex], [1400, 0, 0], m(apex) + " cruce", size=13, ext_from=([fB[0], 0, 0], [crossX + legR, 0, apex]))
yT = foot * (1 - tieZ / apex)
tB = [axisX(tieZ) - legR - tieR + 50, yT + 130, tieZ]
dimline([tB[0], tB[1], 0], tB, [0, 560, 0], m(tieZ) + " tirante", size=13)
# 6. Asiento y trapecio
dimline([SLOTS[2] + 215, -90, 0], [SLOTS[2] + 215, -90, seatZ], [0, -420, 0], m(seatZ), size=12)
dimline([-230, 0, 0], [-230, 0, 1300], [0, 520, 0], m(1300) + " trapecio", size=12)
# 7. Libre entre patas a la altura del asiento (patas del frente)
yS = -foot * (1 - seatZ / apex)
xi = axisX(seatZ) - legR - lap
dimline([-xi, yS, seatZ], [xi, yS, seatZ], [0, 0, 0], m(2 * xi) + " libres a la altura del asiento", size=13, ext_from=([-xi, yS, seatZ], [xi, yS, seatZ]))

# Ángulo lateral (A del muro, pata del frente)
f, e = legs[(-1, -1)]
pv = P(f)
pu = P(add(f, [0, 0, 700]))
dims.append(f'<line x1="{pv[0]:.1f}" y1="{pv[1]:.1f}" x2="{pu[0]:.1f}" y2="{pu[1]:.1f}" class="ext"/>')
hdir = [0, 1, 0]
arc = [P(add(f, mul(add(mul([0, 0, 1], math.cos(t)), mul(hdir, math.sin(t))), 560))) for t in [math.radians(legDeg) * i / 16 for i in range(17)]]
dims.append(f'<polyline points="{fmt(arc)}" class="dl" fill="none"/>')
am = arc[8]
angtxt = f"{legDeg:.0f}° lateral".replace(".", ",")
dims.append(f'<text x="{am[0]-8:.1f}" y="{am[1]-10:.1f}" class="dt" font-size="13" text-anchor="end">{angtxt}</text>')
# Ángulo frontal (A del césped, pata del frente)
f, e = legs[(1, -1)]
pv = P(f); pu = P(add(f, [0, 0, 800]))
dims.append(f'<line x1="{pv[0]:.1f}" y1="{pv[1]:.1f}" x2="{pu[0]:.1f}" y2="{pu[1]:.1f}" class="ext"/>')
arc = [P(add(f, mul(add(mul([0, 0, 1], math.cos(t)), mul([-1, 0, 0], math.sin(t))), 700))) for t in [math.radians(frontDeg) * i / 12 for i in range(13)]]
dims.append(f'<polyline points="{fmt(arc)}" class="dl" fill="none"/>')
am = arc[6]
angtxt = f"{frontDeg:.0f}° frontal"
dims.append(f'<text x="{am[0]-10:.1f}" y="{am[1]-4:.1f}" class="dt" font-size="13" text-anchor="end">{angtxt}</text>')

# Diámetros (rótulos con línea guía)
def tag(p3, dx, dy, text):
    p = P(p3)
    q = (p[0] + dx, p[1] + dy)
    dims.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="2.6" class="dotc"/>')
    dims.append(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" class="ldr"/>')
    anchor = "start" if dx >= 0 else "end"
    dims.append(f'<text x="{q[0] + (4 if dx >= 0 else -4):.1f}" y="{q[1]+4:.1f}" class="tg" text-anchor="{anchor}">{text}</text>')

tag([-1300, -60, beamZ + 60], -40, -150, "Travesaño Ø20 cm · 3,70 m")
mid = lambda f, e, t: add(f, mul(sub(e, f), t))
tag(mid(*legs[(1, 1)], 0.66), 60, -80, "Pata Ø17 cm · 2,95 m (20 cm enterrados)")
tAm = [-(axisX(tieZ) - legR - tieR + 50), -(yT + 60), tieZ]
tag(tAm, 70, 95, "Tirante Ø15 cm · 1,15 m")
tag(mid([-(axisX(tieZ) - legR - tieR + 50), 0, tieZ + 60], [-braceTopX, 0, beamZ - beamR], 0.55), 50, -40, "Cartela Ø12 cm · 1,00 m")
tag([axisX(beamZ), -230, beamZ + 10], 60, -70, "Horqueta (ver detalle)")
tag([HANG[3], -105, beamZ - 40], 40, 70, "6 abrazaderas de cuelgue")

# ---------------- ensamblar ----------------
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="Perspectiva acotada del pórtico de hamacas">
<defs><marker id="ar" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M0,1.5 L9,5 L0,8.5 z" class="arh"/></marker></defs>
<rect x="0" y="0" width="{W}" height="{H}" fill="var(--paper)"/>
{''.join(ground)}
{''.join(s for _, s in items)}
{''.join(dims)}
</svg>'''
open(OUT, "w").write(svg)
print(f"cruce {apex:.0f} lateral {legDeg:.2f} frontal {frontDeg:.2f}")
