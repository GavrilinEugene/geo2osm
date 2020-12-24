# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
# import dash_table_experiments as dt
import pandas as pd

from plotly import graph_objs as go
from plotly.graph_objs import *
from dash.dependencies import Input, Output, State, Event

app = dash.Dash(__name__)
server = app.server
app.title = 'geo2osm'

layout_map = dict(
    autosize=True,
    height=500,
    font=dict(color="#191A1A"),
    titlefont=dict(color="#191A1A", size='14'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor='#fffcfc',
    paper_bgcolor='#fffcfc',
    legend=dict(font=dict(size=10), orientation='h'),
    # title='WiFi Hotspots in NYC',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(
            lon=-73.91251,
            lat=40.7342
        ),
        zoom=10,
    )
)


if __name__ == '__main__':
    app.run_server(debug=True)
