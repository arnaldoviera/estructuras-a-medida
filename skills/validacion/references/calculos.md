# Cálculos — pórtico de hamacas (simplificados)

Ejes: x a lo largo del travesaño, y vaivén, z arriba. mm, N.

## Geometría
- Cruce de la A (tangencia del travesaño en la V): `zc = z_eje − (R_trav + R_pata) / sin(atan(semibase / zc))`, por iteración. Caso: 1,762 m.
- Ángulo lateral = atan(semibase / zc) → 33°. Ángulo frontal = atan((pie_x − cruce_x) / zc) → 14°.
- Luz del travesaño = distancia entre ejes de las horquetas = 2·(pie_x − tan(frontal)·z_eje) → 3,10 m.
- Largo de pata = |pie → cruce| + prolongación + enterrado / cos(ángulo con la vertical) → 2,95 m (rollizo de 3 m).

## Flexión del travesaño (viga simplemente apoyada en las horquetas)
W = π·d³/32, I = π·d⁴/64; E y σ admisible desde `catalogo/materiales.json` (eucalipto: 12 000 MPa, 10 MPa).
1. Carga de diseño × factor dinámico repartida en las 2 abrazaderas exteriores (cama): M = (P/2)·a.
2. Un adulto por puesto (carga_por_puesto × factor dinámico) en los 3 puestos.
3. Envolvente: toda la carga de diseño × factor dinámico en el centro, M = P·L/4.
Flecha límite: L/300.

## Vuelco sin anclaje (sentido del vaivén)
Péndulo soltado desde θ0 (amplitud por accesorio en la tipología: hamaca 60°, cama 20°): T(θ) = m·g·(3·cosθ − 2·cosθ0). Se toma el θ que maximiza H = T·senθ y su V = T·cosθ. Todos los puestos en fase (peor caso).
FS = (peso propio + ΣV) · semibase / (ΣH · z_giro) ≥ 1,5.

## Pandeo de pata
N = (carga de diseño × factor dinámico + peso propio) / 4 / cos(ángulo con la vertical). Euler con L = pie → cruce. FS ≥ 3.

## Varillas
Largo ≥ agarre (madera atravesada, descontando rebajes) + 2 × 30 mm (arandela + tuerca + contratuerca + 2 hilos).
