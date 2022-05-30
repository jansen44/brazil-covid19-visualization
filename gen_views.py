'''
O dataset em questão é um apanhado de dados referentes à pandemia de COVID-19 em território
brasileiro.

As visualizações são organizadas principalmente em duas partes:
    - A primeira parte é uma representação do todo -- mostrando a frequência de novos casos
    e de mortes causadas por COVID-19 com o passar do tempo.
    - A segunda parte é a visualização da situação por estado, onde é possível verificar
    quais estados foram mais afetados;

Referências:
    Dataframe Source: https://brasil.io/dataset/covid19
    Calendário Epidemiológico: http://www.portalsinan.saude.gov.br/calendario-epidemiologico
'''

# Imports
import json
import numpy as np
import pandas as pd
import plotly as plt
import plotly.express as px
import plotly.graph_objects as go

from urllib.request import urlopen
from plotly.subplots import make_subplots

'''
    =========================================================================================================
    ======= DATA LOADING ====================================================================================
    =========================================================================================================
'''
# Informações geográficas do território brasileiro
with urlopen('https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson') as response:
    Brazil = json.load(response)
for feature in Brazil['features']:
    feature['id'] = feature['properties']['sigla']

# Carregar dataframe
df = pd.read_csv(
    "covid19.csv",
    parse_dates=True,
    infer_datetime_format=True
)

# Helper pra ajudar ao renderizar choropleth_mapbox com os dados certos
last_df = df.reindex(index=df.index[::-1])

# Total de mortes ao fim do período
total_deaths = df.groupby('epidemiological_week').agg({
    'last_available_deaths': sum
}).reset_index().iloc[-1]['last_available_deaths']

per_day = df.groupby('date').agg({
    "epidemiological_week": lambda x: list(set(x))[0],
    "new_confirmed": np.sum,
    "new_deaths": np.sum,
}).reset_index()

per_week = per_day.groupby('epidemiological_week').agg({
    "date": lambda x: list(x)[0],
    "new_confirmed": np.mean,
    "new_deaths": np.mean,
})


'''
    =========================================================================================================
    ======= NOVOS CASOS DE COVID EM TERRITÓRIO BRASILEIRO ===================================================
    =========================================================================================================
'''
week_scatter = go.Scatter(x=per_week['date'], y=per_week['new_confirmed'],
                          mode='lines',
                          name='Média semanal',
                          line=dict(color='#4B86CD'))

day_scatter = go.Scatter(x=per_day['date'], y=per_day['new_confirmed'],
                         mode='lines',
                         name='Novos casos diários',
                         line=dict(color='#9CC0EE'))

brazil_cases_fig = go.Figure()

brazil_cases_fig.update_layout(title_text='Novos Casos de COVID-19')
brazil_cases_fig.add_trace(day_scatter)
brazil_cases_fig.add_trace(week_scatter)


'''
    =========================================================================================================
    ======= MORTES POR COVID EM TERRITÓRIO BRASILEIRO =======================================================
    =========================================================================================================
'''
week_scatter = go.Scatter(x=per_week['date'], y=per_week['new_deaths'],
                          mode='lines',
                          name='Média semanal',
                          line=dict(color='#4B86CD'))

day_scatter = go.Scatter(x=per_day['date'], y=per_day['new_deaths'],
                         mode='lines',
                         name='Mortes diárias',
                         line=dict(color='#9CC0EE'))

brazil_death_cases_fig = go.Figure()
brazil_death_cases_fig.update_layout(title_text='Mortes causadas por COVID-19')
brazil_death_cases_fig.add_trace(day_scatter)
brazil_death_cases_fig.add_trace(week_scatter)


'''
    =========================================================================================================
    ======= MORTES POR COVID POR ESTADO BRASILEIRO ==========================================================
    =========================================================================================================
'''
deaths_per_state_map = px.choropleth_mapbox(
    last_df,
    locations="state",
    geojson=Brazil,
    color="last_available_deaths",
    hover_name="state",
    hover_data=["last_available_deaths"],
    mapbox_style="carto-positron",
    center={"lat": -14, "lon": -55},
    zoom=3,
    opacity=0.5,
    title=f'Mortes por COVID-19 por estado brasileiro<br>\
        <span style="font-size: 14px">Total: {"{:,}".format(total_deaths)} \
            mortes acumuladas desde o início da pandemia até o dia 27/03/2022\
        </span>',
    labels={
        'last_available_deaths': 'Total Mortes Acumuladas',
        'state': 'Estado'
    }
)
deaths_per_state_map.update_geos(fitbounds="locations", visible=False)


