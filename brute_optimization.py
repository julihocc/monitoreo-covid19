##

from scipy.optimize import brute
from data_tools import *
from graphic_tools import *
from model_tools import *

#pars0 = [0.03, 0.37500937, 0.2594221, 0.02329369]

municipios = get_locations()
N = municipios['Habitantes'].sum()
q0 = 0.03
R0 = 0
t_up = 10
today_str, ics = get_ics()
totales = ventana(ics, n=1)

C0, D0, U0, N0 = totales.iloc[0].values
S0 = q0 * (N - C0)
X0 = [S0, C0, R0, D0, N]
t0 = range(len(totales.index))
pars0 = [q0, 0.37500937, 0.2594221, 0.02329369]
loss = 'linear'

T = len(totales.index)
t_train = range(T)
# print(totales)
init_date = totales.index[0]

confirmados = 'Confirmados'
defunciones = 'Defunciones'

y_train = totales[[confirmados, defunciones]].values.ravel()

rranges = (
    slice(0.01, 1, 0.001),
    slice(0.1, 1, 0.1),
    slice(0.1, 1, 0.1),
    slice(0.1, 1, 0.1)
)


def g(pars):
    output = np.sum(np.power(fun(pars, t_train, y_train, X0),2))
    print(pars, output)
    return output

##

resbrute = brute(g, rranges, finish=None)

##

print(resbrute)

