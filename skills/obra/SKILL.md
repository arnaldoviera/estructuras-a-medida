---
name: obra
description: "Recomendaciones de obra, herramientas, paso a paso de instalación (apto 1 persona con ayuda puntual) y mantenimiento de una estructura a medida, generados desde ficha.json. Usar en la corrida completa o cuando se pida el instructivo de armado o de mantenimiento."
---

# Obra

Lo hace `correr.py todo <carpeta>` (`motor/obra.py`) → `salida/obra.json` con `herramientas`, `recomendaciones`, `pasos` y `mantenimiento`. Todas las medidas de los pasos salen de la ficha.

Solo `portico-hamacas`. En `jaula-cerdas` el mantenimiento, las pruebas de prototipo y los pendientes de taller salen en la página técnica (secciones «Lo que falta definir» y «Condiciones»).

Criterios:
- El armado lo hace 1 persona; la ayuda puntual (`requisitos.personas_armado`, en el ejemplo 2 personas) se reserva para parar las A y subir el travesaño. Las A se arman y perforan acostadas en el piso.
- Orden: replanteo → pozos → patas → A en el piso (cruce, tirante, asientos de horqueta) → levantar las A → travesaño → cartelas → compactar → abrazaderas → accesorios y prueba de carga → reajuste a la semana.
- La mano de obra no se calcula: en la propuesta va como renglón aparte ("se cotiza aparte").
- Si la ficha cambia `requisitos.personas_armado` o las herramientas, revisar que los pasos sigan siendo posibles; si no, ajustar el texto en `motor/obra.py`, no a mano en la página.
