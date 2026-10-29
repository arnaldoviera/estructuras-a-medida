"""Láminas 2D de detalles de uniones del pórtico (SVG, mm), generadas desde ficha.json.
Refactor de insumos/portico-v3/detalles/detalles.py (clase Fig sin cambios)."""
import html as _html
import math
from comun import m, cm, num
WOOD, WOODHI, WOODEDGE, CAP = "#c98a55", "#e0a874", "#7a4a26", "#e8c9a2"
STEEL, STEELD = "#9aa3ab", "#3e464d"



def _esc(s):
    """Escapa texto que viene de la ficha (& < >) para que el SVG siga siendo XML válido."""
    return _html.escape(str(s), quote=False)


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
            self.g.append(f'<text x="{B[0] + (4 if anchor == "start" else -4):.1f}" y="{B[1] + 4 + i * 15:.1f}" class="tg" text-anchor="{anchor}">{_esc(t)}</text>')

    def text(self, p, t, cls="vw", anchor="middle"):
        A = self.P(*p)
        self.g.append(f'<text x="{A[0]:.1f}" y="{A[1]:.1f}" class="{cls}" text-anchor="{anchor}">{_esc(t)}</text>')

    def svg(self, label):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.W} {self.H:.0f}" role="img" aria-label="{label}">'
                '<defs><marker id="ar" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,1.5 L9,5 L0,8.5 z" class="arh"/></marker></defs>'
                f'<rect width="{self.W}" height="{self.H:.0f}" fill="var(--paper)"/>' + "".join(self.g) + f'<text x="16" y="26" class="vw">{self.title_txt}</text>' + "</svg>")


