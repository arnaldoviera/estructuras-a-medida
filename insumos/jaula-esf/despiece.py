"""Despiece, plan de corte y pedido de la jaula desde medidas.json (sin precios).
Largos de corte entre caras (uniones a tope con boca de pescado), barras comerciales de 6 m, corte 3 mm."""
import json
import math
from pathlib import Path

BARRA = 6000
CORTE = 3


def kg_m(d, e):
    return math.pi * (d - e) * e * 7.85e-3


def despiece(M):
    T = M["tubos"]
    L, H = M["box"]["largo"], M["box"]["alto"]
    AL = M["box"]["ancho_libre"]
    dP, dS, dL, dB = T["parante"]["diam"], T["pasamanos"]["diam"], T["larguero"]["diam"], T["barrote"]["diam"]
    YC = (AL + dP) / 2
    PX = M["parantes_x"]
    pie_alto = 9.5 + M["pie"]["pletina"]["esp"]
    P = M["puerta"]
    luz_trav = round(2 * YC - dP)          # entre caras internas de parantes = ancho libre
    luz_lar = round(2 * (YC - dL / 2))     # entre caras internas de largueros
    vanos = [round(PX[i + 1] - PX[i] - dP) for i in range(len(PX) - 1)]

    piezas = []

    def pz(id_, pieza, cant, tubo, largo, sub, ops):
        t = T[tubo] if tubo else None
        piezas.append({"id": id_, "pieza": pieza, "cant": cant, "subconjunto": sub,
                       "material": t["nombre"] if t else None, "tubo": tubo,
                       "seccion": f"Ø{str(t['diam']).replace('.', ',')} × {str(t['esp']).replace('.', ',')}" if t else None,
                       "largo": largo, "operaciones": ops})

    def otra(id_, pieza, cant, material, medida, sub, ops):
        piezas.append({"id": id_, "pieza": pieza, "cant": cant, "subconjunto": sub, "material": material,
                       "tubo": None, "seccion": medida, "largo": None, "operaciones": ops})

    n_lat = 2
    # Laterales
    pz("L1", "Parante", n_lat * len(PX), "parante", round(H - pie_alto - dS / 2), "Lateral",
       "Pie a escuadra con tapa soldada; cabeza con boca de pescado Ø50,8 contra el pasamanos; venteo Ø10 cerca de cada punta, cara exterior")
    pz("L2", "Pasamanos", n_lat, "pasamanos", round(L + dP), "Lateral",
       "Puntas a escuadra con tapa soldada; 1 oreja para actuador a x 450 (solo en un lateral); venteos Ø10")
    for i, v in enumerate(vanos):
        pz(f"L3.{i + 1}", f"Larguero, vano {i + 1}", n_lat * len(M["largueros_z"]), "larguero", v, "Lateral",
           "Boca de pescado Ø50,8 en las dos puntas; a z " + " · ".join(str(z) for z in M["largueros_z"]) + "; venteo Ø10 por tramo, cara exterior")
    pz("L4", "Soporte de dosificador", n_lat, "larguero", round(M["dosificador"]["z1"] + 50 - H - dS / 2 - dL / 2), "Lateral",
       "Boca de pescado Ø50,8 abajo (sobre el pasamanos, en x 2.240) y Ø38,1 arriba (travesaño z 1.950)")
    # Frente
    for z, tubo, nom in ((100, "larguero", "Travesaño inferior frontal (apoyo comedero)"), (330, "larguero", "Travesaño frontal z 330"),
                         (700, "larguero", "Barra de cabeza z 700"), (H, "pasamanos", "Travesaño frontal superior")):
        pz(f"F{ {100: 1, 330: 2, 700: 3, H: 4}[z] }", nom, 1, tubo, luz_trav, "Frente",
           f"Boca de pescado Ø50,8 en las dos puntas; z {z}; se une a los parantes delanteros con planchuela y 2 M10")
    pz("F5", "Barrote frontal, tramo inferior", 4, "barrote", round(700 - 330 - dL), "Frente",
       "Entre travesaños z 330 y 700; boca de pescado Ø38,1 en las dos puntas; luz 90 mm entre barrotes")
    pz("F6", "Barrote frontal, tramo superior", 4, "barrote", round(H - 700 - dL / 2 - dS / 2), "Frente",
       "Entre barra z 700 y travesaño superior; boca de pescado Ø38,1 abajo y Ø50,8 arriba")
    pz("F7", "Travesaño del dosificador", 1, "larguero", round(2 * YC - dL), "Frente",
       "z 1.950; boca de pescado Ø38,1 en las dos puntas; 2 planchuelas para el dosificador")
    pz("F8", "Apoyo trasero del comedero", 1, "larguero", luz_lar, "Frente",
       "x 1.860, z 100; se cuelga del larguero z 150 de cada lateral con planchuela y 2 M10")
    otra("F9", "Zócalo frontal", 1, "Chapa galvanizada 2 mm", f"{AL} × 280", "Frente", "z 50 a 330; 6 agujeros Ø9 para abulonar a parantes y travesaños; cantos doblados o protegidos")
    # Trasero
    pz("R1", "Travesaño trasero superior", 1, "pasamanos", luz_trav, "Trasero",
       "z 1.130; boca de pescado Ø50,8; se une a los parantes traseros con planchuela y 2 M10")
    # Puerta
    alto_p = P["pivote_z"] - P["borde_inf_z"]
    pz("P1", "Lateral de puerta", 2, "puerta", alto_p, "Puerta", "Arriba: planchuela soldada con agujero Ø21 para el eje y pasador; abajo a escuadra")
    pz("P2", "Travesaño de puerta", 3, "puerta", round(P["ancho"] - T["puerta"]["diam"]), "Puerta",
       "z 250 · 400 · 950; boca de pescado Ø38,1 en las dos puntas")
    otra("P3", "Panel ciego", 1, "PEAD 10 mm", f"{round(P['ancho'] - T['puerta']['diam'])} × {P['panel_ciego']['z1'] - P['panel_ciego']['z0']}", "Puerta",
         "Abulonado a los travesaños z 400 y 950 con 6 M8 inox y arandelas grandes; cantos redondeados")
    otra("P4", "Eje de puerta", 1, "Barra redonda inox 304 maciza", f"Ø{P['eje']['diam']} × {luz_trav + 2 * 12}", "Puerta",
         "Entra 12 mm en cada buje; agujero transversal Ø6 para el pasador; leva soldada en un extremo")
    otra("P5", "Oreja del eje", 2, "Planchuela 2\" × ¼\" galvanizada", "50,8 × 6,35 × 100", "Trasero", "Soldada al parante trasero; agujero Ø30 para buje de PEAD")
    otra("P6", "Buje", 2, "PEAD", "Ø30 ext. × Ø20 int. × 15", "Trasero", "A presión en la oreja; aísla el eje inox del galvanizado")
    otra("P7", "Trinquete con tope", 2, "Planchuela 2\" × ¼\" galvanizada", "50,8 × 6,35 × 80 + tope 50,8 × 6,35 × 60", "Trasero",
         "A z 300, uno por lado; pivote con bulón M10 y tope de goma")
    otra("P8", "Varilla de mando", 2, "Barra redonda maciza galvanizada", f"Ø10 × {P['pivote_z'] - 20 - 330}", "Trasero",
         "Detrás del parante (x −45); ojal en cada punta; une la leva con el trinquete")
    otra("P9", "Guarda de la varilla", 2, "Chapa galvanizada 2 mm", f"100 × {P['pivote_z'] - 20 - 330}", "Trasero", "Doblada en U, abulonada al parante")
    otra("P10", "Resorte regulable y topes de goma", 1, "Juego", "1 resorte + 4 topes", "Puerta", "Topes en los parantes traseros y en el pasamanos (apertura 90°)")
    # Comedero, caída, antena
    co = M["comedero"]
    otra("C1", "Comedero", 1, "Inox 304", f"{co['x1'] - co['x0']} × {co['ancho']} × {co['z1'] - co['z0']}", "Frente",
         "Sin bordes filosos; 6 agujeros Ø9 para M8 inox con bujes de nylon")
    otra("C2", "Caída de alimento", 1, "Caño inox 304 Ø50 × 1,5", f"{M['caida']['z1'] - M['caida']['z0']}", "Frente",
         "Abrazadera inox con buje de nylon al travesaño frontal superior")
    otra("C3", "Separador de antena", 1, "PEAD", "60 × 56 × 30", "Lateral", "2 agujeros Ø9 al larguero z 740")
    # Pies
    n_pies = n_lat * len(PX)
    PL = M["pie"]["pletina"]
    otra("B1", "Placa base", n_pies, "Chapa 9,5 mm galvanizada", "150 × 150 × 9,5", "Lateral",
         "Concéntrica con la pletina; parante corrido 25 mm hacia adentro; 4 agujeros Ø11 a ±55; soldada al parante")
    otra("B2", "Cartela", 4 * n_pies, "Chapa 6 mm galvanizada", "60 × 60 × 6 (triángulo)", "Lateral", "4 por parante, en cruz")
    otra("B3", "Tapa de caño", n_pies + 2 * n_lat, "Chapa 3 mm galvanizada", "Ø50,8 × 3", "Lateral", "Pie de cada parante y puntas de pasamanos")
    otra("B4", "Pletina de apoyo", n_pies, "Inox 304 10 mm", f"{PL['largo']} × {PL['ancho']} × {PL['esp']}", "Pie",
         "Cantos chaflanados 2 × 45°, esquinas R15; 4 agujeros roscados o pasantes M10 a ±55; 2 colisos avellanados para M12 en y ±20 del centro")
    otra("B5", "Contrapletina", n_pies, "Inox 304 8 mm", "300 × 100 × 8", "Pie", "Abraza 2 vigas del slat; 2 colisos Ø13 en y ±20")
    otra("B6", "Junta aislante", n_pies, "Fenólico 3 mm", "160 × 160 × 3", "Pie", "Entre placa base y pletina; sobresale 5 mm de los cantos")
    otra("U1", "Planchuela de unión", 10, "Planchuela 2\" × ¼\" galvanizada", "50,8 × 6,35 × 80", "Uniones",
         "2 agujeros Ø11; une travesaños de frente y trasero (8) y apoyo del comedero (2)")
    otra("U2", "Planchuela del dosificador", 2, "Planchuela 2\" × ¼\" galvanizada", "50,8 × 6,35 × 120", "Frente", "2 agujeros Ø13 a 100 mm")
    otra("U3", "Oreja del actuador", 1, "Planchuela 2\" × ¼\" galvanizada", "50,8 × 6,35 × 80", "Lateral", "Agujero Ø13; previsión etapa 4")

    # Plan de corte por tipo de tubo (primer ajuste decreciente)
    cortes, clave = {}, {}
    for p in piezas:
        if p["tubo"]:
            t = T[p["tubo"]]
            k = clave.setdefault((t["diam"], t["esp"]), p["tubo"])  # mismo tubo, misma barra
            cortes.setdefault(k, []).extend([p["largo"]] * p["cant"])
    barras = {}
    for tubo, lst in cortes.items():
        bs = []
        for c in sorted(lst, reverse=True):
            for b in bs:
                if b["libre"] >= c + CORTE:
                    b["cortes"].append(c)
                    b["libre"] -= c + CORTE
                    break
            else:
                bs.append({"cortes": [c], "libre": BARRA - c - CORTE})
        barras[tubo] = bs

    # Pedido (sin precios)
    pedido = {"tubo": [], "chapa_y_planchuela": [], "inox": [], "bulones_y_aislacion": [], "otros": []}
    peso_tubo = 0
    for tubo, bs in barras.items():
        t = T[tubo]
        util = sum(sum(b["cortes"]) for b in bs)
        peso_tubo += util / 1000 * kg_m(t["diam"], t["esp"])
        pedido["tubo"].append({"id": f"tubo_{tubo}", "descripcion": t["nombre"] + ", barra de 6 m", "cant": len(bs), "unidad": "barra",
                               "uso_mm": util, "desperdicio_pct": round(100 * (1 - util / (len(bs) * BARRA)), 1)})
    pedido["chapa_y_planchuela"] += [
        {"id": "planch_2x14", "descripcion": "Planchuela 2\" × ¼\" (50,8 × 6,35)", "cant": 1, "unidad": "barra de 6 m",
         "uso": "orejas, trinquetes, uniones, dosificador, actuador (≈ 2,3 m)"},
        {"id": "chapa_95", "descripcion": "Chapa 9,5 mm, placas base 150 × 150", "cant": n_pies, "unidad": "u", "uso": "B1"},
        {"id": "chapa_6", "descripcion": "Chapa 6 mm, cartelas 60 × 60", "cant": 4 * n_pies, "unidad": "u", "uso": "B2"},
        {"id": "chapa_3", "descripcion": "Chapa 3 mm, tapas Ø50,8", "cant": n_pies + 2 * n_lat, "unidad": "u", "uso": "B3"},
        {"id": "chapa_2", "descripcion": f"Chapa galvanizada 2 mm: zócalo {AL} × 280 y 2 guardas 100 × {P['pivote_z'] - 350}", "cant": 1, "unidad": "juego", "uso": "F9, P9"},
        {"id": "barra_10", "descripcion": f"Barra redonda maciza Ø10, 2 × {P['pivote_z'] - 350} mm", "cant": 1, "unidad": "juego", "uso": "P8"},
    ]
    pedido["inox"] += [
        {"id": "inox_pletina", "descripcion": f"Pletina inox 304 {PL['largo']} × {PL['ancho']} × {PL['esp']}, corte láser", "cant": n_pies, "unidad": "u", "uso": "B4"},
        {"id": "inox_contra", "descripcion": "Contrapletina inox 304 300 × 100 × 8", "cant": n_pies, "unidad": "u", "uso": "B5"},
        {"id": "inox_eje", "descripcion": f"Barra inox 304 maciza Ø20 × {luz_trav + 24}", "cant": 1, "unidad": "u", "uso": "P4"},
        {"id": "inox_comedero", "descripcion": f"Comedero inox 304 {co['x1'] - co['x0']} × {co['ancho']} × {co['z1'] - co['z0']} (a medida)", "cant": 1, "unidad": "u", "uso": "C1"},
        {"id": "inox_caida", "descripcion": "Caño inox 304 Ø50 × 1,5 × 900 + abrazadera", "cant": 1, "unidad": "juego", "uso": "C2"},
    ]
    pedido["bulones_y_aislacion"] += [
        {"id": "m12_avell", "descripcion": "Bulón M12 × 140 inox, cabeza avellanada DIN 7991, con tuerca autofrenante y arandela", "cant": 4 * n_pies, "unidad": "u", "uso": "anclaje al slat (largo según espesor real del slat)"},
        {"id": "m10_inox_pie", "descripcion": "Bulón M10 × 40 inox con vaina y 2 arandelas aislantes", "cant": 4 * n_pies, "unidad": "juego", "uso": "pie (B1–B4)"},
        {"id": "fenolico", "descripcion": "Junta fenólica 160 × 160 × 3", "cant": n_pies, "unidad": "u", "uso": "B6"},
        {"id": "m10_galv", "descripcion": "Bulón M10 × 70 galvanizado con tuerca autofrenante y 2 arandelas", "cant": 22, "unidad": "u", "uso": "uniones de subconjuntos (20) y trinquetes (2)"},
        {"id": "m8_inox", "descripcion": "Bulón M8 inox con buje y arandelas de nylon", "cant": 12, "unidad": "juego", "uso": "comedero (6) y panel ciego (6)"},
        {"id": "m8_galv", "descripcion": "Bulón M8 galvanizado con arandela", "cant": 8, "unidad": "u", "uso": "zócalo (6) y separador de antena (2)"},
        {"id": "pasador", "descripcion": "Pasador elástico Ø6 galvanizado con vaina aislante", "cant": 2, "unidad": "u", "uso": "puerta–eje"},
    ]
    pedido["otros"] += [
        {"id": "pead_10", "descripcion": f"Placa PEAD 10 mm {round(P['ancho'] - T['puerta']['diam'])} × {P['panel_ciego']['z1'] - P['panel_ciego']['z0']}", "cant": 1, "unidad": "u", "uso": "P3"},
        {"id": "pead_buje", "descripcion": "Barra PEAD Ø30 para 2 bujes y separador de antena", "cant": 1, "unidad": "juego", "uso": "P6, C3"},
        {"id": "resorte", "descripcion": "Resorte de tracción regulable + 4 topes de goma", "cant": 1, "unidad": "juego", "uso": "P10"},
        {"id": "galvanizado", "descripcion": "Servicio de galvanizado por inmersión en caliente (subconjuntos ya soldados)", "cant": round(peso_tubo + 25), "unidad": "kg aprox.", "uso": "laterales, frente, trasero, puerta, chapas y planchuelas"},
    ]
    return {"piezas": piezas, "barras_corte": barras, "pedido": pedido,
            "barra_comercial_mm": BARRA, "corte_mm": CORTE, "peso_tubo_kg": round(peso_tubo, 1),
            "nota": "Largos entre caras para uniones a tope con boca de pescado; verificar en el plano de taller. Sin precios ni presupuesto."}


