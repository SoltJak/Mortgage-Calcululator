import json
import logging
import os

import dash

from flask_caching import Cache
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

from callbacks import get_callbacks
import app_layout

# Start logging
logging.basicConfig(level=logging.DEBUG)

# Set up APP
external_stylesheets = []
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server  # used by gunicorn in production mode
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

# Set up styling
# This has to do with layout/styling
fig_layout_defaults = dict(
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
)
load_figure_template('DARKLY')

# Application layout
app.layout = app_layout.layout

# App callbacks
get_callbacks(app)

# Run app
if __name__ == '__main__':
    app.run_server(debug=True)