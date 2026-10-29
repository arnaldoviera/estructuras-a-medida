# Preguntas por tipología

## Comunes a todas
- Cliente, contacto (teléfono o mail), localidad y dirección de la obra. Solo en tipologías con presupuesto: zona donde se compran los materiales (define dónde se buscan los precios).
- ¿Para cuándo lo necesita? ¿Lo arma el cliente, nosotros o un tercero? ¿Cuántas personas arman?
- Herramientas disponibles: taladro y mechas largas, motosierra, escalera, andamio.
- Materiales que prefiere o ya tiene: madera (eucalipto o pino impregnado, varilla roscada) o hierro (tubo estructural, planchuela, inoxidable).
- Terminación deseada: en madera, impregnado + Cetol, pintura o natural; en hierro, galvanizado en caliente (y pintura si se quiere color).
- Condiciones comerciales: validez, garantía, plazo; IVA (con o sin) solo en tipologías con presupuesto.

## portico-hamacas
- Uso: ¿qué se cuelga? Hamacas, trapecio, escalera de soga, hamaca-cama, columpio de bebé. ¿Intercambiables? ¿Cuántos puestos?
- Superficie bajo las hamacas: al ras del entorno (césped, sintético) o suelta contenida (arena, chips). Define la zona libre de la EN 1176-2.
- Usuarios: edades y pesos; ¿suben adultos? Carga de diseño en kg del peor caso (ej. cama con 2 adultos + 2 chicos = 350 kg).
- Tipo de uso de cada accesorio: hamacarse fuerte o solo mecerse (define la amplitud que se usa para el vuelco).
- Espacio disponible: largo en el sentido del travesaño y largo en el sentido del vaivén, en metros. Orientación: hacia dónde se hamaca (paralelo a un muro, hacia el césped). Obstáculos: muros, árboles, cables, pendiente.
- Suelo: césped, tierra o contrapiso. ¿Se admite hormigón o va apoyado en pozos?
- Altura deseada del travesaño o de los asientos.
- Fotos y medidas del lugar, si hay.

## jaula-cerdas
Box de alimentación individual para cerdas gestantes en grupo, tipo Gestal 3G (hierro). Ejemplo: `ejemplos/jaula-cerdas/ficha.json`.
- Cantidad de boxes y uso: ¿la cerda solo come o también descansa adentro? (define el ancho libre: 520 solo comer, hasta 600 si descansa).
- Genética y tamaño de las cerdas: peso y altura de lomo de la más grande (la puerta tiene que pasar por arriba).
- Salida: ¿de culata como el Gestal (hay pasillo trasero despejado de unos 3 m) o hacia adelante (box de paso, otra puerta y pasillo de retorno)?
- Etapa de automatización inicial: 1 mecánico, 2 dosificador mecánico, 3 RFID + dosificador electrónico, 4 puerta actuada. Sin RFID va 1 cerda por box; con RFID, 15–18.
- Galpón: piso de slats (ancho de viga, ranura, espesor y orientación respecto del box) o contrapiso; línea de alimento existente (diámetro y altura).
- Fabricación: taller propio o tercero, ¿suelda inoxidable?, ¿hay galvanizado en caliente cerca? Largo de barra del proveedor (6 o 6,40 m).
- Electrónica prevista: marca del dosificador y del lector RFID (distancia mínima a metal de la antena).


## estructura-libre
Muebles y estructuras simples de madera y/o hierro que no son una tipología propia: mesas, bancos, estantes, bastidores, soportes. Ejemplo: `ejemplos/mesa-hierro-madera/ficha.json`.

**Desde una foto.** Si el cliente manda una foto ("quiero una mesa que se parezca a esto"):
1. Mirar la imagen y describir en una o dos líneas qué se ve: cuántas patas, qué piezas son de hierro y cuáles de madera, secciones aparentes (caño cuadrado, redondo, tirante, tablero), uniones a la vista y terminación.
2. Proponer la lista de piezas (secciones, barras y placas) con medidas comerciales. De la foto se toman proporciones e idea; **las medidas nunca salen de la foto**: las da el cliente o el uso.
3. Preguntar solo lo que falta, en una tanda: largo × ancho × alto (o para cuántas personas), uso (mesa, banco, estante u otro), interior o exterior, cuántas unidades, color de la madera y del hierro.
4. Anotar en `requisitos.referencia` qué se tomó de la foto (`tomado`) y qué se cambió y por qué (`cambiado`). La foto no se guarda en la ficha: queda en la carpeta del proyecto si el cliente la mandó como archivo.

**Desde un pedido sin foto.** Las mismas preguntas del punto 3, más: estilo (industrial, rústico, liviano), qué tiene que aguantar (personas sentadas, peso de libros, macetas) y si hay que desarmarlo para pasar por una puerta.

**Cómo se arma la ficha.**
- `requisitos.tipo_uso`: `mesa`, `banco` o `estante` traen cargas del catálogo; cualquier otro uso necesita `requisitos.cargas` completo (`distribuida_kg_m2`, `puntual_kg`, `empuje_lateral_kg`, `carga_borde_kg`) con su criterio.
- `diseno.secciones`: `tubo-rect` (b × h × esp), `tubo-redondo` (diam × esp), `madera` (b × h y especie del catálogo) o `planchuela`. En vigas, `h` es el alto.
- `diseno.barras`: cada pieza lineal con dos puntos `a` y `b` en mm (x a lo largo, y al fondo, z arriba, piso en 0) y un rol: `pata` (apoya en el piso), `viga` (lleva carga) o `riostra`. Las barras alineadas a un eje se dibujan como cajas; las inclinadas, como cilindros. Una tabla de asiento o un listón que carga directo lleva `ancho_carga` (mm).
- `diseno.placas`: tapas, estantes y tableros como cajas `x`, `y`, `z` con un material de `tableros`; el espesor (z) es el del tablero. La placa tiene que apoyar sobre vigas cuya cara de arriba toque su cara de abajo.
- `insumos`, `uniones`, `terminacion` y `pendientes` en texto: los copia la página.
- Si la estructura necesita cálculo de ingeniería (techos, entrepisos, pérgolas con viento, algo que sostenga personas en altura), decirlo y no forzarla en esta tipología.
