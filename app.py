
import json
import logging
import os

import dash
from dash.dependencies import Input, Output, State
from dash import Dash, dash_table, dcc, html

from flask_caching import Cache
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

import plotly.graph_objs as go
import pandas as pd

# import callbacks

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
    # Stores
    dcc.Store(id='total_interest', data=mortgage.totalInterestRate),
    dcc.Store(id='first_installment'),
    dcc.Store(id='installments_df'),
    dcc.Store(id='installments_df_yr'),
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
# App callbacks
## Language selection - update text
@app.callback(
    Output('title_main', 'children'),
    Output('subtitle_main', 'children'),
    Input('lang_sel', 'value')
)
def change_lang_main(lang):
    if lang == 1:
        return "Mortgage Calculator", "Check your installment amount and payment schedule!"
    else:
        return "Kalulator kredytowy", "Sprawdź szczegóły swojego kredytu"
@app.callback(
    Output('input_menu_title', 'title'),
    Output('loan_amount', 'children'),
    Output('install_no', 'children'),
    Output('install_no_yr', 'children'),
    Output('install_no_mo', 'children'),
    Output('install_no_t', 'children'),
    Output('install_type_sel', 'children'),
    Output('interest_inp', 'children'),
    Output('bank_interest_inp', 'children'),
    Output('installments_type', 'options'),
    Input('lang_sel', 'value')
)
def change_lang(lang):
    if lang == 1:
        return "Modify your mortgage parameters", "Loan Amount", "Number of Installments (in years and months)", "Years:", "Months:", "Total:", "Installments Type", "Interest: Bank & WIBOR", "Bank %", [          {'label': 'Fixed', 'value': 'fixed'}, {'label': 'Descending', 'value': 'desc'}]
    else:
        return "Zmień parametry swojego kredytu", "Kwota kredytu", "Liczba rat (lat i miesięcy)", "Lata:", "Miesiące:", "W sumie:", "Typ rat", "Oprocentowanie (marża banku i WIBOR)", "Marża %", [          {'label': 'Stała', 'value': 'fixed'}, {'label': 'Malejąca', 'value': 'desc'}]
## Update number of years of installments if months are defined
@app.callback(
    Output('no_of_installments_t', 'value'),
    Input('no_of_installments_y', 'value'),
    Input('no_of_installments_m', 'value')
)
def update_no_of_yearly_installments(value_y, value_m):
    return int(0 if value_y is None else value_y) * 12 + int(0 if value_m is None else value_m)
## Recalculate all DFs for updated inputs
### Stores
#### 1. Total interest
@app.callback(
    Output('total_interest', 'data'),
    Input('bank_interest', 'value'),
    Input('wibor_interest', 'value')
)
def calc_total_interest(interest_b, interest_w):
    return (interest_b + interest_w)/100
#### 2. First installment
@app.callback(
    Output('first_installment', 'data'),
    Input('principal_value', 'value'),
    Input('no_of_installments_t', 'value'),
    Input('installments_type', 'value'),
    Input('total_interest', 'data'),
)
def calculate_first_installment(principal, install_no, install_type, totalInterestRate):
    if install_type == "fixed":
        first_payment = round((principal * totalInterestRate) / (12 * (1 - (12/(12+totalInterestRate)) ** install_no)), 2)
    elif install_type == "desc":
        first_payment = round(principal * (1 / install_no + totalInterestRate / 12), 2)
    return first_payment
#### TODO 2. Custom installment (for WIBOR effect check)

