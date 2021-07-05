from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.graph_objs as go
import matplotlib.pyplot as plt
from model_exp_tools import F

paleta = {
    'Confirmados': 'darkslateblue',
    'Recuperados': 'darkgreen',
    'Defunciones': 'darkred',
    'Activos': 'darkorange',
    'Velocidad': 'darkcyan',
    'Aceleración': 'darkorchid'
}

def simula(t_test, ypred):
    ypred = np.array(ypred)
    simulacion = pd.DataFrame()
    simulacion['Confirmados'] = ypred[:, 1]
    simulacion['Recuperados'] = ypred[:, 2]
    simulacion['Defunciones'] = ypred[:, 3]
    simulacion['Activos'] = simulacion.Confirmados - simulacion.Recuperados - simulacion.Defunciones
    simulacion['Velocidad'] = simulacion.Activos.diff(periods=1)
    simulacion['Aceleración'] = simulacion.Velocidad.diff(periods=1)
    simulacion.index = t_test

    return simulacion


def comparar(totales, X0, res_lsq):
    N = np.sum(X0)
    T = len(totales.index)
    #t_test = np.linspace(0, T, T * 100)
    t_test = list(range(T))
    ypred = F(X0, t_test, res_lsq.x)
    T = len(totales.index)
    primer_activo = totales.index[0]
    t_train = [str(x) for x in pd.date_range(start=primer_activo, periods=T)]
    simulacion = simula(t_test, ypred)
    plt.scatter(t_train, totales['Defunciones'], s=1)
    plt.plot(simulacion.index, N*simulacion.Defunciones, color='r')
    plt.scatter(t_train, totales['Confirmados'], s=1)
    plt.plot(simulacion.index, N*simulacion.Confirmados, color='g')
    plt.show()

def panorama(totales, N):
    T = len(totales.index)
    primer_activo = totales.index[0]
    datelist = pd.date_range(primer_activo,
                             periods=T + N).tolist()
    return datelist


def proyectar(X0, t_lapse, res):
    t_test = range(len(t_lapse))
    ypred = F(X0, t_test, res)
    simulacion = simula(t_test, ypred)

    return simulacion


def pronosticar(totales, X0, res_lsq, N=120):
    t_lapse = panorama(totales, N)
    # print(t_lapse)
    futuro = proyectar(X0, t_lapse, res_lsq.x)
    cats = ['Confirmados', 'Recuperados', 'Defunciones', 'Activos']
    #futuro[cats].plot(grid=True)
    #plt.show()
    traces = {}
    for cat in cats:
        traces[cat] = go.Scatter(
            x=t_lapse,
            y=futuro[cat],
            mode='lines',
            name=cat,
            marker=dict(
                color=paleta[cat]
            )
        )

    return traces


def pico(init_date, sim_lsq):
    condicion = sim_lsq['Aceleración'] < 0
    rango = sim_lsq['Velocidad'].abs()[condicion]
    # print(rango)
    t = rango.argmin()
    # print(t)
    days = int(rango.index[int(t)])
    # print(days)
    return days, init_date + timedelta(days=days)


def inflexion(init_date, sim_lsq, tol=1e-3):
    condicion = (sim_lsq['Velocidad'] < 0) & (sim_lsq['Aceleración']>=0)
    rango = sim_lsq['Aceleración'][condicion]
    # print(rango)
    t = rango.iloc[0]
    # print(t)
    days = int(rango.index[int(t)])
    # print(days)
    return days, init_date + timedelta(days=days)


def analizar_activos(totales, X0, res_lsq, N=120):
    t_lapse = panorama(totales, N)
    futuro = proyectar(X0, t_lapse, res_lsq.x)
    cats = ['Activos', 'Velocidad', 'Aceleración']
    escalas = {'Activos':1, 'Velocidad':10, 'Aceleración':100}
    traces = {}
    for cat in cats:
        escala = escalas[cat],
        traces[cat] = go.Scatter(
            x=t_lapse,
            y=futuro[cat],#*escala,
            mode='lines',
            #name=f'{cat} (Escala {escala[0]}:1)',
            name=f'{cat}',
            marker=dict(
                color=paleta[cat]
            )
        )


    init_date = totales.index[0]

    i, pto_crit = pico(init_date, futuro)
    y_crit = futuro[['Activos']].iloc[i].values
    print(pto_crit, y_crit)

    j, pto_inf = inflexion(init_date, futuro, tol=.1)
    y_inf = futuro[['Activos']].iloc[j].values
    #print(pto_inf, y_inf)

    traces['pto_critico'] = go.Scatter(
        x = [t_lapse[i]],
        y = y_crit,
        mode='markers',
        marker= dict(
            size=15,
            symbol='triangle-right',
            color=paleta['Velocidad']
        ),
        name='Punto crítico'
    )

    traces['pto_inflexion'] = go.Scatter(
        x = [t_lapse[j]],
        y = y_inf,
        mode='markers',
        marker= dict(
            size=15,
            symbol='triangle-se',
            color=paleta['Aceleración']
        ),
        name='Punto de inflexión'
    )
    return traces


