---
name: propuesta-web
description: Arma y publica la propuesta comercial de una estructura a medida como página web única (Artifact HTML, responsive, tema claro/oscuro) desde ficha.json y las salidas de cada etapa. Usar para generar, regenerar o publicar la propuesta, o para cambiar su diseño.
---

# Propuesta web

```
python "${CLAUDE_PLUGIN_ROOT}/motor/correr.py" propuesta <carpeta>
```

Toma `ficha.json`, `precios.json` y `auditoria.json` (si existen) y escribe `salida/propuesta.html` (un solo archivo) y `salida/propuesta.txt` (texto plano para el auditor). Plantilla: `assets/plantilla.html` (sin doctype ni head: el Artifact la envuelve; CSS con tokens claro/oscuro, visor 3D Three.js r128 por CDN, botones de configuración).

Secciones:
1. Datos del proyecto (n°, fecha, validez, cliente, contacto, obra)
2. Qué se propone (texto, perspectiva acotada por configuración, croquis 3D armado)
3. Especificación técnica y normas (medidas + tabla de verificaciones)
4. Detalles constructivos (6 láminas)
5. Materiales con precios (cantidad, unitario sin IVA, subtotal, fuente con enlace)
6. Instalación (recomendaciones, paso a paso; MOD aparte)
7. Presupuesto (materiales sin flete: sin IVA, IVA y con IVA; MOD "se cotiza aparte")
8. Condiciones (validez, plazo, incluye/no incluye, garantía, mantenimiento, "no reemplaza el cálculo de un ingeniero")
9. Anexo de autoconstrucción (opcional: `comercial.anexo_autoconstruccion`)
10. Anexo: informe de auditoría

Publicar: Artifact tool con `file_path` = `salida/propuesta.html`, ícono "blueprint" o "house", descripción de una línea. Para actualizar la misma página, volver a publicar el mismo archivo (o pasar la `url` si es de otra sesión). Antes de publicar, revisar a 400 px de ancho que no haya desborde horizontal.

Campos en null (cliente, garantía, plazo) se ven como "a completar": completarlos en la ficha antes de mandar la propuesta al cliente.
