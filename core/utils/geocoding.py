# core/utils/geocoding.py
import requests
from django.conf import settings

def obtener_lat_lng(direccion_completa):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": direccion_completa,
        "key": settings.GOOGLE_MAPS_API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
    return None, None
