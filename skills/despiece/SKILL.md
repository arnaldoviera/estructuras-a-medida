---
name: despiece
description: "Despiece y pedido de materiales de una estructura a medida desde ficha.json — cada pieza con material, sección, largo, ángulos, rebajes y agujeros; madera por medida comercial; ferretería (varilla por barra con plan de corte, tuercas, contratuercas, arandelas, planchuela, goma, grilletes); terminación y apoyo; % de desperdicio. Usar en la corrida completa o cuando se pida la lista de materiales o de cortes."
---

# Despiece y pedido

Lo hace `correr.py todo <carpeta>` (`motor/portico.py → despiece`). Salidas:
- `salida/despiece.json`: `piezas` (id, pieza, cant, material, sección, largo, ángulos, rebajes, agujeros), `varillas_corte` (plan de corte por barra de 1 m, corte 3 mm), `pedido` y `desperdicio_madera_pct`.
- `salida/pedido.json`: el pedido agrupado en `madera`, `ferreteria` y `terminacion_apoyo`. Cada renglón tiene un `id` estable que usa la skill `compras` para el precio.

En `jaula-cerdas` (hierro): `salida/despiece.json` con `piezas` por subconjunto (lateral, frente, trasero, puerta, pie, uniones; id, cantidad, sección × largo de corte entre caras y operaciones: boca de pescado, venteos, agujeros), `barras_corte` agrupadas por sección (mismo tubo, misma barra; barra comercial y corte del catálogo), `pedido` (tubo, chapa y planchuela, inox, bulonería y aislación, otros, incluido el servicio de galvanizado en kg) y `peso` (total, galvanizado con 5 % de zinc, lateral). Sin precios.

Reglas:
- Hierro: tubo estructural redondo pedido por Ø exterior en pulgadas × espesor (`catalogo/materiales.json`); nunca medidas de cañería. Inox y galvanizado se unen abulonados con aislación, nunca soldados.
- Madera por largo comercial (`catalogo/materiales.json`): se busca el largo comercial más corto que contiene las piezas. Diámetro por rango comercial, exigiendo el de proyecto como mínimo en la punta fina.
- Varilla: barras de 1 m. Por cada tramo: 2 tuercas por punta (tuerca + contratuerca) y 1 arandela por punta (ancha de 50–60 mm en 12 y 16 mm).
- Presupuesto solo de materiales: ni flete ni mano de obra.
- Si cambia una medida, se cambia la ficha y se vuelve a correr; nunca se edita el despiece a mano.
