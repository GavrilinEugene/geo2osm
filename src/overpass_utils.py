import requests
from osm2geojson import json2geojson

def get_geojson(bbox, list_node_types = ['way["building"]']):
    """

    """
    (left, bottom, right, top) = bbox
    way_query = ""
    for node_type in list_node_types:
        way_query += f"{node_type}({bottom},{left},{top},{right});\n"
    query = f"""
        [out:json][timeout:25];
        ({way_query}
        );
        out body;
        >;
        out skel qt;
    """
    url = "http://overpass-api.de/api/interpreter"
    r = requests.get(url, params={'data': query})
    if r.status_code != 200:
        raise requests.exceptions.HTTPError(f'Overpass server respond with status {r.status_code}')

    data = json2geojson(r.json())
    for x in range(0, len(data['features'])):
        data['features'][x]['id'] = data['features'][x]['properties']['id']
    return data
