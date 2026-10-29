---
name: validacion
description: "Validación rápida (sin graficar) de un diseño de estructura a medida a partir de ficha.json: normas de la tipología, que entre en el espacio, cargas, vuelco sin anclajes, flexión de la pieza principal, separaciones y ángulos. Devuelve un resumen corto para iterar con el usuario hasta aprobar. Usar después del relevamiento o cada vez que cambie la ficha."
---

# Validación rápida

```
python3 "${CLAUDE_PLUGIN_ROOT}/motor/correr.py" validar <carpeta>
```

Escribe `validacion.json` (todas las verificaciones con valor, límite y estado) e imprime el resumen.

Qué verifica en `jaula-cerdas` (`motor/jaula_cerdas.py`; criterios con su origen en `catalogo/tipologias/jaula-cerdas.json`):
- Bienestar: ancho libre 520–600, largo útil ≥ 2.100, luces entre largueros y barrotes ≤ 100 mm, holgura puerta–parante fuera de 8–25 mm (pellizco), panel ciego a la altura de la vulva.
- Mecánica: puerta a 90° sobre el lomo (≥ 980 mm), lugar para el eje, reacción en los trinquetes.
- Resistencia (cálculo simplificado, fy 235 MPa, FS ≥ 1,15): larguero, barrote, travesaño de puerta y pasamanos con 1,5 kN a media luz; parante en la base con 0,9 kN·m; travesaño del dosificador.
- Montaje y fabricación: invasión del pie ≤ 30 mm, pletina sobre 2 vigas de slat, bulones del pie sin choque, antena ≥ 50 mm del metal, línea de alimento, tubos comerciales, peso del lateral ≤ 80 kg.

Qué verifica en `estructura-libre` (`motor/estructura_libre.py`; criterios en `catalogo/tipologias/estructura-libre.json`, cálculo simplificado):
- Medidas totales contra las pedidas, secciones comerciales, largos que salen de una barra o tirante, placas que salen de una hoja.
- Placas: flexión entre apoyos y en el voladizo, y flecha L/300 (carga distribuida, puntual en franja de 300 mm, carga en el borde).
- Vigas: flexión y flecha con su ancho de influencia o con la carga puntual en el medio (acero: fy/1,1 con carga × 1,5; madera: tensión admisible con carga de uso).
- Patas: pandeo (Euler con longitud efectiva 2L, FS ≥ 2), corrimiento arriba con el empuje lateral (≤ alto/150) y tensión en el nudo con el bastidor.
- Vuelco con carga en el borde de la tapa (y empuje arriba en estantes), FS ≥ 1,5; peso de la pieza más pesada; protección del hierro si va afuera.

Qué verifica en `portico-hamacas` (detalle en `references/`):
- Espacio: pies por fuera contra el largo disponible; zona libre de vaivén EN 1176-2 contra el largo de vaivén.
- Norma: separación entre asientos, asiento–pata, altura de asiento, caída del trapecio (`references/normas-hamacas.md`).
- Geometría: altura del cruce (tangencia del travesaño en la V), ángulos, largo de pata contra el rollizo comercial, voladizos, largo de cartela.
- Cálculo (`references/calculos.md`): flexión y flecha del travesaño en 3 casos, vuelco sin anclaje por configuración, pandeo de patas, largo de varillas.

Cómo responder al usuario: como mucho 6 líneas. Primero "X/Y cumplen". Después solo lo que no cumple o es dudoso, con el número y una corrección concreta. Las que cumplen justo (margen menor al 5 %) se nombran como "justo". No graficar en esta etapa.

Iterar: el usuario corrige, se edita `ficha.json` y se valida de nuevo. Cuando el usuario aprueba: `estado.validacion_aprobada = true`, `estado.aprobada_por` = quién y cuándo.
