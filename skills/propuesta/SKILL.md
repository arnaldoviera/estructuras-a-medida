---
name: propuesta
description: Orquestador de punta a punta del plugin estructuras-a-medida. Lleva un proyecto de estructura a medida (v1 pórtico de hamacas en rollizos de madera con varilla roscada) desde el relevamiento con el cliente hasta la propuesta comercial publicada como página web, pasando por validación, graficado, despiece, obra, compras con precios web y auditoría independiente. Usar SIEMPRE que se pida una propuesta, presupuesto o cotización de una estructura de madera o metal a medida (hamacas, pórtico, pérgola, deck), o se invoque /propuesta.
---

# /propuesta — orquestador

Todo el proyecto vive en UNA carpeta con `ficha.json` como única fuente de verdad. Ninguna etapa inventa medidas: todas leen la ficha y escriben su salida al lado.

Motor: `python "${CLAUDE_PLUGIN_ROOT}/motor/correr.py" <comando> <carpeta>` (Python 3.10+, solo biblioteca estándar). Comandos: `validar`, `todo`, `propuesta`.

Idioma de todo lo que ve el cliente: español rioplatense, cotas en metros con coma decimal.

## Etapas (con checkpoint entre cada una)

1. **Relevamiento** → skill `relevamiento`. Crea la carpeta (por defecto `proyectos/<numero>-<cliente>/` en el directorio de trabajo) y `ficha.json`. Si la tipología no es `portico-hamacas`, avisar que v1 solo cubre esa (v2: pérgolas y decks; v3: metal) y frenar.
2. **Validación rápida, sin graficar** → skill `validacion`. Mostrar el resumen corto. El usuario corrige; se actualiza la ficha y se valida de nuevo hasta que el usuario apruebe explícitamente. Al aprobar: `estado.validacion_aprobada = true`.
3. **Corrida completa** (solo con la validación aprobada):
   - `correr.py todo <carpeta>`: graficado (skill `graficado`), despiece y pedido (skill `despiece`), obra (skill `obra`).
   - Compras → skill `compras`: busca precios EN LA WEB en esta corrida y escribe `precios.json`. Nunca reutilizar precios de otra corrida ni del plugin.
   - `correr.py propuesta <carpeta>`: arma `salida/propuesta.html` (skill `propuesta-web`).
4. **Auditoría** → lanzar el agente `auditor` (agents/auditor.md) pasándole SOLO tres rutas: `ficha.json`, `salida/despiece.json` y `salida/propuesta.txt`, más la ruta donde escribir `auditoria.json`. No pasarle este razonamiento ni la validación.
   - Si hay ítems "no cumple" o "dudoso": corregir la ficha (o el dato que corresponda), repetir el paso 3 y volver a auditar. Llevar la cuenta en `estado.vueltas_auditoria`.
   - Conflictos entre requisitos (ej. "más alto" contra "entra en el espacio"): NO resolverlos solo. Escalarlos al usuario con opciones y esperar su respuesta.
   - Límite: 4 vueltas. Si el problema persiste, detener y reportar qué falla.
   - La propuesta no se emite hasta 100 % "cumple", o hasta que el usuario acepte por escrito los conflictos escalados.
5. **Emitir**: `correr.py propuesta <carpeta>` (incorpora el informe como anexo) y publicar `salida/propuesta.html` como Artifact (página privada, compartible, se ve en el celular). Dar el enlace.

## Reglas
- Presupuesto SOLO de materiales, sin flete. Mano de obra en renglón aparte, no calculada. IVA configurable en `comercial.iva_pct` y `comercial.mostrar_con_iva`; la página trae botón con/sin IVA.
- Datos que falten (cliente, garantía, plazo): preguntar o dejar en null. La página los muestra como "a completar". No rellenar con supuestos.
- Croquis 3D SIEMPRE armado; nunca vista desarmada.
- Texto para copiar/pegar, siempre en bloque de código.
