"""Genera jaula.html (planta, vista lateral y croquis 3D) desde medidas.json.
Uso: python genera.py   (solo biblioteca estándar)."""
import json
import despiece as D
from pathlib import Path

AQUI = Path(__file__).parent
M = json.loads((AQUI / "medidas.json").read_text(encoding="utf-8"))

L = M["box"]["largo"]
T = M["tubos"]
RP, RL, RG = T["parante"]["diam"] / 2, T["larguero"]["diam"] / 2, T["puerta"]["diam"] / 2
YC = (M["box"]["ancho_libre"] + T["parante"]["diam"]) / 2  # eje de los parantes
H = M["box"]["alto"]
EXT = round(2 * YC + T["parante"]["diam"])


def mm(v):
    return f"{v:,.0f}".replace(",", ".")


# ---------- escena 3D (formato del plugin: cilindros a→b, cajas) ----------
def escena():
    p, c = [], []
    cil = lambda n, a, b, r, m: p.append({"n": n, "a": a, "b": b, "r": r, "m": m})
    caja = lambda n, x, y, z, m: c.append({"n": n, "x": x, "y": y, "z": z, "m": m})
    PL = M["pie"]["pletina"]
    for s in (-1, 1):
        y = s * YC
        for x in M["parantes_x"]:
            cil("parante", [x, y, 19.5], [x, y, H], RP, "galva")
            yp = y + s * PL["desplazamiento_afuera"]
            caja("pletina inox", [x - PL["largo"] / 2, x + PL["largo"] / 2], [yp - PL["ancho"] / 2, yp + PL["ancho"] / 2], [0, 10], "inox")
            caja("placa base galva", [x - 75, x + 75], [y + s * 25 - 75, y + s * 25 + 75], [10, 19.5], "galva")
            caja("contrapletina inox 300x100x8", [x - 150, x + 150], [y + s * 25 - 50, y + s * 25 + 50], [-98, -90], "inox")
        for z in M["largueros_z"]:
            cil("larguero", [0, y, z], [L, y, z], RL, "galva")
        cil("pasamanos", [0, y, H], [L, y, H], RP, "galva")
        cil("soporte dosificador", [L, y, H], [L, y, 1950], RL, "galva")
    cil("travesaño trasero superior", [0, -YC, H], [0, YC, H], RP, "galva")
    cil("travesaño frontal", [L, -YC, H], [L, YC, H], RP, "galva")
    cil("travesaño dosificador", [L, -YC, 1950], [L, YC, 1950], RL, "galva")
    # puerta trasera basculante (cerrada), eje en orejas de los parantes traseros
    P = M["puerta"]
    g, pz, bz = P["ancho"] / 2, P["pivote_z"], P["borde_inf_z"]
    for s in (-1, 1):
        caja("oreja eje 2x1/4", [-25, 25], [s * (YC - RP - 6), s * (YC - RP)][::s], [pz - 25, pz + 25], "galva")
        cil("varilla de mando (detrás del parante)", [-45, s * YC, pz - 20], [-45, s * YC, 330], 5, "galva")
        caja("guarda de chapa", [-60, -30], [s * (YC - 20), s * (YC + 20)][::s], [330, pz - 20], "galva")
        caja("tope + trinquete", [22, 72], [s * (g + 6), s * (YC - RP)][::s], [270, 330], "oscuro")
    cil("eje puerta inox", [0, -YC + RP, pz], [0, YC - RP, pz], P["eje"]["diam"] / 2, "inox")
    for y in (-g, g):
        cil("puerta lateral", [0, y, pz], [0, y, bz], RG, "puerta")
    for z in (bz, 400, 950):
        cil("puerta travesaño", [0, -g, z], [0, g, z], RG, "puerta")
    pc = P["panel_ciego"]
    caja("panel ciego PEAD", [-5, 5], [-g + RG, g - RG], [pc["z0"], pc["z1"]], "pead")
    # frente con barrotes verticales cada 110 mm
    rb = T["barrote"]["diam"] / 2
    luz = (M["box"]["ancho_libre"] - 4 * 2 * rb) / 5
    for i in range(4):
        yb = -M["box"]["ancho_libre"] / 2 + luz * (i + 1) + rb * (2 * i + 1)
        cil("barrote frontal", [L, yb, 330], [L, yb, H], rb, "galva")
    caja("zócalo frontal chapa 2 mm", [L - 1, L + 1], [-YC + RP, YC - RP], [50, 330], "galva")
    cil("travesaño inferior frontal", [L, -YC, 100], [L, YC, 100], RL, "galva")
    cil("travesaño frontal z 330", [L, -YC, 330], [L, YC, 330], RL, "galva")
    cil("barra de cabeza z 700", [L, -YC, 700], [L, YC, 700], RL, "galva")
    cil("apoyo trasero comedero", [1860, -YC, 100], [1860, YC, 100], RL, "galva")
    # comedero, caída frontal, dosificador, línea
    co, do, ca = M["comedero"], M["dosificador"], M["caida"]
    caja("comedero inox", [co["x0"], co["x1"]], [-co["ancho"] / 2, co["ancho"] / 2], [co["z0"], co["z1"]], "inox")
    caja("dosificador", [do["x0"], do["x1"]], [-do["ancho"] / 2, do["ancho"] / 2], [do["z0"], do["z1"]], "electro")
    xm = (do["x0"] + do["x1"]) / 2
    cil("bajada a dosificador", [xm, 0, do["z1"]], [xm, 0, M["linea_alimento"]["z"]], 22, "inox")
    cil("caída al comedero", [ca["x"], 0, ca["z1"]], [ca["x"], 0, ca["z0"]], 25, "inox")
    cil("línea de alimento Ø60", [xm, -1600, M["linea_alimento"]["z"]], [xm, 1600, M["linea_alimento"]["z"]], M["linea_alimento"]["diam"] / 2, "linea")
    r = M["rfid"]
    caja("antena RFID", [r["x0"], r["x1"]], [r["y_cara"] - 22, r["y_cara"]], [r["z0"], r["z1"]], "rfid")
    caja("separador PEAD", [r["x0"] + 10, r["x1"] - 10], [r["y_cara"], YC - RL], [725, 755], "pead")
    # slats
    sl = []
    x = -500
    while x < L + 500:
        sl.append([x, x + M["slat"]["ancho"]])
        x += M["slat"]["ancho"] + M["slat"]["ranura"]
    return {"piezas": p, "cajas": c, "slats": sl, "largo": L, "yc": YC}


