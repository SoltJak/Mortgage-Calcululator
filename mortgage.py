import pandas as pd
import plotly.graph_objects as go

class mortgageData:
    def __init__(self, bankInterestRate, wiborInterestRate, loanAmount, noOfInstallments, installmentsType):
        self.bankInterestRate = bankInterestRate
        self.wiborInterestRate = wiborInterestRate
        self.loanAmount = loanAmount
        self.noOfInstallments = noOfInstallments
        self.installmentsType = installmentsType
        self.totalInterestRate = self.bankInterestRate + self.wiborInterestRate
    
    def calculate_first_installment(self):
        if self.installmentsType == "fixed":
            first_payment = round((self.loanAmount * self.totalInterestRate) / (12 * (1 - (12/(12+self.totalInterestRate)) ** self.noOfInstallments)), 2)
            return first_payment
        elif self.installmentsType == "desc":
            first_payment = round(self.loanAmount * (1 / self.noOfInstallments + self.totalInterestRate / 12), 2)
            return first_payment
        else:
            print("Please specify installment type correctly")
            pass

    def calculate_first_installment_custom(self, amount, wibor):
        if self.installmentsType == "fixed":
            first_payment = round((amount * (self.bankInterestRate + wibor)) / (12 * (1 - (12/(12+(self.bankInterestRate + wibor))) ** self.noOfInstallments)), 2)
            return first_payment
        elif self.installmentsType == "desc":
            first_payment = round(amount * (1 / self.noOfInstallments + (self.bankInterestRate + wibor) / 12), 2)
            return first_payment
        else:
            print("Please specify installment type correctly")
            pass

    @property
    def df_installments(self):
        pd.options.display.float_format = '{:,.2f}'.format
        first_payment = self.calculate_first_installment()
        # create lists
        data = []
        total_pay = 0
        total_interest = 0
        total_principal = 0
        for i in range(0, self.noOfInstallments):
            month = i + 1
            year = (month - 1) // 12 + 1
            if month == 1:
                balance = self.loanAmount 
            else:
                balance = amount_after_payment
            interest = round(balance * self.totalInterestRate / 12, 2) #interest part of the installment
            if self.installmentsType == "desc": #Fixed installments
                principal = round(self.loanAmount / self.noOfInstallments, 2)
                installment = principal + interest
            if self.installmentsType == "fixed": #Descending installments
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
        return df_installments
    
    @property 
    def df_installments_yr(self):
        pd.options.display.float_format = '{:,.2f}'.format
        groups = self.df_installments.groupby(["Year"]).sum()
        df_grouped = pd.DataFrame(data=groups, columns=["Installment", "Interest", "Principal"])
        df_grouped["Ending Balance"] = self.loanAmount - df_grouped["Principal"].cumsum()
        df_grouped["Balance"] = df_grouped["Ending Balance"] + df_grouped["Principal"]
        df_grouped["Total Payment"] = df_grouped["Installment"].cumsum()
        df_grouped["Total Interest"] = df_grouped["Interest"].cumsum()
        df_grouped["Total Principal"] = df_grouped["Principal"].cumsum()
        df_grouped = df_grouped[["Balance", "Installment", "Interest", "Principal", "Total Payment", "Total Interest", "Total Principal", "Ending Balance"]]
        return df_grouped.reset_index()

    def recalc_after_overpayment(self):
        pass

    @property
    def df_wibor_effect(self):
        # wibor options & amount columns hard-coded
        wibor = [0, .01, .02, .03, .04, .05, .06, .07, .08, .1, .12, .15]
        amount = [0.1 * self.loanAmount, 0.2 * self.loanAmount, 0.3 * self.loanAmount, 0.4 * self.loanAmount, 0.5 * self.loanAmount, 0.6 * self.loanAmount, 0.7 * self.loanAmount, 0.8 * self.loanAmount, 0.9 * self.loanAmount, self.loanAmount]
        amount.sort(reverse=True)
        # iterate to find installment value for different loan amounts and Wibor and create column names
        data = []
        column_names = ["Loan Amount Left to pay"]  # Only 1st column name assigned
        for i in range(0, len(amount)):
            row = [amount[i]]                       # Only 1st column value assigned - amount left to pay
            for j in range(0, len(wibor)):
                temp_installment = self.calculate_first_installment_custom(amount[i], wibor[j])
                row.append(temp_installment)
                # get column names - wibor amounts
                if i == 0:
                    column_names.append(str(round((wibor[j]*100), 1)) + "%")
            data.append(row)
        df_wibor_effect = pd.DataFrame(data=data, columns=column_names)
        return df_wibor_effect

    @property
    def wibor_effect_to_list(self):
        return {'z': self.df_wibor_effect.iloc[:,1:].values.tolist(),
                'x': self.df_wibor_effect.iloc[:,1:].columns.tolist(),
                'y': self.df_wibor_effect.iloc[:,0].values.tolist()}

    ## PLOTS DEFINITION
    # 1. Scatter plot with lines - payment/interest/balance
    def create_plot_installments_def(self, x_series, trace_balance, trace_totalPay, trace_totalInt, trace_totalPrin, x_axis_title, y_axis_title): 
        return dict({
            "data": [
                {
                    "type": "scatter",
                    "x": x_series,
                    "y": trace_balance,
                    "name": "Balance",
                    "hovertemplate": "<b>Period</b>: %{x}"+"<br>"+"<b>Balance: </b>: %{y:,.2f} zł<extra></extra>"
                        
                },
                {
                    "type": "scatter",
                    "x": x_series,
                    "y": trace_totalPay,
                    "name": "Total Payment",
                    "hovertemplate": "<b>Period</b>: %{x}"+"<br>"+"<b>Total Payment: </b>: %{y:,.2f} zł<extra></extra>"            
                },
                {
                    "type": "scatter",
                    "x": x_series,
                    "y": trace_totalInt,
                    "name": "Total Interest",    
                    "hovertemplate": "<b>Period</b>: %{x}"+"<br>"+"<b>Total Interest paid: </b>: %{y:,.2f} zł<extra></extra>"            
                },
                {
                    "type": "scatter",
                    "x": x_series,
                    "y": trace_totalPrin,
                    "name": "Total Principal",
                    "hovertemplate": "<b>Period</b>: %{x}"+"<br>"+"<b>Total Principal paid: </b>: %{y:,.2f} zł<extra></extra>"            
        
                }],
            "layout": 
                {
                    "title": 
                        {
                            "text": "Cumulative mortgage payments over time"
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
    
    @property
    def monthlyInstallmentsScatter_fig(self):
        # Data for scatter plot - monthly
        x_series = self.df_installments["Month"]
        trace_balance = self.df_installments["Balance"]
        trace_totalPay = self.df_installments["Total Payment"]
        trace_totalInt = self.df_installments["Total Interest"]
        trace_totalPrin = self.df_installments["Total Principal"]
        x_axis_title = "Month"
        y_axis_title = "Cumulative payment, PLN"
        # Get the plot
        plot_installments_def = self.create_plot_installments_def(x_series, trace_balance, trace_totalPay, trace_totalInt, trace_totalPrin, x_axis_title, y_axis_title)
        return go.Figure(plot_installments_def)
    
    @property
    def yearlyInstallmentsScatter_fig(self):
        # Data for scatter plot - yearly
        x_series = self.df_installments_yr["Year"]
        trace_balance = self.df_installments_yr["Balance"]
        trace_totalPay = self.df_installments_yr["Total Payment"]
        trace_totalInt = self.df_installments_yr["Total Interest"]
        trace_totalPrin = self.df_installments_yr["Total Principal"]
        x_axis_title = "Year"
        y_axis_title = "Cumulative payment, PLN"
        # Get the plot
        plot_installments_def = self.create_plot_installments_def(x_series, trace_balance, trace_totalPay, trace_totalInt, trace_totalPrin, x_axis_title, y_axis_title)
        return go.Figure(plot_installments_def)     
    
    # 2. Pie chart - share of interest & principal within total payment
    def PayPiePlot_def(self, labels, values):
        return dict({
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
                            "text": "Payment breakdown"
                        },
                    "template" : "plotly_dark",
                    # "textinfo": "label+percent",
                    # "insidetextorientation": "radial"
                }
        })
    
    @property
    def paymentSplit_piePlot_fig(self):
        # Data for pie plot
        labels_ = ['Total Principal','Total Interest']
        values_ = [self.df_installments["Total Principal"].max(), self.df_installments["Total Interest"].max()]
        # Get the plot
        piePlot_def = self.PayPiePlot_def(labels_, values_)
        return go.Figure(piePlot_def)

    # 3. Heat map - the effect of WIBOR on installment
    def create_heatMap_def(self, list_heat_map_data):
        return dict({
            "data": [
                {
                    "type": "heatmap",
                    "x": list_heat_map_data["x"],
                    "y": list_heat_map_data["y"],
                    "z": list_heat_map_data["z"],
                    "text": list_heat_map_data["z"],
                    "colorscale": "rdbu_r",
                    "texttemplate": "%{text}",
                    "textfont": {"size":10},
                    "name": "Balance",
                    "hovertemplate": "<b>WIBOR</b>: %{x}"+
                                        "<br><b>Kapitał do spłacenia</b>: %{y} zł<br>"+
                                        "<b>Rata:</b> %{z} zł"+
                                        "<extra></extra>"
                }],
            "layout": {
                "title": {
                    "text": "Wpływ wysokości wskaźnika WIBOR na wysokość raty kredytu",
                    "yanchor": "top",
                    "font": {
                        "size": 18,
                    }
                },
                "xaxis_title": {
                    "text": "WIBOR",
                    "font_size": 16
                },
                "yaxis_title": {
                    "text": "Kwota pozostała do spłacenia",
                    "font_size": 16
                },
                "legend_title": "Wysokość raty",
                "hoverlabel": {
                        "font_size": 12,
                },
                "template": "plotly_dark",
            }
        })
   
    @property
    def wiborEffect_HeatMap_fig(self):
        # Get the plot
        heatMap_def = self.create_heatMap_def(self.wibor_effect_to_list)
        return go.Figure(heatMap_def)

    # 4. Table of payments, split on interest and principal, balance
    # Define the blueprint for table
    def payment_table_data_def(self, period_type):
        if period_type.lower() == "month":
            df_source = self.df_installments
            period_pl = "Miesiąc"
        elif period_type.lower() == "year":
            df_source = self.df_installments_yr
            period_pl = "Rok"
        else:
            print("Improper period type defined")
            pass
        return dict({
            "header_values": [ f"<b>{period_pl}<b>",
                    "<b>Do spłaty - początek<b>",
                    "<b>Rata kredytu<b>",
                    "<b>Część odsetkowa<b>",
                    "<b>Część kapitałowa<b>",
                    "<b>Suma rat<b>",
                    "<b>Suma odsetek<b>",
                    "<b>Suma spłaconego kapitału<b>",
                    "<b>Do spłaty - koniec<b>"],
            "header_align": ["left", "center", "center", "center", "center", "center", "center", "center", "center"],
            "values": [df_source[f"{period_type}"],
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

    def create_table_installments_def(self, period_type):
        # Row colors definition
        headerColor = 'black'
        rowEvenColor = 'black'
        rowOddColor = 'dimgrey'
        # Get basic data for the table
        payment_table_data = self.payment_table_data_def(period_type)
        # Return final input to create the table
        return dict({
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
            "template" : "plotly_dark",
            }
        })
    
    @property
    def installmentsTable_monthly(self):
        period_type = "Month"
        # Get the plot - Monthly installments table
        table_def = self.create_table_installments_def(period_type)
        return go.Figure(table_def)

    @property
    def installmentsTable_yearly(self):
        period_type = "Year"
        # Get the plot - Yearly installments table
        table_def = self.create_table_installments_def(period_type)
        return go.Figure(table_def)