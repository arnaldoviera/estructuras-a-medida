"""Arma la propuesta comercial como página única (Artifact HTML) desde ficha.json + salidas de cada etapa."""
import datetime, html, json, math, os
from comun import m, cm, num, pesos, leer_json, RAIZ

E = html.escape


def presupuesto(ficha, desp, precios):
    iva = ficha["comercial"]["iva_pct"] / 100
    idx = {p["id"]: p for p in (precios or {}).get("items", [])}
    filas, faltan, total = [], [], 0.0
    for grupo, titulo in (("madera", "Madera"), ("ferreteria", "Ferretería"), ("terminacion_apoyo", "Terminación y apoyo")):
        for it in desp["pedido"][grupo]:
            p = idx.get(it["id"])
            fila = {"grupo": titulo, "id": it["id"], "desc": it["descripcion"], "uso": it["uso"], "cant": it["cant"], "unidad": it["unidad"]}
            if p and p.get("precio") is not None:
                cont = p.get("contenido", 1) or 1
                bruto = it["cant"] / cont
                # por metro se compra lo justo (al décimo); por unidad o envase, se redondea para arriba
                cant_v = math.ceil(round(bruto * 10, 6)) / 10 if p.get("unidad") == "m" else math.ceil(round(bruto, 6))
                unit_sin = p["precio"] / (1 + iva) if p.get("iva_incluido", True) else p["precio"]
                sub = cant_v * unit_sin
                total += sub
                fila.update({"cant_venta": cant_v, "unidad_venta": p.get("unidad", it["unidad"]), "unit_sin": unit_sin, "sub_sin": sub,
                             "fuente": p.get("fuente"), "url": p.get("url"), "producto": p.get("descripcion"), "nota": p.get("nota", "")})
            else:
                faltan.append(it["id"])
            filas.append(fila)
    return {"filas": filas, "subtotal_sin_iva": total, "iva": total * iva, "total_con_iva": total * (1 + iva), "faltan": faltan,
            "fecha": (precios or {}).get("fecha_consulta"), "localidad": (precios or {}).get("localidad")}


def _dl(pares):
    return "<dl>" + "".join(f"<dt>{E(k)}</dt><dd>{v}</dd>" for k, v in pares) + "</dl>"


def _estado(e):
    cls = {"cumple": "ok", "no cumple": "bad", "dudoso": "warn"}.get(e, "warn")
    return f'<span class="st {cls}">{E(e)}</span>'


