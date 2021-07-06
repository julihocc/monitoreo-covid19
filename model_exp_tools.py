import numpy as np
from itertools import combinations
from scipy.integrate import odeint
from scipy.optimize import least_squares


def model(X, t, *pars):
    S, C, R, D = X
    M = np.array(pars).reshape(3,10)
    I = (C - R - D)
    vec = [S,I,R,D]
    for a,b in combinations([S,I,R,D], 2):
        c = a*b
        vec.append(c)
    vec = np.array(vec).reshape(10,1)
    St, It, Rt = np.matmul(M,vec).ravel()
    Dt = -St-It-Rt
    Ct = It+Rt+Dt
    output = np.array([St, Ct, Rt, Dt])
    print(np.round(output,4))
    return output


def F(X0, t, pars):
    pars = pars.reshape(1,-1)
    predictions = odeint(model, X0, t, args=tuple(pars))
    return predictions


def fun(pars, t, y, X0):
    return F(X0, t, pars)[:, [1, 3]].ravel() - y


def create_model(totales, X0, pars0, loss='linear', marco=14, bounds=(-2, 2)):
    T = len(totales.index)
    t_train = range(T)
    # print(totales)
    init_date = totales.index[0]
    print("Initial date: ", init_date)

    confirmados = 'Confirmados'
    defunciones = 'Defunciones'

    y_train = totales[[confirmados, defunciones]].values.ravel()

    res_lsq = least_squares(fun,
                            pars0,
                            loss=loss,
                            f_scale=0.1,
                            args=(t_train,
                                  y_train,
                                  X0),
                            bounds=bounds)

    return res_lsq
