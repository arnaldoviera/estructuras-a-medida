---
name: relevamiento
description: "Releva con el cliente los datos de una estructura a medida y los guarda en ficha.json, la única fuente de verdad del proyecto. También arma la ficha a partir de una foto de referencia (\"quiero una mesa como esta\"). Usar al iniciar una propuesta, cuando el usuario dicta datos de un cliente o una obra, manda una foto de un mueble o estructura, o cuando hay que corregir requisitos (espacio, cargas, uso, materiales)."
---

# Relevamiento → ficha.json

1. Datos comerciales: fecha, n° de propuesta (formato `EAM-AAAA-NNN`, correlativo dentro de `proyectos/`), validez en días, cliente, contacto, localidad, dirección de obra y zona de compras (solo en tipologías con presupuesto: define dónde se buscan los precios).
2. Requisitos por tipología: seguir `references/preguntas-por-tipologia.md`. Preguntar en tandas cortas (3 a 5 preguntas), en rioplatense. El usuario suele dictar por voz: interpretar con flexibilidad.
3. Escribir `ficha.json` según `references/ficha-schema.json`. Usar como plantilla el ejemplo de la tipología y reemplazar los valores: `${CLAUDE_PLUGIN_ROOT}/ejemplos/pueblo-andino/ficha.json` (pórtico de madera), `${CLAUDE_PLUGIN_ROOT}/ejemplos/jaula-cerdas/ficha.json` (jaula de hierro) o `${CLAUDE_PLUGIN_ROOT}/ejemplos/mesa-hierro-madera/ficha.json` (estructura libre: cualquier mueble o estructura simple como lista de piezas).
4. Bloque `diseno`: si el usuario no trae un diseño, proponer uno inicial a partir del caso de ejemplo adaptado al espacio, la carga o el animal, y marcarlo como propuesta a validar. En hierro, cada bloque lleva `_origen` que empieza con fuente, criterio o supuesto.
5. Foto de referencia: leer la imagen, describir lo que se ve y proponer la lista de piezas con medidas comerciales; preguntar solo las medidas y el uso que faltan (detalle en `references/preguntas-por-tipologia.md#estructura-libre`). Las medidas nunca se sacan de la foto.
6. Lo que el cliente no sabe o no definió va en `null` (nunca inventar). Al terminar, listar lo que quedó en null.

Reglas: un solo archivo. Si cambia un requisito, se edita la ficha y se vuelve a validar. En la ficha van datos, no razonamientos.
