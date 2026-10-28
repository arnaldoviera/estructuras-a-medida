# estructuras-a-medida
Facilita diseño y desarrollo de estructuras de madera y/o metálicas.

Plugin de Claude (Claude Code / Cowork) que lleva una estructura a medida desde el relevamiento con el cliente hasta una **propuesta comercial publicada como página web**. En el camino valida el diseño, lo grafica (perspectiva acotada, detalles de uniones, croquis 3D siempre armado), lo despieza, busca precios de referencia en la web y lo hace revisar por un auditor independiente.

- **v1 (esta):** pórtico de hamacas en rollizos de madera con varilla roscada.
- v2: pérgolas y decks en madera. v3: metal (caño estructural y perfiles; uniones soldadas y abulonadas).

Marca provisoria: "Estructuras a medida". Precios sin IVA, con IVA configurable (`comercial.iva_pct`). Presupuesto solo de materiales, sin flete; mano de obra aparte.

## Uso

```
/propuesta
```

El orquestador (`skills/propuesta`) recorre: relevamiento → validación rápida (iterar hasta aprobar) → corrida completa (graficado, despiece, obra, compras con precios web, página) → auditoría (corregir y re-auditar hasta 100 % o escalar conflictos; máximo 4 vueltas) → publicación como Artifact.

Todo el proyecto vive en una carpeta con `ficha.json` como única fuente de verdad. El motor es Python 3.10+ con biblioteca estándar:

```
python motor/correr.py validar   ejemplos/pueblo-andino
python motor/correr.py todo      ejemplos/pueblo-andino
python motor/correr.py propuesta ejemplos/pueblo-andino
```

## Estructura

```
.claude-plugin/plugin.json
skills/propuesta/            orquestador /propuesta
skills/relevamiento/         preguntas por tipología + esquema de ficha.json
skills/validacion/           normas (EN 1176-2 vía Playcentre) y cálculos
skills/graficado/            perspectiva, detalles y croquis 3D
skills/despiece/             piezas, plan de corte y pedido
skills/obra/                 herramientas, paso a paso, mantenimiento
skills/compras/              precios web en cada corrida -> precios.json
skills/propuesta-web/        plantilla de la página (assets/plantilla.html)
agents/auditor.md            auditor independiente
motor/                       Python: geometría, validación, despiece, SVG, página
catalogo/                    tipologías y materiales (sin precios)
ejemplos/pueblo-andino/      caso de prueba v1 (ficha, precios, auditoría, salida)
insumos/portico-v3/          scripts y página originales (referencia)
```

## Caso de prueba

`ejemplos/pueblo-andino/`: pórtico para un área libre de 4,50 × 5,50 m, carga de diseño 350 kg (hamaca-cama) con factor dinámico 2,5, travesaño Ø20 × 3,70 m con el eje a 2,10 m, patas Ø17 a 33° / 14°, cruce a 1,76 m, 6 abrazaderas de cuelgue. Las 25 verificaciones cumplen; la zona libre (2,75 m por lado) entra justo.

## Notas técnicas

- El croquis 3D original usaba el kit "anatomy-reveal" (Node + Chrome headless). En el plugin se reemplazó por un visor Three.js r128 dentro de la página: no necesita Node y se gira con el dedo en el celular. Siempre armado.
- Empaquetado: `python empaquetar.py` genera `dist/estructuras-a-medida.plugin` (zip del directorio sin `insumos/`, `dist/` ni archivos de sesión).
- La propuesta usa un cálculo simplificado y no reemplaza el cálculo de un ingeniero matriculado.