def mm(v):
    return f"{v:,.0f}".replace(",", ".")


def html(d, M):
    T = M["tubos"]
    filas = []
    sub_ant = None
    for p in d["piezas"]:
        if p["subconjunto"] != sub_ant:
            filas.append(f'<tr class="grupo"><th colspan="5">{p["subconjunto"]}</th></tr>')
            sub_ant = p["subconjunto"]
        medida = (f'{p["seccion"]} × {mm(p["largo"])}' if p["largo"] else p["seccion"])
        mat = p["material"] if not p["tubo"] else T[p["tubo"]]["nombre"].split(" (")[0]
        filas.append(f'<tr><td class="v">{p["id"]}</td><td>{p["pieza"]}</td><td class="v">{p["cant"]}</td>'
                     f'<td class="v">{medida}</td><td>{p["operaciones"]}<br><small>{mat}</small></td></tr>')
    corte = []
    for tubo, bs in d["barras_corte"].items():
        t = T[tubo]
        bars = []
        for i, b in enumerate(bs, 1):
            segs = "".join(f'<span class="seg" style="flex:{c}" title="{c}">{mm(c)}</span>' for c in b["cortes"])
            bars.append(f'<div class="barra"><b>{i}</b><div class="tira">{segs}<span class="sobra" style="flex:{max(b["libre"], 1)}">{mm(b["libre"])}</span></div></div>')
        corte.append(f'<div class="corte"><h3>{t["nombre"].split(" (")[0]} · {len(bs)} barras de 6 m</h3>{"".join(bars)}</div>')
    ped = []
    nombres = {"tubo": "Tubo estructural", "chapa_y_planchuela": "Chapa y planchuela", "inox": "Acero inoxidable 304",
               "bulones_y_aislacion": "Bulonería y aislación", "otros": "Otros"}
    for k, lst in d["pedido"].items():
        ped.append(f'<tr class="grupo"><th colspan="3">{nombres[k]}</th></tr>')
        for r in lst:
            extra = f' · desperdicio {str(r["desperdicio_pct"]).replace(".", ",")} %' if "desperdicio_pct" in r else ""
            ped.append(f'<tr><td>{r["descripcion"]}<br><small>{r["uso"] if "uso" in r else ""}{extra}</small></td>'
                       f'<td class="v">{r["cant"]}</td><td>{r["unidad"]}</td></tr>')
    return (f'<div class="tabla"><table class="desp"><thead><tr><th>Id</th><th>Pieza</th><th>Cant.</th><th>Medida (mm)</th><th>Operaciones</th></tr></thead>'
            f'<tbody>{"".join(filas)}</tbody></table></div>'
            f'<div class="cortes"><h3 class="sub">Plan de corte</h3><p class="hint">Barras de 6 m, 3 mm por corte. Gris: sobrante.</p>{"".join(corte)}</div>'
            f'<div class="tabla"><h3 class="sub">Pedido de materiales (sin precios)</h3><table><thead><tr><th>Material</th><th>Cant.</th><th>Unidad</th></tr></thead>'
            f'<tbody>{"".join(ped)}</tbody></table></div>')


if __name__ == "__main__":
    aqui = Path(__file__).parent
    M = json.loads((aqui / "medidas.json").read_text(encoding="utf-8"))
    d = despiece(M)
    (aqui / "despiece.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    for tubo, bs in d["barras_corte"].items():
        print(tubo, len(bs), "barras", [b["cortes"] for b in bs])
    print("peso tubo", d["peso_tubo_kg"])
