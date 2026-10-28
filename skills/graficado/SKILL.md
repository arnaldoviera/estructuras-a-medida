---
name: graficado
description: Genera los gráficos de una estructura a medida desde ficha.json — perspectiva cónica acotada (SVG), láminas de detalles de uniones con agujeros y rebajes (SVG) y la escena del croquis 3D interactivo, siempre armado. Usar en la corrida completa o cuando el usuario pida ver, corregir o regenerar un plano, detalle o el 3D.
---

# Graficado

Lo hace `correr.py todo <carpeta>`. Salidas en `salida/`:
- `perspectiva-<config>.svg`: perspectiva cónica acotada, una por configuración (`motor/perspectiva.py`). Cilindros por tramos con orden de pintado por profundidad, cotas 3D proyectadas (líneas de referencia, flechas, texto rotado con halo), rótulos con línea guía, área libre, muro y pozos.
- `detalle_1..6.svg`: horqueta (vista lateral), cruce a media madera (vista frontal), tirante–pata (corte horizontal), cartela, abrazadera de cuelgue, apoyo en pozo (`motor/detalles.py`). Agujeros en línea de trazos; varillas con arandela, tuerca y contratuerca.
- `escena3d.json`: piezas del croquis 3D (`motor/croquis3d.py`). La página lo dibuja con Three.js y se gira con el dedo o el mouse.

Reglas fijas:
- El 3D va SIEMPRE ARMADO. No existe vista desarmada: el cliente no puede evaluar piezas sueltas.
- Todo sale de la ficha. Si algo se ve mal, se corrige la ficha (o el script), nunca el SVG a mano.
- Cotas en metros con coma decimal; textos en español rioplatense.

Revisión visual: abrir `salida/propuesta.html` en el navegador integrado y mirar la perspectiva, las 6 láminas y el 3D, también a 400 px de ancho.

Origen: refactor de `insumos/portico-v3` (plano.py, detalles.py). El croquis 3D del kit anatomy-reveal (Node + Chrome headless) se reemplazó por un visor Three.js dentro de la página: no requiere Node y funciona en el celular. Los archivos originales quedan en `insumos/` como referencia.