#### 3. Installments dataframe - monthly
@app.callback(
    Output('installments_df', 'data'),
    Input('first_installment', 'data'),
    Input('principal_value', 'value'),
    Input('no_of_installments_t', 'value'),
    Input('installments_type', 'value'),
    Input('total_interest', 'data'),
)
def df_installments(first_inst, principal_val, install_no, install_type, interest_t):
    pd.options.display.float_format = '{:,.2f}'.format
    first_payment = first_inst
    # create lists
    data = []
    total_pay = 0
    total_interest = 0
    total_principal = 0
    for i in range(0, install_no):
        month = i + 1
        year = (month - 1) // 12 + 1
        if month == 1:
            balance = principal_val
        else:
            balance = amount_after_payment
        interest = round(balance * interest_t / 12, 2) #interest part of the installment
        if install_type == "desc": #Fixed installments
            principal = round(principal_val / install_no, 2)
            installment = principal + interest
        if install_type == "fixed": #Descending installments
            installment = first_payment
            principal = installment - interest
        amount_after_payment = balance - principal
        if amount_after_payment < 0:
            correction = -amount_after_payment
            amount_after_payment = 0
            principal -= correction
            installment -= correction
        total_pay += installment
        total_interest += interest
        total_principal += principal
        data.append([month, year, balance, installment, interest, principal, total_pay, total_interest, total_principal, amount_after_payment]) #append data to the data list
    df_installments = pd.DataFrame(data=data, columns=["Month", "Year", "Balance", "Installment", "Interest", "Principal", "Total Payment", "Total Interest", "Total Principal", "Ending Balance"])
    return df_installments.to_json(orient='split', date_format='iso')
#### 4. Installments dataframe - yearly
@app.callback(
    Output('installments_df_yr', 'data'),
    Input('installments_df', 'data'),
    Input('principal_value', 'value'),
)
def df_installments_yr(data, principal_val):
    df_installments = pd.read_json(data, orient='split')
    pd.options.display.float_format = '{:,.2f}'.format
    groups = df_installments.groupby(["Year"]).sum()
    df_grouped = pd.DataFrame(data=groups, columns=["Installment", "Interest", "Principal"])
    df_grouped["Ending Balance"] = principal_val - df_grouped["Principal"].cumsum()
    df_grouped["Balance"] = df_grouped["Ending Balance"] + df_grouped["Principal"]
    df_grouped["Total Payment"] = df_grouped["Installment"].cumsum()
    df_grouped["Total Interest"] = df_grouped["Interest"].cumsum()
    df_grouped["Total Principal"] = df_grouped["Principal"].cumsum()
    df_grouped = df_grouped[["Balance", "Installment", "Interest", "Principal", "Total Payment", "Total Interest", "Total Principal", "Ending Balance"]]
    return df_grouped.reset_index().to_json(orient='split', date_format='iso')
