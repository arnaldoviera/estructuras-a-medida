---
name: compras
description: "Solo para tipologías con presupuesto (hoy, pórtico de hamacas en madera). Busca en la web, en cada corrida, productos sugeridos y precios de referencia en Argentina (según la localidad de la obra) para cada renglón del pedido de materiales, con fuente, URL y fecha, y escribe precios.json. Nunca usa precios fijos. Usar en la corrida completa o cuando se pida actualizar precios de una propuesta."
---

# Compras → precios.json

Solo para tipologías con `presupuesto: true` en `catalogo/tipologias/<id>.json` (hoy, `portico-hamacas`). En `jaula-cerdas` no se buscan precios: el motor ignora `precios.json`.

Entrada: `salida/pedido.json` y `cliente.zona_compras` / `cliente.localidad` de la ficha.

1. Fuentes admitidas, SOLO estas y SOLO de Argentina (precio en pesos, venta en el país): publicaciones de MercadoLibre Argentina (mercadolibre.com.ar), tiendas argentinas hechas en Tiendanube y otras tiendas online argentinas con carrito y precio publicado (ej. Easy, Sodimac, ferreterías o madereras con tienda web). Nunca cotizar por WhatsApp, teléfono, mail ni formularios de "consultar precio", y no usar páginas sin precio publicado. Por cada `id` del pedido, buscar en esas fuentes priorizando la zona de compras. Si se puede, lanzar un subagente con todos los ítems en una sola tanda.
2. Elegir UNA fuente por ítem, con el precio publicado hoy en la página del producto. Anotar URL exacta y fecha. Si la fuente es de otra zona, decirlo en `nota`.
3. Normalizar a la unidad del pedido con `contenido` = cuántas unidades del pedido trae una unidad de venta (ej. ripio pedido en kg y vendido en bolsa de 25 kg → `contenido: 25`; tuercas vendidas por 10 → `contenido: 10`). El motor calcula `ceil(cant / contenido)` unidades de venta.
4. Si no se encuentra un precio en esas fuentes: `precio: null` y la razón en `nota`. La página lo muestra como "sin precio de referencia" y no lo suma. Nunca estimar.
5. Escribir `<carpeta>/precios.json`:

```json
{"fecha_consulta": "AAAA-MM-DD", "localidad": "…", "moneda": "ARS",
 "items": [{"id": "varilla_16", "descripcion": "texto del producto en la fuente", "unidad": "u", "contenido": 1,
            "precio": 12345.0, "iva_incluido": true, "fuente": "Comercio", "url": "https://…", "nota": ""}]}
```

`iva_incluido`: los precios al consumidor en Argentina incluyen IVA; el motor los pasa a sin IVA con `comercial.iva_pct`.

Después: `correr.py propuesta <carpeta>` para rearmar la página con los precios.
