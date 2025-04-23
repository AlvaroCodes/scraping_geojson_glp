import json
import requests
import time
from pathlib import Path

from .rest_busqueda_estaciones_mapa import get_data_rest_busqueda_estaciones_mapa

def get_station_info(id):
    try:
        print(f"Fetching data for station ID: {id}")
        
        url = f"https://geoportalgasolineras.es/geoportal/rest/{id}/busquedaEstacion"
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers, timeout=10)
        # print 
        if response.status_code == 200:
            data = response.json()
            return {
                "rotulo": data.get("rotulo"),
                "direccion": data.get("direccion"),
                "codPostal": data.get("codPostal"),
                "localidad": data.get("localidad"),
                "provincia": data.get("provincia"),
                "venta": data.get("tipoVenta"),
                "horario": data.get("horario"),
                "coordenadaX": data.get("coordenadaX"),
                "coordenadaY": data.get("coordenadaY"),
            }
        else:
            print(f"Error: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    
def recursive_get_station_info(id, retries=3):
    """
    Recursively fetches station information with retries.
    """
    for attempt in range(retries):
        station_info = get_station_info(id)
        if station_info is not None:
            return station_info
        print(f"Retrying... Attempt {attempt + 1} of {retries}")
        time.sleep(2)  # Wait before retrying
    return None
    
def generate_geojson(filename="gasolineras-glp"):
    data = get_data_rest_busqueda_estaciones_mapa()

    features = []
    for estacion in data["estaciones"]["listaEstaciones"]:
        estaciones = recursive_get_station_info(estacion.get("id"))
        if estaciones is None:
            print(f"Skipping station ID: {estacion.get('id')}")
            continue
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    estacion["coordenadaX_dec"],  # Longitud
                    estacion["coordenadaY_dec"]   # Latitud
                ]
            },
            "properties": {
                "id": estacion.get("id"),
                "precio": estacion.get("precio"),
                "imagenEESS": estacion.get("imagenEESS").split("\\")[-1],
                "rotulo": estaciones.get("rotulo"),
                "direccion": estaciones.get("direccion"),
                "codPostal": estaciones.get("codPostal"),
                "localidad": estaciones.get("localidad"),
                "provincia": estaciones.get("provincia"),
                "venta": estaciones.get("venta"),
                "horario": estaciones.get("horario"),
                "coordenadaX": estaciones.get("coordenadaX"),
                "coordenadaY": estaciones.get("coordenadaY"),
            }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    project_root = Path(__file__).parents[1]
    data_dir = project_root / "data" / f"{filename}.geojson"

    with open(data_dir, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=4)

    print("Archivo GeoJSON creado: gasolineras-glp.geojson")



