# Bot de publicación diaria — @gutgoodbueno

Este sistema publica automáticamente, cada día, un "Sabías que..." sobre
Canarias en el Instagram de Gut Good Bueno, con foto incluida.

No necesitas dejar ningún ordenador encendido: GitHub se encarga de
ejecutarlo por ti, todos los días, de forma gratuita.

---

## Qué contiene esta carpeta

- `curiosidades.json` → el banco de datos con las curiosidades. Puedes
  añadir más entradas cuando quieras, copiando el formato de las que ya
  hay.
- `publicar.py` → el script que elige la curiosidad del día, busca una
  foto y publica en Instagram.
- `requirements.txt` → lo que necesita instalar Python para funcionar.
- `.github/workflows/publicar_diario.yml` → la programación: le dice a
  GitHub que ejecute el script todos los días a las 18:00 UTC (sobre las
  19:00 en Canarias).

---

## Paso 1 — Consigue tu clave gratuita de Pexels (5 minutos)

Pexels es el banco de imágenes gratuito que usará el bot para buscar
fotos.

1. Ve a **https://www.pexels.com/api/**
2. Pulsa "Get Started" y crea una cuenta gratuita (solo pide email)
3. Una vez dentro, te dan directamente tu **API Key** — cópiala, la
   necesitarás en el Paso 3

No pide tarjeta de crédito ni nada de pago, es gratis para este uso.

---

## Paso 2 — Crea el repositorio en GitHub

1. Ve a **https://github.com** y crea una cuenta gratuita si no tienes
   (con tu email)
2. Una vez dentro, pulsa el botón **"+"** de arriba a la derecha →
   **"New repository"**
3. Ponle un nombre, por ejemplo `gutgoodbueno-bot`
4. Marca la opción **"Private"** (privado) — así nadie más puede ver tu
   código ni tus claves
5. Pulsa **"Create repository"**
6. Dentro del repositorio recién creado, busca el enlace o botón
   **"uploading an existing file"** / "Subir archivos existentes"
7. Arrastra ahí **todos los archivos y carpetas** que están en esta
   carpeta que te he preparado (incluida la carpeta `.github` completa,
   con el archivo `.yml` dentro)
8. Baja y pulsa **"Commit changes"** para guardar la subida

---

## Paso 3 — Añade tus claves secretas (Secrets)

Estas claves permiten que el robot publique en tu nombre, pero se
guardan cifradas — ni siquiera tú puedes volver a verlas una vez
guardadas, solo GitHub las usa internamente.

1. Dentro de tu repositorio en GitHub, ve a **"Settings"** (pestaña de
   arriba)
2. En el menú lateral izquierdo, busca **"Secrets and variables"** →
   **"Actions"**
3. Pulsa **"New repository secret"** y añade estas tres claves, una por
   una:

   | Nombre exacto              | Valor                                            |
   |-----------------------------|---------------------------------------------------|
   | `IG_USER_ID`                | `17841423303076816`                               |
   | `INSTAGRAM_ACCESS_TOKEN`    | el token que generaste en Meta for Developers      |
   | `PEXELS_API_KEY`            | la clave que conseguiste en el Paso 1              |

   Para cada una: escribe el nombre exacto (tal cual aparece en la
   tabla, en mayúsculas), pega el valor correspondiente, y pulsa
   **"Add secret"**.

---

## Paso 4 — Pruébalo manualmente

No hace falta esperar a mañana para comprobar que funciona:

1. Ve a la pestaña **"Actions"** de tu repositorio
2. Verás el flujo **"Publicación diaria en Instagram"** en la lista de
   la izquierda — pulsa sobre él
3. A la derecha aparecerá un botón **"Run workflow"** → pulsa ahí y
   confirma
4. Espera 1-2 minutos y recarga la página. Si aparece un ✅ verde, ¡se
   ha publicado correctamente en tu Instagram! Si aparece una ❌ roja,
   pulsa encima para ver el mensaje de error exacto (avísame y lo
   revisamos juntos)

---

## Y a partir de ahora...

No tienes que hacer nada más. Cada día, a la hora programada, GitHub
ejecutará el script solo y publicará una curiosidad nueva con su foto.

### Cosas a tener en cuenta

- **El token caduca cada 60 días aproximadamente.** Instagram no permite
  tokens permanentes por seguridad. Te recomiendo poner un recordatorio
  en el calendario para dentro de 50 días, y avisarme para generar uno
  nuevo (es un proceso de 5 minutos, mucho más rápido que la primera
  vez, porque toda la configuración ya está hecha).
- **Las 30 curiosidades se repetirán cada 30 días.** Puedes pedirme en
  cualquier momento que añada más al archivo `curiosidades.json` para
  que tarden más en repetirse.
- **Puedes cambiar la hora de publicación** editando la línea `cron` del
  archivo `.github/workflows/publicar_diario.yml`. Si quieres, dime la
  hora que prefieres y te calculo el valor exacto.
