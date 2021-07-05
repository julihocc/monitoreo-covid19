##

from data_tools import *
from graphic_tools import *
from model_tools import *

##

N = 6e5
q0 = 0.01785
R0 = 0
today, ics = get_ics(fixed_date='20200723')
#ics = get_ics()
print(ics.head())
totales = ventana(ics, n=1)

##

C0, D0, U0, N0 = totales.iloc[0].values
S0 = q0 * (N - C0)
X0 = [S0, C0, R0, D0, N]
t0 = range(len(totales.index))
pars0 = [q0, 0.37500937, 0.2594221, 0.02329369]
loss = 'linear'
# %%

res_lsq = create_model(totales, X0, pars0)

print(f'loos:{loss},\nres:{res_lsq.x}')

comparar(totales, F, X0, res_lsq)
pronosticar(totales, F, X0, res_lsq)
analizar_activos(totales, F, X0, res_lsq)