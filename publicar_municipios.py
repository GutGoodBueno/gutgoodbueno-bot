"""
Serie diaria "¿Sabías que...? Los 88 municipios de Canarias" — @gutgoodbueno
-----------------------------------------------------------------------------
Cada día publica UN municipio, en orden de oeste a este:
El Hierro → La Palma → La Gomera → Tenerife → Gran Canaria → Fuerteventura → Lanzarote.

Cómo funciona:
1. Lee datos/estado.json para saber cuál fue el último municipio publicado
   y elige el siguiente de datos/municipios.json. Si un día falla, al día
   siguiente se reintenta el mismo: no se salta ninguno.
2. Dibuja la imagen: silueta real de la isla con sus municipios y el del día
   resaltado en naranja (una plantilla por isla, válida para todos sus municipios).
3. Sube la imagen al repositorio, publica en Instagram y guarda el avance.
4. Cuando se publica el número 88 (Haría), la serie termina sola.

Variables de entorno (Secrets de GitHub):
- IG_USER_ID, INSTAGRAM_ACCESS_TOKEN
Opcionales para pruebas:
- SOLO_IMAGEN=1        -> genera la imagen y el texto sin publicar ni guardar avance
- MUNICIPIO_N=12       -> fuerza un número concreto (solo con SOLO_IMAGEN=1)
"""

import json
import os
import subprocess
import sys
import time
from datetime import date

import requests
from PIL import Image, ImageDraw, ImageFont

GRAPH_URL = "https://graph.instagram.com/v21.0"
CARPETA = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_MUNICIPIOS = os.path.join(CARPETA, "datos", "municipios.json")
ARCHIVO_GEO = os.path.join(CARPETA, "datos", "canarias_municipios.json")
ARCHIVO_ESTADO = os.path.join(CARPETA, "datos", "estado.json")
CARPETA_IMAGENES = os.path.join(CARPETA, "imagenes")
LOGO = os.path.join(CARPETA, "imagenes_base", "logo.png")

# Paleta de la marca
AZUL_MARINO = (20, 49, 79)
AZUL_MEDIO = (32, 76, 115)
CREMA = (243, 240, 225)
NARANJA = (189, 116, 39)
BLANCO = (255, 255, 255)

ANCHO, ALTO = 1080, 1350  # formato vertical 4:5

FUENTE_BOLD = os.path.join(CARPETA, "fuentes", "Poppins-Bold.ttf")
FUENTE_MEDIA = os.path.join(CARPETA, "fuentes", "Poppins-Medium.ttf")
FUENTE_REGULAR = os.path.join(CARPETA, "fuentes", "Poppins-Regular.ttf")

TOTAL = 88


# ---------- Datos y avance ----------

def leer_json(ruta, por_defecto=None):
    if not os.path.exists(ruta):
        return por_defecto
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def municipio_de_hoy(municipios):
    forzado = os.environ.get("MUNICIPIO_N")
    if forzado and os.environ.get("SOLO_IMAGEN") == "1":
        n = int(forzado)
    else:
        estado = leer_json(ARCHIVO_ESTADO, {"ultimo_publicado": 0})
        n = estado["ultimo_publicado"] + 1
    if n > TOTAL:
        return None
    return next(m for m in municipios if m["n"] == n)


def guardar_estado(n):
    with open(ARCHIVO_ESTADO, "w", encoding="utf-8") as f:
        json.dump({"ultimo_publicado": n, "fecha": date.today().isoformat()}, f, ensure_ascii=False, indent=1)


# ---------- Imagen ----------

def fondo_degradado(ancho, alto, arriba, abajo):
    img = Image.new("RGB", (ancho, alto), arriba)
    draw = ImageDraw.Draw(img)
    for y in range(alto):
        t = y / alto
        color = tuple(int(arriba[i] + (abajo[i] - arriba[i]) * t) for i in range(3))
        draw.line([(0, y), (ancho, y)], fill=color)
    return img


def anillos(geometria):
    """Devuelve los anillos exteriores e interiores de un Polygon/MultiPolygon."""
    if geometria["type"] == "Polygon":
        return [geometria["coordinates"]]
    return geometria["coordinates"]


