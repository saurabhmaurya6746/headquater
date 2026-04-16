import requests
import math

API_KEY = "ed9052c8a57d4ad9a9d16687b7e3dd77"

# Convert address → lat, long
def get_lat_long(address):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={address}&key={API_KEY}"
    res = requests.get(url).json()
    
    if res['results']:
        lat = res['results'][0]['geometry']['lat']
        lng = res['results'][0]['geometry']['lng']
        return lat, lng
    return None, None


# Haversine formula (distance in KM)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius (km)

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c