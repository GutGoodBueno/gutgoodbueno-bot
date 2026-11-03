# Serie "¿Sabías que...? Los 88 municipios de Canarias"

Un post al día, de El Hierro a Lanzarote (de oeste a este), a las 18:00 UTC.
Cada dato sale de la web del ayuntamiento, del Cabildo o de un boletín oficial,
y la fuente aparece en el texto del post.

## Qué hay en esta carpeta

| Archivo | Para qué sirve |
|---|---|
| `publicar_municipios.py` | Elige el municipio del día, dibuja la imagen y publica |
| `datos/municipios.json` | Los 88 textos, con su fuente y su enlace |
| `datos/canarias_municipios.json` | Los contornos de los municipios para dibujar el mapa |
| `.github/workflows/publicar_municipios.yml` | La programación diaria |
| `.github/workflows/renovar_token.yml` | Renueva el token de Instagram los días 1 y 15 |

El avance se guarda en `datos/estado.json`, que se crea solo. Si un día falla,
al siguiente se reintenta el mismo municipio: no se salta ninguno. Tras el 88
(Haría) la serie se para sola.

## Paso 1 · Token nuevo de Instagram (el motivo de que dejara de publicar)

1. Entra en Meta for Developers → app **GutGoodBueno Bot** → Instagram →
   *Configuración de la API con inicio de sesión de Instagram* → genera un
   token nuevo para @gutgoodbueno.
2. En GitHub: repositorio → **Settings → Secrets and variables → Actions** →
   `INSTAGRAM_ACCESS_TOKEN` → **Update** → pega el token nuevo.

## Paso 2 · Subir los archivos

En el repositorio, **Add file → Upload files** y arrastra:
`publicar_municipios.py` y la carpeta `datos` (con sus dos archivos).

Los dos workflows créalos con **Add file → Create new file**, escribiendo como
nombre `.github/workflows/publicar_municipios.yml` (y después
`.github/workflows/renovar_token.yml`) y pegando su contenido.

## Paso 3 · Apagar las dos series antiguas

Pestaña **Actions** → "Publicación diaria en Instagram" → botón **···** →
**Disable workflow**. Lo mismo con "Publicación El sabor de Canarias".
No se borra nada: se pueden volver a activar cuando quieras.

## Paso 4 · Renovación automática del token (para que no vuelva a pasar)

1. GitHub → tu foto → **Settings → Developer settings → Personal access tokens
   → Fine-grained tokens → Generate new token**.
2. Repository access: **Only select repositories** → `gutgoodbueno-bot`.
3. Permissions → Repository permissions → **Secrets: Read and write**.
4. Genera y copia el token. En el repositorio: **Settings → Secrets → Actions →
   New repository secret**, nombre `GH_PAT`, pega el token.

Pon la caducidad del token de GitHub en 1 año y apúntate renovarlo.

## Paso 5 · Probar

**Actions → "Serie 88 municipios de Canarias" → Run workflow**. Debe publicar
el 1/88 (La Frontera). A partir de ahí sigue sola cada día.
