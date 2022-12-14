''' This file contains definition of components
used for OUTPUT tab definition including charts
in the visualization. Also included callbacks
to make input tab (as well entire application 
reactive to user changes'''

from dash import dcc, html
from dash import Input, Output, callback

import dash_bootstrap_components as dbc

import pandas as pd
import plotly.graph_objs as go

from mortgage import mortgageData as mD

# Initial Data:
mortgage = mD(.02, .075, 300000, 360, 'fixed')

# Set up plots templates:
plot_template = 'plotly_white'

#### OUTPUT DATA TAB - definition of GUI components
# 1. Ovierview tab content
overview_content = html.Div([
    dbc.Row([
        dbc.Col(
            dbc.Spinner(html.Div(
                [
                    dbc.Label("Your Installment per Month:", id="kpi_label", color="primary"),
                    html.Br(),
                    html.Hr(className="my-2"),
                    html.H1(id="kpi_installment", className="display-7"),
                    dbc.FormText("Please note that for descending installment type, above amount is for 1st installment only.", id="kpi_note", color="dark"),
                ],
                className="h-100 p-2 text-primary bg-light border rounded-3",
                style={"margin-top": "20px", "margin-left": "10px"}, 
            ), size="lg"),
            md=6,
        ),
        dbc.Col([
            html.Div([
                dbc.Label("Payment Breakdown", id="pie_label", color="primary"),
                html.Br(),
                html.Hr(className="my-2"),
                dbc.Spinner(dcc.Graph(id='pie_plot_split', figure=mortgage.paymentSplit_piePlot_fig), size="lg")               
            ], 
            className="h-100 p-2 text-primary bg-white",
            style={"margin-top": "20px", "margin-right": "10px"})
        ], width=6)
    ]),
])

# 2. Payment chart tab content
payment_content = html.Div([
    dbc.Label("Cumulative mortgage payments over time - view by:", id="pay_label", style={"margin-top": "20px"}),
    dbc.RadioItems(
        options=[
            {"label": "Month", "value": 1},
            {"label": "Year", "value": 2},
        ],
        value=1,
        id="radioitems-payment_scatter",
        inline=True,
    ),
    dbc.Spinner(dcc.Graph(id='monthly_install_chart', figure=mortgage.monthlyInstallmentsScatter_fig), size="lg")
])

# 3. Amortization schedule tab content
amort_content = html.Div([
    dbc.Label("Amortization Schedule - view by:", id="amort_label", style={"margin-top": "20px"}),
    dbc.RadioItems(
        options=[
            {"label": "Month", "value": 1},
            {"label": "Year", "value": 2},
        ],
        value=1,
        id="radioitems-payment_table",
        inline=True,
    ),
    html.Br(),
    dbc.Spinner(html.Div(id='table_wrapper', style={"maxHeight": "400px", "overflow": "scroll"}), size="lg")
])

# 4. WIBOR changes sensitivity tab
wiboreff_content = html.Div([
    dbc.Spinner(dcc.Graph(id='wibor_effect_chart', figure=mortgage.wiborEffect_HeatMap_fig), size="lg")
])

###### Apply layout of Output panel as a composition of tabs defined above ######
outputs = html.Div([
    html.H5(id='title_output', children="Details of mortgage simulation"),
    html.Hr(className="my-2"),
    dbc.Tabs(
    [
        dbc.Tab(overview_content, id="overview_tab_label", label="Overview"),
        dbc.Tab(payment_content, id="payment_tab_label", label="Payment over time"),
        dbc.Tab(amort_content, id="amort_tab_label", label="Amortization schedule"),
        dbc.Tab(wiboreff_content, id="wiboreff_tab_label", label="WIBOR effect"),
    ])
],style = {"margin-left": "7px", "margin-top": "7px", "margin-right": "7px"})