## Update graphs
### 1. Updated scatter plot - monthly
@app.callback(
    Output('monthly_install_chart', 'figure'),
    Output('monthly_install_chart1', 'figure'),
    Input('installments_df', 'data'),
    Input('lang_sel', 'value')
)
def update_scatter_monthly(data, lang):
    df_installments = pd.read_json(data, orient='split')
    x_series = df_installments["Month"]
    trace_balance = df_installments["Balance"]
    trace_totalPay = df_installments["Total Payment"]
    trace_totalInt = df_installments["Total Interest"]
    trace_totalPrin = df_installments["Total Principal"]
    chart_title = "Cumulative mortgage payments over time" if lang == 1 else "Suma wpłat na spłatę kredytu w czasie jego trwania"
    x_axis_title = "Month" if lang == 1 else "Miesiąc"
    y_axis_title = "Cumulative payment, PLN" if lang == 1 else "Suma wpłat, PLN"
    balance_name = "Balance" if lang == 1 else "Kapitał do spłaty"
    total_pay_name = "Total payment" if lang == 1 else "Suma wpłat"
    tot_interest = "Total Interest" if lang == 1 else "Suma odsetek"
    tot_principal = "Total Principal" if lang == 1 else "Suma spłaconego kapitału"
    fig_def = dict({
        "data": [
            {
                "type": "scatter",
                "x": x_series,
                "y": trace_balance,
                "name": balance_name,
                "hovertemplate": "<b>Month</b>: %{x}"+"<br>"+"<b>Balance: </b>: %{y:,.2f} zł<extra></extra>" if lang == 1 else "<b>Miesiąc</b>: %{x}"+"<br>"+"<b>Kapitał do spłaty: </b>: %{y:,.2f} zł<extra></extra>"
                    
            },
            {
                "type": "scatter",
                "x": x_series,
                "y": trace_totalPay,
                "name": total_pay_name,
                "hovertemplate": "<b>Month</b>: %{x}"+"<br>"+"<b>Total Payment: </b>: %{y:,.2f} zł<extra></extra>" if lang == 1 else "<b>Miesiąc</b>: %{x}"+"<br>"+"<b>Suma wpłat: </b>: %{y:,.2f} zł<extra></extra>"            
            },
            {
                "type": "scatter",
                "x": x_series,
                "y": trace_totalInt,
                "name": tot_interest,    
                "hovertemplate": "<b>Month</b>: %{x}"+"<br>"+"<b>Total Interest paid: </b>: %{y:,.2f} zł<extra></extra>" if lang == 1 else "<b>Miesiąc</b>: %{x}"+"<br>"+"<b>Suma zapłaconych odsetek: </b>: %{y:,.2f} zł<extra></extra>"           
            },
            {
                "type": "scatter",
                "x": x_series,
                "y": trace_totalPrin,
                "name": tot_principal,
                "hovertemplate": "<b>Month</b>: %{x}"+"<br>"+"<b>Total Principal paid: </b>: %{y:,.2f} zł<extra></extra>" if lang == 1 else "<b>Miesiąc</b>: %{x}"+"<br>"+"<b>Spłacony kapitał: </b>: %{y:,.2f} zł<extra></extra>"
    
            }],
        "layout": 
            {
                "title": 
                    {
                        "text": chart_title
                    },
                "xaxis":
                    {
                        "title": x_axis_title
                    },
                "yaxis":
                    {
                        "title": y_axis_title
                    },
                "template" : "plotly_dark"
            }
    })
    return go.Figure(fig_def), go.Figure(fig_def)
### 2. Updated scatter plot - yearly
@app.callback(
    Output('yearly_install_chart', 'figure'),
    Output('yearly_install_chart1', 'figure'),
    Input('installments_df_yr', 'data'),
    Input('lang_sel', 'value')
)
def update_scatter_yearly(data, lang):
    df_installments_yr = pd.read_json(data, orient='split')
    x_series = df_installments_yr["Year"]
    trace_balance = df_installments_yr["Balance"]
    trace_totalPay = df_installments_yr["Total Payment"]
    trace_totalInt = df_installments_yr["Total Interest"]
    trace_totalPrin = df_installments_yr["Total Principal"]
    chart_title = "Cumulative mortgage payments over time" if lang == 1 else "Suma wpłat na spłatę kredytu w czasie jego trwania"
    x_axis_title = "Year" if lang == 1 else "Rok"
    y_axis_title = "Cumulative payment, PLN" if lang == 1 else "Suma wpłat, PLN"
    balance_name = "Balance" if lang == 1 else "Kapitał do spłaty"
    total_pay_name = "Total payment" if lang == 1 else "Suma wpłat"
    tot_interest = "Total Interest" if lang == 1 else "Suma odsetek"
    tot_principal = "Total Principal" if lang == 1 else "Suma spłaconego kapitału"
    fig_def = dict({
        "data": [
            {
                "type": "scatter",
                "x": x_series,
                "y": trace_balance,
                "name": balance_name,
                "hovertemplate": "<b>Year</b>: %{x}"+"<br>"+"<b>Balance: </b>: %{y:,.2f} zł<extra></extra>" if lang == 1 else "<b>Rok</b>: %{x}"+"<br>"+"<b>Kapitał do spłaty: </b>: %{y:,.2f} zł<extra></extra>"
                    
            },
            {
                "type": "scatter",
                "x": x_series,
                "y": trace_totalPay,
                "name": total_pay_name,
                "hovertemplate": "<b>Year</b>: %{x}"+"<br>"+"<b>Total Payment: </b>: %{y:,.2f} zł<extra></extra>" if lang == 1 else "<b>Rok</b>: %{x}"+"<br>"+"<b>Suma wpłat: </b>: %{y:,.2f} zł<extra></extra>"
            },
            {
                "type": "scatter",
                "x": x_series,
                "y": trace_totalInt,
                "name": tot_interest,    
                "hovertemplate": "<b>Year</b>: %{x}"+"<br>"+"<b>Total Interest paid: </b>: %{y:,.2f} zł<extra></extra>" if lang == 1 else "<b>Rok</b>: %{x}"+"<br>"+"<b>Suma zapłaconych odsetek: </b>: %{y:,.2f} zł<extra></extra>"
            },
            {
                "type": "scatter",
                "x": x_series,
                "y": trace_totalPrin,
                "name": tot_principal,
                "hovertemplate": "<b>Year</b>: %{x}"+"<br>"+"<b>Total Principal paid: </b>: %{y:,.2f} zł<extra></extra>" if lang == 1 else "<b>Rok</b>: %{x}"+"<br>"+"<b>Spłacony kapitał: </b>: %{y:,.2f} zł<extra></extra>"
    
            }],
        "layout": 
            {
                "title": 
                    {
                        "text": chart_title
                    },
                "xaxis":
                    {
                        "title": x_axis_title
                    },
                "yaxis":
                    {
                        "title": y_axis_title
                    },
                "template" : "plotly_dark"
            }
    })
    return go.Figure(fig_def), go.Figure(fig_def)
