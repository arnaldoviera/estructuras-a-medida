# estructuras-a-medida
Facilita diseño y desarrollo de estructuras de madera y/o metálicas.

Plugin multipropósito de Claude (Claude Code / Cowork), para madera y hierro, que lleva una estructura a medida desde el relevamiento con el cliente hasta una **propuesta publicada como página web**. En el camino valida el diseño, lo grafica (perspectiva acotada, detalles de uniones, croquis 3D siempre armado), lo despieza, busca precios de referencia en la web y lo hace revisar por un auditor independiente.

Tipologías:

| Tipología | Material | Salida |
|---|---|---|
| `portico-hamacas` | madera: rollizos con varilla roscada | propuesta comercial con presupuesto de materiales |
| `jaula-cerdas` | hierro: tubo estructural galvanizado + inox | propuesta técnica con despiece, plan de corte y pedido **sin presupuesto** |

Próximas: pérgolas y decks en madera; corrales, mangas y tranqueras en hierro. Cada tipología es un módulo del motor (`modelo`, `validar`, `despiece`, `salidas`) más su ficha de catálogo (`material_base`, `presupuesto`, criterios).

Marca provisoria: "Estructuras a medida". Precios sin IVA, con IVA configurable (`comercial.iva_pct`). Presupuesto (solo en tipologías que lo llevan) solo de materiales, sin flete; mano de obra aparte.

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
ejemplos/pueblo-andino/      caso de prueba madera (ficha, precios, auditoría, salida)
ejemplos/jaula-cerdas/       caso de prueba hierro (ficha, auditoría, salida; sin precios)
insumos/portico-v3/          scripts y página originales (referencia)
```

## Caso de prueba

`ejemplos/pueblo-andino/`: pórtico para un área libre de 4,50 × 5,50 m, carga de diseño 350 kg (hamaca-cama) con factor dinámico 2,5, travesaño Ø20 × 3,70 m con el eje a 2,10 m, base de 2,60 m por A, patas Ø17 de rollizo de 3,5 m (2,95 m con pie y punta horizontales), cruce a 1,79 m, 6 abrazaderas de cuelgue. Las 32 verificaciones cumplen y la auditoría quedó aprobada en la vuelta 6 (31/31), después de que el cliente decidiera los conflictos escalados. Propuesta publicada: https://claude.ai/artifact/Pa5gp1Bd1KF7vUjEcj3QoX (privada).

Hierro — `ejemplos/jaula-cerdas/`: box de 2.240 × 560 libres × 1.130 mm tipo Gestal 3G, 4 parantes por lado en tubo 2" × 3,2, 8 largueros de 1½" × 2,0, puerta basculante con panel ciego y dos trinquetes que se arman y se liberan a 70°, pie galvanizado con pletina inox aislada y anclaje pasante al slat. 22/22 verificaciones; auditoría independiente en 5 vueltas (10/34 → 35/37, últimas correcciones aplicadas). Despiece: 38 tipos de pieza, 12 barras de 6 m, ≈ 211 kg. Medidas cruzadas con un cuaderno de NotebookLM de estaciones ESF y boxes tipo Gestal 3G.

## Notas técnicas

- El croquis 3D original usaba el kit "anatomy-reveal" (Node + Chrome headless). En el plugin se reemplazó por un visor Three.js r128 dentro de la página: no necesita Node y se gira con el dedo en el celular. Siempre armado.
- Empaquetado: `python empaquetar.py` genera `dist/estructuras-a-medida.plugin` (zip del directorio sin `insumos/`, `dist/` ni archivos de sesión).
- La propuesta usa un cálculo simplificado y no reemplaza el cálculo de un ingeniero matriculado.
