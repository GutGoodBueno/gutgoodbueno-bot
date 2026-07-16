"""
Script de publicación diaria para @gutgoodbueno
--------------------------------------------------
Cada día:
1. Elige una curiosidad de Canarias del archivo curiosidades.json
   (rota automáticamente según el día del año, sin repetir hasta
   agotar la lista completa).
2. Genera una imagen propia (silueta de la isla + titular), usando
   los colores y el logo de la marca. No depende de bancos de fotos.
3. Sube esa imagen al propio repositorio de GitHub para que tenga una
   dirección pública, y publica el post en Instagram con ella.

Variables de entorno necesarias (se configuran como "Secrets" en GitHub):
- IG_USER_ID              -> identificador numérico de tu cuenta de Instagram
- INSTAGRAM_ACCESS_TOKEN  -> el token que generaste en Meta for Developers
- GITHUB_REPOSITORY       -> la rellena GitHub Actions automáticamente
"""

import math
import os
import json
import random
import subprocess
import sys
import time
from datetime import date

import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter

GRAPH_URL = "https://graph.instagram.com/v21.0"
CARPETA = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_CURIOSIDADES = os.path.join(CARPETA, "curiosidades.json")
CARPETA_IMAGENES = os.path.join(CARPETA, "imagenes")
LOGO = os.path.join(CARPETA, "imagenes_base", "logo.png")

# --- Paleta de colores de la marca (extraída del logo real) ---
AZUL_MARINO = (20, 49, 79)
AZUL_MEDIO = (32, 76, 115)
CREMA = (243, 240, 225)
NARANJA = (189, 116, 39)
BLANCO = (255, 255, 255)

ANCHO = ALTO = 1080

FUENTE_BOLD = os.path.join(CARPETA, "fuentes", "Poppins-Bold.ttf")
FUENTE_MEDIA = os.path.join(CARPETA, "fuentes", "Poppins-Medium.ttf")
FUENTE_REGULAR = os.path.join(CARPETA, "fuentes", "Poppins-Regular.ttf")


def obtener_variable_entorno(nombre):
    valor = os.environ.get(nombre)
    if not valor:
        sys.exit(f"❌ Falta la variable de entorno '{nombre}'. Revisa los Secrets en GitHub.")
    return valor


def cargar_curiosidades():
    with open(ARCHIVO_CURIOSIDADES, "r", encoding="utf-8") as f:
        return json.load(f)


def elegir_curiosidad_de_hoy(curiosidades):
    """Elige una curiosidad distinta cada día, rotando por la lista completa."""
    dia_del_anio = date.today().timetuple().tm_yday
    indice = dia_del_anio % len(curiosidades)
    return curiosidades[indice]


# ---------- Generación de la imagen ----------

def fondo_degradado(ancho, alto, color_arriba, color_abajo):
    base = Image.new("RGB", (ancho, alto), color_arriba)
    bottom = Image.new("RGB", (ancho, alto), color_abajo)
    mask = Image.new("L", (ancho, alto))
    mask_data = []
    for y in range(alto):
        mask_data.extend([int(255 * (y / alto))] * ancho)
    mask.putdata(mask_data)
    base.paste(bottom, (0, 0), mask)
    return base


def generar_blob(nombre_isla, cx, cy, radio_base, puntos=60):
    """Genera una forma orgánica decorativa, siempre igual para la misma isla
    (no es un mapa geográfico exacto, es un icono con identidad propia)."""
    random.seed(nombre_isla)
    fase1 = random.uniform(0, math.tau)
    fase2 = random.uniform(0, math.tau)
    fase3 = random.uniform(0, math.tau)
    coords = []
    for i in range(puntos):
        theta = (i / puntos) * math.tau
        r = radio_base * (
            1
            + 0.16 * math.sin(3 * theta + fase1)
            + 0.10 * math.sin(5 * theta + fase2)
            + 0.06 * math.sin(9 * theta + fase3)
        )
        x = cx + r * math.cos(theta)
        y = cy + r * math.sin(theta) * 0.85
        coords.append((x, y))
    return coords


