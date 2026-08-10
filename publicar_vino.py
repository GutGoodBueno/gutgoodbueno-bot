"""
Script de publicación diaria para @gutgoodbueno — El sabor de Canarias
"""

import math
import os
import json
import subprocess
import sys
import time
from datetime import date

import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter

GRAPH_URL = "https://graph.instagram.com/v21.0"
CARPETA = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_CONTENIDOS = os.path.join(CARPETA, "contenidos_vino.json")
CARPETA_IMAGENES = os.path.join(CARPETA, "imagenes")
LOGO = os.path.join(CARPETA, "imagenes_base", "logo.png")

AZUL_MARINO = (20, 49, 79)
AZUL_MEDIO = (32, 76, 115)
CREMA = (243, 240, 225)
NARANJA = (189, 116, 39)
BLANCO = (255, 255, 255)

TIERRAS = [
    (214, 190, 150),
    (196, 160, 110),
    (170, 124, 72),
    (136, 92, 48),
    (104, 66, 34),
]

ANCHO = ALTO = 1080

FUENTE_BOLD = os.path.join(CARPETA, "fuentes", "Poppins-Bold.ttf")
FUENTE_MEDIA = os.path.join(CARPETA, "fuentes", "Poppins-Medium.ttf")
FUENTE_REGULAR = os.path.join(CARPETA, "fuentes", "Poppins-Regular.ttf")


def obtener_variable_entorno(nombre):
    valor = os.environ.get(nombre)
    if not valor:
        sys.exit(f"Falta la variable de entorno '{nombre}'. Revisa los Secrets en GitHub.")
    return valor


def cargar_contenidos():
    with open(ARCHIVO_CONTENIDOS, "r", encoding="utf-8") as f:
        return json.load(f)


def elegir_contenido_de_hoy(contenidos):
    dia_del_anio = date.today().timetuple().tm_yday
    indice = dia_del_anio % len(contenidos)
    return contenidos[indice]


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


def puntos_bancal(y_base, amplitud, longitud_onda, fase):
    coords = []
    x = -60
    while x <= ANCHO + 60:
        y = y_base + amplitud * math.sin(x / longitud_onda + fase)
        coords.append((x, y))
        x += 12
    coords.append((ANCHO + 60, ALTO + 60))
    coords.append((-60, ALTO + 60))
    return coords


def envolver_texto(draw, texto, fuente, ancho_max, max_lineas=2):
    palabras = texto.split()
    lineas = []
    actual = ""
    for palabra in palabras:
        prueba = f"{actual} {palabra}".strip()
        bbox = draw.textbbox((0, 0), prueba, font=fuente)
        if bbox[2] - bbox[0] <= ancho_max or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
        if len(lineas) == max_lineas:
            break
    if actual and len(lineas) < max_lineas:
        lineas.append(actual)
    return lineas


def texto_centrado(draw, texto, fuente, y, ancho_lienzo, color):
    bbox = draw.textbbox((0, 0), texto, font=fuente)
    ancho_texto = bbox[2] - bbox[0]
    x = (ancho_lienzo - ancho_texto) / 2
    draw.text((x, y), texto, font=fuente, fill=color)


def generar_imagen(contenido, ruta_salida):
    img = fondo_degradado(ANCHO, ALTO, AZUL_MARINO, AZUL_MEDIO)

    capa_sol = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 0))
    dibujo_sol = ImageDraw.Draw(capa_sol)
    cx, cy, radio = ANCHO / 2, 560, 175
    dibujo_sol.ellipse(
        [cx - radio * 1.5, cy - radio * 1.5, cx + radio * 1.5, cy + radio * 1.5],
        fill=(*NARANJA, 45),
    )
    capa_sol = capa_sol.filter(ImageFilter.GaussianBlur(40))
    img.paste(capa_sol, (0, 0), capa_sol)

    draw = ImageDraw.Draw(img, "RGBA")
    draw.ellipse([cx - radio, cy - radio, cx + radio, cy + radio], fill=(*NARANJA, 235))

    configuracion = [
        (600, 22, 260, 0.4),
        (690, 18, 220, 1.7),
        (780, 15, 190, 3.1),
        (870, 13, 165, 4.6),
        (960, 11, 150, 5.9),
    ]
    for (y_base, amplitud, longitud_onda, fase), color in zip(configuracion, TIERRAS):
        coords = puntos_bancal(y_base, amplitud, longitud_onda, fase)
        draw.polygon(coords, fill=color)
        draw.line(coords[:-2], fill=(*CREMA, 130), width=3)

    fuente_titulo = ImageFont.truetype(FUENTE_BOLD, 66)
    texto_centrado(draw, "EL SABOR DE CANARIAS", fuente_titulo, 90, ANCHO, BLANCO)

    draw.line([(ANCHO / 2 - 120, 185), (ANCHO / 2 + 120, 185)], fill=NARANJA, width=4)

    fuente_sub = ImageFont.truetype(FUENTE_MEDIA, 40)
    lineas = envolver_texto(draw, contenido["titulo"], fuente_sub, 880, max_lineas=3)
    y = 240
    for linea in lineas:
        texto_centrado(draw, linea, fuente_sub, y, ANCHO, CREMA)
        y += 54

    if os.path.exists(LOGO):
        logo = Image.open(LOGO).convert("RGBA")
        tamano_logo = 150
        logo = logo.resize((tamano_logo, tamano_logo), Image.LANCZOS)
        logo_x = (ANCHO - tamano_logo) // 2
        logo_y = ALTO - 185
        img.paste(logo, (logo_x, logo_y), logo)

    img.save(ruta_salida, quality=92)


