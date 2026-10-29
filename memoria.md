# Memoria — estructuras-a-medida
> Reglas aprendidas de correcciones y decisiones. Una línea por entrada,
> con fecha. Compactar mensualmente.

## Preferencias y reglas de trabajo
- 2026-10-28 · Gráficos y textos en español rioplatense, cotas en metros con coma decimal; el croquis 3D va siempre armado, nunca desarmado.
- 2026-10-28 · Cotizar solo en Argentina, con MercadoLibre Argentina, tiendas argentinas en Tiendanube y tiendas online argentinas con precio publicado; nunca por WhatsApp, teléfono ni "consultar precio".
- 2026-10-28 · Presupuesto solo de materiales, sin flete; MOD en renglón aparte sin calcular; precios buscados en la web en cada corrida, nunca fijos.

## Decisiones tomadas
- 2026-10-28 · Marca provisoria "Estructuras a medida" y precios sin IVA con IVA configurable, hasta que el usuario defina nombre y criterio de IVA.
- 2026-10-28 · El croquis 3D se hace con Three.js dentro de la página (no con anatomy-reveal/Node, que no está instalado en esta máquina).
- 2026-10-28 · Caso Pueblo Andino tras la auditoría: patas enterradas 15 cm (rollizo de 3 m), hamaca-cama a 0,50 m, pozo 27 × 45 × 30 cm con 2 ladrillos centrado en el tramo enterrado, ayuda de 2 personas también para parar las A.
- 2026-10-28 · Pueblo Andino, por vuelco y punta de pata: base abierta a 2,60 m (semibase 1,30 m), tirante 1,23 m a 1,15 m, patas de rollizo de 3,5 m con pie y punta horizontales paralelos (2,95 m en todas las fibras).
- 2026-10-28 · Precios sin fuente publicada (ej. rollizo Ø16-18 × 3 m, arandelas anchas): no estimar; la propuesta muestra "total parcial" y se cotizan aparte.

- 2026-10-28 · Plugin multipropósito (madera y hierro): cada tipología es un módulo del motor con su ficha de catálogo; `presupuesto: false` saltea compras y presupuesto.
- 2026-10-28 · Tipología jaula-cerdas (hierro, tipo Gestal 3G): solo despiece y pedido, sin presupuesto. Decisiones del cliente: salida de culata, 1 cerda por box sin RFID y 15–18 con RFID, parantes cada ~750 mm, pie galvanizado + pletina inox aislada, 8 largueros y antena con separador de PEAD.

- 2026-10-29 · Norma de hamacas: EN 1176-2:2017 (4.2, 4.4.1, 4.10.2). Zona libre 0,867·L + 1,75 m (+0,5 m) al ras o + 2,25 m suelta; entre asientos +0,30 m y a la pata +0,20 m. La guía Playcentre NZ (1,50 m y sumandos invertidos) no se usa como fuente de esos valores. Pueblo Andino no cumple con la norma vigente y queda así hasta rediseñarlo.
- 2026-10-29 · Repo público con licencia MIT (autor Arnaldo Viera); sin insumos/ (notas de investigación con citas de terceros), sin enlaces privados en el paquete. Ejemplo del pórtico con rollizos «a cotizar».
- 2026-10-29 · v1.3.0: tipología «estructura libre» (ficha = secciones + barras con dos puntos + placas; desde una foto, las medidas las da el cliente). Sin presupuesto. Ejemplo: mesa de hierro y madera.
- 2026-10-29 · El plano de taller y los descuentos de cada unión los hace el herrero o carpintero, no el plugin: la propuesta llega a anteproyecto + despiece + pedido.

## Errores a no repetir
- 2026-10-29 · El motor tiene que compilar en Python 3.10: nada de barras invertidas ni comillas del mismo tipo dentro de las expresiones de una f-string (empaquetar.py lo revisa).
- 2026-10-28 · Hierro: pedir tubo estructural por Ø exterior en pulgadas × espesor; las medidas de cañería (Ø33,7, Ø42,4) no vienen en 2 mm.
- 2026-10-28 · Al corregir una pieza, revisar las vecinas en todas las vistas: varias correcciones de la jaula metieron errores nuevos (placa descentrada, barrotes sin barra intermedia, bulones que chocan).

## En curso (borrar al retomar)