def texto_centrado(draw, texto, fuente, y, ancho_lienzo, color):
    bbox = draw.textbbox((0, 0), texto, font=fuente)
    ancho_texto = bbox[2] - bbox[0]
    x = (ancho_lienzo - ancho_texto) / 2
    draw.text((x, y), texto, font=fuente, fill=color)


def generar_imagen(curiosidad, ruta_salida):
    isla = curiosidad["isla"]
    img = fondo_degradado(ANCHO, ALTO, AZUL_MARINO, AZUL_MEDIO)
    draw = ImageDraw.Draw(img, "RGBA")

    # Halo decorativo detrás de la silueta
    blob_grande = generar_blob(isla, ANCHO / 2, ALTO / 2 + 50, 320)
    capa_blob = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 0))
    ImageDraw.Draw(capa_blob).polygon(blob_grande, fill=(*NARANJA, 50))
    capa_blob = capa_blob.filter(ImageFilter.GaussianBlur(2))
    img.paste(capa_blob, (0, 0), capa_blob)
    draw = ImageDraw.Draw(img, "RGBA")

    # Silueta de la isla
    blob_pequeno = generar_blob(isla, ANCHO / 2, ALTO / 2 + 30, 210)
    draw.polygon(blob_pequeno, fill=(*CREMA, 240), outline=(*BLANCO, 255))

    # Pin de ubicación
    cx, cy = ANCHO / 2, ALTO / 2 + 10
    radio_pin = 15
    draw.ellipse([cx - radio_pin, cy - radio_pin, cx + radio_pin, cy + radio_pin], fill=NARANJA)
    draw.polygon(
        [(cx - radio_pin, cy + 2), (cx + radio_pin, cy + 2), (cx, cy + radio_pin * 2.6)],
        fill=NARANJA,
    )
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=CREMA)

    # Titular
    fuente_titulo = ImageFont.truetype(FUENTE_BOLD, 78)
    texto_centrado(draw, "¿SABÍAS QUE...?", fuente_titulo, 80, ANCHO, BLANCO)

    fuente_sub = ImageFont.truetype(FUENTE_MEDIA, 30)
    titulo_corto = curiosidad["titulo"]
    if len(titulo_corto) > 46:
        titulo_corto = titulo_corto[:43].rsplit(" ", 1)[0] + "..."
    texto_centrado(draw, titulo_corto, fuente_sub, 190, ANCHO, NARANJA)

    # Badge con el nombre de la isla
    fuente_isla = ImageFont.truetype(FUENTE_BOLD, 46)
    bbox = draw.textbbox((0, 0), isla.upper(), font=fuente_isla)
    ancho_texto = bbox[2] - bbox[0]
    alto_texto = bbox[3] - bbox[1]
    pad_x, pad_y = 40, 18
    badge_ancho = ancho_texto + pad_x * 2
    badge_alto = alto_texto + pad_y * 2
    badge_x = (ANCHO - badge_ancho) / 2
    badge_y = ALTO - 250
    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_ancho, badge_y + badge_alto],
        radius=badge_alto / 2,
        fill=NARANJA,
    )
    draw.text(
        (badge_x + pad_x, badge_y + pad_y - bbox[1]),
        isla.upper(),
        font=fuente_isla,
        fill=AZUL_MARINO,
    )

    # Logo de la marca
    if os.path.exists(LOGO):
        logo = Image.open(LOGO).convert("RGBA")
        tamano_logo = 140
        logo = logo.resize((tamano_logo, tamano_logo), Image.LANCZOS)
        logo_x = (ANCHO - tamano_logo) // 2
        logo_y = ALTO - 165
        img.paste(logo, (logo_x, logo_y), logo)

    img.save(ruta_salida, quality=92)


def subir_imagen_al_repositorio(ruta_imagen):
    """Sube la imagen generada al propio repositorio de GitHub para que
    tenga una dirección pública que Instagram pueda usar."""
    subprocess.run(["git", "config", "user.name", "Bot de publicaciones"], check=True, cwd=CARPETA)
    subprocess.run(["git", "config", "user.email", "actions@github.com"], check=True, cwd=CARPETA)
    subprocess.run(["git", "add", ruta_imagen], check=True, cwd=CARPETA)

    resultado = subprocess.run(
        ["git", "commit", "-m", f"Imagen generada para la publicación del {date.today()}"],
        cwd=CARPETA,
    )
    if resultado.returncode != 0:
        print("ℹ️ No había cambios nuevos que subir (puede que ya existiera la imagen de hoy).")

    subprocess.run(["git", "push"], check=True, cwd=CARPETA)


