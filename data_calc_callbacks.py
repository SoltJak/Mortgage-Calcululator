''' This file contains callback functions 
to re-calculculate mortgage data based on 
user's input - the resulting data is stored
at dcc.Store component in the app layout'''

from dash import Input, Output, callback
import pandas as pd

def data_callbacks(app):
    ######### Recalculate all DFs for updated inputs #########
    ### Stores - storing data used for visualization creation
    
    # 1. Total interest
    @app.callback(
        Output('total_interest', 'data'),
        Input('bank_interest', 'value'),
        Input('wibor_interest', 'value')
    )
    def calc_total_interest(interest_b, interest_w):
        return (interest_b + interest_w)/100
    
    # 2. First installment
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
    
    # 3. Installments dataframe - monthly
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
    
    # 4. Installments dataframe - annually
    @app.callback(
        Output('installments_df_yr', 'data'),
        Input('installments_df', 'data'),
        Input('principal_value', 'value')
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
    
    # 5 Installments dataframe - selected for the scatter plot
    @app.callback(
        Output('installments_df_sel', 'data'),
        Input('installments_df', 'data'),
        Input('installments_df_yr', 'data'),
        Input('radioitems-payment_scatter', 'value')
    )
    def select_df(df_month, df_year, period):
        if period == 1:
            return df_month
        else:
            return df_year    

    # 6 Installments dataframe - selected for amortization table
    @app.callback(
        Output('installments_df_sel_amort', 'data'),
        Input('installments_df', 'data'),
        Input('installments_df_yr', 'data'),
        Input('radioitems-payment_table', 'value')
    )
    def select_df(df_month, df_year, period):
        if period == 1:
            return df_month
        else:
            return df_year

    # 7. Custom installment (for WIBOR effect check)
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