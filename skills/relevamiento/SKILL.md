---
name: relevamiento
description: Releva con el cliente los datos de una estructura a medida y los guarda en ficha.json, la única fuente de verdad del proyecto. Usar al iniciar una propuesta, cuando el usuario dicta datos de un cliente o una obra, o cuando hay que corregir requisitos (espacio, cargas, uso, materiales).
---

# Relevamiento → ficha.json

1. Datos comerciales: fecha, n° de propuesta (formato `EAM-AAAA-NNN`, correlativo dentro de `proyectos/`), validez en días, cliente, contacto, localidad, dirección de obra y zona de compras (define dónde se buscan los precios).
2. Requisitos por tipología: seguir `references/preguntas-por-tipologia.md`. Preguntar en tandas cortas (3 a 5 preguntas), en rioplatense. El usuario suele dictar por voz: interpretar con flexibilidad.
3. Escribir `ficha.json` según `references/ficha-schema.json`. Usar como plantilla el ejemplo de la tipología y reemplazar los valores: `${CLAUDE_PLUGIN_ROOT}/ejemplos/pueblo-andino/ficha.json` (pórtico de madera) o `${CLAUDE_PLUGIN_ROOT}/ejemplos/jaula-cerdas/ficha.json` (jaula de hierro).
4. Bloque `diseno`: si el usuario no trae un diseño, proponer uno inicial a partir del caso de ejemplo adaptado al espacio, la carga o el animal, y marcarlo como propuesta a validar. En hierro, cada bloque lleva `_origen` que empieza con fuente, criterio o supuesto.
5. Lo que el cliente no sabe o no definió va en `null` (nunca inventar). Al terminar, listar lo que quedó en null.

Reglas: un solo archivo. Si cambia un requisito, se edita la ficha y se vuelve a validar. En la ficha van datos, no razonamientos.
