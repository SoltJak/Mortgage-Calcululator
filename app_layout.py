from dash import Dash, dash_table, dcc, html

from flask_caching import Cache
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from mortgage import mortgageData as mD

mortgage = mD(.02, .075, 300000, 360, 'fixed')

layout = html.Div(className='app-body', children=[
    # Stores
    dcc.Store(id='total_interest', data=mortgage.totalInterestRate),
    dcc.Store(id='first_installment'),
    dcc.Store(id='installments_df'),
    dcc.Store(id='installments_df_yr'),
    dcc.Store(id='table_mo_def'),
    dcc.Store(id='table_yr_def'),
    dcc.Store(id='wibor_eff_store'),
    # About the app
    html.Div(className="row",
        children=[
            dbc.Col(children=[
                html.Div(children=[
                    html.H1(
                        id='title_main', 
                        children='Mortgage Calculator'),
                    html.H4(
                        id='subtitle_main', 
                        children="Check your installment amount and payment schedule!")
                ]),
            ], width = 10),
            dbc.Col(children=[
                html.Div(children=[
                    # dbc.Label("Language"),
                    dbc.RadioItems(
                    id="lang_sel",
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary",
                    labelCheckedClassName="active",
                    options=[
                        {"label": "EN", "value": 1},
                        {"label": "PL", "value": 2},
                    ],
                    value=1,
                    )
                ])
            ], align="center")
        ]
    ),
    # Input data tab
    html.Div(dbc.Accordion(
        [
            dbc.AccordionItem(
                [
                    # html.P("Modify your mortgage parameters"),
                    html.Div(children=[
                        html.Div(className="row",
                            children=[
                                dbc.Col(children=[html.Div(id="loan_amount", children="Loan Amount", className="menu-title"),
                                dbc.Input(
                                    id="principal_value",
                                    type="number",
                                    placeholder="Mortgage amount",
                                    value=mortgage.loanAmount,
                                )], width=2),
                                dbc.Col(children=[html.Div(id="install_no", children="Number of Installments (in years and months)", className="menu-title"),
                                dbc.InputGroup(
                                    [
                                        dbc.InputGroupText(id="install_no_yr", children="Years:"),
                                        dbc.Input(
                                            id="no_of_installments_y",
                                            type="number",
                                            value=mortgage.noOfInstallments/12
                                        ),
                                        dbc.InputGroupText(id="install_no_mo", children="Months:"),
                                        dbc.Input(
                                            id="no_of_installments_m",
                                            type="number"
                                        ),
                                        dbc.InputGroupText(id="install_no_t", children="Total:"),
                                        dbc.Input(
                                            id="no_of_installments_t",
                                            type="number",
                                            readonly=True,
                                        )
                                    ],
                                )
                                ], width=5),
                                dbc.Col(children=[html.Div(id="install_type_sel", children="Installments Type", className="menu-title"),
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
                                    html.Div(id="interest_inp", children="Interest: Bank & WIBOR", className="menu-title"),
                                    dbc.InputGroup([
                                        dbc.InputGroupText(id="bank_interest_inp", children="Bank %"),
                                        dbc.Input(
                                            id="bank_interest",
                                            type="number",
                                            value=mortgage.bankInterestRate*100,
                                        ),
                                        dbc.InputGroupText("WIBOR %"),
                                        dbc.Input(
                                            id="wibor_interest",
                                            type="number",
                                            value=mortgage.wiborInterestRate*100,
                                        )
                                    ])
                                ], width=3),
                            ]
                        ),]),
                ],
                id="input_menu_title",
                title="Modify your mortgage parameters",
            )
        ],
    )),
    # The Visuals
    html.Div(className="row",
    children=[
        dbc.Col(children=[html.Div(children="Test cell", className="menu-title"),
        dbc.Input(
            id="test_id",
            type="number",
            placeholder="Test Result",
        )], width=3),]),
    html.Div(className="row",
    children=[
        dbc.Col(children=[html.Div(children="Test cell2", className="menu-title"),
        dbc.Input(
            id="test_id2",
            type="number",
            placeholder="Test Result2",
        )], width=3),]),
    html.Div(className="row",
    children=[
        dbc.Col(children=[html.Div(children="Test cell3", className="menu-title"),
        dbc.Input(
            id="test_id3",
            type="number",
            placeholder="Test Result3",
        )], width=3),]),
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
            dcc.Graph(id='pie_plot_split_',
                        figure=mortgage.paymentSplit_piePlot_fig),
        ]), width=4),
        # Define heat map plot to show WIBOR effect on installment amount
        dbc.Col(html.Div(className="four columns pretty_container", children=[
            dcc.Graph(id='wibor_effect_chart',
                        figure=mortgage.wiborEffect_HeatMap_fig),
        ]), width=8)]),
    html.Div(className="row", children=[    
        # Define table to show payments schedule (monthly)
        dbc.Col(html.Div(className="four columns pretty_container", children=[
            dcc.Graph(id='table_inst_mo',
                        figure=mortgage.installmentsTable_monthly),
        ])),
        # Define table to show payments schedule (yearly)
        dbc.Col(html.Div(className="four columns pretty_container", children=[
            dcc.Graph(id='table_inst_yr',
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
                            dcc.Graph(id='monthly_install_chart1',
                                            figure=mortgage.monthlyInstallmentsScatter_fig)
                        ]
                    ))
                ]),
                dcc.Tab(label='Yealy', id='tab_yearly', children=[
                    dbc.Card(dbc.CardBody(
                        [
                            dcc.Graph(id='yearly_install_chart1',
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
    ]),
    # Store for intermediate values
    dcc.Store(id='intermediate_data')
])