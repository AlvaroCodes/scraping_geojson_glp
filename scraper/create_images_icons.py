import os
import requests
from pathlib import Path
from io import BytesIO
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from .rest_busqueda_estaciones_mapa import get_data_rest_busqueda_estaciones_mapa


def get_names(data):
    names = set()
    for estacion in data["estaciones"]["listaEstaciones"]:
        imagen_eess = estacion.get("imagenEESS", "")
        if imagen_eess:
            name = imagen_eess.split("\\")[-1]
            names.add(name)
    return names


def get_icons(data, path, base_url):
    # Crear la carpeta si no existe
    os.makedirs(path, exist_ok=True)

    for name in get_names(data):
        file_path = os.path.join(path, name)
        # Saltar si ya existe la versión limpia
        if os.path.exists(file_path):
            print(f"El archivo ya existe: {file_path}")
            continue

        # Descargar imagen PNG
        try:
            response = requests.get(base_url + name, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error al descargar {name}: {e}")
            continue

        # Abrir en memoria y limpiar metadatos
        try:
            img = Image.open(BytesIO(response.content))
            # Crear contenedor de metadata vacío
            meta = PngInfo()
            # Guardar sólo píxeles, sin metadatos
            img.save(file_path, format='PNG', pnginfo=meta)
        except Exception as e:
            print(f"Error al procesar {name}: {e}")

def create_images_icons():
    project_root = Path(__file__).parents[1]
    img_dir = project_root / "data" / "images"
    data = get_data_rest_busqueda_estaciones_mapa()

    print(f"Se encontraron {len(get_names(data))} iconos.")
    get_icons(data, str(img_dir), "https://geoportal.minetur.gob.es/symbols/logosEESS/")
    print(f"Imágenes guardadas en: {img_dir}")