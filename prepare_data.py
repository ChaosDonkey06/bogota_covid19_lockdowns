from global_config import config
import pandas as pd
import numpy as np
import os

data_dir_mnps = config.get_property('geo_dir')
data_dir      = config.get_property('data_dir')
results_dir   = config.get_property('results_dir')

data_df = pd.read_csv(os.path.join(data_dir, 'cases', 'covid19_26012021.csv'),
    usecols=['FECHA_DE_INICIO_DE_SINTOMAS',
            'FECHA_DIAGNOSTICO',
            'EDAD',
            'SEXO',
            'LOCALIDAD_ASIS'],  sep=';')

data_df['cases'] = 1

data_df = data_df.replace( {'Usaqu�n' :              '01 - Usaquén',
            'Usaquén' :              '01 - Usaquén',
            'Chapinero' :            '02 - Chapinero',
            'Santa Fe' :             '03 - Santa Fe',
            'San Crist�bal' :        '04 - San Cristóbal',
            'San Cristóbal' :        '04 - San Cristóbal',
            'Usme' :                 '05 - Usme',
            'Tunjuelito' :           '06 - Tunjuelito',
            'Bosa' :                 '07 - Bosa',
            'Kennedy' :              '08 - Kennedy',
            'Fontib�n' :             '09 - Fontibón',
            'Fontibón' :             '09 - Fontibón',
            'Engativ�' :             '10 - Engativá',
            'Engativá' :             '10 - Engativá',
            'Suba' :                 '11 - Suba',
            'Barrios Unidos' :       '12 - Barrios Unidos',
            'Teusaquillo' :          '13 - Teusaquillo',
            'Los M�rtires' :         '14 - Los Mártires',
            'Los Mártires' :         '14 - Los Mártires',
            'Antonio Nari�o' :       '15 - Antonio Nariño',
            'Antonio Nariño' :       '15 - Antonio Nariño',
            'Puente Aranda' :        '16 - Puente Aranda',
            'La Candelaria' :        '17 - La Candelaria',
            'Rafael Uribe Uribe' :   '18 - Rafael Uribe Uribe',
            'Ciudad Bol�var' :       '19 - Ciudad Bolívar',
            'Ciudad Bolívar' :       '19 - Ciudad Bolívar',
            'Sumapaz' :              '20 - Sumapaz',
            'Fuera de Bogot�' :      '21 - Fuera de Bogotá',
            'Fuera de Bogotá' :      '21 - Fuera de Bogotá',
            'Sin dato' :             '22 - En Rev_Loc'})




localidades1 = np.sort(data_df.LOCALIDAD_ASIS.unique())

data_df2 = pd.read_csv(os.path.join(data_dir, 'cases', 'cases_raw.csv'), sep=';')
localidades2 = np.sort(data_df2.localidadAsis.unique())

cases_df = data_df.groupby(['FECHA_DIAGNOSTICO', 'LOCALIDAD_ASIS']).sum()[['cases']].reset_index().rename(columns={
    'FECHA_DIAGNOSTICO': 'date_time',
    'LOCALIDAD_ASIS': 'locality'}).pivot(index='date_time', columns='locality', values='cases')

cases_df = cases_df.fillna(0).reset_index()
cases_df['date_time'] = pd.to_datetime(cases_df['date_time'], format='%d/%m/%Y')
cases_df = cases_df.set_index('date_time')
#deaths_df = data_df.groupby(['FechadeMuerte', 'localidadAsis']).sum()[['cases']].reset_index().rename(columns={
#    'FechadeMuerte': 'date_time',
#    'localidadAsis': 'locality'}).pivot(index='date_time', columns='locality', values='cases')
#deaths_df = deaths_df.fillna(0)

#hosp_df = data_df.groupby(['FechaHospitalizacion', 'localidadAsis']).sum()[['cases']].reset_index().rename(columns={
#    'FechaHospitalizacion': 'date_time',
#    'localidadAsis': 'locality'}).pivot(index='date_time', columns='locality', values='cases')
#hosp_df = hosp_df.fillna(0)

df_all = []
region = []
for l in cases_df.keys():
    df_all.append(cases_df[[l]].rename(columns={l:'confirm'}))
    region.extend([l]*len(cases_df))
df_all = pd.concat(df_all)
df_all['region'] = region

#df_all_deaths = []
#region = []
#for l in deaths_df.keys():
#    df_all_deaths.append(deaths_df[[l]].rename(columns={l:'deaths'}))
#    region.extend([l]*len(deaths_df))
#df_all_deaths = pd.concat(df_all_deaths)
#df_all_deaths['region'] = region

#df_all_hosp = []
#region = []
#for l in deaths_df.keys():
#    df_all_hosp.append(deaths_df[[l]].rename(columns={l:'hospitalization'}))
#    region.extend([l]*len(deaths_df))
#df_all_hosp = pd.concat(df_all_hosp)
#df_all_hosp['region'] = region

df_bogota = df_all.reset_index().fillna(0)
#df_bogota = pd.merge(df_all.reset_index(), df_all_deaths.reset_index(), on=['date_time', 'region'], how='outer').fillna(0)
#df_bogota = pd.merge(df_bogota, df_all_hosp.reset_index(), on=['date_time', 'region'], how='outer').fillna(0)

#df_bogota = df_bogota[['date_time','confirm', 'deaths', 'region']].rename(columns={'date_time': 'date'})
df_bogota = df_bogota[['date_time','confirm', 'region']].rename(columns={'date_time': 'date'})
df_bogota = df_bogota.sort_values(by=['date'])

df_bogota.to_csv(os.path.join(data_dir, 'cases', 'cases_prepared.csv'), index=False)
