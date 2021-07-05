import io
from datetime import date, timedelta

import numpy as np
import pandas as pd
import requests


def get_locations():
    municipios = pd.read_excel(
        "municipios_zona_metro_oaxaca.xlsx", engine="openpyxl"
    )
    municipios['Habitantes'] = municipios['poblacion']
    return municipios.set_index(['cve_ent', 'poblacion'])


def get_date(n):
    #print(date.today())
    today_dt = date.today() - timedelta(days=n)
    today_str = str(today_dt).replace("-", "")
    return today_str


def format_data(today_str, rubro):
    municipios = get_locations()
    url = "https://datos.covid-19.conacyt.mx/Downloads/Files/Casos_Diarios_Municipio_{}_{}.csv"

    confirmados_url = url.format(rubro, today_str)

    s = requests.get(confirmados_url).content

    confirmados_mx = pd.read_csv(
        io.StringIO(s.decode('utf-8'))
    ).set_index(['cve_ent', 'poblacion'])

    es_zona_metro = confirmados_mx.index.isin(municipios.index)

    confirmados_metro = confirmados_mx[es_zona_metro]

    confirmados_df = pd.DataFrame()

    confirmados_df['fecha'] = pd.to_datetime(
        confirmados_metro.columns[1:],
        format='%d-%m-%Y'
    )

    confirmados_df['fecha']

    for idx in confirmados_metro.index:
        municipio = confirmados_metro.loc[idx]
        confirmados_df[municipio.nombre] = municipio.values[1:]

    confirmados_df.set_index('fecha', inplace=True)

    confirmados_df['total'] = confirmados_df.sum(axis=1)

    return confirmados_df


def get_data(rubro):
    n = 0
    while True:
        try:
            #print("init: ", n)
            today_str = get_date(n)
            #print(today_str)
            df = format_data(today_str, rubro)
            break
        except:
            n = n + 1
            #print(n)
            if n > 7:
                break
    return today_str, df


# %%
def get_data_fixed(fecha, rubro):
    municipios = get_locations()
    archivo = "./datos_{}/{}.csv".format(fecha, rubro)

    confirmados_mx = pd.read_csv(
        archivo).set_index(['cve_ent', 'poblacion'])

    es_zona_metro = confirmados_mx.index.isin(municipios.index)

    confirmados_metro = confirmados_mx[es_zona_metro]

    confirmados_df = pd.DataFrame()

    confirmados_df['fecha'] = pd.to_datetime(
        confirmados_metro.columns[1:],
        format='%d-%m-%Y'
    )

    confirmados_df['fecha']

    for idx in confirmados_metro.index:
        municipio = confirmados_metro.loc[idx]
        confirmados_df[municipio.nombre] = municipio.values[1:]

    confirmados_df.set_index('fecha', inplace=True)

    confirmados_df['total'] = confirmados_df.sum(axis=1)

    return confirmados_df


##
def fecha_inicial(data):
    primeras_fechas = [fecha.index[0] for fecha in data.values()]
    primera_fecha = np.min(primeras_fechas)
    return primera_fecha


def create_df(fixed_date = None):
    data = {}
    actualizacion = None
    categorias = ['Confirmados', 'Defunciones', 'Sospechosos', 'Negativos']
    for categoria in categorias:
        if fixed_date is None:
            actualizacion, data[categoria] = get_data(categoria)
            #print("actualizacion:", actualizacion)
            #print(type(actualizacion))
        else:
            actualizacion = fixed_date
            data[categoria] = get_data_fixed(fixed_date, categoria)
    primer_activo = fecha_inicial(data)
    ts0 = pd.date_range(start=primer_activo, end=actualizacion).tolist()
    return actualizacion, data, ts0


##

def completar(df, idx):
    if idx in df.index:
        return df['total'].loc[idx]
    else:
        return 0


# %%
def preproc_data(ts0, data):
    pretotales = pd.DataFrame.from_dict({'fecha': ts0})

    for categoria in data.keys():
        pretotales[categoria] = [
            completar(data[categoria], idx) for idx in ts0
        ]

    pretotales.set_index('fecha', inplace=True)

    return pretotales


# %%

def primero_cat(data, categoria_init):
    confirmados = data[categoria_init].total
    primer_confirmado = confirmados[confirmados > 0].index.values[0]
    return primer_confirmado


def get_ics(fixed_date=None):
    actualizacion, data, ts0 = create_df(fixed_date=fixed_date)
    pretotales = preproc_data(ts0, data)
    primer_confirmado = primero_cat(data, 'Confirmados')

    periodo = {}

    periodo['totales'] = pd.period_range(
        start=primer_confirmado, end=actualizacion
    ).to_timestamp()

    condicion = {}

    condicion['totales'] = pretotales.index.isin(periodo['totales'])

    totales = pretotales[condicion["totales"]]

    primera_fecha = fecha_inicial(data)

    periodo['acumulados'] = pd.period_range(
        start=primera_fecha, end=primer_confirmado
    ).to_timestamp()

    condicion['acumulados'] = pretotales.index.isin(periodo["acumulados"])
    temp_data = pretotales[condicion["acumulados"]].sum()

    print(temp_data)

    for categoria in temp_data.index:
        # print(categoria, temp_data[categoria])
        totales.iloc[0][categoria] = temp_data[categoria]

    return actualizacion, totales


##
def ventana(totales, n=7):
    datos_ponderados = pd.DataFrame()

    categorias = ['Confirmados', 'Defunciones', 'Sospechosos', 'Negativos']

    for categoria in categorias:
        datos_ponderados[categoria] = totales[categoria].rolling(n).mean()

    datos_ponderados.dropna(inplace=True)

    df_dict = {}

    for categoria in categorias:
        columna = datos_ponderados[[categoria]]
        valores = [
            np.sum(columna.loc[:idx].values) for idx, row in columna.iterrows()
        ]
        df_dict[categoria] = valores

    datos_acumulados = pd.DataFrame.from_dict(df_dict)
    datos_acumulados.index = datos_ponderados.index

    # print(datos_acumulados.head())
    df = datos_ponderados.merge(datos_acumulados, left_index=True, right_index=True)

    return datos_acumulados
