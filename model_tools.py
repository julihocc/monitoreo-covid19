from scipy.integrate import odeint
from scipy.optimize import least_squares


def model(X, t, q, b, g, m):
    S, C, R, D, N = X
    I = (C - R - D)
    l = b * I / (q * N)
    St = -l * S
    Ct = l * S
    Rt = g * I
    Dt = m * I

    return [St, Ct, Rt, Dt, 0]


def F(X0, t, pars):
    predictions = odeint(model, X0, t, args=tuple(pars), mxstep=5000)
    return predictions


def fun(pars, t, y, X0):
    return F(X0, t, pars)[:, [1, 3]].ravel() - y


def create_model(totales, X0, pars0, loss='linear', marco=14, bounds=(0, 2)):
    T = len(totales.index)
    t_train = range(T)
    # print(totales)
    init_date = totales.index[0]

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
