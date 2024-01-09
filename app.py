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
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], title='Mortgage Calculator')
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

def show_in_native_window(app: dash.Dash) -> None:
    """
    This function will launch a minimal browser window, and shut down when this window is closed,
    to give the look & feel of a native application.
    Per: https://gist.github.com/adamgreg/cc1abd2123cf820d9e71bf3afb5e63f5
    """

    from threading import Timer

    import flask
    import native_web_app 

    # Add URL that can be used to shut down the Dash application
    @app.server.route('/shutdown', methods=['GET', 'POST'])
    def shutdown():
        func = flask.request.environ.get('werkzeug.server.shutdown')
        if func is not None:
            func()
        return ''

    # Add Javascript that POSTs to the shutdown URL when the window is closed
    shutdown_js = "window.addEventListener('pagehide', () => {navigator.sendBeacon('/shutdown');});"
    app.config.external_scripts.append('data:,' + shutdown_js)

    def open_native_window():
        native_web_app.open('http://127.0.0.1:8050')

    # Open the application in a local window once the Dash server has had some time to start
    Timer(1, open_native_window).start()
    
    # Start the Dash application
    app.run_server()

# Run app
if __name__ == '__main__':
    show_in_native_window(app)