#### CALLBACKS ####
def output_callbacks(app):

    # 1. Installment KPI - display of 1st installment definition & update
    @app.callback(
        Output('kpi_installment', 'children'),
        Input('first_installment', 'data'),
        Input('lang_sel', 'value')
    )
    def display_KPI_installment(data, lang):
        return f"{data:,.2f}" + " z??"

    # 2. Pie plot - payments split - chart definition & update
    @app.callback(
        Output('pie_plot_split', 'figure'),
        Input('installments_df', 'data'),
        Input('lang_sel', 'value')
    )
    def update_pie_plot(data, lang):
        df_installments = pd.read_json(data, orient='split')
        # Data for pie plot
        labels = ['Total Principal','Total Interest'] if lang == 1 else ['Ca??kowity kapita??','Suma odsetek']
        values = [df_installments["Total Principal"].max(), df_installments["Total Interest"].max()]
        colors_ = ['#18BC9C', '#2C3E50']
        chart_title = "Payment breakdown" if lang == 1 else "Sk??adowe wp??at"
        # Get the plot
        piePlot_def = dict({
            "data": [
                {
                    "type": "pie",
                    "labels": labels,
                    "values": values,
                    "textinfo": "label+percent",
                    "texttemplate": "<b>%{label}</b><br>%{value:,.2f} z??<br><b>(%{percent})</b>",
                    "insidetextorientation": "radial",
                    "hovertemplate": "<b>%{label}</b><br>%{value:,.2f} z??<br><b>(%{percent})</b><extra></extra>",    
                    "hoverinfo": "label+percent+value",
                    "hole": .4,
                    "marker": {"colors": colors_}                          
                }],
            "layout": 
                {
                    # "title": 
                    #     {
                    #         "text": chart_title
                    #     },
                    "legend": {
                        "yanchor": "bottom",
                        "y": -.1,
                        "xanchor": "center",
                        "x": .5,
                        "orientation": "h"
                    },
                    "margin": {"t": 0},
                    "template" : plot_template,
                }
        })
        return go.Figure(piePlot_def)

    # 3. Payment over time - scatter chart definition & update
    @app.callback(
        Output('monthly_install_chart', 'figure'),
        Input('installments_df_sel', 'data'),
        Input('lang_sel', 'value'),
        Input('radioitems-payment_scatter', 'value')
    )
    def update_scatter(data, lang, period):
        if period == 1:
            df_installments = pd.read_json(data, orient='split')
            x_series = df_installments["Month"]
            trace_balance = df_installments["Balance"]
            trace_totalPay = df_installments["Total Payment"]
            trace_totalInt = df_installments["Total Interest"]
            trace_totalPrin = df_installments["Total Principal"]
            chart_title = "Cumulative mortgage payments over time" if lang == 1 else "Suma wp??at na sp??at?? kredytu w czasie jego trwania"
            x_axis_title = "Month" if lang == 1 else "Miesi??c"
            y_axis_title = "Cumulative payment, PLN" if lang == 1 else "Suma wp??at, PLN"
            balance_name = "Balance" if lang == 1 else "Kapita?? do sp??aty"
            total_pay_name = "Total payment" if lang == 1 else "Suma wp??at"
            tot_interest = "Total Interest" if lang == 1 else "Suma odsetek"
            tot_principal = "Total Principal" if lang == 1 else "Suma sp??aconego kapita??u"
            traces = [trace_balance, trace_totalPay, trace_totalInt, trace_totalPrin]
            traces_names = [balance_name, total_pay_name, tot_interest, tot_principal]
            axes_names = [x_axis_title, y_axis_title]
            hovertemplates = ["<b>Month</b>: %{x}"+"<br>"+"<b>Balance: </b>: %{y:,.2f} z??<extra></extra>" if lang == 1 else "<b>Miesi??c</b>: %{x}"+"<br>"+"<b>Kapita?? do sp??aty: </b>: %{y:,.2f} z??<extra></extra>",
            "<b>Month</b>: %{x}"+"<br>"+"<b>Total Payment: </b>: %{y:,.2f} z??<extra></extra>" if lang == 1 else "<b>Miesi??c</b>: %{x}"+"<br>"+"<b>Suma wp??at: </b>: %{y:,.2f} z??<extra></extra>",
            "<b>Month</b>: %{x}"+"<br>"+"<b>Total Interest paid: </b>: %{y:,.2f} z??<extra></extra>" if lang == 1 else "<b>Miesi??c</b>: %{x}"+"<br>"+"<b>Suma zap??aconych odsetek: </b>: %{y:,.2f} z??<extra></extra>",
            "<b>Month</b>: %{x}"+"<br>"+"<b>Total Principal paid: </b>: %{y:,.2f} z??<extra></extra>" if lang == 1 else "<b>Miesi??c</b>: %{x}"+"<br>"+"<b>Sp??acony kapita??: </b>: %{y:,.2f} z??<extra></extra>"]
            fig_def = create_scatter_definition(x_series, traces, traces_names, chart_title, axes_names, hovertemplates)    
        else:
            df_installments_yr = pd.read_json(data, orient='split')
            x_series = df_installments_yr["Year"]
            trace_balance = df_installments_yr["Balance"]
            trace_totalPay = df_installments_yr["Total Payment"]
            trace_totalInt = df_installments_yr["Total Interest"]
            trace_totalPrin = df_installments_yr["Total Principal"]
            chart_title = "Cumulative mortgage payments over time" if lang == 1 else "Suma wp??at na sp??at?? kredytu w czasie jego trwania"
            x_axis_title = "Year" if lang == 1 else "Rok"
            y_axis_title = "Cumulative payment, PLN" if lang == 1 else "Suma wp??at, PLN"
            balance_name = "Balance" if lang == 1 else "Kapita?? do sp??aty"
            total_pay_name = "Total payment" if lang == 1 else "Suma wp??at"
            tot_interest = "Total Interest" if lang == 1 else "Suma odsetek"
            tot_principal = "Total Principal" if lang == 1 else "Suma sp??aconego kapita??u"
            traces = [trace_balance, trace_totalPay, trace_totalInt, trace_totalPrin]
            traces_names = [balance_name, total_pay_name, tot_interest, tot_principal]
            axes_names = [x_axis_title, y_axis_title]
            hovertemplates = ["<b>Year</b>: %{x}"+"<br>"+"<b>Balance: </b>: %{y:,.2f} z??<extra></extra>" if lang == 1 else "<b>Rok</b>: %{x}"+"<br>"+"<b>Kapita?? do sp??aty: </b>: %{y:,.2f} z??<extra></extra>",
            "<b>Year</b>: %{x}"+"<br>"+"<b>Total Payment: </b>: %{y:,.2f} z??<extra></extra>" if lang == 1 else "<b>Rok</b>: %{x}"+"<br>"+"<b>Suma wp??at: </b>: %{y:,.2f} z??<extra></extra>",
            "<b>Year</b>: %{x}"+"<br>"+"<b>Total Interest paid: </b>: %{y:,.2f} z??<extra></extra>" if lang == 1 else "<b>Rok</b>: %{x}"+"<br>"+"<b>Suma zap??aconych odsetek: </b>: %{y:,.2f} z??<extra></extra>",
            "<b>Year</b>: %{x}"+"<br>"+"<b>Total Principal paid: </b>: %{y:,.2f} z??<extra></extra>" if lang == 1 else "<b>Rok</b>: %{x}"+"<br>"+"<b>Sp??acony kapita??: </b>: %{y:,.2f} z??<extra></extra>"]
            fig_def = create_scatter_definition(x_series, traces, traces_names, chart_title, axes_names, hovertemplates)
        return go.Figure(fig_def)

    # 4. Amortization schedule table
    @app.callback(
        Output('table_wrapper', 'children'),
        Input('installments_df_sel_amort', 'data'),
        Input('lang_sel', 'value'),
        Input('radioitems-payment_table', 'value')
    )
    def update_table(data, lang, period):
        df_en = pd.read_json(data, orient='split')
        if lang == 1:
            df = df_en
        else:
            df_pl = df_en.copy()
            if period == 1:
                df_pl.rename(columns = {"Year":'Rok', "Balance":'Do sp??aty', 'Installment':'Rata', "Interest": "Odsetki", "Principal": "Kapita??", "Total Payment": "Suma wp??at", "Total Interest": "Zap??acone odsetki", "Total Principal": "Sp??acony kapita??", "Ending Balance": "Do sp??aty - po"}, inplace = True)
            else:
                df_pl.rename(columns = {"Month": "Miesi??c", "Year":'Rok', "Balance":'Do sp??aty', 'Installment':'Rata', "Interest": "Odsetki", "Principal": "Kapita??", "Total Payment": "Suma wp??at", "Total Interest": "Zap??acone odsetki", "Total Principal": "Sp??acony kapita??", "Ending Balance": "Do sp??aty - po"}, inplace = True)
            df = df_pl
        return dbc.Table.from_dataframe(df.round(2), id="amort_table", striped=True, bordered=True, hover=True, index=False, size="sm"),

    # 5. WIBOR effect chart - definition & update
    @app.callback(
        Output('wibor_effect_chart', 'figure'),
        Input('wibor_eff_store', 'data'),
        Input('bank_interest', 'value'),
        Input('lang_sel', 'value')
    )
    def create_heatMap_plot(wibor_data, bank_interest, lang):
        chart_title = f"WIBOR impact on installment value (bank interest: {bank_interest}%)" if lang == 1 else f"Wp??yw wysoko??ci wska??nika WIBOR na wysoko???? raty kredytu (mar??a banku: {bank_interest}%)"
        xaxis_title = "WIBOR rate, %" if lang == 1 else "Wysoko???? WIBOR, %"
        yaxis_title = "Mortgage balanace to pay" if lang == 1 else "Kwota pozosta??a do sp??acenia"
        legend_title = "Installment value" if lang == 1 else "Wysoko???? raty"
        heatmap_plot_def = dict({
            "data": [
                {
                    "type": "heatmap",
                    "x": wibor_data["x"],
                    "y": wibor_data["y"],
                    "z": wibor_data["z"],
                    "text": wibor_data["z"],
                    "colorscale": "rdbu_r",
                    "texttemplate": "%{text}",
                    "textfont": {"size":10},
                    "name": "Balance",
                    "hovertemplate": "<b>WIBOR</b>: %{x}"+
                                        "<br><b>Principal left to pay</b>: %{y} z??<br>"+
                                        "<b>Installment:</b> %{z} z??"+
                                        "<extra></extra>" if lang == 1 else "<b>WIBOR</b>: %{x}"+
                                        "<br><b>Kapita?? do sp??acenia</b>: %{y} z??<br>"+
                                        "<b>Rata:</b> %{z} z??"+
                                        "<extra></extra>"
                }],
            "layout": {
                "title": {
                    "text": chart_title,
                    "yanchor": "top",
                    "font": {
                        "size": 18,
                    }
                },
                "xaxis_title": {
                    "text": xaxis_title,
                    "font_size": 16
                },
                "yaxis_title": {
                    "text": yaxis_title,
                    "font_size": 16
                },
                "legend_title": legend_title,
                "hoverlabel": {
                        "font_size": 12,
                },
                "template": plot_template,
            }
        })
        # Get the plot
        return go.Figure(heatmap_plot_def)
    
    ###### Other methods:
    def create_scatter_definition(x_series, traces, traces_names, chart_title, axes_names, hovertemplates):
        colors = ["#18BC9C", "#2C3E50","#F39C12", "#3498DB", "#E74C3C"]
        fig_def = dict({
            "data": [],
            "layout": 
                {
                    # "title": 
                    #     {
                    #         "text": chart_title,
                    #         "font": {
                    #             # "family": "OpenSans"
                    #             # "family": "Times New Roman"
                    #             "family": "Roboto",
                    #             # "style": "normal",
                    #             # "weight": 400
                    #         }
                    #     },
                    "xaxis":
                        {
                            "title": axes_names[0],
                            "title_font_size": 16,
                            # "title_font_family": "Roboto",
                        },
                    "yaxis":
                        {
                            "title": axes_names[1],
                            "title_font_size": 16,
                            # "title_font_family": "Roboto",
                        },
                    "legend": {
                        "yanchor": "bottom",
                        "y": -0.25,
                        "xanchor": "center",
                        "x": .5,
                        "orientation": "h",
                        "font_size": 14,
                    },
                    "margin": {"t": 20},
                    "template" : plot_template
                }
        })
        for i in range (0, len(traces)):
            fig_def["data"].append({"type": "scatter", "x": x_series, "y": traces[i], "name": traces_names[i], "hovertemplate": hovertemplates[i], "marker": {"color": colors[i]}, "line": {"width": 3}})    
        return fig_def
