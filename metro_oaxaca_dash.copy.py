##

from data_tools import *
from graphic_tools import *
from model_tools import *
import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime
from dash.dependencies import Input, Output

##

municipios = get_locations()
N = municipios['Habitantes'].sum()
q0 = 0.03
R0 = 0
#today_str, ics = get_ics(fixed_date='20200723')
today_str, ics = get_ics()

#today = datetime.strptime(today_str,'%Y%m%d')

#ics = get_ics()
#print(ics.head())
totales = ventana(ics, n=1)

##

C0, D0, U0, N0 = totales.iloc[0].values
S0 = q0 * (N - C0)
#S0 = (N - C0)
X0 = [S0, C0, R0, D0, N]
t0 = range(len(totales.index))
pars0 = [q0, 0.37500937, 0.2594221, 0.02329369]
loss = 'linear'
# %%

res_lsq = create_model(totales, X0, pars0)

print(f'loos:{loss},\nres:{res_lsq.x}')

fig = {}
fig['comparar'] = comparar(totales, F, X0, res_lsq)
fig['pronosticar'] =pronosticar(totales, F, X0, res_lsq)
fig['analizar'] = analizar_activos(totales, F, X0, res_lsq)

#for key, value in fig.items(): pyo.plot(value, filename=key+'.html')

app = dash.Dash()

app.layout = html.Div([
    html.H1(
        "Monitoreo del COVID-19 en la Zona Metropolitana de la Ciudad de Oaxaca"
    ),
    # html.Div([
    #     html.Div(id='actualizacion')    ,
    #     dcc.Interval(id='interval-component',
    #             interval=15*1000,
    #             n_intervals=0)
    # ]),
    html.Div([html.Div(id='actualizacion'),
        dcc.Interval(id='interval-component', interval=15 * 1000,
                     n_intervals=0)]),
    html.Div([
        html.H3(
            "Comparación entre datos y simulación."
        ),
        dcc.Graph(
            id='comparar',
            figure = {
                'data':list(fig['comparar'].values())
            }
        )
    ]
    ),
    html.Div([
        html.H3(
            'Pronósticos.'
        ),
        dcc.Graph(
            id='pronosticar',
            figure = {
                'data':list(fig['pronosticar'].values())
            }
        )
    ]),
    html.Div([
        html.H3(
            'Análisis de activos.'
        ),
        dcc.Graph(
            id='analizar',
            figure = {
                'data':list(fig['analizar'].values())
            }
        )
    ]),
],
    style={'color': 'darkblue', 'font-family':"Indivisa"})

@app.callback(
    Output('actualizacion', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_date(n):
    today_str, ics = get_ics()
    today = datetime.strptime(today_str, '%Y%m%d')
    #return html.H2(f"Actualización: {today.year}/{today.month}/{today.day}")
    return [html.H2(f"Actualización: {today.year}/{today.month}/"
                    f"{today.day}"), html.H2(f"Hora actual:"
                                             f" {datetime.now()}")]


# Add the server clause:
if __name__ == '__main__':
    app.run_server()