### 3. Pie chart - share of interest & principal within total payment
@app.callback(
    Output('pie_plot_split_', 'figure'),
    Output('pie_plot_split', 'figure'),
    Input('installments_df', 'data'),
    Input('lang_sel', 'value')
)
def update_pie_plot(data, lang):
    df_installments = pd.read_json(data, orient='split')
    # Data for pie plot
    labels = ['Total Principal','Total Interest'] if lang == 1 else ['Całkowity kapitał','Suma odsetek']
    values = [df_installments["Total Principal"].max(), df_installments["Total Interest"].max()]
    chart_title = "Payment breakdown" if lang == 1 else "Składowe wpłat"
    # Get the plot
    piePlot_def = dict({
        "data": [
            {
                "type": "pie",
                "labels": labels,
                "values": values,
                "textinfo": "label+percent",
                "texttemplate": "<b>%{label}</b><br>%{value:,.2f} zł<br><b>(%{percent})</b>",
                "insidetextorientation": "radial",
                "hovertemplate": "<b>%{label}</b><br>%{value:,.2f} zł<br><b>(%{percent})</b><extra></extra>",    
                "hoverinfo": "label+percent+value"                        
            }],
        "layout": 
            {
                "title": 
                    {
                        "text": chart_title
                    },
                "template" : "plotly_dark",
            }
    })
    return go.Figure(piePlot_def), go.Figure(piePlot_def)
### 4. WIBOR effect chart

### 5. Table of payments, split on interest and principal, balance - montly

### 6. Table of payments, split on interest and principal, balance - yearly

#### X. TEST
@app.callback(
    Output('test_id', 'value'),
    Input('first_installment', 'data')
)
def put_test_val(first_installnment):
    return first_installnment
@app.callback(
    Output('test_id2', 'value'),
    Input('total_interest', 'data'),
)
def show_total_interest(value):
    return value*100
@app.callback(
    Output('test_id3', 'value'),
    Input('installments_df_yr', 'data'),
)
def show_total_interest(data):
    return pd.read_json(data, orient='split').iloc[0,8]

# Run app
if __name__ == '__main__':
    app.run_server(debug=True)