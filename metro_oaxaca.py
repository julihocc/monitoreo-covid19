##

import data_tools as d
import graphic_tools as g
import model_exp_tools as m
import numpy as np

municipios = d.get_locations()
N = municipios['Habitantes'].sum()
#pars0 = [0.051, 0.8, 0.3, 0.1]
#q0 = 1.00#pars0[0]
#pars0 = np.random.normal(scale=0.01, size=40)
pars0 = np.zeros(40)
R0 = 0
t_up = 3600
today_str, ics = d.get_ics()
totales = d.ventana(ics, n=7)
C0, D0, U0, N0 = totales.iloc[0].values
S0 = (N - C0)
X0 = np.array([S0, C0, R0, D0])/N
t0 = range(len(totales.index))
loss = 'linear'

res_lsq = m.create_model(totales, X0, pars0)

print(f'loos:{loss},\nres:{res_lsq.x}')

fig = {}
fig['comparar'] = g.comparar(totales, X0, res_lsq)
#fig['pronosticar'] = g.pronosticar(totales, X0, res_lsq)
#fig['analizar'] = g.analizar_activos(totales, X0, res_lsq)
