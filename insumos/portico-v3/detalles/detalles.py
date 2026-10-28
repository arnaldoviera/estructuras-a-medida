"""Detalles de uniones del pórtico (SVG 2D, en mm). Escribe detalle_N.svg en el directorio dado."""
import math, sys, os

OUT = sys.argv[1]
WOOD, WOODHI, WOODEDGE, CAP = "#c98a55", "#e0a874", "#7a4a26", "#e8c9a2"
STEEL, STEELD = "#9aa3ab", "#3e464d"


class Fig:
    def __init__(self, x0, x1, y0, y1, W=760, pad=56, padx=175):
        # ventana en mm (x0..x1, y0..y1 con y hacia arriba); margen lateral para rótulos
        self.k = (W - 2 * padx) / (x1 - x0)
        self.H = (y1 - y0) * self.k + 2 * pad
        self.W, self.pad, self.padx, self.x0, self.y1 = W, pad, padx, x0, y1
        self.title_txt = ""
        self.g = []

    def P(self, x, y):
        return (self.padx + (x - self.x0) * self.k, self.pad + (self.y1 - y) * self.k)

    def pts(self, ps):
        return " ".join("%.1f,%.1f" % self.P(*p) for p in ps)

    def poly(self, ps, fill, stroke=WOODEDGE, sw=1.3, extra=""):
        self.g.append(f'<polygon points="{self.pts(ps)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

    def line(self, a, b, stroke=WOODEDGE, sw=1.2, extra=""):
        A, B = self.P(*a), self.P(*b)
        self.g.append(f'<line x1="{A[0]:.1f}" y1="{A[1]:.1f}" x2="{B[0]:.1f}" y2="{B[1]:.1f}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

    def circle(self, c, r, fill, stroke=WOODEDGE, sw=1.3, extra=""):
        C = self.P(*c)
        self.g.append(f'<circle cx="{C[0]:.1f}" cy="{C[1]:.1f}" r="{r * self.k:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

    def log_side(self, a, b, d, hi=True):
        ux, uy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
        nx, ny = -uy, ux
        r = d / 2
        q = [(a[0] + nx * r, a[1] + ny * r), (b[0] + nx * r, b[1] + ny * r), (b[0] - nx * r, b[1] - ny * r), (a[0] - nx * r, a[1] - ny * r)]
        self.poly(q, WOOD, "none", 0)
        if hi:
            h = [(a[0] + nx * r * 0.15, a[1] + ny * r * 0.15), (b[0] + nx * r * 0.15, b[1] + ny * r * 0.15), (b[0] + nx * r * 0.65, b[1] + ny * r * 0.65), (a[0] + nx * r * 0.65, a[1] + ny * r * 0.65)]
            self.poly(h, WOODHI, "none", 0)
        self.line(q[0], q[1]); self.line(q[3], q[2])
        return q

    def section(self, c, r):
        self.circle(c, r, CAP)
        for f in (0.68, 0.38):
            self.circle(c, r * f, "none", "#b98c62", 0.7)

    def rod(self, a, b, d=16, nuts=True, wash=50):
        ux, uy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
        nx, ny = -uy, ux
        r = d / 2
        q = [(a[0] + nx * r, a[1] + ny * r), (b[0] + nx * r, b[1] + ny * r), (b[0] - nx * r, b[1] - ny * r), (a[0] - nx * r, a[1] - ny * r)]
        self.poly(q, STEEL, STEELD, 0.9)
        if nuts:
            for p, s in ((a, 1), (b, -1)):
                # arandela, tuerca y contratuerca desde la punta hacia adentro
                for off, w, h, col in ((s * 26, 4, wash / 2, "#c4cbd1"), (s * 16, 12, 14, "#5b636a"), (s * 4, 12, 14, "#454c53")):
                    c = (p[0] + ux * off, p[1] + uy * off)
                    box = [(c[0] - ux * w / 2 + nx * h, c[1] - uy * w / 2 + ny * h), (c[0] + ux * w / 2 + nx * h, c[1] + uy * w / 2 + ny * h),
                           (c[0] + ux * w / 2 - nx * h, c[1] + uy * w / 2 - ny * h), (c[0] - ux * w / 2 - nx * h, c[1] - uy * w / 2 - ny * h)]
                    self.poly(box, col, STEELD, 0.8)

    def hole(self, a, b, d=18):
        ux, uy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
        nx, ny = -uy, ux
        for s in (1, -1):
            self.line((a[0] + nx * d / 2 * s, a[1] + ny * d / 2 * s), (b[0] + nx * d / 2 * s, b[1] + ny * d / 2 * s), "#5a3a1e", 1, 'stroke-dasharray="5 3"')

    def dim(self, a, b, off, text, size=13):
        ux, uy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
        nx, ny = -uy, ux
        A = (a[0] + nx * off, a[1] + ny * off); B = (b[0] + nx * off, b[1] + ny * off)
        for p, q in ((a, A), (b, B)):
            self.line((p[0] + nx * 6 * (1 if off > 0 else -1), p[1] + ny * 6 * (1 if off > 0 else -1)), (q[0] + nx * 8 * (1 if off > 0 else -1), q[1] + ny * 8 * (1 if off > 0 else -1)), "#1f5f8b", 0.8, 'opacity=".7"')
        PA, PB = self.P(*A), self.P(*B)
        self.g.append(f'<line x1="{PA[0]:.1f}" y1="{PA[1]:.1f}" x2="{PB[0]:.1f}" y2="{PB[1]:.1f}" class="dl" marker-start="url(#ar)" marker-end="url(#ar)"/>')
        mx, my = (PA[0] + PB[0]) / 2, (PA[1] + PB[1]) / 2
        ang = math.degrees(math.atan2(PB[1] - PA[1], PB[0] - PA[0]))
        if ang > 90: ang -= 180
        if ang < -90: ang += 180
        sx, sy = math.sin(math.radians(ang)), -math.cos(math.radians(ang))
        tx, ty = mx + sx * 10, my + sy * 10
        self.g.append(f'<text x="{tx:.1f}" y="{ty:.1f}" class="dt" font-size="{size}" text-anchor="middle" dominant-baseline="middle" transform="rotate({ang:.1f} {tx:.1f} {ty:.1f})">{text}</text>')

    def tag(self, p, dx, dy, text, anchor=None):
        A = self.P(*p)
        B = (A[0] + dx, A[1] + dy)
        anchor = anchor or ("start" if dx >= 0 else "end")
        self.g.append(f'<circle cx="{A[0]:.1f}" cy="{A[1]:.1f}" r="2.4" class="dotc"/><line x1="{A[0]:.1f}" y1="{A[1]:.1f}" x2="{B[0]:.1f}" y2="{B[1]:.1f}" class="ldr"/>')
        lines = text.split("|")
        for i, t in enumerate(lines):
            self.g.append(f'<text x="{B[0] + (4 if anchor == "start" else -4):.1f}" y="{B[1] + 4 + i * 15:.1f}" class="tg" text-anchor="{anchor}">{t}</text>')

    def text(self, p, t, cls="vw", anchor="middle"):
        A = self.P(*p)
        self.g.append(f'<text x="{A[0]:.1f}" y="{A[1]:.1f}" class="{cls}" text-anchor="{anchor}">{t}</text>')

    def svg(self, label):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.W} {self.H:.0f}" role="img" aria-label="{label}">'
                '<defs><marker id="ar" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,1.5 L9,5 L0,8.5 z" class="arh"/></marker></defs>'
                f'<rect width="{self.W}" height="{self.H:.0f}" fill="var(--paper)"/>' + "".join(self.g) + f'<text x="16" y="26" class="vw">{self.title_txt}</text>' + "</svg>")


# --- geometría común ---
beamZ, beamR, legR, foot = 2100, 100, 85, 1150
cz = 1760
for _ in range(50):
    cz = beamZ - (beamR + legR) / math.sin(math.atan(foot / cz))
tanA = foot / cz
A = math.degrees(math.atan(tanA))
lean = 430 / cz
out = {}

# ===== 1. Horqueta: vista lateral (mirando a lo largo del travesaño) =====
f = Fig(-560, 560, 1480, 2330)
ext = 560
for s in (-1, 1):
    a = (s * foot * (1 - 1480 / cz), 1480)
    u = (-s * foot, cz); L = math.hypot(*u); u = (u[0] / L, u[1] / L)
    b = (0 + u[0] * ext, cz + u[1] * ext)
    q = f.log_side(a, b, 170)
    # corte de la punta (perpendicular)
    f.poly([q[1], q[2], (q[2][0] - u[0] * 4, q[2][1] - u[1] * 4), (q[1][0] - u[0] * 4, q[1][1] - u[1] * 4)], CAP, WOODEDGE, 1.2)
f.section((0, beamZ), beamR)
yTop = foot * (beamZ / cz - 1)
f.hole((-(yTop + 85), beamZ), (yTop + 85, beamZ))
f.rod((-(yTop + 135), beamZ), (yTop + 135, beamZ))
f.circle((0, cz), 25, "#c4cbd1", STEELD, 0.9)
f.circle((0, cz), 8, STEEL, STEELD, 0.9)
f.dim((-(yTop + 135), beamZ), (yTop + 135, beamZ), 150, f"varilla 16 mm × {(2*(yTop+135)+60)/1000:.2f} m".replace(".", ","), 12)
f.tag((0, beamZ + 60), 150, -20, "Travesaño Ø20|apoya en la V (asiento|rebajado 1,5 cm en cada pata)")
f.tag((-yTop + 40, beamZ - 20), -150, 70, "Agujero Ø18 pasante:|pata – travesaño – pata", "end")
f.tag((0, cz), 150, 30, "Cruce a media madera|varilla 16 mm a lo largo|del travesaño (ver vista B)")
f.dim((0, beamZ), (0, cz), -330, f"{(beamZ - cz)/10:.0f} cm", 12)
f.text((0, 1500), f"{A:.0f}° respecto de la vertical", "vw2")
f.title_txt = "A · VISTA LATERAL"
out[1] = ("Horqueta y apoyo del travesaño", f.svg("Detalle de la horqueta"))

# ===== 1B. Cruce a media madera: vista frontal =====
f = Fig(-330, 330, 1500, 2040, W=640)
lap = 30
for s in (-1, 1):
    a = (s * lap + 270 * lean * 0, 1500)
    b = (s * lap - lean * (2040 - 1500), 2040)
    f.log_side(a, b, 170)
# zona de encastre (media madera, rebaje 1/3)
cx = -lean * (cz - 1500)
f.poly([(cx - 55, cz - 90), (cx + 55, cz - 90), (cx + 55, cz + 90), (cx - 55, cz + 90)], "#b77a48", WOODEDGE, 1, 'stroke-dasharray="4 3"')
f.hole((cx - 115 - 10, cz), (cx + 115 + 10, cz))
f.rod((cx - 175, cz), (cx + 175, cz))
f.dim((cx - 115, cz - 120), (cx + 115, cz - 120), -40, "23 cm (2 × Ø17 − 2 rebajes)", 11)
f.tag((cx, cz + 60), 120, -60, "Rebaje de 1/3 del diámetro|(≈ 5,5 cm) en cada pata;|quedan encastradas")
f.tag((cx + 150, cz), 40, 90, "Varilla 16 mm, arandela 50 mm,|tuerca y contratuerca")
f.text((cx - 20, 1530), f"{lean*57.3:.0f}° vista frontal", "vw2")
f.title_txt = "B · VISTA FRONTAL DEL CRUCE"
out[2] = ("Cruce de patas a media madera", f.svg("Detalle del cruce de patas"))

# ===== 2. Tirante – pata: corte horizontal a 1,10 m (planta) =====
f = Fig(1450, 2080, 120, 760)
ax = 2065 - lean * 1100
yT = foot * (1 - 1100 / cz)
flat = ax - legR + 25
tx = flat - 75 + 25
# tirante (a lo largo de y), rebajado en su cara exterior
f.poly([(tx - 75, 140), (flat, 140), (flat, 740), (tx - 75, 740)], WOOD, WOODEDGE, 1.3)
f.poly([(tx - 75 + 20, 140), (tx - 20, 140), (tx - 20, 740), (tx - 75 + 20, 740)], WOODHI, "none", 0)
# pata en corte, con el plano rebajado
pts = []
xc, yc = ax, yT
for i in range(73):
    t = 2 * math.pi * i / 72
    x, y = xc + legR * math.cos(t), yc + legR * math.sin(t)
    pts.append((max(x, flat), y))
f.poly(pts, CAP, WOODEDGE, 1.3)
f.circle((xc + 10, yc), legR * 0.55, "none", "#b98c62", 0.7)
f.hole((tx - 75 - 5, yT), (ax + legR + 5, yT))
f.rod((tx - 75 - 55, yT), (ax + legR + 55, yT))
f.dim((tx - 75, 140), (flat, 140), -30, "Ø15 − 2,5", 11)
f.tag((flat, yT + 120), 70, -40, "Rebaje plano 2,5 cm|en tirante y en pata")
f.tag((ax, yT - 40), 40, 70, "Pata Ø17 (corte)")
f.tag((tx - 75 - 40, yT), -10, -80, "Varilla 16 mm|agujero Ø18", "end")
f.text((tx - 40, 700), "TIRANTE", "vw2")
f.title_txt = "CORTE HORIZONTAL A 1,10 m"
f.text((2060, 150), "← interior del pórtico", "vw2", "end")
out[3] = ("Tirante contra la pata", f.svg("Detalle del tirante y la pata"))

# ===== 3. Cartela: vista frontal =====
f = Fig(1150, 1900, 980, 2260)
txc = flat - 50
# travesaño (de costado) con rebaje plano abajo
f.poly([(1150, 2020), (1900, 2020), (1900, 2200), (1150, 2200)], WOOD, WOODEDGE, 1.3)
f.poly([(1150, 2120), (1900, 2120), (1900, 2170), (1150, 2170)], WOODHI, "none", 0)
f.line((1150, 2000), (1900, 2000), "#7a4a26", 0.8, 'stroke-dasharray="4 3"')
# tirante (corte) con rebaje plano arriba
pts = []
for i in range(73):
    t = 2 * math.pi * i / 72
    pts.append((txc + 75 * math.cos(t), min(1100 + 75 * math.sin(t), 1155)))
f.poly(pts, CAP, WOODEDGE, 1.3)
# cartela con cortes horizontales en las puntas
a, b = (txc, 1155), (1350, 2020)
ux, uy = b[0] - a[0], b[1] - a[1]
L = math.hypot(ux, uy)
w = 60 / (uy / L)  # medio ancho horizontal
f.poly([(a[0] - w, a[1]), (a[0] + w, a[1]), (b[0] + w, b[1]), (b[0] - w, b[1])], WOOD, WOODEDGE, 1.3)
f.poly([(a[0] - w * 0.65, a[1]), (a[0] - w * 0.15, a[1]), (b[0] - w * 0.15, b[1]), (b[0] - w * 0.65, b[1])], WOODHI, "none", 0)
# varillas verticales
f.hole((txc, 1025), (txc, 1155 + 165), 14)
f.rod((txc, 1000), (txc, 1155 + 175), 12, wash=40)
f.hole((1350, 2200), (1350, 2020 - 165), 14)
f.rod((1350, 2230), (1350, 2020 - 175), 12, wash=40)
f.tag((1350 + 20, 2010), 120, 30, "Rebaje plano 2 cm|bajo el travesaño")
f.tag((txc + 20, 1160), 80, -10, "Rebaje plano 2 cm|sobre el tirante")
f.tag((1350, 1880), -40, -80, "Varilla 12 mm vertical;|sale por el costado de la|cartela: asiento plano", "end")
f.tag((txc, 1260), -80, 40, "Varilla 12 mm atraviesa|tirante y pie de cartela", "end")
f.dim(a, b, -110, f"≈ {L/1000:.2f} m".replace(".", ","), 12)
f.title_txt = "VISTA FRONTAL"
out[4] = ("Cartela entre tirante y travesaño", f.svg("Detalle de la cartela"))

# ===== 4. Abrazadera de cuelgue: corte transversal =====
f = Fig(-260, 260, 1760, 2240)
f.section((0, beamZ), 100)
f.circle((0, beamZ), 103, "none", "#2b2b2b", 3 * f.k)  # goma
# planchuela (dos medias cañas) con orejas abajo
ring_r = 108
f.circle((0, beamZ), ring_r, "none", "#7d868e", 5 * f.k)
for s in (-1, 1):
    f.poly([(s * 6, beamZ - ring_r - 2), (s * 11, beamZ - ring_r - 2), (s * 11, beamZ - ring_r - 90), (s * 6, beamZ - ring_r - 90)], "#7d868e", STEELD, 0.9)
# bulones de cierre (vistos de punta)
for zz in (beamZ - ring_r - 25, beamZ - ring_r - 55):
    f.line((-30, zz), (30, zz), STEELD, 4)
    f.poly([(14, zz - 7), (24, zz - 7), (24, zz + 7), (14, zz + 7)], "#5b636a", STEELD, 0.8)
    f.poly([(-24, zz - 7), (-14, zz - 7), (-14, zz + 7), (-24, zz + 7)], "#5b636a", STEELD, 0.8)
# grillete con buje
gz = beamZ - ring_r - 80
pts = [(18 * math.cos(t), gz - 30 - 30 * math.sin(t)) for t in [math.pi * i / 20 for i in range(21)]]
f.g.append(f'<polyline points="{f.pts([(-18, gz)] + pts[::-1] + [(18, gz)])}" fill="none" stroke="#454c53" stroke-width="{10*f.k:.1f}" stroke-linecap="round"/>')
f.line((0, gz - 60), (0, 1770), "#9c958a", 6 * f.k)
f.tag((70, beamZ + 75), 70, -30, "Planchuela galvanizada 40 × 5 mm|en dos medias cañas")
f.tag((-100, beamZ - 20), -50, -90, "Banda de goma 3 mm|(no marca ni resbala)", "end")
f.tag((24, beamZ - ring_r - 25), 80, -5, "Cierre: 2 varillas 10 mm|con tuerca y contratuerca")
f.tag((18, gz - 20), 80, 30, "Grillete 10 mm o gancho|giratorio para la soga")
f.text((0, 1775), "soga / cadena", "vw2")
f.title_txt = "CORTE TRANSVERSAL"
out[5] = ("Abrazadera de cuelgue (×6)", f.svg("Detalle de la abrazadera de cuelgue"))

# ===== 5. Apoyo de la pata en el piso =====
f = Fig(-520, 520, -420, 420)
g0 = 0
# suelo
f.poly([(-520, -420), (520, -420), (520, 0), (-520, 0)], "var(--soil)", "none", 0)
f.line((-520, 0), (520, 0), "#7a6a55", 1.5)
# pozo 30 x 30, 25 cm de profundidad
f.poly([(-150, -250), (150, -250), (150, 0), (-150, 0)], "var(--gravel)", "#7a6a55", 1)
for i in range(70):
    x = -140 + (i * 37) % 280; y = -240 + (i * 53) % 230
    f.circle((x, y), 7, "#b3a58f", "#8d7f69", 0.5)
# ladrillo / laja de apoyo
f.poly([(-110, -250), (110, -250), (110, -195), (-110, -195)], "#b0574a", "#6e3027", 1)
# pata (corte horizontal del pie), inclinada 34,9° en el plano que contiene el eje
ang = math.radians(33)
u = (math.sin(ang), math.cos(ang))
base = (0, -195)
top = (base[0] + u[0] * 700, base[1] + u[1] * 700)
# pie cortado horizontal: el polígono arranca en una línea horizontal
r = 85
nx, ny = -u[1], u[0]
p1 = (base[0] - r / u[1], base[1]); p2 = (base[0] + r / u[1], base[1])
q1 = (top[0] + nx * r, top[1] + ny * r); q2 = (top[0] - nx * r, top[1] - ny * r)
f.poly([p1, p2, q2, q1], WOOD, WOODEDGE, 1.3)
f.line(p1, p2, WOODEDGE, 2)
# tratamiento en la base
f.poly([p1, p2, (p2[0] + u[0] * 400, p2[1] + u[1] * 400), (p1[0] + u[0] * 400, p1[1] + u[1] * 400)], "#3b2a1c", "none", 0, 'opacity=".35"')
f.dim((-150, -250), (150, -250), -40, "30 cm", 12)
f.dim((150, -250), (150, 0), -50, "25 cm", 12)
f.dim((-110, -195), (-110, 0), 60, "≈ 20 cm enterrado", 11)
f.tag((p2[0] + 10, -100), 170, 60, "Pie cortado horizontal|(apoya plano)")
f.tag((-80, -225), -80, 40, "Ladrillo macizo o laja", "end")
f.tag((100, -60), 120, -20, "Ripio apisonado")
f.tag((p1[0] + u[0] * 300, p1[1] + u[1] * 300), -150, -60, "Últimos 40 cm con|asfalto en frío o brea", "end")
f.title_txt = "APOYO DE CADA PATA"
out[6] = ("Apoyo de cada pata", f.svg("Detalle del apoyo de la pata"))

os.makedirs(OUT, exist_ok=True)
for k, (title, svg) in out.items():
    open(os.path.join(OUT, f"detalle_{k}.svg"), "w").write(svg)
    open(os.path.join(OUT, f"detalle_{k}.txt"), "w").write(title)
print("ok", list(out))
