
# Bot de publicación diaria — @gutgoodbueno

Este sistema publica automáticamente, cada día, un "¿Sabías que...?" sobre
Canarias en el Instagram de Gut Good Bueno. La imagen se genera con diseño
propio (silueta de la isla + titular + vuestro logo), no depende de bancos
de fotos externos.

No necesitas dejar ningún ordenador encendido: GitHub se encarga de
ejecutarlo por ti, todos los días, de forma gratuita.

---

## Qué ha cambiado respecto a la versión anterior

- ❌ Ya no se usa Pexels ni fotos de stock (podías tener el semáforo de
  antes por eso). Si tenías guardada esa clave como Secret en GitHub,
  puedes borrarla, ya no se usa.
- ✅ Ahora el propio sistema **dibuja la imagen**: fondo con los colores
  de la marca, una silueta decorativa de la isla, el titular "¿SABÍAS
  QUE...?", un adelanto corto, el nombre de la isla y vuestro logo.
- ✅ Las 24 curiosidades son datos poco conocidos, contrastados con
  fuentes oficiales (Instituto de Astrofísica de Canarias, Gobierno de
  Canarias, UNESCO, parques nacionales, etc.). Cada una lleva un campo
  interno `"fuente"` en el archivo `curiosidades.json` — no se publica,
  es solo para que tengas respaldo si alguna vez alguien pregunta de
  dónde sale el dato.

---

## Qué contiene esta carpeta

- `curiosidades.json` → el banco de datos con las curiosidades y sus
  fuentes.
- `publicar.py` → el script que elige la curiosidad del día, genera la
  imagen y publica en Instagram.
- `imagenes_base/logo.png` → tu logo, usado en cada imagen generada.
- `fuentes/` → las tipografías usadas en el diseño (para que no dependa
  de lo que tenga instalado GitHub).
- `requirements.txt` → lo que necesita instalar Python para funcionar.
- `.github/workflows/publicar_diario.yml` → la programación diaria.

---

## Si ya tenías el sistema anterior funcionando

Solo tienes que **sustituir** estos archivos por los nuevos (mismo
proceso de siempre: abrir el archivo en GitHub, lápiz ✏️ para editar,
borrar todo, pegar el contenido nuevo, Commit changes):

1. `publicar.py`
2. `curiosidades.json`
3. `requirements.txt`
4. `.github/workflows/publicar_diario.yml`

Y **añadir dos archivos nuevos** que antes no existían:
5. `imagenes_base/logo.png` → sube tu logo aquí (crea la carpeta
   `imagenes_base` al subirlo, escribiendo `imagenes_base/logo.png`
   como nombre de archivo al subirlo, igual que hiciste con el workflow)
6. Los 3 archivos de la carpeta `fuentes/` (las tipografías)

También puedes borrar el Secret `PEXELS_API_KEY` de tu repositorio
(Settings → Secrets and variables → Actions), ya no se usa.

---

## Si es la primera vez que lo instalas

### Paso 1 — Crea el repositorio en GitHub

1. Ve a **https://github.com** y crea una cuenta gratuita si no tienes
2. Pulsa **"+"** → **"New repository"**
3. Nómbralo, por ejemplo `gutgoodbueno-bot`, y márcalo como **Private**
4. Sube ahí todos los archivos y carpetas de este proyecto (incluida la
   carpeta oculta `.github`)

### Paso 2 — Añade tus 2 claves secretas

1. Dentro del repositorio → **Settings** → **Secrets and variables** →
   **Actions** → **"New repository secret"**
2. Añade estas dos:

   | Nombre exacto              | Valor                                          |
   |-----------------------------|-------------------------------------------------|
   | `IG_USER_ID`                | `17841423303076816`                             |
   | `INSTAGRAM_ACCESS_TOKEN`    | el token que generaste en Meta for Developers    |

Ya no hace falta la clave de Pexels.

### Paso 3 — Comprueba los permisos de escritura

Como el sistema ahora sube la imagen generada al propio repositorio,
necesita permiso de escritura:

1. Ve a **Settings** → **Actions** → **General**
2. Baja hasta **"Workflow permissions"**
3. Asegúrate de que está marcado **"Read and write permissions"**
4. Guarda si has hecho algún cambio

### Paso 4 — Pruébalo manualmente

1. Ve a la pestaña **"Actions"**
2. Selecciona **"Publicación diaria en Instagram"**
3. Pulsa **"Run workflow"**
4. Espera 1-2 minutos y comprueba el resultado (✅ o ❌)

---

## Y a partir de ahora...

Cada día, a la hora programada (sobre las 19:00 hora Canarias), GitHub
generará la imagen, la subirá y publicará el post solo, sin que tengas
que hacer nada.

### Cosas a tener en cuenta

- **El token de Instagram caduca cada ~60 días.** Te avisaré para
  generar uno nuevo cuando corresponda.
- **Las 24 curiosidades se repetirán cada 24 días.** Puedo añadirte más
  en cualquier momento, siempre documentadas con fuentes.
- **Si quieres cambiar algo del diseño** (colores, tamaños de texto,
  posición del logo), dímelo y lo ajusto en `publicar.py`.
- **Las imágenes generadas se van guardando** en la carpeta `imagenes/`
  del repositorio, así queda un histórico de todo lo publicado.
