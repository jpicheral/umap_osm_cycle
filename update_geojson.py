import os
import requests
import json

# URL de l'API Overpass
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Requête Overpass pour extraire des pistes cyclables avec divers tags
QUERY = """
[out:json][timeout:125];
(
  way["highway"="cycleway"]({{bbox}});
  way["cycleway"]({{bbox}});
  way["cycleway:left"]({{bbox}});
  way["cycleway:right"]({{bbox}});
  way["cycleway:both"]({{bbox}});
  way[highway=path][bicycle=designated]({{bbox}});
);
out geom;
"""

# Définir une zone géographique (remplacez par les coordonnées souhaitées)
BBOX = "48.526639171910894,1.8525698326088416,48.865647379541315,2.412872566983842"  # Coordonnées pour Paris-Saclay

# Fichier de sortie GeoJSON
OUTPUT_FILE = "data_layer.geojson"

def fetch_osm_data():
    """Récupérer les données depuis l'API Overpass."""
    print("Fetching data from Overpass...")
    # Injecter la bbox dans la requête
    final_query = QUERY.replace("{{bbox}}", BBOX)
    response = requests.post(OVERPASS_URL, data={"data": final_query})
    if response.status_code == 200:
        print("Data fetched successfully.")
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        print(response.text)
        return None

def save_as_geojson(data):
    """Convertir les données OSM au format GeoJSON et les sauvegarder."""
    print("Saving data as GeoJSON...")
    features = []

    # Parcourir chaque « way » extrait
    for element in data.get("elements", []):
        if element["type"] == "way" and "geometry" in element:
            # Géométrie de type LineString
            geometry = {
                "type": "LineString",
                "coordinates": [[point["lon"], point["lat"]] for point in element["geometry"]]
            }
            # Propriétés associées au chemin
            feature = {
                "type": "Feature",
                "geometry": geometry,
                "properties": element.get("tags", {})
            }
            features.append(feature)

    # Construction de l'objet GeoJSON
    geojson = {"type": "FeatureCollection", "features": features}
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=4)
    print(f"GeoJSON saved to {OUTPUT_FILE}.")

def main():
    print("Starting GeoJSON update process...")
    data = fetch_osm_data()
    if data:
        save_as_geojson(data)
    print("Process completed.")

if __name__ == "__main__":
    main()
