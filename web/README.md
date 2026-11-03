# Bloques dinámicos de gutgoodbueno.com

La web (Carrd) tiene dos bloques "Embed" que cargan `ggb-web.js` desde jsDelivr:

- `<div id="ggb-proximas"></div>` → agenda, leída de `eventos.json` (los carteles van en `carteles/`). Cada actividad desaparece sola al día siguiente de su fecha.
- `<div id="ggb-experiencias"></div>` → tarjetas de productos, leídas de `experiencias.json`.

Para añadir una actividad: subir el cartel a `carteles/` (900 px de ancho) y añadir una entrada en `eventos.json`. No hace falta tocar Carrd.

Si se cambia `ggb-web.js`, jsDelivr tarda hasta 12 h en refrescar; se puede forzar con https://purge.jsdelivr.net/gh/GutGoodBueno/gutgoodbueno-bot@main/web/ggb-web.js
