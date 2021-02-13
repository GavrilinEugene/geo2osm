# -*- coding: utf-8 -*-
# dash components
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

# python libraries
from plotly import graph_objs as go
import pandas as pd

# own libraries
import app.app_utils  as app_utils
from app.tile_utils import TileUtils
from app.overpass_utils import get_geojson


app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
server = app.server
# model = Geo2osmModel(app_utils.get_model_path(),
#                      app_utils.get_project_tmp_data_path())
app.title = 'geo2osm'


def __update_map_layout(zoom, center_coord):
    """

    """
    map_layout = dict(
        autosize=True,
        automargin=True,
        margin=dict(l=10, r=10, b=0, t=10),
        hovermode="closest",
        mapbox=dict(accesstoken=app_utils.get_mapbox_token(),
                    style="satellite",
                    zoom=zoom,
                    center=center_coord)
    )
    return map_layout


def update_map_data(zoom=11, center_coord=app_utils.get_default_coord(), data=app_utils.get_default_data()):
    """
    
    """
    map_layout = __update_map_layout(zoom=zoom, center_coord=center_coord)
    figure = dict(data=data, layout=map_layout)
    return figure


app.layout = html.Div(
    [
        dbc.Row(dbc.Col(html.Div("Geo2Osm"), width=6)),

        dbc.Row(
            [
                dbc.Col(html.Div(dcc.Graph(id='navigation_map',
                                           figure=update_map_data())), width=12),
            ]
        ),
        dbc.Row(dbc.Col(html.Button('Generate', id='generate', n_clicks=0), width=3))
    ]
)


def get_bounding_box(relayoutData):
    left = relayoutData['mapbox._derived']['coordinates'][0][0]
    bottom = relayoutData['mapbox._derived']['coordinates'][2][1]
    right = relayoutData['mapbox._derived']['coordinates'][1][0]
    top = relayoutData['mapbox._derived']['coordinates'][0][1]
    return [left, bottom, right, top]


@app.callback(
    Output(component_id='navigation_map', component_property='figure'),
    [Input(component_id='generate', component_property='n_clicks'),
     Input(component_id='navigation_map', component_property='relayoutData')]
)
def update_map(n_clicks, relayoutData):
    if relayoutData == None or n_clicks == None:
        raise PreventUpdate

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if "generate" in changed_id:
        tile_params = {"api_token": app_utils.get_mapbox_token(),
                       "tile_size": 256,
                       "tmp_dir": app_utils.get_project_tmp_data_path()}
        tileGen = TileUtils(tile_params)
        _ = tileGen.get_map(get_bounding_box(
            relayoutData), int(relayoutData['mapbox.zoom'] + 1))

        geo_json = get_geojson(get_bounding_box(relayoutData))

        df = pd.DataFrame([geo_json['features'][x]['properties']['id']
                           for x in range(0, len(geo_json['features']))],
                          columns=['osm_id'])
        result_figure = update_map_data(
            relayoutData['mapbox.zoom'], relayoutData['mapbox.center'])
        result_figure['data'].append(
            go.Choroplethmapbox(geojson=geo_json, locations=df.osm_id, z=df.osm_id))
        return result_figure
    raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True)
