from dash import Dash, dash_table, dcc, html
from dash import Input, Output, callback
# from app import app

from flask_caching import Cache
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

from mortgage import mortgageData as mD

# Initial Data:
mortgage = mD(.02, .075, 300000, 360, 'fixed')

# INPUT DATA TAB
inputs = html.Div(
    [
        html.H5(id='title_input', children="Input Data"),
        html.Hr(className="my-2"),
        dbc.Label("Mortgage amount", id="loan_amount_label", html_for="prin-value"),
        dbc.Input(type="number", id="principal_value", value=mortgage.loanAmount),
        html.Br(),
        dbc.Label("Mortgage duration (years + months)", id="mort_duration_label", html_for="mort-duration"),
        html.Br(),
        dbc.FormText("Provide number of years", id="label_no_years", color="secondary"),
        dcc.Slider(id="no_of_installments_y", min=1, max=50, step=1, value=mortgage.noOfInstallments//12, marks=None,  tooltip={"placement": "bottom", "always_visible": True}),
        dbc.FormText("Provide number of months", id="label_no_months", color="secondary"),
        dcc.Slider(id="no_of_installments_m", min=0, max=12, step=1, value=mortgage.noOfInstallments%12),
        dbc.FormText("Total number of installments", id="label_no_total", color="secondary"),
        dbc.Input(id="no_of_installments_t", type="number", readonly=True),
        html.Br(),
        dbc.Label("Installment type", id="label_inst_type", html_for="inst-type"),
        dbc.Select(id="installments_type", options=[
                        {'label': 'Fixed', 'value': 'fixed'},
                        {'label': 'Descending', 'value': 'desc'},
                    ], value=mortgage.installmentsType),
        html.Br(),
        dbc.Label("Mortgage interest (bank + WIBOR)", id="label_mort_int", html_for="mort-interest"),
        dbc.InputGroup([
            dbc.InputGroupText(id="bank_interest_inp", children="Bank %"),
            dbc.Input(id="bank_interest", type="number", value=mortgage.bankInterestRate*100)],
            size="sm"
        ),
        dbc.InputGroup([                                
            dbc.InputGroupText(id="WIBOR_interest_inp", children="WIBOR %"),
            dbc.Input(id="wibor_interest", type="number", value=mortgage.wiborInterestRate*100)],
            size="sm"
        )
    ],
    style = {"margin-left": "7px", "margin-top": "7px"},
)

#### CALLBACKS ####
def input_callbacks(app):
    # Calculate 
    @app.callback(
        Output('no_of_installments_t', 'value'),
        Input('no_of_installments_y', 'value'),
        Input('no_of_installments_m', 'value')
    )
    def update_no_of_yearly_installments(value_y, value_m):
        return int(0 if value_y is None else value_y) * 12 + int(0 if value_m is None else value_m)