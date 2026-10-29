# Cálculos — pórtico de hamacas (simplificados)

Ejes: x a lo largo del travesaño, y vaivén, z arriba. mm, N.

## Geometría
- Cruce de la A (tangencia del travesaño en la V): `zc = z_eje − (R_trav + R_pata) / sin(atan(semibase / zc))`, por iteración.
- Ángulo lateral = atan(semibase / zc) . Ángulo frontal = atan((pie_x − cruce_x) / zc).
- Luz del travesaño = distancia entre ejes de las horquetas = 2·(pie_x − tan(frontal)·z_eje).
- Largo de pata = |pie → cruce| + prolongación + enterrado / cos(ángulo con la vertical); se compra el largo comercial que contiene largo + 2 cm de corte.
Los valores de cada caso salen en `validacion.json` (son datos informativos, fuera del conteo N/N).

## Flexión del travesaño (viga simplemente apoyada en las horquetas)
W = π·d³/32, I = π·d⁴/64; E y σ admisible desde `catalogo/materiales.json` (eucalipto: 12 000 MPa, 10 MPa).
1. Carga de diseño × factor dinámico repartida en las 2 abrazaderas exteriores (cama): M = (P/2)·a.
2. Un adulto por puesto (carga_por_puesto × factor dinámico) en todos los puestos; se toma el momento máximo bajo alguna de las cargas.
3. Envolvente: toda la carga de diseño × factor dinámico en el centro, M = P·L/4.
Flecha límite: L/300.

## Vuelco sin anclaje (sentido del vaivén)
Péndulo soltado desde θ0 (amplitud por accesorio en la tipología: hamaca 60°, cama 20°): T(θ) = m·g·(3·cosθ − 2·cosθ0). Se recorre el ciclo y se toma el instante de FS mínimo (H = ΣT·senθ, V = ΣT·cosθ). Todos los puestos en fase (peor caso).
FS = (peso propio + ΣV) · semibase / (ΣH · z_giro) ≥ 1,5.

## Pandeo de pata
N = (carga de diseño × factor dinámico + peso propio) / 4 / cos(ángulo con la vertical). Euler con L = pie → cruce. FS ≥ 3.

## Varillas
Largo ≥ agarre (madera atravesada, descontando rebajes) + 2 × 30 mm (arandela + tuerca + contratuerca + 2 hilos).