# ---------- SVG ----------
def cota_h(x0, x1, y, txt, off=0, arriba=True):
    ty = y - 28 if arriba else y + 78
    return (f'<line class="cota" x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" marker-start="url(#fl)" marker-end="url(#fl)"/>'
            f'<text class="ct" x="{(x0 + x1) / 2 + off}" y="{ty}" text-anchor="middle">{txt}</text>')


def cota_v(x, y0, y1, txt, izq=True):
    tx = x - 30 if izq else x + 30
    anc = "end" if izq else "start"
    return (f'<line class="cota" x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" marker-start="url(#fl)" marker-end="url(#fl)"/>'
            f'<text class="ct" x="{tx}" y="{(y0 + y1) / 2 + 22}" text-anchor="{anc}">{txt}</text>')


DEFS = ('<defs><marker id="fl" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0,1 L9,5 L0,9 z" class="flecha"/></marker>'
        '<pattern id="hatch" width="24" height="24" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        '<line x1="0" y1="0" x2="0" y2="24" class="hatch"/></pattern></defs>')


def planta():
    W = 2 * YC + T["parante"]["diam"]
    pad_l, pad_r, pad_t, pad_b = 560, 560, 260, 300
    vw, vh = L + pad_l + pad_r, W + pad_t + pad_b
    ox, oy = pad_l, pad_t + W / 2  # origen: x=0, y=0 (eje)
    X = lambda x: ox + x
    Y = lambda y: oy - y
    s = [f'<svg viewBox="0 0 {vw:.0f} {vh:.0f}" role="img" aria-label="Planta de la jaula">', DEFS]
    co, do = M["comedero"], M["dosificador"]
    s.append(f'<rect class="comedero" x="{X(co["x0"])}" y="{Y(co["ancho"] / 2)}" width="{co["x1"] - co["x0"]}" height="{co["ancho"]}"/>')
    s.append(f'<rect class="dosif" x="{X(do["x0"])}" y="{Y(do["ancho"] / 2)}" width="{do["x1"] - do["x0"]}" height="{do["ancho"]}"/>')
    for sg in (-1, 1):
        y = sg * YC
        s.append(f'<rect class="tubo" x="{X(0)}" y="{Y(y) - RP}" width="{L}" height="{2 * RP}"/>')
        for x in M["parantes_x"]:
            PL = M["pie"]["pletina"]
            s.append(f'<rect class="pie" x="{X(x) - PL["largo"] / 2}" y="{Y(y + sg * PL["desplazamiento_afuera"]) - PL["ancho"] / 2}" width="{PL["largo"]}" height="{PL["ancho"]}"/>')
            s.append(f'<circle class="parante" cx="{X(x)}" cy="{Y(y)}" r="{RP}"/>')
    s.append(f'<rect class="tubo" x="{X(L) - RP}" y="{Y(YC)}" width="{2 * RP}" height="{2 * YC}"/>')
    s.append(f'<line class="puerta" x1="{X(0)}" y1="{Y(M["puerta"]["ancho"] / 2)}" x2="{X(0)}" y2="{Y(-M["puerta"]["ancho"] / 2)}"/>')
    s.append(f'<line class="caida" x1="{X(M["caida"]["x"])}" y1="{Y(0) - 25}" x2="{X(M["caida"]["x"])}" y2="{Y(0) + 25}"/>')
    r = M["rfid"]
    s.append(f'<rect class="rfid" x="{X(r["x0"])}" y="{Y(r["y_cara"])}" width="{r["x1"] - r["x0"]}" height="22"/>')
    # rótulos
    s.append(f'<text class="rot" x="{X(-60)}" y="{Y(0) + 22}" text-anchor="end">ENTRADA →</text>')
    s.append(f'<text class="rot ac" x="{X(90)}" y="{Y(-YC) + 120}">puerta trasera</text>')
    s.append(f'<text class="rot" x="{X((co["x0"] + co["x1"]) / 2)}" y="{Y(-YC) + 140}" text-anchor="middle">comedero inox</text>')
    s.append(f'<text class="rot" x="{X(r["x0"]) - 40}" y="{Y(YC) - 70}" text-anchor="end">antena RFID</text>')
    s.append(f'<text class="rot" x="{X(747)}" y="{Y(YC) - 110}" text-anchor="middle">pletina de anclaje</text>')
    # cotas
    s.append(cota_h(X(0), X(L), Y(-YC) + 190, f"{mm(L)}", arriba=False))
    s.append(cota_h(X(0), X(747), Y(YC) - 190, f"{mm(747)}"))
    s.append(cota_v(X(1120), Y(YC - RP), Y(-YC + RP), f"{mm(M['box']['ancho_libre'])} libre", izq=False))
    s.append(cota_v(X(L) + 200, Y(YC + RP), Y(-YC - RP), f"{mm(EXT)} ext.", izq=False))
    s.append("</svg>")
    return "".join(s)


def lateral():
    zt = M["linea_alimento"]["z"] + 60
    pad_l, pad_r, pad_t, pad_b = 1000, 980, 120, 420
    vw, vh = L + pad_l + pad_r, zt + pad_t + pad_b
    ox, oz = pad_l, pad_t + zt
    X = lambda x: ox + x
    Z = lambda z: oz - z
    s = [f'<svg viewBox="0 0 {vw:.0f} {vh:.0f}" role="img" aria-label="Vista lateral de la jaula">', DEFS]
    # piso de slats (corte)
    x = -500
    while x < L + 400:
        s.append(f'<rect class="slat" x="{X(x)}" y="{Z(0)}" width="{M["slat"]["ancho"]}" height="90"/>')
        x += M["slat"]["ancho"] + M["slat"]["ranura"]
    co, do, la = M["comedero"], M["dosificador"], M["linea_alimento"]
    xm = (do["x0"] + do["x1"]) / 2
    for z in M["largueros_z"]:
        s.append(f'<rect class="tubo" x="{X(0)}" y="{Z(z) - RL}" width="{L}" height="{2 * RL}"/>')
    s.append(f'<rect class="tubo" x="{X(0)}" y="{Z(H) - RP}" width="{L}" height="{2 * RP}"/>')
    for x in M["parantes_x"]:
        s.append(f'<rect class="tubo" x="{X(x) - RP}" y="{Z(H)}" width="{2 * RP}" height="{H}"/>')
        s.append(f'<rect class="pie" x="{X(x) - M["pie"]["pletina"]["largo"] / 2}" y="{Z(19.5)}" width="{M["pie"]["pletina"]["largo"]}" height="19.5"/>')
    s.append(f'<rect class="tubo" x="{X(L) - RL}" y="{Z(1950)}" width="{2 * RL}" height="{1950 - H}"/>')
    s.append(f'<circle class="parante" cx="{X(L)}" cy="{Z(1950)}" r="{RL}"/>')
    s.append(f'<rect class="comedero" x="{X(co["x0"])}" y="{Z(co["z1"])}" width="{co["x1"] - co["x0"]}" height="{co["z1"] - co["z0"]}"/>')
    s.append(f'<rect class="dosif" x="{X(do["x0"])}" y="{Z(do["z1"])}" width="{do["x1"] - do["x0"]}" height="{do["z1"] - do["z0"]}"/>')
    s.append(f'<line class="bajada" x1="{X(xm)}" y1="{Z(la["z"])}" x2="{X(xm)}" y2="{Z(do["z1"])}"/>')
    s.append(f'<line class="bajada" x1="{X(M["caida"]["x"])}" y1="{Z(M["caida"]["z1"])}" x2="{X(M["caida"]["x"])}" y2="{Z(M["caida"]["z0"])}"/>')
    s.append(f'<line class="tubo-l" x1="{X(L)}" y1="{Z(330)}" x2="{X(L)}" y2="{Z(H)}"/>')
    s.append(f'<rect class="zocalo" x="{X(L) - 8}" y="{Z(330)}" width="16" height="280"/>')
    for zz in (100, 330, 700):
        s.append(f'<circle class="parante" cx="{X(L)}" cy="{Z(zz)}" r="{RL}"/>')
    s.append(f'<circle class="parante" cx="{X(1860)}" cy="{Z(100)}" r="{RL}"/>')
    s.append(f'<circle class="linea" cx="{X(xm)}" cy="{Z(la["z"])}" r="{la["diam"] / 2}"/>')
    r = M["rfid"]
    s.append(f'<rect class="rfid" x="{X(r["x0"])}" y="{Z(r["z1"])}" width="{r["x1"] - r["x0"]}" height="{r["z1"] - r["z0"]}"/>')
    # puerta (cerrada), panel ciego, arco de apertura hasta 90° y trinquetes
    P = M["puerta"]
    pz, bz, pc = P["pivote_z"], P["borde_inf_z"], P["panel_ciego"]
    R = pz - bz
    import math
    for sg in (1, -1):  # +1 hacia adentro (entrar), -1 hacia afuera (salir de culata)
        pts = " ".join(f"{X(sg * R * math.sin(math.radians(t))):.0f},{Z(pz - R * math.cos(math.radians(t))):.0f}" for t in range(0, 91, 5))
        s.append(f'<polyline class="arco" points="{pts}"/>')
    s.append(f'<rect class="panel" x="{X(0) - 22}" y="{Z(pc["z1"])}" width="44" height="{pc["z1"] - pc["z0"]}"/>')
    s.append(f'<line class="puerta" x1="{X(0)}" y1="{Z(pz)}" x2="{X(0)}" y2="{Z(bz)}"/>')
    s.append(f'<circle class="pivote" cx="{X(0)}" cy="{Z(pz)}" r="20"/>')
    s.append(f'<rect class="trinq" x="{X(0) + 22}" y="{Z(330)}" width="50" height="60"/>')
    # rótulos
    s.append(f'<text class="rot ac" x="{X(-60)}" y="{Z(700)}" text-anchor="end">puerta con</text>')
    s.append(f'<text class="rot ac" x="{X(-60)}" y="{Z(700) + 80}" text-anchor="end">panel ciego</text>')
    s.append(f'<text class="rot" x="{X(100)}" y="{Z(300) + 20}">2 trinquetes z 300</text>')
    s.append(f'<text class="rot" x="{X(do["x0"]) - 40}" y="{Z(1620)}" text-anchor="end">dosificador</text>')
    s.append(f'<text class="rot" x="{X(xm) - 60}" y="{Z(la["z"]) + 18}" text-anchor="end">línea Ø{la["diam"]}</text>')
    s.append(f'<text class="rot" x="{X(co["x0"]) - 40}" y="{Z(220)}" text-anchor="end">comedero</text>')
    s.append(f'<text class="rot" x="{X(1120)}" y="{Z(0) + 160}" text-anchor="middle">piso de slats</text>')
    # cotas
    s.append(cota_v(X(L) + 340, Z(H), Z(0), f"{mm(H)}", izq=False))
    s.append(cota_v(X(L) + 340, Z(la["z"]), Z(H), f"{mm(la['z'] - H)}", izq=False))
    s.append(f'<text class="ct" x="{X(L) + 370}" y="{Z(la["z"]) - 20}">{mm(la["z"])} al piso</text>')
    s.append(cota_v(X(0) - 560, Z(bz), Z(0), f"{bz}"))
    s.append(cota_h(X(0), X(L), Z(0) + 240, f"{mm(L)}", arriba=False))
    for z in M["largueros_z"]:
        s.append(f'<text class="ct ch" x="{X(1120)}" y="{Z(z) - 24}" text-anchor="middle">{mm(z)}</text>')
    s.append("</svg>")
    return "".join(s)


def main():
    global DESP
    DESP = D.despiece(M)
    (AQUI / "despiece.json").write_text(json.dumps(DESP, ensure_ascii=False, indent=1), encoding="utf-8")
    tpl = (AQUI / "plantilla.html").read_text(encoding="utf-8")
    out = (tpl.replace("{{PLANTA}}", planta())
              .replace("{{LATERAL}}", lateral())
              .replace("{{ESCENA}}", json.dumps(escena()))
              .replace("{{DESPIECE}}", D.html(DESP, M))
              .replace("{{EXT}}", mm(EXT))
              .replace("{{ESTADO}}", M.get("estado", "para validar")))
    (AQUI / "jaula.html").write_text(out, encoding="utf-8")
    print("ok", len(out), "bytes; ancho exterior", EXT)


if __name__ == "__main__":
    main()