def dibujar_mapa(img, geo, municipio, caja):
    """Dibuja la isla del municipio dentro de 'caja' (x0, y0, x1, y1)."""
    import math

    isla = municipio["isla"]
    piezas = [m for m in geo["municipios"] if m["isla"] == isla]
    xs, ys = [], []
    for m in piezas:
        for poligono in anillos(m["geometry"]):
            for lon, lat in poligono[0]:
                xs.append(lon)
                ys.append(lat)
    lat_media = (min(ys) + max(ys)) / 2
    k = math.cos(math.radians(lat_media))
    ancho_geo = (max(xs) - min(xs)) * k
    alto_geo = max(ys) - min(ys)
    x0, y0, x1, y1 = caja
    escala = min((x1 - x0) / ancho_geo, (y1 - y0) / alto_geo)
    off_x = x0 + ((x1 - x0) - ancho_geo * escala) / 2
    off_y = y0 + ((y1 - y0) - alto_geo * escala) / 2

    def proyectar(lon, lat):
        return (off_x + (lon - min(xs)) * k * escala, off_y + (max(ys) - lat) * escala)

    capa = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    # Sombra suave
    for m in piezas:
        for poligono in anillos(m["geometry"]):
            d.polygon([(x + 8, y + 10) for x, y in (proyectar(*p) for p in poligono[0])], fill=(0, 0, 0, 70))
    # Municipios
    for m in piezas:
        destacado = m["ine"] == municipio["ine"]
        relleno = (*NARANJA, 255) if destacado else (*CREMA, 245)
        for poligono in anillos(m["geometry"]):
            d.polygon([proyectar(*p) for p in poligono[0]], fill=relleno, outline=(*AZUL_MEDIO, 255))
    # Contorno del municipio del día por encima
    for m in piezas:
        if m["ine"] == municipio["ine"]:
            for poligono in anillos(m["geometry"]):
                d.line([proyectar(*p) for p in poligono[0]] + [proyectar(*poligono[0][0])], fill=BLANCO, width=4)
    img.paste(capa, (0, 0), capa)


def ajustar_fuente(draw, texto, ruta_fuente, tam_max, ancho_max):
    tam = tam_max
    while tam > 20:
        fuente = ImageFont.truetype(ruta_fuente, tam)
        bbox = draw.textbbox((0, 0), texto, font=fuente)
        if bbox[2] - bbox[0] <= ancho_max:
            return fuente
        tam -= 2
    return ImageFont.truetype(ruta_fuente, tam)


def texto_centrado(draw, texto, fuente, y, color):
    bbox = draw.textbbox((0, 0), texto, font=fuente)
    draw.text(((ANCHO - (bbox[2] - bbox[0])) / 2 - bbox[0], y), texto, font=fuente, fill=color)


def partir_en_lineas(draw, texto, fuente, ancho_max):
    palabras, lineas, actual = texto.split(), [], ""
    for p in palabras:
        prueba = (actual + " " + p).strip()
        if draw.textbbox((0, 0), prueba, font=fuente)[2] <= ancho_max:
            actual = prueba
        else:
            lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    return lineas