'''
    =========================================================================================================
    ======= TOTAL DE CASOS CONFIRMADOS POR ESTADO BRASILEIRO ================================================
    =========================================================================================================
'''
confirmed_cases_per_state_map = px.choropleth_mapbox(
    last_df,
    locations="state",
    geojson=Brazil,
    color="last_available_confirmed",
    hover_name="state",
    hover_data=["last_available_confirmed"],
    mapbox_style="carto-positron",
    center={"lat": -14, "lon": -55},
    zoom=3,
    opacity=0.5,
    title=f'Casos confirmados acumulados por estado brasileiro (Covid19)',
    labels={
        'state': 'Estado',
        'last_available_confirmed': 'Total de Casos Confirmados'
    }
)
confirmed_cases_per_state_map.update_geos(fitbounds="locations", visible=False)

confirmed_cases_per_state_tree = px.treemap(
    last_df,
    path=[px.Constant("Brasil"), 'state'],
    values='last_available_confirmed',
    title=f'Casos confirmados acumulados por estado brasileiro (Covid19)')
confirmed_cases_per_state_tree.update_traces(root_color="lightgrey")
confirmed_cases_per_state_tree.update_layout(
    margin=dict(t=80, l=25, r=25, b=25))


'''
    =========================================================================================================
    ======= CASOS CONFIRMADOS A CADA 100K HABITANTES POR ESTADO BRASILEIRO ==================================
    =========================================================================================================
'''
confirmed_cases_per_inhabitants_per_state_map = px.choropleth_mapbox(
    last_df,
    locations="state",
    geojson=Brazil,
    color="last_available_confirmed_per_100k_inhabitants",
    hover_name="state",
    hover_data=["last_available_confirmed_per_100k_inhabitants"],
    mapbox_style="carto-positron",
    center={"lat": -14, "lon": -55},
    zoom=3,
    opacity=0.5,
    title=f'Casos confirmados a cada 100k habitantes por estado brasileiro (Covid19)',
    labels={
        'state': 'Estado',
        'last_available_confirmed_per_100k_inhabitants': 'Confirmados acum./100k habitantes'
    }
)
confirmed_cases_per_inhabitants_per_state_map.update_geos(
    fitbounds="locations", visible=False)

confirmed_cases_per_inhabitants_per_state_tree = px.treemap(
    last_df,
    path=[px.Constant("Brasil"), 'state'],
    values='last_available_confirmed_per_100k_inhabitants',
    title=f'Casos confirmados a cada 100k habitantes por estado brasileiro (Covid19)')
confirmed_cases_per_inhabitants_per_state_tree.update_traces(
    root_color="lightgrey")
confirmed_cases_per_inhabitants_per_state_tree.update_layout(
    margin=dict(t=80, l=25, r=25, b=25))

'''
    =========================================================================================================
    ======= GERAÇÃO DE PLOTS ================================================================================
    =========================================================================================================
'''

target_dir = './'

plt.offline.plot(brazil_cases_fig,
                 filename=f'{target_dir}/brazil_cases_fig.html')
plt.offline.plot(brazil_death_cases_fig,
                 filename=f'{target_dir}/brazil_death_cases_fig.html')
plt.offline.plot(deaths_per_state_map,
                 filename=f'{target_dir}/deaths_per_state_map.html')
plt.offline.plot(confirmed_cases_per_state_map,
                 filename=f'{target_dir}/confirmed_cases_per_state_map.html')
plt.offline.plot(confirmed_cases_per_state_tree,
                 filename=f'{target_dir}/confirmed_cases_per_state_tree.html')
plt.offline.plot(confirmed_cases_per_inhabitants_per_state_map,
                 filename=f'{target_dir}/confirmed_cases_per_inhabitants_per_state_map.html')
plt.offline.plot(confirmed_cases_per_inhabitants_per_state_tree,
                 filename=f'{target_dir}/confirmed_cases_per_inhabitants_per_state_tree.html')
