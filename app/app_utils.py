from pathlib import Path
import os


def get_project_root() -> str:
    return str(Path(os.path.dirname(os.path.abspath(__file__))).parent)

def get_project_tmp_data_path() -> str:
    return get_project_root() + "/data/tmp_data"

def get_model_path() -> str:
    return get_project_root() + "/models/model.pkl"


def get_mapbox_token() -> str:
    return 'pk.eyJ1IjoiZXZnZW5paWdhdnJpbGluIiwiYSI6ImNrMG50N3ptdjAzNW8zbm8wZzVmaXpzcWoifQ.LMSJohnSoBN-6YlAgKPO0w'
    # return os.environ.get('MAPBOX_ACCESS_TOKEN')

def get_default_data() -> list:
    return [dict(
        lat=[51.98799603],
        lon=[5.922999562],
        type='scattermapbox',
        marker=[dict(size=5, color='white', opacity=0)]
    )]

def get_default_coord() -> dict:
    return dict(lat=55.749062, lon=37.540283)