def subir_imagen_al_repositorio(ruta_imagen):
    subprocess.run(["git", "config", "user.name", "Bot de publicaciones"], check=True, cwd=CARPETA)
    subprocess.run(["git", "config", "user.email", "actions@github.com"], check=True, cwd=CARPETA)
    subprocess.run(["git", "add", ruta_imagen], check=True, cwd=CARPETA)

    resultado = subprocess.run(
        ["git", "commit", "-m", f"Imagen de El sabor de Canarias del {date.today()}"],
        cwd=CARPETA,
    )
    if resultado.returncode != 0:
        print("No había cambios nuevos que subir.")

    subprocess.run(["git", "pull", "--rebase"], cwd=CARPETA)
    subprocess.run(["git", "push"], check=True, cwd=CARPETA)


def construir_url_publica_de_la_imagen(nombre_archivo):
    repo = obtener_variable_entorno("GITHUB_REPOSITORY")
    return f"https://raw.githubusercontent.com/{repo}/main/imagenes/{nombre_archivo}"


def construir_texto(contenido):
    hashtags = contenido["hashtags"]
    if isinstance(hashtags, list):
        hashtags = " ".join(hashtags)
    return (
        f"EL SABOR DE CANARIAS\n"
        f"{contenido['titulo']}\n\n"
        f"{contenido['texto']}\n\n"
        f"{hashtags}"
    )


def esperar_a_que_la_imagen_este_lista(creation_id, access_token, intentos=12, espera_segundos=5):
    for intento in range(1, intentos + 1):
        resp = requests.get(
            f"{GRAPH_URL}/{creation_id}",
            params={"fields": "status_code", "access_token": access_token},
            timeout=20,
        )
        if resp.ok:
            estado = resp.json().get("status_code")
            print(f"Comprobando estado de la imagen (intento {intento}/{intentos}): {estado}")
            if estado == "FINISHED":
                return True
            if estado == "ERROR":
                sys.exit(f"Instagram no pudo procesar la imagen: {resp.text}")
        time.sleep(espera_segundos)

    sys.exit("La imagen no estuvo lista a tiempo.")


def publicar_en_instagram(ig_user_id, access_token, url_imagen, texto):
    resp_crear = requests.post(
        f"{GRAPH_URL}/{ig_user_id}/media",
        data={"image_url": url_imagen, "caption": texto, "access_token": access_token},
        timeout=30,
    )
    if not resp_crear.ok:
        sys.exit(f"Error al crear la publicación: {resp_crear.text}")

    creation_id = resp_crear.json()["id"]
    esperar_a_que_la_imagen_este_lista(creation_id, access_token)

    resp_publicar = requests.post(
        f"{GRAPH_URL}/{ig_user_id}/media_publish",
        data={"creation_id": creation_id, "access_token": access_token},
        timeout=30,
    )
    if not resp_publicar.ok:
        sys.exit(f"Error al publicar en Instagram: {resp_publicar.text}")

    return resp_publicar.json()


def main():
    ig_user_id = obtener_variable_entorno("IG_USER_ID")
    access_token = obtener_variable_entorno("INSTAGRAM_ACCESS_TOKEN")

    contenidos = cargar_contenidos()
    contenido = elegir_contenido_de_hoy(contenidos)
    print(f"Contenido de hoy: {contenido['titulo']}")

    os.makedirs(CARPETA_IMAGENES, exist_ok=True)
    nombre_archivo = f"vino-{date.today().isoformat()}.jpg"
    ruta_imagen = os.path.join(CARPETA_IMAGENES, nombre_archivo)
    generar_imagen(contenido, ruta_imagen)
    print(f"Imagen generada: {ruta_imagen}")

    ruta_relativa = os.path.join("imagenes", nombre_archivo)
    subir_imagen_al_repositorio(ruta_relativa)
    url_imagen = construir_url_publica_de_la_imagen(nombre_archivo)
    print(f"Imagen publicada en: {url_imagen}")

    time.sleep(10)

    texto = construir_texto(contenido)
    resultado = publicar_en_instagram(ig_user_id, access_token, url_imagen, texto)

    print("Publicado correctamente en Instagram.")
    print(resultado)


if __name__ == "__main__":
    main()
