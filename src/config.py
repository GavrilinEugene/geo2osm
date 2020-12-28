from pathlib import Path
import os


def get_project_root() -> str:
    return str(Path(os.path.dirname(os.path.abspath(__file__))).parent)


def get_mapbox_token() -> str:
    return 'pk.eyJ1IjoiZXZnZW5paWdhdnJpbGluIiwiYSI6ImNrMG50N3ptdjAzNW8zbm8wZzVmaXpzcWoifQ.LMSJohnSoBN-6YlAgKPO0w'
    # return os.environ.get('MAPBOX_ACCESS_TOKEN')


default_data = [dict(
    lat=[51.98799603],
    lon=[5.922999562],
    type='scattermapbox',
    marker=[dict(size=5, color='white', opacity=0)]
)]

default_coord = dict(lat=55.749062, lon=37.540283)

dict_map_type = dict(navigation=dict(margin=dict(l=10, r=10, b=0, t=10), style="open-street-map"),
                     result=dict(margin=dict(l=10, r=10, b=0, t=10), style="open-street-map"))


print(get_project_root())
