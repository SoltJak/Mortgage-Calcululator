
import json
import logging
import os

import dash
# from dash.dependencies import Input, Output, State
from dash import Dash, dash_table, dcc, html

from flask_caching import Cache
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

import plotly.graph_objs as go

# Import mortgageData class
from mortgage import mortgageData as mD

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

# Initial Data:
mortgage = mD(.02, .075, 300000, 360, 'fixed')

# Application layout
app.layout = html.Div(className='app-body', children=[
    # # Stores
    # dcc.Store(id='map_clicks', data=0),
    # dcc.Store(id='zone', data=zone_initial),
    # dcc.Store(id='trip_start', data=trip_start_initial),
    # dcc.Store(id='trip_end', data=trip_end_initial),
    # dcc.Store(id='heatmap_limits', data=heatmap_limits_initial),
    # About the app
    html.Div(className="row", children=[
        html.Div(className='twelve columns', children=[
            html.Div(style = {"margin-left": "7px", "margin-top": "7px"}, children=[
                    html.H1('Mortgage Calculator'),
                    html.H4("Check your installment amount and payment schedule!")
                ]
            ),
        ]),
    ]),
    # Input data tab
    html.Div(dbc.Accordion(
        [
            dbc.AccordionItem(
                [
                    # html.P("Modify your mortgage parameters"),
                    html.Div(children=[
                        html.Div(className="row",
                            children=[
                                dbc.Col(children=[html.Div(children="Loan Amount", className="menu-title"),
                                dbc.Input(
                                    id="principal_value",
                                    type="number",
                                    placeholder="Mortgage amount",
                                    value=mortgage.loanAmount,
                                )], width=2),
                                dbc.Col(children=[html.Div(children="Number of Installments", className="menu-title"),
                                dbc.Input(
                                    id="no_of_installments",
                                    type="number",
                                    placeholder="Number of Installments",
                                    value=mortgage.noOfInstallments,
                                )], width=2),
                                dbc.Col(children=[html.Div(children="Installments Type", className="menu-title"),
                                dcc.Dropdown(
                                    id="installments_type",
                                    options=[
                                        {'label': 'Fixed', 'value': 'fixed'},
                                        {'label': 'Descending', 'value': 'desc'},
                                    ],
                                    clearable=False,
                                    searchable=False,
                                    value=mortgage.installmentsType,
                                    className="dropdown"
                                )], width=2),
                                dbc.Col(children=[
                                    html.Div(children="Bank Interest", className="menu-title"),
                                    dbc.InputGroup([
                                        dbc.Input(
                                            id="bank_interest",
                                            type="number",
                                            placeholder="Bank Interest",
                                            value=mortgage.bankInterestRate*100,
                                        ),
                                        dbc.InputGroupText("%")
                                    ])
                                ], width=2),
                                dbc.Col(children=[
                                    html.Div(children="WIBOR Interest", className="menu-title"),
                                    dbc.InputGroup([
                                        dbc.Input(
                                            id="wibor_interest",
                                            type="number",
                                            placeholder="WIBOR Interest",
                                            value=mortgage.wiborInterestRate*100,
                                        ),
                                        dbc.InputGroupText("%")
                                    ])
                                ], width=2)
                            ]
                        ),]),
                    dbc.Button("Recalculate"),
                ],
                title="Modify your mortgage parameters",
            )
        ],
    )),
    # The Visuals
    html.Div(className="row", children=[
        # Define scatter plot to show monthly installments
        dbc.Col(html.Div(style = {"margin-left": "7px", "margin-top": "7px"}, className="four columns pretty_container", children=[
            dcc.Graph(id='monthly_install_chart',
                        figure=mortgage.monthlyInstallmentsScatter_fig,
                        config={"modeBarButtonsToRemove": ['lasso2d', 'select2d']})
        ])),
        # Define scatter plot to show yearly installments
        dbc.Col(html.Div(className="four columns pretty_container", children=[
            dcc.Graph(id='yearly_install_chart',
                        figure=mortgage.yearlyInstallmentsScatter_fig),
        ]))]),
    html.Div(className="row", children=[
        # Define pie plot to show split of payment (interest vs. principal)
        dbc.Col(html.Div(className="four columns pretty_container", children=[
            dcc.Graph(id='pie_plot_split',
                        figure=mortgage.paymentSplit_piePlot_fig),
        ]), width=4),
        # Define heat map plot to show WIBOR effect on installment amount
        dbc.Col(html.Div(className="four columns pretty_container", children=[
            dcc.Graph(id='pie_plot_split',
                        figure=mortgage.wiborEffect_HeatMap_fig),
        ]), width=8)]),
    html.Div(className="row", children=[    
        # Define table to show payments schedule (monthly)
        dbc.Col(html.Div(className="four columns pretty_container", children=[
            dcc.Graph(id='pie_plot_split',
                        figure=mortgage.installmentsTable_monthly),
        ])),
        # Define table to show payments schedule (yearly)
        dbc.Col(html.Div(className="four columns pretty_container", children=[
            dcc.Graph(id='pie_plot_split',
                        figure=mortgage.installmentsTable_yearly),
                ]))            
            ]),
    html.Div(className="row", children=[    
        # Define table to show payments schedule (monthly)
        dbc.Col(html.Div(className="four columns pretty_container", children=[
            dcc.Tabs(id='tabs', children=[
                dcc.Tab(label='Monthly', id='tab_monthly', children=[
                    dbc.Card(dbc.CardBody(
                        [
                            dcc.Graph(id='yearly_install_chart',
                                            figure=mortgage.monthlyInstallmentsScatter_fig)
                        ]
                    ))
                ]),
                dcc.Tab(label='Yealy', id='tab_yearly', children=[
                    dbc.Card(dbc.CardBody(
                        [
                            dcc.Graph(id='yearly_install_chart',
                                            figure=mortgage.yearlyInstallmentsScatter_fig)
                        ]
                    ))
                ])
            ])
        ]), width=8),
                # Define pie plot to show split of payment (interest vs. principal)
        dbc.Col(html.Div(className="four columns pretty_container", children=[
            dcc.Graph(id='pie_plot_split',
                        figure=mortgage.paymentSplit_piePlot_fig),
        ]), width=4),
    ])
])
# # App callbacks
# @app.callback(
#     Output('out', 'children'),
#     Output('err', 'children'),
#     Input('bank_interest', 'value')
# )
# def update_interest(bank_interest):
#     mortgage.bankInterestRate = bank_interest
if __name__ == '__main__':
    app.run_server(debug=True)