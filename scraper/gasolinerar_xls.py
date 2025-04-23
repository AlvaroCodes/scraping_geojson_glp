import requests
import pandas as pd
import json
import uuid
import time
from pathlib import Path
from .rest_busqueda_estaciones_mapa import get_data_rest_busqueda_estaciones_mapa

URL_XLS = "https://geoportalgasolineras.es/geoportal/resources/files/preciosEESS_es.xls"
RETRIES = 4

def recursive_dowload_xls(url, retries=3):
    """
    Recursively download the XLS file with retries.
    """
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            with open("preciosEESS_es.xls", "wb") as file:
                file.write(response.content)
            print("XLS file downloaded successfully.")
            return
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                print("Retrying...")
                time.sleep(2)
    print("Failed to download the XLS file after multiple attempts.")

def download_xls(url):
    """
    Download the XLS file from the given URL.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open("preciosEESS_es.xls", "wb") as file:
            file.write(response.content)
        print("XLS file downloaded successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading XLS file: {e}")

def generate_json_from_xls():
    df = pd.read_excel('preciosEESS_es.xls', engine='xlrd', skiprows=3)

    columna_objetivo = 'Precio gases licuados del petróleo'
    df_filtrado = df[df[columna_objetivo].notnull()]

    df_filtrado.to_json('filtrado_gases.json', orient='records', force_ascii=False, indent=2)

def generate_geojson_data():
    data_img = data = get_data_rest_busqueda_estaciones_mapa()
    with open('filtrado_gases.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    features = []
    for estacion in data:
        if estacion.get("Tipo venta") != "P":
            continue
        
        img_logo = get_imagenEESS_by_coord(data_img, (float(estacion["Longitud"].replace(',', '.')), float(estacion["Latitud"].replace(',', '.'))))

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    float(estacion["Longitud"].replace(',', '.')),  # Longitud
                    float(estacion["Latitud"].replace(',', '.'))   # Latitud
                ]
            },
            "properties": {
                "id": str(uuid.uuid4()),
                "precio": estacion.get("Precio gases licuados del petróleo"),
                "rotulo": estacion.get("Rótulo"),
                "direccion": estacion.get("Dirección"),
                "codPostal": estacion.get("Código postal"),
                "localidad": estacion.get("Localidad"),
                "provincia": estacion.get("Provincia"),
                "horario": estacion.get("Horario"),
                "imagenEESS": img_logo.split("//")[-1],
                # Coordenadas
                "coordenadaX": float(estacion["Longitud"].replace(',', '.')),
                "coordenadaY": float(estacion["Latitud"].replace(',', '.')),
            }
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }

def generate_geosjon_from_xls():
    # download_xls(URL_XLS)
    recursive_dowload_xls(URL_XLS, RETRIES)
    generate_json_from_xls()
    geojson_data = generate_geojson_data()

    project_root = Path(__file__).parents[1]
    data_dir = project_root / "data" / "gasolineras-glp.geojson"

    with open(data_dir, "w", encoding="utf-8") as f:
        json.dump(geojson_data, f, ensure_ascii=False, indent=4)

    print("GeoJSON file generated successfully.")

def get_imagenEESS_by_coord(data, coord):
    """
    Get the image URL for a given coordinate.
    """
    for estacion in data["estaciones"]["listaEstaciones"]:
        if (estacion["coordenadaX_dec"] == coord[0] and estacion["coordenadaY_dec"] == coord[1]):
            return estacion["imagenEESS"]
    return None
