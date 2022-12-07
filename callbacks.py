from dash import Input, Output, callback
import pandas as pd
import plotly.graph_objs as go

# Set up plots templates:
plot_template = 'plotly_white'
# App callbacks
def get_callbacks(app):
    ## Language selection - update text
    @app.callback(
        Output('title_main', 'children'),
        # Output('subtitle_main', 'children'),
        Input('lang_sel', 'value')
    )
    def change_lang_main(lang):
        if lang == 1:
            # return "MORTGAGE CALCULATOR", "Check your installment amount and payment schedule!"
            return "MORTGAGE CALCULATOR"
        else:
            # return "KALKULATOR KREDYTYOWY", "Sprawdź szczegóły swojego kredytu"
            return "KALKULATOR KREDYTYOWY"
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
    #### 2. Custom installment (for WIBOR effect check)
    @app.callback(
        Output('wibor_eff_store', 'data'),
        Input('principal_value', 'value'),
        Input('no_of_installments_t', 'value'),
        Input('installments_type', 'value'),
        Input('bank_interest', 'value'),
    )
    def df_wibor_effect(loanAmount, no_of_install, inst_type, bank_iterest):
        # wibor options & amount columns hard-coded
        wibor = [0, .01, .02, .03, .04, .05, .06, .07, .08, .1, .12, .15]
        amount = [0.1 * loanAmount, 0.2 * loanAmount, 0.3 * loanAmount, 0.4 * loanAmount, 0.5 * loanAmount, 0.6 * loanAmount, 0.7 * loanAmount, 0.8 * loanAmount, 0.9 * loanAmount, loanAmount]
        amount.sort(reverse=True)
        # iterate to find installment value for different loan amounts and Wibor and create column names
        data = []
        column_names = ["Loan Amount Left to pay"]  # Only 1st column name assigned
        for i in range(0, len(amount)):
            row = [amount[i]]                       # Only 1st column value assigned - amount left to pay
            for j in range(0, len(wibor)):
                temp_installment = calculate_first_installment_custom(inst_type, amount[i], bank_iterest/100, no_of_install, wibor[j])
                row.append(temp_installment)
                # get column names - wibor amounts
                if i == 0:
                    column_names.append(str(round((wibor[j]*100), 1)) + "%")
            data.append(row)
        df_wibor_effect = pd.DataFrame(data=data, columns=column_names)
        # convereted to dictionary:
        return {'z': df_wibor_effect.iloc[:,1:].values.tolist(),
                'x': df_wibor_effect.iloc[:,1:].columns.tolist(),
                'y': df_wibor_effect.iloc[:,0].values.tolist()}
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
    #### 5. Installments table data - Monthly
    @app.callback(
        Output('table_mo_def', 'data'),
        Input('installments_df', 'data'),    
        Input('lang_sel', 'value')
    )
    def create_table_mo_def(table_mo_def, lang):
        df_source = pd.read_json(table_mo_def, orient='split')
        table_def = create_inst_table_def(df_source, "month", lang)
        return table_def
    #### 6. Installments table data - Yearly
    @app.callback(
        Output('table_yr_def', 'data'),
        Input('installments_df_yr', 'data'),    
        Input('lang_sel', 'value')
    )
    def create_table_yr_def(table_yr_def, lang):
        df_source = pd.read_json(table_yr_def, orient='split')
        table_def = create_inst_table_def(df_source, "year", lang)
        return table_def
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
        traces = [trace_balance, trace_totalPay, trace_totalInt, trace_totalPrin]
        traces_names = [balance_name, total_pay_name, tot_interest, tot_principal]
        axes_names = [x_axis_title, y_axis_title]
        hovertemplates = ["<b>Month</b>: %{x}"+"<br>"+"<b>Balance: </b>: %{y:,.2f} zł<extra></extra>" if lang == 1 else "<b>Miesiąc</b>: %{x}"+"<br>"+"<b>Kapitał do spłaty: </b>: %{y:,.2f} zł<extra></extra>",
        "<b>Month</b>: %{x}"+"<br>"+"<b>Total Payment: </b>: %{y:,.2f} zł<extra></extra>" if lang == 1 else "<b>Miesiąc</b>: %{x}"+"<br>"+"<b>Suma wpłat: </b>: %{y:,.2f} zł<extra></extra>",
        "<b>Month</b>: %{x}"+"<br>"+"<b>Total Interest paid: </b>: %{y:,.2f} zł<extra></extra>" if lang == 1 else "<b>Miesiąc</b>: %{x}"+"<br>"+"<b>Suma zapłaconych odsetek: </b>: %{y:,.2f} zł<extra></extra>",
        "<b>Month</b>: %{x}"+"<br>"+"<b>Total Principal paid: </b>: %{y:,.2f} zł<extra></extra>" if lang == 1 else "<b>Miesiąc</b>: %{x}"+"<br>"+"<b>Spłacony kapitał: </b>: %{y:,.2f} zł<extra></extra>"]
        fig_def = create_scatter_definition(x_series, traces, traces_names, chart_title, axes_names, hovertemplates)    
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
        traces = [trace_balance, trace_totalPay, trace_totalInt, trace_totalPrin]
        traces_names = [balance_name, total_pay_name, tot_interest, tot_principal]
        axes_names = [x_axis_title, y_axis_title]
        hovertemplates = ["<b>Year</b>: %{x}"+"<br>"+"<b>Balance: </b>: %{y:,.2f} zł<extra></extra>" if lang == 1 else "<b>Rok</b>: %{x}"+"<br>"+"<b>Kapitał do spłaty: </b>: %{y:,.2f} zł<extra></extra>",
        "<b>Year</b>: %{x}"+"<br>"+"<b>Total Payment: </b>: %{y:,.2f} zł<extra></extra>" if lang == 1 else "<b>Rok</b>: %{x}"+"<br>"+"<b>Suma wpłat: </b>: %{y:,.2f} zł<extra></extra>",
        "<b>Year</b>: %{x}"+"<br>"+"<b>Total Interest paid: </b>: %{y:,.2f} zł<extra></extra>" if lang == 1 else "<b>Rok</b>: %{x}"+"<br>"+"<b>Suma zapłaconych odsetek: </b>: %{y:,.2f} zł<extra></extra>",
        "<b>Year</b>: %{x}"+"<br>"+"<b>Total Principal paid: </b>: %{y:,.2f} zł<extra></extra>" if lang == 1 else "<b>Rok</b>: %{x}"+"<br>"+"<b>Spłacony kapitał: </b>: %{y:,.2f} zł<extra></extra>"]
        fig_def = create_scatter_definition(x_series, traces, traces_names, chart_title, axes_names, hovertemplates)
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
                    "template" : plot_template,
                }
        })
        return go.Figure(piePlot_def), go.Figure(piePlot_def)
    ### 4. WIBOR effect chart
    @app.callback(
        Output('wibor_effect_chart', 'figure'),
        Input('wibor_eff_store', 'data'),
        Input('bank_interest', 'value'),
        Input('lang_sel', 'value')
    )
    def create_heatMap_plot(wibor_data, bank_interest, lang):
        chart_title = f"WIBOR impact on installment value (bank interest: {bank_interest}%)" if lang == 1 else f"Wpływ wysokości wskaźnika WIBOR na wysokość raty kredytu (marża banku: {bank_interest}%)"
        xaxis_title = "WIBOR rate, %" if lang == 1 else "Wysokość WIBOR, %"
        yaxis_title = "Mortgage balanace to pay" if lang == 1 else "Kwota pozostała do spłacenia"
        legend_title = "Installment value" if lang == 1 else "Wysokość raty"
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
                                        "<br><b>Principal left to pay</b>: %{y} zł<br>"+
                                        "<b>Installment:</b> %{z} zł"+
                                        "<extra></extra>" if lang == 1 else "<b>WIBOR</b>: %{x}"+
                                        "<br><b>Kapitał do spłacenia</b>: %{y} zł<br>"+
                                        "<b>Rata:</b> %{z} zł"+
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

    ### 5. Table of payments, split on interest and principal, balance - montly
    @app.callback(
        Output('table_inst_mo', 'figure'),
        Input('table_mo_def', 'data')
    )
    def create_table_monthly(table_mo_def):
        table_def = create_table_installments_def(table_mo_def)
        # Get the plot - Monthly installments table
        return go.Figure(table_def)
    ### 6. Table of payments, split on interest and principal, balance - yearly
    @app.callback(
        Output('table_inst_yr', 'figure'),
        Input('table_yr_def', 'data')
    )
    def create_table_yearly(table_yr_def):
        table_def = create_table_installments_def(table_yr_def)
        # Get the plot - Yearly installments table
        return go.Figure(table_def)
    # #### X. TEST
    # @app.callback(
    #     Output('test_id', 'value'),
    #     Input('first_installment', 'data')
    # )
    # def put_test_val(first_installnment):
    #     return first_installnment
    # @app.callback(
    #     Output('test_id2', 'value'),
    #     Input('total_interest', 'data'),
    # )
    # def show_total_interest(value):
    #     return value*100
    # @app.callback(
    #     Output('test_id3', 'value'),
    #     Input('installments_df_yr', 'data'),
    # )
    # def show_total_interest(data):
    #     return pd.read_json(data, orient='split').iloc[0,8]

    # Other methods:
    def calculate_first_installment_custom(installmentsType, amount, bankInterestRate, noOfInstallments, wibor):
        if installmentsType == "fixed":
            first_payment = round((amount * (bankInterestRate + wibor)) / (12 * (1 - (12/(12+(bankInterestRate + wibor))) ** noOfInstallments)), 2)
            return first_payment
        elif installmentsType == "desc":
            first_payment = round(amount * (1 / noOfInstallments + (bankInterestRate + wibor) / 12), 2)
            return first_payment
        else:
            print("Please specify installment type correctly")
            pass
    
    def create_table_installments_def(inp_table_def):
        # Row colors definition
        headerColor = 'black'
        rowEvenColor = 'black'
        rowOddColor = 'dimgrey'
        # Get basic data for the table
        payment_table_data = inp_table_def
        # Return final input to create the table
        table_def = dict({
            "data": [
            {
                "type": "table",
                "header": {
                "values": payment_table_data["header_values"],
                "line": {
                    "color": "white",
                    "width": .2
                },
                "fill_color": headerColor,
                "align": payment_table_data["header_align"],
                "font": {
                    "color": "white",
                    "size": 12
                }
                },
                "cells": {
                "values": payment_table_data["values"],
                "format": payment_table_data["values_format"],
                "line": {
                    "color": "white",
                    "width": .2
                },
                # 2-D list of colors for alternating rows
                "fill_color": [[rowOddColor,rowEvenColor]*1000],
                "align": payment_table_data["values_align"],
                # "font": {
                #   "color": "white",
                #   "size": 11}
                }    
            }],
            "layout": {
            "template" : plot_template,
            }
        })
        return table_def
    
    def create_inst_table_def(df_source, periodType, lang):
        period_name = []
        if periodType == "month":
            period_name.append("Month")
            period_name.append("Miesiąc")
        elif periodType == "year":
            period_name.append("Year")
            period_name.append("Rok")           

        table_def = dict({
        "header_values": [ f"<b>{period_name[0]}<b>",
                "<b>Beginning Balance<b>",
                "<b>Installment<b>",
                "<b>Interest<b>",
                "<b>Principal<b>",
                "<b>Cumulative installment<b>",
                "<b>Cumulative interest<b>",
                "<b>Cumulative princiapl paid<b>",
                "<b>Ending Balance<b>"] if lang == 1 else
                [ f"<b>{period_name[1]}<b>",
                "<b>Do spłaty - początek<b>",
                "<b>Rata kredytu<b>",
                "<b>Część odsetkowa<b>",
                "<b>Część kapitałowa<b>",
                "<b>Suma rat<b>",
                "<b>Suma odsetek<b>",
                "<b>Suma spłaconego kapitału<b>",
                "<b>Do spłaty - koniec<b>"],
        "header_align": ["left", "center", "center", "center", "center", "center", "center", "center", "center"],
        "values": [df_source[f"{period_name[0]}"],
                df_source["Balance"],
                df_source["Installment"],
                df_source["Interest"],
                df_source["Principal"],
                df_source["Total Payment"],
                df_source["Total Interest"],
                df_source["Total Principal"],
                df_source["Ending Balance"]],
        "values_align": ["left", "center", "center", "center", "center", "center", "center", "center", "center"],
        "values_format": [".4", ",.2f", ",.2f", ",.2f", ",.2f", ",.2f", ",.2f", ",.2f", ",.2f"]
        })
        return table_def
    
    def create_scatter_definition(x_series, traces, traces_names, chart_title, axes_names, hovertemplates):
        fig_def = dict({
            "data": [],
            "layout": 
                {
                    "title": 
                        {
                            "text": chart_title,
                            "font": {
                                # "family": "OpenSans"
                                # "family": "Times New Roman"
                                "family": "Roboto",
                                # "style": "normal",
                                # "weight": 400
                            }
                        },
                    "xaxis":
                        {
                            "title": axes_names[0]
                        },
                    "yaxis":
                        {
                            "title": axes_names[1]
                        },
                    "template" : plot_template
                }
        })
        for i in range (0, len(traces)):
            fig_def["data"].append({"type": "scatter", "x": x_series, "y": traces[i], "name": traces_names[i], "hovertemplate": hovertemplates[i]})    
        return fig_def
