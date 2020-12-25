# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
# from .config import default_coord, default_data, dict_map_type
from dash.dependencies import Input, Output, State
from plotly import graph_objs as go


default_data = [dict(
        lat=[51.98799603],
        lon=[5.922999562],
        type='scattermapbox',
        marker=[dict(size=5, color='white', opacity=0)]
    )]

default_coord = dict(lat=55.749062, lon=37.540283)

dict_map_type = dict(navigation=dict(margin=dict(l=10, r=10, b=0, t=10), style="open-street-map"),
                     result=dict(margin=dict(l=10, r=10, b=0, t=10), style="open-street-map"))

app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
server = app.server
app.title = 'geo2osm'
mapbox_access_token = 'pk.eyJ1IjoiZXZnZW5paWdhdnJpbGluIiwiYSI6ImNrMG50N3ptdjAzNW8zbm8wZzVmaXpzcWoifQ.LMSJohnSoBN-6YlAgKPO0w'

def __update_map_layout(map_type, zoom, center_coord):
    """

    """
    map_layout = dict(
        autosize=True,
        automargin=True,
        # height=1050,
        margin=dict_map_type[map_type]["margin"],
        hovermode="closest",
        # legend=dict(font=dict(size=14), orientation='h'),
        mapbox=dict(accesstoken=mapbox_access_token,
                    style=dict_map_type[map_type]["style"],
                    zoom=zoom,
                    center=center_coord)
    )
    return map_layout


def update_map_data(map_type):
    map_layout = __update_map_layout(
        map_type, zoom=11, center_coord=default_coord)
    figure = dict(data=default_data, layout=map_layout)
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
    ]
)


@app.callback(
    Output(component_id='result_map', component_property='figure'),
    Output(component_id='result_map', component_property='config'),
    [Input(component_id='navigation_map', component_property='relayoutData')]
)
def update_map(relayoutData):
    if relayoutData == None:
        return
    if relayoutData.get('mapbox.center', 0) != 0:
        map_layout = __update_map_layout(
            'result', zoom=relayoutData['mapbox.zoom'], center_coord=relayoutData['mapbox.center'])
        figure = dict(data=default_data, layout=map_layout)
        map_config = dict(scrollZoom = True)
        return figure, map_config


if __name__ == '__main__':
    app.run_server(debug=True)
