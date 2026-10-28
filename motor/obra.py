"""Obra: recomendaciones, herramientas, paso a paso (1 persona + ayuda puntual) y mantenimiento, desde ficha.json."""
from comun import m, cm


def obra(ficha, M):
    d, D = ficha["diseno"], M["d"]
    tr, pa, ti, ca, va, ap, cu = d["travesano"], d["patas"], d["tirante"], d["cartela"], d["varillas"], d["apoyo"], d["cuelgues"]
    hol = va["holgura_agujero"]
    herramientas = [
        f"Taladro con mechas largas de {va['horqueta']['d'] + hol} y {va['cartela_inf']['d'] + hol} mm (largo ≥ 45 cm para la horqueta)",
        "Motosierra o serrucho de poda, formón y maza para rebajes",
        f"Llaves fijas o de tubo de {va['horqueta']['d']} mm (24) y {va['cartela_inf']['d']} mm (19), y de 10 mm (17)",
        "Cinta métrica, nivel, plomada, escuadra, tiza o lápiz de carpintero",
        "Pala de punta y pisón para los pozos",
        "Escalera de 2 m, 2 caballetes y sogas o cinchas para subir el travesaño",
        "Pincel o rodillo; guantes, anteojos y protector auditivo",
    ]
    recomendaciones = [
        f"Elegir rollizos rectos, sin rajaduras pasantes, con el diámetro de proyecto como mínimo en la punta fina (travesaño Ø{cm(tr['diametro'])}, patas Ø{cm(pa['diametro'])}).",
        "Marcar y perforar con las piezas presentadas en el piso (las dos A armadas acostadas), no en el aire.",
        f"Todos los agujeros {hol} mm mayores que la varilla; todas las varillas con arandela ancha, tuerca y contratuerca.",
        "Pintar con Cetol los cortes, rebajes y agujeros antes de armar (son la entrada del agua).",
        "Usar el pórtico recién cuando estén todas las uniones ajustadas y los pozos compactados.",
    ]
    pasos = [
        ("Replanteo", f"Marcar en el terreno el área libre y los 4 pies: a ±{m(pa['pie_x'])} del centro a lo largo del travesaño y ±{m(pa['semibase'])} en el sentido del vaivén. Verificar escuadra midiendo diagonales."),
        ("Pozos", f"Cavar 4 pozos de {cm(ap['pozo'][0])} × {cm(ap['pozo'][1])} × {cm(ap['pozo'][2])}. Asentar en el fondo {ap['base']} bien nivelado."),
        ("Preparar las patas", f"Cortar las 4 patas a {m(pa['largo'])} con el pie horizontal (ángulo de {D['ang_lateral']:.0f}° respecto de la vertical). Pintar los últimos {cm(ap['proteccion_largo'])} con {ap['proteccion']}."),
        ("Armar cada A en el piso", f"Presentar las 2 patas cruzadas a {m(D['apex'])} del pie. Marcar y tallar la media madera (1/3 del diámetro), perforar Ø{va['cruce']['d'] + hol} y colocar la varilla del cruce con arandela, tuerca y contratuerca."),
        ("Tirante", f"Presentar el tirante Ø{cm(ti['diametro'])} por la cara {ti['cara']} a {m(ti['z'])} del pie. Rebajar {cm(ti['rebaje'], 1)} en tirante y pata, perforar Ø{va['tirante']['d'] + hol} y colocar las 2 varillas."),
        ("Asientos de la horqueta", f"Rebajar {cm(pa['asiento_horqueta'], 1)} en cada pata donde apoya el travesaño (arriba del cruce) y perforar Ø{va['horqueta']['d'] + hol} a la altura del eje."),
        ("Levantar las A", "Parar cada A dentro de sus pozos (una persona sola, apoyando el pie en el pozo y empujando desde la horqueta). Apuntalar provisoriamente con una tabla y verificar plomo."),
        ("Subir el travesaño (ayuda puntual)", f"Entre 3 personas, apoyar el travesaño ({m(tr['largo'])}) en las dos horquetas. Pasar la varilla de {va['horqueta']['d']} mm × {m(va['horqueta']['largo'])} pata–travesaño–pata en cada lado y ajustar."),
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
