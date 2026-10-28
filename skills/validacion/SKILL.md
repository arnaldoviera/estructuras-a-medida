---
name: validacion
description: Validación rápida (sin graficar) de un diseño de estructura a medida a partir de ficha.json: normas de la tipología, que entre en el espacio, cargas, vuelco sin anclajes, flexión de la pieza principal, separaciones y ángulos. Devuelve un resumen corto para iterar con el usuario hasta aprobar. Usar después del relevamiento o cada vez que cambie la ficha.
---

# Validación rápida

```
python "${CLAUDE_PLUGIN_ROOT}/motor/correr.py" validar <carpeta>
```

Escribe `validacion.json` (todas las verificaciones con valor, límite y estado) e imprime el resumen.

Qué verifica (pórtico de hamacas; detalle en `references/`):
- Espacio: pies por fuera contra el largo disponible; zona libre de vaivén EN 1176-2 contra el largo de vaivén.
- Norma: separación entre asientos, asiento–pata, altura de asiento, caída del trapecio (`references/normas-hamacas.md`).
- Geometría: altura del cruce (tangencia del travesaño en la V), ángulos, largo de pata contra el rollizo comercial, voladizos, largo de cartela.
- Cálculo (`references/calculos.md`): flexión y flecha del travesaño en 3 casos, vuelco sin anclaje por configuración, pandeo de patas, largo de varillas.

Cómo responder al usuario: como mucho 6 líneas. Primero "X/Y cumplen". Después solo lo que no cumple o es dudoso, con el número y una corrección concreta. Las que cumplen justo (margen menor al 5 %) se nombran como "justo". No graficar en esta etapa.

Iterar: el usuario corrige, se edita `ficha.json` y se valida de nuevo. Cuando el usuario aprueba: `estado.validacion_aprobada = true`, `estado.aprobada_por` = quién y cuándo.
