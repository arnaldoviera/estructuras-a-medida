---
name: propuesta
description: "Orquestador de punta a punta del plugin multipropósito estructuras-a-medida (madera y hierro). Lleva un proyecto de estructura a medida — pórtico de hamacas en rollizos de madera, o box/jaula de alimentación para cerdas gestantes en tubo de hierro — desde el relevamiento con el cliente hasta la propuesta publicada como página web, pasando por validación, graficado, despiece, obra, compras con precios web (solo en tipologías con presupuesto) y auditoría independiente. Usar SIEMPRE que se pida una propuesta, presupuesto, despiece o cotización de una estructura de madera o hierro a medida (hamacas, pórtico, jaula, box, comedero para cerdas), o se invoque /estructuras-a-medida:propuesta."
---

# /estructuras-a-medida:propuesta — orquestador

Todo el proyecto vive en UNA carpeta con `ficha.json` como única fuente de verdad. Ninguna etapa inventa medidas: todas leen la ficha y escriben su salida al lado.

Motor: `python3 "${CLAUDE_PLUGIN_ROOT}/motor/correr.py" <comando> <carpeta>` (Python 3.10+, solo biblioteca estándar). Comandos: `validar`, `todo`, `propuesta`.

Tipologías (`catalogo/tipologias/<id>.json`, módulo en `motor/`):

| id | material | presupuesto | ejemplo |
|---|---|---|---|
| `portico-hamacas` | madera (rollizos + varilla roscada) | sí | `ejemplos/pueblo-andino` |
| `jaula-cerdas` | hierro (tubo estructural galvanizado + inox) | no: despiece y pedido sin precios | `ejemplos/jaula-cerdas` |

`presupuesto: false` en el catálogo de la tipología saltea la skill `compras` y la sección de presupuesto: la propuesta es técnica.

Idioma de todo lo que ve el cliente: español rioplatense, cotas en metros con coma decimal.

## Etapas (con checkpoint entre cada una)

1. **Relevamiento** → skill `relevamiento`. Crea la carpeta (por defecto `proyectos/<numero>-<cliente>/` en el directorio de trabajo) y `ficha.json`. Si la estructura pedida no es una tipología de la tabla, avisarlo (próximas: pérgolas y decks en madera; corrales, mangas y tranqueras en hierro) y frenar.
2. **Validación rápida, sin graficar** → skill `validacion`. Mostrar el resumen corto. El usuario corrige; se actualiza la ficha y se valida de nuevo hasta que el usuario apruebe explícitamente. Al aprobar: `estado.validacion_aprobada = true`.
3. **Corrida completa** (solo con la validación aprobada):
   - `correr.py todo <carpeta>`: graficado (skill `graficado`), despiece y pedido (skill `despiece`), obra (skill `obra`, solo pórtico).
   - Compras → skill `compras`, SOLO si la tipología lleva presupuesto: busca precios EN LA WEB en esta corrida y escribe `precios.json`. Nunca reutilizar precios de otra corrida ni del plugin. En `jaula-cerdas` se saltea.
   - `correr.py propuesta <carpeta>`: arma `salida/propuesta.html` (skill `propuesta-web`).
4. **Auditoría** → lanzar el agente `estructuras-a-medida:auditor` (agents/auditor.md) pasándole SOLO tres rutas: `ficha.json`, `salida/despiece.json` y `salida/propuesta.txt`, más la ruta donde escribir `auditoria.json`, la tipología y el número de vuelta (`estado.vueltas_auditoria` + 1). No pasarle este razonamiento ni la validación. El auditor anota la huella de la ficha (`ficha_sha256`); si después cambia la ficha, la propuesta marca la auditoría como desactualizada.
   - Si hay ítems "no cumple" o "dudoso": corregir la ficha (o el dato que corresponda), repetir el paso 3 y volver a auditar. Llevar la cuenta en `estado.vueltas_auditoria`.
   - Conflictos entre requisitos (ej. "más alto" contra "entra en el espacio"): NO resolverlos solo. Escalarlos al usuario con opciones y esperar su respuesta.
   - Límite: 4 vueltas. Si el problema persiste, detener y reportar qué falla. Más vueltas solo si el usuario lo pide expresamente.
   - La propuesta no se emite hasta 100 % "cumple", o hasta que el usuario acepte por escrito los conflictos escalados.
5. **Emitir**: `correr.py propuesta <carpeta>` (incorpora el informe como anexo) y publicar `salida/propuesta.html` como Artifact (página privada, compartible, se ve en el celular). Dar el enlace.

## Reglas
- Tipologías sin presupuesto (`jaula-cerdas`): ni precios ni totales; la página muestra despiece, plan de corte y pedido sin precios.
- Presupuesto SOLO de materiales, sin flete. Mano de obra en renglón aparte, no calculada. IVA configurable en `comercial.iva_pct` y `comercial.mostrar_con_iva` (qué total va resaltado; la página muestra sin IVA, IVA y con IVA).
- Datos que falten (cliente, garantía, plazo): preguntar o dejar en null. La página los muestra como "a completar". No rellenar con supuestos.
- Croquis 3D SIEMPRE armado; nunca vista desarmada.
- Texto para copiar/pegar, siempre en bloque de código.
