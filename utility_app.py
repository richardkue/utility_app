from dash import Dash, dash_table, dcc, html, Input, Output, callback
import plotly.graph_objs as go
import numpy as np
import pandas as pd


def get_wealth_of_utility(utility: float, risk_aversion: float = 3.0) -> float:
    if risk_aversion == 1.0:
        wealth = np.exp(utility)
    else:
        wealth = (utility * (1.0 - risk_aversion)) ** (1.0 / (1.0 - risk_aversion))
    return wealth


def get_utility_of_wealth(wealth: float, risk_aversion: float) -> float:
    if wealth <= 0:
        raise ValueError("Game over! You poor motherfucker!")
    if risk_aversion == 1.0:
        utility = np.log(wealth)
    else:
        utility = -(wealth ** (1.0 - risk_aversion)) / (risk_aversion - 1.0)
    return utility


def get_utility_with_insurance(
    initial_wealth: float, monthly_costs: float, risk_aversion: float
) -> float:
    wealth_with_insurance = initial_wealth - monthly_costs
    utility_with_insurance = get_utility_of_wealth(wealth_with_insurance, risk_aversion)
    return utility_with_insurance


def get_utility_without_insurance(
    initial_wealth: float,
    payout: float,
    probability_per_month: float,
    risk_aversion: float,
) -> float:
    wealth_without_incident = initial_wealth
    utility_without_incident = get_utility_of_wealth(
        wealth_without_incident, risk_aversion
    )
    wealth_with_incident = initial_wealth - payout
    utility_with_incident = get_utility_of_wealth(wealth_with_incident, risk_aversion)
    utility_without_insurance = (
        utility_without_incident * (1.0 - probability_per_month)
        + utility_with_incident * probability_per_month
    )
    return utility_without_insurance

def result_figure(wealth_with_insurance, wealth_without_insurance):
    data = [go.Bar(
        x = ["Mit Versicherung", "Ohne Versicherung"],
        y = [wealth_with_insurance, wealth_without_insurance]
    )]
    fig = go.Figure(data=data)
    return fig

app = Dash(__name__)
server = app.server

app.layout = html.Div([
    dcc.Markdown('''
        # Ist diese Versicherung sinnvoll?
        '''),
    html.P("Aktuelles Vermögen", style={'display':'inline-block','margin-right':20}),
    dcc.Input(
            id="current_wealth",
            placeholder='input your wealth',
            type='number',
            debounce=True,
            required=True,
            value=30_000,
            min=0,
            step=1000,
        ),
    html.Div(),
    html.P("Risiko Aversion", style={'display':'inline-block','margin-right':20}),
    dcc.Input(
            id="risk_aversion",
            placeholder='input your risk_aversion',
            type='number',
            debounce=True,
            required=True,
            value=3.0,
            min=0.0,
            max=10.0,
            step=0.5,
        ),
    html.P("Versicherung"),
    html.P("monatliche Kosten", style={'display':'inline-block','margin-right':20}),
    dcc.Input(
            id="monthly_costs",
            placeholder='input your monthly cost',
            type='number',
            debounce=True,
            required=True,
            min=0.0,
            value=20.0,
        ),
    html.Div(),
    html.P("Versicherungssumme", style={'display':'inline-block','margin-right':20}),
    dcc.Input(
            id="payout",
            placeholder='Versicherungssumme',
            type='number',
            debounce=True,
            required=True,
            min=0.0,
            value=10_000.0,
        ),
    html.Div(),
    html.P("Eintrittswahrscheinlichkeit", style={'display':'inline-block','margin-right':20}),
    dcc.Input(
            id="probability_per_month",
            placeholder='Eintrittswahrscheinlichkeit',
            type='number',
            debounce=True,
            required=True,
            min=0.0,
            value=1/2000,
        ),
    dcc.Markdown(" "),
    html.H1("Results"),
    dcc.Graph(id='result_graph')
], style={"text-align":"center"})


@callback(
    Output('result_graph', component_property='figure'),
    Input('current_wealth', component_property='value'),
    Input('risk_aversion', component_property='value'),
    Input('monthly_costs', component_property='value'),
    Input('payout', component_property='value'),
    Input('probability_per_month', component_property='value'),)
def display_output(current_wealth, risk_aversion, monthly_costs, payout, probability_per_month):
    utility_with_insurance = get_utility_with_insurance(
        current_wealth, monthly_costs, risk_aversion
    )
    utility_without_insurance = get_utility_without_insurance(
        current_wealth, payout, probability_per_month, risk_aversion
    )
    wealth_with_insurance = get_wealth_of_utility(utility_with_insurance, risk_aversion)
    wealth_without_insurance = get_wealth_of_utility(utility_without_insurance, risk_aversion)

    return result_figure(wealth_with_insurance, wealth_without_insurance)


if __name__ == '__main__':
    app.run(debug=True)
