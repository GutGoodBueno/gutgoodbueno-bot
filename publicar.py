"""
Script de publicación diaria para @gutgoodbueno
--------------------------------------------------
Cada día:
1. Elige una curiosidad de Canarias del archivo curiosidades.json
   (rota automáticamente según el día del año, sin repetir hasta
   agotar la lista completa).
2. Busca una foto relacionada en Pexels (banco de imágenes gratuito).
3. Publica el post en Instagram usando la API de Instagram Graph.

Variables de entorno necesarias (se configuran como "Secrets" en GitHub):
- IG_USER_ID              -> identificador numérico de tu cuenta de Instagram
- INSTAGRAM_ACCESS_TOKEN  -> el token que generaste en Meta for Developers
- PEXELS_API_KEY          -> tu clave gratuita de https://www.pexels.com/api/
"""

import os
import json
import random
import sys
import time
from datetime import date

import requests

GRAPH_URL = "https://graph.instagram.com/v21.0"
CARPETA = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_CURIOSIDADES = os.path.join(CARPETA, "curiosidades.json")


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


def buscar_imagen(pexels_api_key, curiosidad):
    # Si has fijado una foto concreta para esta curiosidad, se usa esa siempre
    if curiosidad.get("imagen_fija"):
        return curiosidad["imagen_fija"]

    headers = {"Authorization": pexels_api_key}
    intentos_busqueda = curiosidad["busquedas_imagen"] + ["Canary Islands nature landscape"]

    for busqueda in intentos_busqueda:
        params = {"query": busqueda, "per_page": 8, "orientation": "square"}
        resp = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=20)
        resp.raise_for_status()
        fotos = resp.json().get("photos", [])
        if fotos:
            print(f"🔎 Búsqueda usada: '{busqueda}' ({len(fotos)} resultados)")
            foto_elegida = random.choice(fotos)
            return foto_elegida["src"]["large"]

    sys.exit("❌ No se ha encontrado ninguna imagen en Pexels, ni siquiera con la búsqueda de respaldo.")


def construir_texto(curiosidad):
    return (
        f"🔍 SABÍAS QUE... {curiosidad['titulo']}\n"
        f"📍 {curiosidad['isla']}\n\n"
        f"{curiosidad['texto']}\n\n"
        f"✨ {curiosidad['cierre']}\n\n"
        f"{curiosidad['hashtags']}"
    )


def esperar_a_que_la_imagen_este_lista(creation_id, access_token, intentos=12, espera_segundos=5):
    """Instagram tarda unos segundos en descargar y procesar la imagen antes de
    poder publicarla. Aquí preguntamos varias veces, con pausas, hasta que
    confirme que está lista (status_code = FINISHED)."""
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
    # Paso 1: crear el contenedor de la publicación
    resp_crear = requests.post(
        f"{GRAPH_URL}/{ig_user_id}/media",
        data={
            "image_url": url_imagen,
            "caption": texto,
            "access_token": access_token,
        },
        timeout=30,
    )
    if not resp_crear.ok:
        sys.exit(f"❌ Error al crear la publicación: {resp_crear.text}")

    creation_id = resp_crear.json()["id"]

    # Paso 2: esperar a que Instagram termine de procesar la imagen
    esperar_a_que_la_imagen_este_lista(creation_id, access_token)

    # Paso 3: publicar el contenedor creado
    resp_publicar = requests.post(
        f"{GRAPH_URL}/{ig_user_id}/media_publish",
        data={
            "creation_id": creation_id,
            "access_token": access_token,
        },
        timeout=30,
    )
    if not resp_publicar.ok:
        sys.exit(f"❌ Error al publicar en Instagram: {resp_publicar.text}")

    return resp_publicar.json()


def main():
    ig_user_id = obtener_variable_entorno("IG_USER_ID")
    access_token = obtener_variable_entorno("INSTAGRAM_ACCESS_TOKEN")
    pexels_api_key = obtener_variable_entorno("PEXELS_API_KEY")

    curiosidades = cargar_curiosidades()
    curiosidad = elegir_curiosidad_de_hoy(curiosidades)
    print(f"📌 Curiosidad de hoy: {curiosidad['titulo']}")

    url_imagen = buscar_imagen(pexels_api_key, curiosidad)
    print(f"🖼️  Imagen encontrada: {url_imagen}")

    texto = construir_texto(curiosidad)
    resultado = publicar_en_instagram(ig_user_id, access_token, url_imagen, texto)

    print("✅ Publicado correctamente en Instagram.")
    print(resultado)


if __name__ == "__main__":
    main()
