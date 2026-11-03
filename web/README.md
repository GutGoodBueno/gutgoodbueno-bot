# Bloques dinámicos de gutgoodbueno.com

La web (Carrd) tiene dos bloques "Embed". Cada uno lleva un cargador mínimo que descarga `ggb-web.js` desde raw.githubusercontent.com y lo inyecta (raw sirve texto plano, por eso no se usa `<script src>`):

- `<div id="ggb-proximas"></div>` → agenda, leída de `eventos.json` (los carteles van en `carteles/`). Cada actividad desaparece sola al día siguiente de su `fecha` (o `fecha_fin`).
- `<div id="ggb-experiencias"></div>` → tarjetas de productos, leídas de `experiencias.json`.

Para añadir una actividad: subir el cartel a `carteles/` (900 px de ancho, nombre `AAAA-MM-DD-slug.jpg`) y añadir una entrada en `eventos.json`. No hace falta tocar Carrd ni volver a publicar.

Caché: raw.githubusercontent tarda unos 5 min en servir lo nuevo, y el cargador cambia su `?v=` cada 10 min. Cualquier cambio está en la web en 15 min como máximo.

Si el bloque se ve estrecho (menos de 700 px), las tarjetas pasan a carrusel con flechas.
