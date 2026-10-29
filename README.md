# estructuras-a-medida
Facilita diseño y desarrollo de estructuras de madera y/o metálicas.

Plugin multipropósito de Claude (Claude Code / Cowork), para madera y hierro, que lleva una estructura a medida desde el relevamiento con el cliente hasta una **propuesta publicada como página web**. En el camino valida el diseño, lo grafica (vistas acotadas, detalles y croquis 3D siempre armado), lo despieza, busca precios de referencia en la web cuando la tipología lleva presupuesto y lo hace revisar por un auditor independiente.

Tipologías:

| Tipología | Material | Salida |
|---|---|---|
| `portico-hamacas` | madera: rollizos con varilla roscada | propuesta comercial con presupuesto de materiales |
| `jaula-cerdas` | hierro: tubo estructural galvanizado + inox | propuesta técnica con despiece, plan de corte y pedido **sin presupuesto** |

Próximas: una tipología genérica de «estructura libre» (desde una foto o un pedido, para muebles y estructuras simples de madera y hierro); pérgolas y decks en madera; corrales, mangas y tranqueras en hierro. Cada tipología es un módulo del motor (`modelo`, `validar`, `despiece`, `salidas`) más su ficha de catálogo (`material_base`, `presupuesto`, criterios).

Marca provisoria: "Estructuras a medida". Precios sin IVA, con IVA configurable (`comercial.iva_pct`). Presupuesto (solo en tipologías que lo llevan) solo de materiales, sin flete; mano de obra aparte.

Uso interno. Licencia propietaria: todos los derechos reservados.

## Instalación y uso

Instalar el paquete `dist/estructuras-a-medida.plugin` (se arma con `python3 empaquetar.py`) en Claude Code o Cowork, o cargar el directorio con `claude --plugin-dir <ruta>`. Después:

```
/estructuras-a-medida:propuesta
```

El orquestador (`skills/propuesta`) recorre: relevamiento → validación rápida (iterar hasta aprobar) → corrida completa (graficado, despiece, obra, compras con precios web si la tipología lleva presupuesto, página) → auditoría con el agente `estructuras-a-medida:auditor` (corregir y re-auditar hasta 100 % o escalar conflictos; máximo 4 vueltas salvo que el usuario pida más) → publicación como Artifact.

Todo el proyecto vive en una carpeta con `ficha.json` como única fuente de verdad. El motor es Python 3.10+ con biblioteca estándar:

```
python3 motor/correr.py validar   ejemplos/pueblo-andino
python3 motor/correr.py todo      ejemplos/jaula-cerdas
python3 motor/correr.py propuesta ejemplos/pueblo-andino
```

Si la ficha está incompleta o mal cargada, el motor dice qué falta (por ejemplo «falta diseno.rfid») en lugar de cortar con un error de Python. Al terminar imprime la huella de la ficha: el auditor la anota en `auditoria.json` y, si la ficha cambia después, la propuesta marca la auditoría como desactualizada.

## Estructura

```
.claude-plugin/plugin.json
skills/propuesta/            orquestador
skills/relevamiento/         preguntas por tipología + esquema de ficha.json
skills/validacion/           normas (EN 1176-2:2017) y cálculos
skills/graficado/            vistas acotadas, detalles y croquis 3D
skills/despiece/             piezas, plan de corte y pedido
skills/obra/                 herramientas, paso a paso, mantenimiento (pórtico)
skills/compras/              precios web en cada corrida -> precios.json (solo con presupuesto)
skills/propuesta-web/        plantillas de la página (assets/)
agents/auditor.md            auditor independiente
motor/                       Python: geometría, validación, despiece, SVG, página
catalogo/                    tipologías y materiales (sin precios)
ejemplos/pueblo-andino/      caso de prueba madera (ficha, precios, auditoría, salida)
ejemplos/jaula-cerdas/       caso de prueba hierro (ficha, auditoría, salida; sin precios)
insumos/                     originales y bitácora de diseño (solo en el repositorio, no en el paquete)
```

## Casos de prueba

Madera — `ejemplos/pueblo-andino/`: pórtico para un área libre de 4,50 × 5,50 m sobre césped, carga de diseño 350 kg (hamaca-cama) con factor dinámico 2,5, travesaño Ø20 × 3,70 m con el eje a 2,10 m, base de 2,60 m por A, patas Ø17 de rollizo de 3,5 m, 6 abrazaderas de cuelgue. Se diseñó con los valores simplificados de la guía Playcentre NZ; con los de la EN 1176-2:2017 no entra en el vaivén disponible (pide 7,00 m) y le falta separación entre accesorios. Queda como caso real de verificaciones que no cumplen hasta rediseñarlo. Los rollizos figuran «a cotizar».

Hierro — `ejemplos/jaula-cerdas/`: box de 2.240 × 560 libres × 1.130 mm tipo Gestal 3G, 4 parantes por lado en tubo 2" × 3,2, 8 largueros de 1½" × 2,0, puerta basculante con panel ciego y dos trinquetes que se arman y se liberan a 70°, pie galvanizado con pletina inox aislada y anclaje pasante al slat. Despiece: 38 tipos de pieza, 12 barras de 6 m, ≈ 211 kg. Las verificaciones y la auditoría independiente están en `validacion.json` y `auditoria.json`.

## Notas técnicas

- El croquis 3D es un visor Three.js r128 dentro de la página: no necesita Node y se gira con el dedo en el celular. Siempre armado.
- Empaquetado: `python3 empaquetar.py` revisa que el motor compile en Python 3.10/3.11 (si están instalados) y genera `dist/estructuras-a-medida.plugin` (zip del directorio sin `insumos/`, `dist/` ni archivos de sesión).
- La propuesta usa un cálculo simplificado y no reemplaza el cálculo de un ingeniero matriculado.
