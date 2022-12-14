from dash import Input, Output, callback
import app_layout as al

def lang_callbacks(app):
    ### Chart title language change
    @app.callback(
        Output('title_main', 'children'),
        Input('lang_sel', 'value')        
    )
    def header_change_lang(lang):
        if lang == 1:
            return "Mortgage Calculation & Analysis"
        else:
            return "Symulacja Kosztów Kredytu"
    #### Inputs tab langauage change
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
    #### Outputs tab langauage change
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