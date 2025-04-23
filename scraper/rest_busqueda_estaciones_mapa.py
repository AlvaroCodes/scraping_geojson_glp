import requests
import time

URL = "https://geoportalgasolineras.es/geoportal/rest/busquedaEstacionesMapa"
ARCHIVO_JSON = "gasolineras-glp"
PAYLOAD = {
        "tipoEstacion": "EESS",
        "idProvincia": "",
        "idMunicipio": "",
        "idProducto": "17",
        "rotulo": "",
        "eessEconomicas": False,
        "conPlanesDescuento": False,
        "horarioInicial": "",
        "horarioFinal": "",
        "calle": "",
        "numero": "",
        "codPostal": "",
        "tipoVenta": "P",
        "tipoServicio": None,
        "idOperador": "",
        "nombrePlan": "",
        "idTipoDestinatario": None,
        "x0": "",
        "y0": "",
        "x1": "",
        "y1": ""
    }

def get_data():
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(URL, headers=headers, json=PAYLOAD)
    data = response.json()

    return data

def get_data_rest_busqueda_estaciones_mapa(retries=3):
    """
    Recursively fetches data from the API with retries.
    """
    for attempt in range(retries):
        try:
            data = get_data()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if attempt < retries - 1:
                print(f"Retrying... Attempt {attempt + 1} of {retries}")
                time.sleep(2)  # Wait before retrying
    return None