def pagina(ficha, M, val, desp, obra_, laminas, persp, escena, precios=None, auditoria=None):
    pr, cl, req, d, co = ficha["proyecto"], ficha["cliente"], ficha["requisitos"], ficha["diseno"], ficha["comercial"]
    D = M["d"]
    tr, pa, ti, ca, va, cu, ac = d["travesano"], d["patas"], d["tirante"], d["cartela"], d["varillas"], d["cuelgues"], d["accesorios"]
    pres = presupuesto(ficha, desp, precios)
    fecha = datetime.date.fromisoformat(pr["fecha"])
    vence = fecha + datetime.timedelta(days=pr["validez_dias"])
    f_ = lambda x: x.strftime("%d/%m/%Y")
    falta = '<span class="tbd">a completar</span>'
    val_ = lambda v: E(v) if v else falta

    # 1. datos
    s1 = _dl([("Propuesta", E(pr["numero"])), ("Fecha", f_(fecha)), ("Validez", f"{pr['validez_dias']} días (hasta el {f_(vence)})"),
              ("Cliente", val_(cl.get("nombre"))), ("Contacto", val_(cl.get("contacto"))),
              ("Obra", f"{val_(cl.get('direccion_obra'))} — {E(cl['localidad'])}, {E(cl['provincia'])}")])

    # 2. qué se propone
    cfgs = req["configuraciones"]
    tabs_p = "".join(f'<button type="button" aria-pressed="{str(i == 0).lower()}" data-cfg="{c["id"]}">{E(c["nombre"])}</button>' for i, c in enumerate(cfgs))
    persp_html = "".join(f'<div class="frame pl" data-persp="{c["id"]}"{"" if i == 0 else " hidden"}>{persp[c["id"]]}</div>' for i, c in enumerate(cfgs))
    s2 = (f'<p>{E(req["uso"])}</p>'
          f'<p>Estructura de rollizos de eucalipto impregnado con uniones de varilla roscada galvanizada: travesaño Ø{cm(tr["diametro"])} × {m(tr["largo"])} con el eje a {m(tr["z_eje"])}, '
          f'apoyado en la horqueta de dos A de patas Ø{cm(pa["diametro"])}. Apoyada en el terreno, sin hormigón. Entra en el espacio de {num(req["espacio"]["largo_eje_travesano_m"])} × {num(req["espacio"]["largo_vaiven_m"])} m.</p>'
          f'<div class="tabs" role="group" aria-label="Configuración">{tabs_p}</div>'
          f'<h3>Perspectiva acotada</h3>{persp_html}<p class="hint">Medidas en metros.</p>'
          f'<h3>Croquis 3D</h3><div class="viewer"><div id="v3d" role="img" aria-label="Croquis 3D del pórtico armado"></div></div>'
          f'<p class="hint">Arrastrá para girarlo, pellizcá o usá la rueda para acercar. Siempre se muestra armado.</p>')

    # 3. especificación
    hang_abs = sorted(set(abs(round(h)) for h in D["hang"]))
    esp = [
        ("Travesaño", f"Rollizo Ø{cm(tr['diametro'])} × {m(tr['largo'])}; eje a {m(tr['z_eje'])} (cara inferior a {m(D['cara_inf_travesano'])}). Apoya en la horqueta (V) de cada A, no atravesado entre patas"),
        ("Patas", f"{pa['cantidad']} rollizos Ø{cm(pa['diametro'])} × {m(pa['largo'])} (de rollizo de {m(pa['largo_comercial'], 0)}), {cm(pa['enterrado'])} enterrados; {D['ang_lateral']:.0f}° en la vista lateral y {D['ang_frontal']:.0f}° en la frontal"),
        ("Horqueta", f"Cruce a {m(D['apex'])} a media madera (rebaje 1/3 ≈ {cm(pa['diametro'] * pa['rebaje_cruce_frac'], 1)}); las patas siguen {cm(pa['prolongacion'])} sobre el cruce; varilla {va['horqueta']['d']} mm × {m(va['horqueta']['largo'])} pata–travesaño–pata"),
        ("Base", f"{m(D['base_A'])} por A en el sentido del vaivén; {m(D['pies_exterior'])} de pie a pie por fuera"),
        ("Tirantes", f"Rollizo Ø{cm(ti['diametro'])} × {m(ti['largo'])} por la cara {ti['cara']} de cada A a {m(ti['z'])}; rebaje {cm(ti['rebaje'], 1)} y varilla {va['tirante']['d']} mm"),
        ("Cartelas", f"Rollizo Ø{cm(ca['diametro'])} × {m(ca['largo'])}, del tirante al travesaño (a {m(ca['x_sup'])} del centro); varilla {va['cartela_inf']['d']} mm vertical en cada punta. Alternativa si se la ve débil: {E(ca['alternativa'].split(': ', 1)[-1])}"),
        ("Cuelgues", f"{len(D['hang'])} abrazaderas de planchuela {cu['abrazadera']['planchuela'].replace('x', ' × ')} mm con goma, sin perforar el travesaño, en x = ±" + " / ±".join(m(h) for h in hang_abs) + f"; pares a {m(cu['separacion_par'])}, puestos a {m(cu['puestos_x'][1] - cu['puestos_x'][0])}; punto de giro a {m(cu['z_giro'])}"),
        ("Accesorios", f"Asientos a {m(ac['asiento_z'])} ({ac['asiento_ancho']} mm de ancho); trapecio a {m(ac['trapecio_z'])}; {m(D['libre_asiento'])} libres entre patas a la altura del asiento"),
        ("Hamaca-cama", f"{num(ac['cama']['largo'] / 1000, 1)} × {num(ac['cama']['ancho'] / 1000, 1)} m a {m(ac['cama']['z'])}, de las 2 abrazaderas exteriores; solo para mecerse"),
        ("Varilla", f"Galvanizada, siempre con arandela ancha {d['arandela_ancha_mm']}-60 mm, tuerca y contratuerca; agujeros {va['holgura_agujero']} mm mayores que la varilla"),
        ("Carga de diseño", f"{req['carga_diseno_kg']} kg ({E(req['carga_diseno_desc'])}) con factor dinámico {num(req['factor_dinamico'], 1)}; peso de la madera ≈ {num(val['peso_total_kg'], 0)} kg ({num(val['peso_propio_kg'], 0)} kg sobre el terreno, usado en el vuelco)"),
        ("Terminación", E(req.get("terminacion", ""))),
    ]
    filas_v = "".join(f"<tr><td>{E(c['requisito'])}</td><td>{E(c['valor'])}</td><td>{E(c['limite'])}</td><td>{_estado(c['estado'])}</td></tr>" for c in val["checks"])
    s3 = (_dl(esp) + '<h3>Normas y verificaciones</h3><p>Separaciones y zona libre según EN 1176-2 (guía Playcentre NZ). '
          'Cálculo simplificado de flexión, flecha, pandeo y vuelco sin anclaje.</p>'
          f'<div class="tw"><table><thead><tr><th>Verificación</th><th>Valor</th><th>Límite</th><th>Estado</th></tr></thead><tbody>{filas_v}</tbody></table></div>')

    # 4. detalles
    s4 = '<div class="grid">' + "".join(f'<figure class="det"><figcaption><b>{E(t)}</b><span>{E(x)}</span></figcaption><div class="pl">{s}</div></figure>' for t, x, s in laminas) + "</div>"

    # 5. materiales con precios
    rows, g0 = [], None
    for f in pres["filas"]:
        if f["grupo"] != g0:
            rows.append(f'<tr class="grp"><td colspan="5">{E(f["grupo"])}</td></tr>'); g0 = f["grupo"]
        cant = num(f["cant"], 1 if isinstance(f["cant"], float) and f["cant"] % 1 else 0) + " " + E(f["unidad"])
        if "sub_sin" in f:
            fuente = f'<a href="{E(f["url"])}" target="_blank" rel="noopener">{E(f["fuente"])}</a>' if f.get("url") else E(f.get("fuente") or "")
            venta = f'{num(f["cant_venta"], 1 if f["cant_venta"] % 1 else 0)} × {E(f["unidad_venta"])}' if f["unidad_venta"] != f["unidad"] or f["cant_venta"] != f["cant"] else ""
            rows.append(f'<tr><td><b>{E(f["desc"])}</b><small>{E(f["uso"])}</small></td><td class="n">{cant}{"<small>" + venta + "</small>" if venta else ""}</td>'
                        f'<td class="n">{pesos(f["unit_sin"])}</td><td class="n">{pesos(f["sub_sin"])}</td><td><small>{fuente}{" · " + E(f["nota"]) if f.get("nota") else ""}</small></td></tr>')
        else:
            rows.append(f'<tr><td><b>{E(f["desc"])}</b><small>{E(f["uso"])}</small></td><td class="n">{cant}</td><td class="n" colspan="2"><span class="tbd">sin precio de referencia</span></td><td></td></tr>')
    s5 = (f'<p>Precios de referencia buscados en la web el {E(pres["fecha"] or "—")} ({E(pres["localidad"] or "")}), sin IVA, sin flete. Son orientativos: se confirman al comprar.</p>'
          f'<div class="tw"><table class="mat"><thead><tr><th>Material</th><th>Cantidad</th><th>Unitario s/IVA</th><th>Subtotal s/IVA</th><th>Fuente</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
          f'<p class="hint">Desperdicio de madera estimado: {num(desp["desperdicio_madera_pct"], 0)} % (largos comerciales vs. piezas).</p>')

    # 6. instalación
    pasos = "".join(f"<li><b>{E(t)}.</b> {E(x)}</li>" for t, x in obra_["pasos"])
    s6 = (f'<p>Armado pensado para {E((obra_["personas"] or "1 persona con ayuda puntual").rstrip("."))}.</p>'
          '<h3>Recomendaciones</h3><ul>' + "".join(f"<li>{E(x)}</li>" for x in obra_["recomendaciones"]) + "</ul>"
          f'<h3>Paso a paso</h3><ol class="steps">{pasos}</ol>'
          f'<p class="note">Mano de obra (MOD): {E(co["mod"]["texto"])}</p>')

    # 7. presupuesto
    iva = co["iva_pct"]
    con = co["mostrar_con_iva"]
    s7 = ('<div class="tw"><table class="tot"><tbody>'
          f'<tr{" class=\"hl\"" if not con else ""}><td>Materiales sin IVA (sin flete)</td><td class="n">{pesos(pres["subtotal_sin_iva"])}</td></tr>'
          f'<tr><td>IVA {iva} %</td><td class="n">{pesos(pres["iva"])}</td></tr>'
          f'<tr{" class=\"hl\"" if con else ""}><td>Materiales con IVA</td><td class="n">{pesos(pres["total_con_iva"])}</td></tr>'
          f'<tr><td>Mano de obra de armado</td><td class="n">{"Incluida" if co["mod"]["incluida"] else "Se cotiza aparte"}</td></tr>'
          '</tbody></table></div>'
          + (f'<p class="note">Total parcial: sin precio de referencia publicado para {E(", ".join(pres["faltan"]))}. No se suman; se cotizan aparte.</p>' if pres["faltan"] else ""))

    # 8. condiciones
    s8 = _dl([
        ("Validez", f"{pr['validez_dias']} días desde la fecha de la propuesta; los precios de materiales son de referencia y pueden cambiar."),
        ("Plazo", val_(co.get("plazo_entrega"))),
        ("Incluye", "Diseño, verificación, planos de detalle, despiece, pedido de materiales con precios de referencia e instructivo de armado."),
        ("No incluye", "Flete, mano de obra de armado (se cotiza aparte), trabajo de herrería de las abrazaderas (curvado, perforado y galvanizado en frío), accesorios (asientos, sogas, trapecio, cama) salvo que se indique, permisos." + ("" if not co.get("incluye_flete") else "")),
        ("Garantía", val_(co.get("garantia"))),
        ("Mantenimiento", "<ul>" + "".join(f"<li>{E(x)}</li>" for x in obra_["mantenimiento"]) + "</ul>"),
        ("Importante", "Esta propuesta usa un cálculo simplificado y no reemplaza el cálculo de un ingeniero matriculado."),
    ])

    # 9. anexo autoconstrucción
    s9 = ""
    if co.get("anexo_autoconstruccion"):
        dp = "".join(f"<tr><td>{E(p['id'])}</td><td><b>{E(p['pieza'])}</b> ×{p['cant']}<small>{E(p['material'])}</small></td><td>{E(p['seccion'])} × {m(p['largo'])}</td>"
                     f"<td><small><b>Ángulos:</b> {E(p['angulos'])}<br><b>Rebajes:</b> {E(p['rebajes'])}<br><b>Agujeros:</b> {E(p['agujeros'])}</small></td></tr>" for p in desp["piezas"])
        cortes = "".join(f"<li>Varilla {k} mm: " + "; ".join(" + ".join(m(c) for c in b["cortes"]) for b in v) + "</li>" for k, v in desp["varillas_corte"].items())
        s9 = ('<details open><summary>Anexo · Autoconstrucción</summary>'
              '<h3>Herramientas</h3><ul>' + "".join(f"<li>{E(x)}</li>" for x in obra_["herramientas"]) + "</ul>"
              f'<h3>Despiece</h3><div class="tw"><table><thead><tr><th>Id</th><th>Pieza</th><th>Medida</th><th>Trabajo</th></tr></thead><tbody>{dp}</tbody></table></div>'
              f'<h3>Corte de varillas (barras de 1 m)</h3><ul>{cortes}</ul></details>')

    # 10. auditoría
    if auditoria:
        it = "".join(f"<tr><td>{E(a['requisito'])}<small>{E(a.get('tipo', ''))}</small></td><td>{_estado(a['estado'])}</td><td><small>{E(a.get('evidencia', ''))}</small></td><td><small>{E(a.get('correccion', '') or '—')}</small></td></tr>" for a in auditoria["items"])
        ok = sum(a["estado"] == "cumple" for a in auditoria["items"])
        conf = "".join(f"<li>{E(c)}</li>" for c in auditoria.get("conflictos", []))
        s10 = (f'<details><summary>Anexo · Informe de auditoría ({ok}/{len(auditoria["items"])} cumple · {auditoria["vueltas"]} vuelta{"s" if auditoria["vueltas"] != 1 else ""})</summary>'
               f'<p>Auditor independiente: recibió solo la ficha, el despiece y la propuesta, y recalculó cargas, vuelco, flexión, zonas libres y cantidades por su cuenta. Estado: <b>{E(auditoria["estado"])}</b> ({E(auditoria.get("fecha", ""))}).</p>'
               + (f"<h3>Conflictos escalados</h3><ul>{conf}</ul>" if conf else "")
               + f'<div class="tw"><table><thead><tr><th>Requisito</th><th>Estado</th><th>Evidencia</th><th>Corrección</th></tr></thead><tbody>{it}</tbody></table></div></details>')
    else:
        s10 = '<details><summary>Anexo · Informe de auditoría</summary><p class="tbd">Pendiente.</p></details>'

    secciones = [("Datos del proyecto", s1), ("Qué se propone", s2), ("Especificación técnica y normas", s3), ("Detalles constructivos", s4),
                 ("Materiales con precios", s5), ("Instalación", s6), ("Presupuesto", s7), ("Condiciones", s8)]
    cuerpo = "".join(f'<section id="s{i}"><h2><span class="num">{i}</span>{E(t)}</h2>{c}</section>' for i, (t, c) in enumerate(secciones, 1))
    cuerpo += f'<section class="anx">{s9}{s10}</section>'

    plantilla = open(os.path.join(RAIZ, "skills", "propuesta-web", "assets", "plantilla.html"), encoding="utf-8").read()
    return (plantilla.replace("{{TITULO}}", E(f"{pr['titulo']} · {pr['numero']}"))
            .replace("{{MARCA}}", E(pr["marca"]))
            .replace("{{H1}}", E(pr["titulo"]))
            .replace("{{SUB}}", E(f"Propuesta {pr['numero']} · {cl['localidad']}, {cl['provincia']} · {f_(fecha)}"))
            .replace("{{CUERPO}}", cuerpo)
            .replace("{{ESCENA}}", json.dumps(escena, ensure_ascii=False, separators=(",", ":"))))
