from dash import Dash, dash_table, dcc, html

from flask_caching import Cache
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from mortgage import mortgageData as mD

# Import layout components
import input_tab as itab
import output_tab as otab

# Initial Data:
mortgage = mD(.02, .075, 300000, 360, 'fixed')

# LAYOUT
layout = html.Div(className='app-body', children=[
    # Stores
    dcc.Store(id='total_interest', data=mortgage.totalInterestRate),
    dcc.Store(id='first_installment'),
    dcc.Store(id='installments_df'),
    dcc.Store(id='installments_df_yr'),
    dcc.Store(id='installments_df_sel'),
    dcc.Store(id='installments_df_sel_amort'),
    dcc.Store(id='table_mo_def'),
    dcc.Store(id='table_yr_def'),
    dcc.Store(id='wibor_eff_store'),
    # About the app
    ##HEADER
    html.Div([
        dbc.Card([
            dbc.CardBody([
                html.Div(className="row", children=[
                    dbc.Col(children=[
                        html.Div(children=[
                            html.H3(
                                id='title_main', 
                                children="Mortgage Calculation & Analysis",
                                className="card-title"),
                        ]),
                    ], width = 10),
                    dbc.Col(children=[
                        html.Div(children=[
                            # dbc.Label("Language"),
                            dbc.RadioItems(
                            id="lang_sel",
                            className="btn-group",
                            inputClassName="btn-check",
                            labelClassName="btn btn-outline-secondary",
                            labelCheckedClassName="active",
                            options=[
                                {"label": "EN", "value": 1},
                                {"label": "PL", "value": 2},
                            ],
                            value=1,
                            )
                        ])
                    ])
                ], style={'font-family': 'Verdana'}),
            ])
        ], color="primary", inverse=True, className="border rounded-0 align-middle"),
    ]),
    ###### MAIN BODY OF THE DASHBOARD
    dbc.Row(
        [
        dbc.Col([itab.inputs], width=3), ###### LEFT SIDE BAR - Input data tab
        dbc.Col([otab.outputs], width=9) ###### RIGHT SIDE BAR - Output data tab
        ]
    ),
    
    #             # Define pie plot to show split of payment (interest vs. principal)
    #     dbc.Col(html.Div(className="four columns pretty_container", children=[
    #         dcc.Graph(id='pie_plot_split',
    #                     figure=mortgage.paymentSplit_piePlot_fig),
    #     ]), width=4),
    # ]),
])