from global_config import config
import pandas as pd
import os

data_dir_mnps = config.get_property('geo_dir')
data_dir      = config.get_property('data_dir')
results_dir   = config.get_property('results_dir')

data_df = pd.read_excel(os.path.join(data_dir, 'cases', 'cases_raw.xlsx'),
    usecols=['FechaInicioSintomas',
            'FechaDiagnostResultLaboratorio',
            'FechaHospitalizacion',
            'FechadeMuerte',
            'ESTRATOSOCIOECONOMICO',
            'Edad',
            'Sexo',
            'localidadAsis',
            'Numerolocalidad'], parse_dates=True)
data_df['cases'] = 1

cases_df = data_df.groupby(['FechaDiagnostResultLaboratorio', 'localidadAsis']).sum()[['cases']].reset_index().rename(columns={
    'FechaDiagnostResultLaboratorio': 'date_time',
    'localidadAsis': 'locality'}).pivot(index='date_time', columns='locality', values='cases')
cases_df = cases_df.fillna(0)

deaths_df = data_df.groupby(['FechadeMuerte', 'localidadAsis']).sum()[['cases']].reset_index().rename(columns={
    'FechadeMuerte': 'date_time',
    'localidadAsis': 'locality'}).pivot(index='date_time', columns='locality', values='cases')
deaths_df = deaths_df.fillna(0)

hosp_df = data_df.groupby(['FechaHospitalizacion', 'localidadAsis']).sum()[['cases']].reset_index().rename(columns={
    'FechaHospitalizacion': 'date_time',
    'localidadAsis': 'locality'}).pivot(index='date_time', columns='locality', values='cases')
hosp_df = hosp_df.fillna(0)



df_all = []
region = []
for l in cases_df.keys():
    df_all.append(cases_df[[l]].rename(columns={l:'confirm'}))
    region.extend([l]*len(cases_df))
df_all = pd.concat(df_all)
df_all['region'] = region

df_all_deaths = []
region = []
for l in deaths_df.keys():
    df_all_deaths.append(deaths_df[[l]].rename(columns={l:'deaths'}))
    region.extend([l]*len(deaths_df))
df_all_deaths = pd.concat(df_all_deaths)
df_all_deaths['region'] = region

df_all_hosp = []
region = []
for l in deaths_df.keys():
    df_all_hosp.append(deaths_df[[l]].rename(columns={l:'hospitalization'}))
    region.extend([l]*len(deaths_df))
df_all_hosp = pd.concat(df_all_hosp)
df_all_hosp['region'] = region

df_bogota = pd.merge(df_all.reset_index(), df_all_deaths.reset_index(), on=['date_time', 'region'], how='outer').fillna(0)
df_bogota = pd.merge(df_bogota, df_all_hosp.reset_index(), on=['date_time', 'region'], how='outer').fillna(0)

df_bogota = df_bogota[['date_time','confirm', 'deaths', 'region']].rename(columns={'date_time': 'date'})

df_bogota.to_csv(os.path.join(data_dir, 'cases', 'cases_prepared.csv'))