def construir_url_publica_de_la_imagen(nombre_archivo):
    repo = obtener_variable_entorno("GITHUB_REPOSITORY")  # formato "usuario/repositorio"
    return f"https://raw.githubusercontent.com/{repo}/main/imagenes/{nombre_archivo}"


def construir_texto(curiosidad):
    return (
        f"🔍 SABÍAS QUE... {curiosidad['titulo']}\n"
        f"📍 {curiosidad['isla']}\n\n"
        f"{curiosidad['texto']}\n\n"
        f"✨ {curiosidad['cierre']}\n\n"
        f"{curiosidad['hashtags']}"
    )


# ---------- Publicación en Instagram ----------

def esperar_a_que_la_imagen_este_lista(creation_id, access_token, intentos=12, espera_segundos=5):
    for intento in range(1, intentos + 1):
        resp = requests.get(
            f"{GRAPH_URL}/{creation_id}",
            params={"fields": "status_code", "access_token": access_token},
            timeout=20,
        )
        if resp.ok:
            estado = resp.json().get("status_code")
            print(f"⏳ Comprobando estado de la imagen (intento {intento}/{intentos}): {estado}")
            if estado == "FINISHED":
                return True
            if estado == "ERROR":
                sys.exit(f"❌ Instagram no pudo procesar la imagen: {resp.text}")
        time.sleep(espera_segundos)

    sys.exit("❌ La imagen no estuvo lista a tiempo. Instagram tardó demasiado en procesarla.")


def publicar_en_instagram(ig_user_id, access_token, url_imagen, texto):
    resp_crear = requests.post(
        f"{GRAPH_URL}/{ig_user_id}/media",
        data={"image_url": url_imagen, "caption": texto, "access_token": access_token},
        timeout=30,
    )
    if not resp_crear.ok:
        sys.exit(f"❌ Error al crear la publicación: {resp_crear.text}")

    creation_id = resp_crear.json()["id"]
    esperar_a_que_la_imagen_este_lista(creation_id, access_token)

    resp_publicar = requests.post(
        f"{GRAPH_URL}/{ig_user_id}/media_publish",
        data={"creation_id": creation_id, "access_token": access_token},
        timeout=30,
    )
    if not resp_publicar.ok:
        sys.exit(f"❌ Error al publicar en Instagram: {resp_publicar.text}")

    return resp_publicar.json()


def main():
    ig_user_id = obtener_variable_entorno("IG_USER_ID")
    access_token = obtener_variable_entorno("INSTAGRAM_ACCESS_TOKEN")

    curiosidades = cargar_curiosidades()
    curiosidad = elegir_curiosidad_de_hoy(curiosidades)
    print(f"📌 Curiosidad de hoy: {curiosidad['titulo']}")

    os.makedirs(CARPETA_IMAGENES, exist_ok=True)
    nombre_archivo = f"post-{date.today().isoformat()}.jpg"
    ruta_imagen = os.path.join(CARPETA_IMAGENES, nombre_archivo)
    generar_imagen(curiosidad, ruta_imagen)
    print(f"🎨 Imagen generada: {ruta_imagen}")

    ruta_relativa = os.path.join("imagenes", nombre_archivo)
    subir_imagen_al_repositorio(ruta_relativa)
    url_imagen = construir_url_publica_de_la_imagen(nombre_archivo)
    print(f"🌐 Imagen publicada en: {url_imagen}")

    # Pequeña espera para que la CDN de GitHub sirva ya el archivo recién subido
    time.sleep(10)

    texto = construir_texto(curiosidad)
    resultado = publicar_en_instagram(ig_user_id, access_token, url_imagen, texto)

    print("✅ Publicado correctamente en Instagram.")
    print(resultado)


if __name__ == "__main__":
    main()

