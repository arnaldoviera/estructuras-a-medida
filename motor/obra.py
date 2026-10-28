"""Obra: recomendaciones, herramientas, paso a paso (1 persona + ayuda puntual) y mantenimiento, desde ficha.json."""
import math
from comun import m, cm, num, catalogo_materiales, ag, LLAVE


def obra(ficha, M):
    d, D = ficha["diseno"], M["d"]
    tr, pa, ti, ca, va, ap, cu = d["travesano"], d["patas"], d["tirante"], d["cartela"], d["varillas"], d["apoyo"], d["cuelgues"]
    hol = va["holgura_agujero"]
    dens = catalogo_materiales()["maderas"][d["material"]]["densidad_kg_m3"]
    vol_A = (2 * math.pi * (pa["diametro"] / 2) ** 2 * pa["largo"] + math.pi * (ti["diametro"] / 2) ** 2 * ti["largo"]) / 1e9
    peso_A = vol_A * dens
    peso_T = math.pi * (tr["diametro"] / 2) ** 2 * tr["largo"] / 1e9 * dens
    tiene = (ficha["requisitos"].get("herramientas") or "").lower()
    herr = [
        ("taladro", f"Taladro con mecha larga de {ag(va['horqueta']['d'])} mm (≥ 45 cm para la horqueta)"),
        (f"{ag(va['cartela_inf']['d'])} mm", f"Mecha para madera de {ag(va['cartela_inf']['d'])} mm (varillas de las cartelas)"),
        ("serrucho", "Motosierra o serrucho de poda"),
        ("formón", "Formón para los rebajes"),
        ("maza", "Maza de carpintero"),
        ("llaves", f"Llaves fijas o de tubo para rosca en pulgadas: {LLAVE[va['horqueta']['d']]} y {LLAVE[va['cartela_inf']['d']]}" + (f", y {LLAVE[va['abrazadera']['d']]}" if va['abrazadera']['d'] in LLAVE else "")),
        ("nivel", "Nivel, plomada, cinta métrica, escuadra, tiza o lápiz de carpintero"),
        ("escalera", "Escalera de 2 m"),
        ("pala", "Pala de punta y pisón para los pozos"),
        ("caballete", "2 caballetes y sogas o cinchas para subir el travesaño"),
        ("pincel", "Pincel o rodillo; guantes, anteojos y protector auditivo"),
    ]
    herramientas = [t + ("" if k in tiene else " (a conseguir)") for k, t in herr]
    herramientas.append("Abrazaderas: encargarlas a una herrería (curvar la planchuela en medias cañas, perforar las orejas y galvanizar en frío). No incluidas en el presupuesto.")
    recomendaciones = [
        f"Elegir rollizos rectos, sin rajaduras pasantes, con el diámetro de proyecto como mínimo en la punta fina (travesaño Ø{cm(tr['diametro'])}, patas Ø{cm(pa['diametro'])}).",
        "Marcar y perforar con las piezas presentadas en el piso (las dos A armadas acostadas), no en el aire.",
        f"Todos los agujeros {hol} mm mayores que la varilla; todas las varillas con arandela ancha, tuerca y contratuerca.",
        "Pintar con Cetol los cortes, rebajes y agujeros antes de armar (son la entrada del agua).",
        "Usar el pórtico recién cuando estén todas las uniones ajustadas y los pozos compactados.",
    ]
    pasos = [
        ("Replanteo", "Desde el centro del pórtico (punto bajo el centro del travesaño), x a lo largo del travesaño hacia el césped e y en el sentido del vaivén. Las dos patas de cada A van corridas ±" + cm(pa['desfase_media_madera']) + " por la media madera: "
         + "; ".join(f"{n}: pie en x = {m(px_, 3)}, y = {m(py_, 3)} y centro del pozo en x = {m(cx_, 3)}, y = {m(cy_, 3)}" for n, px_, py_, cx_, cy_ in D['replanteo'])
         + f". El borde del pozo del lado del muro queda a {cm(D['pozo_al_muro'], 1)} del muro; si el cimiento del muro asoma, correr todo el pórtico unos cm hacia el césped. Verificar escuadra midiendo diagonales."),
        ("Pozos", f"Cavar 4 pozos de {cm(ap['pozo'][0])} (a lo largo del travesaño) × {cm(ap['pozo'][1])} (sentido del vaivén) × {cm(ap['pozo'][2])}, corridos hacia afuera del pie marcado: {cm(D['pozo_dx'], 1)} a lo largo del travesaño y {cm(D['pozo_dy'], 1)} en el vaivén. Apisonar ripio en el fondo y asentar {ap['base']} bien nivelados a {cm(pa['enterrado'])} de profundidad, centrados bajo el pie, con unos 5 cm de ripio apisonado entre los ladrillos y la pared exterior del pozo."),
        ("Preparar las patas", (f"Cortar las 4 patas con pie y punta horizontales y paralelos, {m(pa['largo'])} en todas las fibras (de rollizos de {m(pa['largo_comercial'], 1)}):" if pa.get("punta") == "horizontal" else f"Cortar las 4 patas a {m(pa['largo'])} con el pie horizontal:") + f" la pata forma {num(D['ang_real'], 1)}° con la vertical ({D['ang_lateral']:.0f}° vista de costado y {D['ang_frontal']:.0f}° vista de frente). Marcar SOBRE la pata, por el eje desde el centro del pie: cruce a {m(D['marca_cruce'])}, tirante a {m(D['marca_tirante'])}, horqueta a {m(D['marca_horqueta'])}. Pintar los últimos {cm(ap['proteccion_largo'])} con {ap['proteccion']}."),
        ("Armar cada A en el piso", f"Presentar las 2 patas cruzadas en la marca de {m(D['marca_cruce'])} (quedará a {m(D['apex'])} de altura). Marcar y tallar la media madera (1/3 del diámetro), perforar Ø{ag(va['cruce']['d'])} y colocar la varilla del cruce con arandela, tuerca y contratuerca."),
        ("Tirante", f"Presentar el tirante Ø{cm(ti['diametro'])} por la cara {ti['cara']} en la marca de {m(D['marca_tirante'])} (altura {m(ti['z'])}); queda apenas oblicuo ({num(D['tirante_oblicuo_grados'], 1)}°) porque las patas están desfasadas por la media madera. Rebajar {cm(ti['rebaje'], 1)} en tirante y pata, perforar Ø{ag(va['tirante']['d'])} y colocar las 2 varillas."),
        ("Asientos de la horqueta", f"Rebajar {cm(pa['asiento_horqueta'], 1)} en cada pata donde apoya el travesaño (arriba del cruce) y perforar Ø{ag(va['horqueta']['d'])} en la marca de {m(D['marca_horqueta'])}. Tallar un asiento plano para la arandela donde sale cada varilla."),
        ("Preparar el travesaño", f"En el piso, marcar a ±{m(M['axisX'](tr['z_eje']))} del centro (horquetas) y a ±{m(ca['x_sup'])} (cartelas), y tallar los planos de {cm(ca['rebaje'])} abajo para las cartelas. Los agujeros del travesaño se hacen ya colocado, usando como guía los de las patas."),
        ("Levantar las A (ayuda puntual)", f"Cada A pesa ≈ {num(peso_A, 0)} kg: pararla con la ayuda puntual de 2 personas (la misma visita que el travesaño), con el pie apoyado en el pozo y empujando desde la horqueta. Apuntalar con una tabla y verificar plomo."),
        ("Subir el travesaño (ayuda puntual)", f"Entre 3 personas, apoyar el travesaño ({m(tr['largo'])}, ≈ {num(peso_T, 0)} kg) en las dos horquetas. Con la mecha larga, perforar el travesaño a través de los agujeros de las patas, pasar la varilla de {va['horqueta']['d']} mm × {m(va['horqueta']['largo'])} pata–travesaño–pata en cada lado y ajustar."),
        ("Cartelas", f"Presentar cada cartela del centro del tirante a la cara inferior del travesaño, a {m(ca['x_sup'])} del centro. Rebajes de {cm(ca['rebaje'])} y varilla vertical de {va['cartela_inf']['d']} mm en cada punta, con asiento plano para la arandela."),
        ("Compactar los pozos", f"Rellenar con {ap['relleno']} en capas de 5 cm, apisonando cada capa. Verificar nivel del travesaño y plomo de las A."),
        ("Abrazaderas", f"Colocar las {len(D['hang'])} abrazaderas con su banda de goma en x = " + " / ".join(f"{m(abs(x))}" for x in sorted(set(abs(h) for h in D['hang']))) + f" del centro (a cada lado). Cerrar con las varillas de {va['abrazadera']['d']} mm y colgar grilletes."),
        ("Accesorios y prueba", "Colgar los accesorios, regular la altura (asientos a " + m(d['accesorios']['asiento_z']) + ") y hacer una prueba de carga gradual antes del primer uso. Reajustar todas las tuercas a la semana."),
    ]
    mantenimiento = [
        "Cada 3 meses: reajustar tuercas y contratuercas; revisar sogas, grilletes y desgaste de la goma de las abrazaderas.",
        "Cada año: lijar suave y dar una mano de Cetol; revisar el pie de las patas y el relleno de los pozos.",
        "Después de tormentas fuertes: verificar plomo de las A y que ningún pie se haya descalzado.",
        "Cambiar sogas o cadenas ante cualquier hilo cortado u óxido; nunca perforar el travesaño para colgar.",
    ]
    return {"herramientas": herramientas, "recomendaciones": recomendaciones, "pasos": pasos, "mantenimiento": mantenimiento,
            "personas": ficha["requisitos"].get("personas_armado")}
