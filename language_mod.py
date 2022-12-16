''' This file contains callback functions 
to modify dashboard labels depending on 
a language selected by a user'''

from dash import Input, Output, callback

def lang_callbacks(app):
    ### Dashboard title (language change)
    @app.callback(
        Output('title_main', 'children'),
        Input('lang_sel', 'value')        
    )
    def header_change_lang(lang):
        if lang == 1:
            return "Mortgage Calculation & Analysis"
        else:
            return "Symulacja Kosztów Kredytu"
    #### Inputs tab (langauage change)
    @app.callback(
        Output('title_input', 'children'),
        Output('loan_amount_label', 'children'),
        Output('mort_duration_label', 'children'),
        Output('label_no_years', 'children'),
        Output('label_no_months', 'children'),
        Output('label_no_total', 'children'),
        Output('label_inst_type', 'children'),
        Output('installments_type', 'options'),
        Output('label_mort_int', 'children'),
        Output('bank_interest_inp', 'children'),
        Output('WIBOR_interest_inp', 'children'),
        Input('lang_sel', 'value')        
    )
    def input_change_lang(lang):
        if lang == 1:
            return "Input Data", "Mortgage amount", "Mortgage duration (years + months)", "Provide number of years", "Provide number of months", "Total number of installments", "Installment type", [{'label': 'Fixed', 'value': 'fixed'}, {'label': 'Descending', 'value': 'desc'}], "Mortgage interest (bank + WIBOR)", "Bank %", "WIBOR %"
        else:
            return "Dane", "Kwota kredytu", "Czas spłaty (lata i miesiące)", "Podaj liczbę lat", "Podaj liczbę miesięcy", "Całkowita ilość rat", "Rodzaj raty", [{'label': 'Stała', 'value': 'fixed'}, {'label': 'Malejąca', 'value': 'desc'}], "Oprocentowanie (marża banku + WIBOR)", "Marża %", "WIBOR %"
    #### Outputs tab - menu (langauage change)
    @app.callback(
        Output('title_output', 'children'),
        Output('overview_tab_label', 'label'),
        Output('payment_tab_label', 'label'),
        Output('amort_tab_label', 'label'),
        Output('wiboreff_tab_label', 'label'),
        Input('lang_sel', 'value')        
    )
    def output_change_lang(lang):
        if lang == 1:
            return "Details of mortgage simulation", "Overview", "Payment over time", "Amortization schedule", "WIBOR effect"
        else:
            return "Wyniki symulacji kredytu", "Podsumowanie", "Struktura płatności", "Harmonogram spłaty", "Wpływ zmian WIBOR"
    #### Output - Overview tab (language change)
    @app.callback(
        Output('kpi_label', 'children'),
        Output('kpi_note', 'children'),
        Output('pie_label', 'children'),
        Input('lang_sel', 'value')        
    )
    def output_overview_change_lang(lang):
        if lang == 1:
            return "Your Installment per Month:", "Please note that for descending installment type, above amount is for 1st installment only.", "Payment Breakdown",
        else:
            return "Wysokość Twojej miesięcznej raty:", "Uwaga! Dla raty stałej powyższa kwota dotyczy tylko pierwszej raty (kolejne maleją)", "Składowe Wpłat",
    #### Output - Payment over time tab (language change)
    @app.callback(
        Output('pay_label', 'children'),
        Output('radioitems-payment_scatter', 'options'),
        Input('lang_sel', 'value')        
    )
    def output_payment_change_lang(lang):
        if lang == 1:
            return "Cumulative mortgage payments over time - view by:", [{"label": "Month", "value": 1}, {"label": "Year", "value": 2},]
        else:
            return "Suma wpłat na spłatę kredytu w czasie jego trwania - widok:", [{"label": "Miesięczny", "value": 1}, {"label": "Roczny", "value": 2},]
    #### Output - Amortization schedule tab (language change)
    @app.callback(
        Output('amort_label', 'children'),
        Output('radioitems-payment_table', 'options'),
        Input('lang_sel', 'value')        
    )
    def output_schedule_change_lang(lang):
        if lang == 1:
            return "Amortization Schedule - view by:", [{"label": "Month", "value": 1}, {"label": "Year", "value": 2},]
        else:
            return "Harmonogram spłaty kredytu - widok:", [{"label": "Miesięczny", "value": 1}, {"label": "Roczny", "value": 2},]
    # #### Output - Amortization schedule - dataframes language change
    # @app.callback(
    #     Output('installments_df', 'data'),
    #     Output('installments_df_yr', 'data'),
    #     Input('installments_df', 'data'),
    #     Input('installments_df_yr', 'data'),
    #     Input('lang_sel', 'value'),
    # )
    # def mod_df_headers_lang(data_mo, data_yr, lang):
    #     return data_mo, data_yr