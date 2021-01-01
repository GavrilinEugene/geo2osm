# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.exceptions import PreventUpdate
import src.app_utils as app_utils
from dash.dependencies import Input, Output, State
from plotly import graph_objs as go
from src.tiles import TileUtils


dict_map_type = dict(navigation=dict(margin=dict(l=10, r=10, b=0, t=10), style="open-street-map"),
                     result=dict(margin=dict(l=10, r=10, b=0, t=10), style="open-street-map"))

app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
server = app.server
app.title = 'geo2osm'

def __update_map_layout(map_type, zoom, center_coord):
    """

    """
    map_layout = dict(
        autosize=True,
        automargin=True,
        margin=dict_map_type[map_type]["margin"],
        hovermode="closest",
        mapbox=dict(accesstoken=app_utils.get_mapbox_token(),
                    style=dict_map_type[map_type]["style"],
                    zoom=zoom,
                    center=center_coord)
    )
    return map_layout


def update_map_data(map_type):
    map_layout = __update_map_layout(
        map_type, zoom=11, center_coord=app_utils.get_default_coord())
    figure = dict(data=app_utils.get_default_data(), layout=map_layout)
    return figure


app.layout = html.Div(
    [
        dbc.Row(dbc.Col(html.Div("Geo2Osm"), width=6)),

        dbc.Row(
            [
                dbc.Col(html.Div(dcc.Graph(id='navigation_map',
                                           figure=update_map_data("navigation"))), width=6),
                dbc.Col(html.Div(dcc.Graph(id='result_map',
                                           figure=update_map_data("result"),
                                           config={'staticPlot': True}
                                           )), width=6),
            ]
        ),
        dbc.Row(dbc.Col(html.Button('Generate', id='generate', n_clicks=0),width=3))
    ]
)

def get_bounding_box(relayoutData):
    left = relayoutData['mapbox._derived']['coordinates'][0][0]
    bottom = relayoutData['mapbox._derived']['coordinates'][2][1]
    right = relayoutData['mapbox._derived']['coordinates'][1][0]
    top = relayoutData['mapbox._derived']['coordinates'][0][1]
    return [left, bottom, right, top]

@app.callback(
    Output(component_id='result_map', component_property='figure'),
    Output(component_id='result_map', component_property='config'),
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
        tileGen.get_map(get_bounding_box(relayoutData), int(relayoutData['mapbox.zoom'] + 2))
    
    if relayoutData.get('mapbox.center', 0) != 0:
        map_layout = __update_map_layout(
            'result', zoom=relayoutData['mapbox.zoom'], center_coord=relayoutData['mapbox.center'])
        result_figure = dict(data=app_utils.get_default_data(), layout=map_layout)
        map_config = dict(scrollZoom = True)
        return result_figure, map_config


if __name__ == '__main__':
    app.run_server(debug=True)