def generar_imagen(municipio, geo, ruta_salida):
    img = fondo_degradado(ANCHO, ALTO, AZUL_MARINO, AZUL_MEDIO)
    draw = ImageDraw.Draw(img)

    texto_centrado(draw, "¿SABÍAS QUE...?", ImageFont.truetype(FUENTE_BOLD, 76), 60, BLANCO)
    texto_centrado(draw, f"LOS 88 MUNICIPIOS DE CANARIAS · {municipio['n']}/{TOTAL}",
                   ImageFont.truetype(FUENTE_MEDIA, 28), 160, NARANJA)

    dibujar_mapa(img, geo, municipio, (90, 230, ANCHO - 90, 860))
    draw = ImageDraw.Draw(img)

    nombre = municipio["municipio"].upper()
    texto_centrado(draw, nombre, ajustar_fuente(draw, nombre, FUENTE_BOLD, 72, ANCHO - 120), 885, BLANCO)

    fuente_tit = ImageFont.truetype(FUENTE_MEDIA, 36)
    lineas = partir_en_lineas(draw, municipio["titulo"], fuente_tit, ANCHO - 160)[:2]
    for i, linea in enumerate(lineas):
        texto_centrado(draw, linea, fuente_tit, 985 + i * 48, CREMA)

    # Etiqueta con el nombre de la isla
    fuente_isla = ImageFont.truetype(FUENTE_BOLD, 38)
    isla = municipio["isla"].upper()
    bbox = draw.textbbox((0, 0), isla, font=fuente_isla)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    bx, by = (ANCHO - (w + 72)) / 2, 1110
    draw.rounded_rectangle([bx, by, bx + w + 72, by + h + 32], radius=(h + 32) / 2, fill=NARANJA)
    draw.text((bx + 36 - bbox[0], by + 16 - bbox[1]), isla, font=fuente_isla, fill=AZUL_MARINO)

    if os.path.exists(LOGO):
        logo = Image.open(LOGO).convert("RGBA").resize((120, 120), Image.LANCZOS)
        img.paste(logo, ((ANCHO - 120) // 2, ALTO - 150), logo)

    img.save(ruta_salida, quality=92)


# ---------- Texto del post ----------

def construir_texto(m):
    return (
        f"🔍 ¿SABÍAS QUE...? {m['titulo']}\n"
        f"📍 {m['municipio']} · {m['isla']} ({m['n']}/{TOTAL})\n\n"
        f"{m['texto']}\n\n"
        f"✨ {m['cierre']}\n\n"
        f"📚 Fuente: {m['fuente']}\n\n"
        f"Recorremos los 88 municipios de Canarias, de El Hierro a Lanzarote, uno cada día.\n\n"
        f"{m['hashtags']}"
    )


# ---------- GitHub e Instagram ----------

def git(*args, check=True):
    return subprocess.run(["git", *args], check=check, cwd=CARPETA)


def subir_al_repositorio(rutas, mensaje):
    git("config", "user.name", "Bot de publicaciones")
    git("config", "user.email", "actions@github.com")
    git("add", *rutas)
    if git("commit", "-m", mensaje, check=False).returncode != 0:
        print("ℹ️ No había cambios nuevos que subir.")
    git("pull", "--rebase", "--autostash", check=False)
    git("push")


def obtener_variable(nombre):
    valor = os.environ.get(nombre)
    if not valor:
        sys.exit(f"❌ Falta la variable de entorno '{nombre}'. Revisa los Secrets en GitHub.")
    return valor


def esperar_imagen(creation_id, token, intentos=12, espera=5):
    for intento in range(1, intentos + 1):
        r = requests.get(f"{GRAPH_URL}/{creation_id}", params={"fields": "status_code", "access_token": token}, timeout=20)
        if r.ok:
            estado = r.json().get("status_code")
            print(f"⏳ Estado de la imagen ({intento}/{intentos}): {estado}")
            if estado == "FINISHED":
                return
            if estado == "ERROR":
                sys.exit(f"❌ Instagram no pudo procesar la imagen: {r.text}")
        time.sleep(espera)
    sys.exit("❌ Instagram tardó demasiado en procesar la imagen.")


def explicar_error(texto):
    if '"code":190' in texto.replace(" ", "") or "OAuthException" in texto:
        return ("❌ El token de Instagram no es válido o ha caducado. Genera uno nuevo en Meta for Developers "
                "y actualiza el Secret INSTAGRAM_ACCESS_TOKEN (ver README). Detalle: " + texto)
    return texto


def publicar_en_instagram(ig_user_id, token, url_imagen, texto):
    r = requests.post(f"{GRAPH_URL}/{ig_user_id}/media",
                      data={"image_url": url_imagen, "caption": texto, "access_token": token}, timeout=30)
    if not r.ok:
        sys.exit("❌ Error al crear la publicación: " + explicar_error(r.text))
    creation_id = r.json()["id"]
    esperar_imagen(creation_id, token)
    r = requests.post(f"{GRAPH_URL}/{ig_user_id}/media_publish",
                      data={"creation_id": creation_id, "access_token": token}, timeout=30)
    if not r.ok:
        sys.exit("❌ Error al publicar en Instagram: " + explicar_error(r.text))
    return r.json()


def main():
    # Una publicación al día: la ejecución programada no repite si ya se publicó hoy
    # (un lanzamiento manual sí publica, por si se quiere recuperar un día).
    if os.environ.get("GITHUB_EVENT_NAME") == "schedule" and os.environ.get("SOLO_IMAGEN") != "1":
        estado = leer_json(ARCHIVO_ESTADO, {})
        if estado.get("fecha") == date.today().isoformat():
            print("⏸️ Ya se publicó un municipio hoy. Mañana sigue la serie.")
            return
    municipios = leer_json(ARCHIVO_MUNICIPIOS)
    geo = leer_json(ARCHIVO_GEO)
    m = municipio_de_hoy(municipios)
    if m is None:
        print("🏁 La serie de los 88 municipios ya está completa. No se publica nada.")
        return

    print(f"📌 Municipio {m['n']}/{TOTAL}: {m['municipio']} ({m['isla']})")
    os.makedirs(CARPETA_IMAGENES, exist_ok=True)
    nombre_archivo = f"municipio-{m['n']:02d}.jpg"
    ruta_imagen = os.path.join(CARPETA_IMAGENES, nombre_archivo)
    generar_imagen(m, geo, ruta_imagen)
    texto = construir_texto(m)

    if os.environ.get("SOLO_IMAGEN") == "1":
        print("🧪 Modo prueba: imagen generada en", ruta_imagen)
        print(texto)
        return

    ig_user_id = obtener_variable("IG_USER_ID")
    token = obtener_variable("INSTAGRAM_ACCESS_TOKEN")
    repo = obtener_variable("GITHUB_REPOSITORY")

    subir_al_repositorio([os.path.join("imagenes", nombre_archivo)], f"Imagen del municipio {m['n']}: {m['municipio']}")
    url = f"https://raw.githubusercontent.com/{repo}/main/imagenes/{nombre_archivo}"
    time.sleep(10)  # margen para que GitHub sirva ya la imagen

    resultado = publicar_en_instagram(ig_user_id, token, url, texto)
    print("✅ Publicado en Instagram:", resultado)

    guardar_estado(m["n"])
    subir_al_repositorio([os.path.join("datos", "estado.json")], f"Publicado municipio {m['n']}: {m['municipio']}")


if __name__ == "__main__":
    main()
