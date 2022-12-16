''' This file contains application main body '''

import logging

import dash

from flask_caching import Cache
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

import app_layout
from data_calc_callbacks import data_callbacks
from input_tab import input_callbacks
from output_tab import output_callbacks
from language_mod import lang_callbacks
import mortgage as mD

# Start logging
logging.basicConfig(level=logging.DEBUG)

# Set up APP
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server  # used by gunicorn in production mode
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

load_figure_template('FLATLY')

# Application layout
app.layout = app_layout.layout

# App callbacks
data_callbacks(app)
input_callbacks(app)
output_callbacks(app)
lang_callbacks(app)

# Run app
if __name__ == '__main__':
    app.run_server(debug=True)