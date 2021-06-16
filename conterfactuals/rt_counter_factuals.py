from covid19_forecast.functions.adjust_cases_functions import prepare_cases
import matplotlib.pyplot as plt
import scipy.io as sio
import pandas as pd
import numpy as np
import os


from rpy2.robjects.conversion import localconverter
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
import rpy2.robjects.numpy2ri
import rpy2.robjects as ro
import rpy2

import sys


sys.path.insert(0,'..')
from global_config import config


rpy2.robjects.numpy2ri.activate()
epinow2 = importr("EpiNow2")
base    = importr('base')

generation_time   = epinow2.get_generation_time(disease = "SARS-CoV-2", source = "ganyani")
incubation_period = epinow2.get_incubation_period(disease = "SARS-CoV-2", source = "lauer")
reporting_delay   = epinow2.estimate_delay(ro.r.rlnorm(1000,  ro.r.log(3), 1),
                                  max_value = 15, bootstraps = 1)

data_dir_mnps = config.get_property('geo_dir')
fb_ppl_data   = config.get_property('covid_fb')
data_dir      = config.get_property('data_dir')
results_dir   = config.get_property('results_dir')


data_dir_mnps = config.get_property('geo_dir')
fb_ppl_data   = config.get_property('covid_fb')
data_dir      = config.get_property('data_dir')
results_dir   = config.get_property('results_dir')

data_cases_path = os.path.join(fb_ppl_data, 'agglomerated', 'geometry')

cases_df = pd.read_csv(os.path.join(data_cases_path, 'cases.csv'), parse_dates=["date_time"])


dict_correct = {'Los Martires': 'Los Mártires', 'Fontibon': 'Fontibón', 'Engativa': 'Engativá',
                            'San Cristobal': 'San Cristóbal', 'Usaquen': 'Usaquén',
                            'Ciudad Bolivar': 'Ciudad Bolívar', 'Candelaria': 'La Candelaria'}

cases_df["poly_id"]  = cases_df["poly_id"].apply(lambda s:   s.replace("colombia_bogota_localidad_",""))

cases_df["poly_name"]  = cases_df["poly_id"].apply(lambda s:   ' '.join( [word.capitalize() for word in s.replace("colombia_bogota_localidad_","").split('_') ] ) )
cases_df["poly_name"]  = cases_df["poly_name"].replace( dict_correct )

cases_bog_df = cases_df.groupby(['poly_id', 'poly_name', 'date_time']).sum()[["num_cases", "num_diseased", "num_infected_in_icu"]]
cases_bog_df = cases_bog_df.unstack([0,1]).resample('1D').sum().stack().stack().reset_index().rename(columns={'date_time':'date','num_cases': 'confirm',
                                                                                                                'num_diseased': 'deaths',
                                                                                                                'num_infected_in_icu': 'icu'})

bog_agg_df = cases_bog_df.groupby('date').sum()
bog_agg_df = prepare_cases(bog_agg_df, col='confirm')
bog_agg_df = prepare_cases(bog_agg_df, col='deaths')


lockdowns = []
lockdowns.append({"code": "A",
                  "start_date" : pd.to_datetime("2020-07-13"),
                  "end_date"   : pd.to_datetime("2020-07-23"),
                  "places":["chapinero",
                            "los_martires",
                            "san_cristobal",
                            "tunjuelito",
                            "rafel_uribe_uribe",
                            "ciudad_bolivar",
                            "santa_fe",
                            "usme"]})

lockdowns.append({"code": "B",
                  "start_date" : pd.to_datetime("2020-07-23"),
                  "end_date"   : pd.to_datetime("2020-08-06"),
                  "places":["bosa",
                            "antonio_narino",
                            "kennedy",
                            "puente_aranda",
                            "fontibon"]})

lockdowns.append({"code": "C",
                  "start_date" : pd.to_datetime("2020-07-31"),
                  "end_date"   : pd.to_datetime("2020-08-14"),
                  "places":["suba",
                            "engativa",
                            "barrios_unidos"]})

lockdowns.append({"code": "D",
                  "start_date" : pd.to_datetime("2020-08-16"),
                  "end_date"   : pd.to_datetime("2020-08-27"),
                  "places":["usaquen",
                            "chapinero",
                            "santa_fe",
                            "candelaria",
                            "teusaquillo",
                           "puente_aranda",
                           "antonio_narino"]})


from datetime import datetime, timedelta

def estimate_rt(cases_df, path_to_save=None):
    cases_bog_df = cases_df.copy()
    cases_bog_df = cases_bog_df.groupby('date').sum()
    cases_bog_df = cases_bog_df.reset_index()[["date", "confirm", "deaths"]]
    cases_bog_df = cases_bog_df.set_index("date").resample('1D').sum().reset_index()
    cases_bog_df["confirm"] = cases_bog_df["confirm"].apply(lambda x: int(x))

    with localconverter(ro.default_converter + pandas2ri.converter):
        r_df_bogota_loc = ro.conversion.py2rpy(cases_bog_df[['date','confirm']])
    r_df_bogota_loc[0]  = base.as_Date(r_df_bogota_loc[0], format= "%Y-%m-%d")

    bogota_rt = epinow2.epinow(reported_cases = r_df_bogota_loc,
                                generation_time = generation_time,
                                delays = epinow2.delay_opts(incubation_period, reporting_delay),
                                rt = epinow2.rt_opts(prior = ro.r.list(mean = 2, sd = 0.2)),
                                stan = epinow2.stan_opts(cores = 4))

    inf_df = pd.DataFrame( bogota_rt[0][0] )
    rt_df  = pd.DataFrame( bogota_rt[0][1] )


    rt_df = rt_df[rt_df.type=='estimate']
    rt_df = rt_df[rt_df.variable=='R']
    rt_df = rt_df.dropna()
    rt_df['date']  = rt_df['date'].map(lambda x: pd.to_datetime(0)+timedelta(days=x))

    rt_df["type_id"] = cases_df["type"]

    inf_df = inf_df[inf_df.type=='estimate']
    rt_df.to_csv(  os.path.join(path_to_save, 'rt.csv'),  index=False)
    inf_df.to_csv( os.path.join(path_to_save, 'inf.csv'), index=False)

    return rt_df, inf_df

for loc in lockdowns:
    data = bog_agg_df.copy()
    path_to_cf = os.path.join( results_dir, 'conterfactuals', loc["code"])

    df_deaths = pd.read_csv( os.path.join(path_to_cf, 'deaths_df.csv'), parse_dates=['date']).set_index('date')[["median", "type"]].rename(columns={'median': 'deaths'})
    df_cases  = pd.read_csv( os.path.join(path_to_cf, 'cases_df.csv'), parse_dates=['date']).set_index('date')[["median", "type"]].rename(columns={'median': 'confirm'})

    data = data.loc[:loc["start_date"]][["confirm", "deaths"]]
    data["type"] = "data"

    df_deaths = df_deaths[df_deaths["type"]=='forecast']
    df_cases  = df_cases [df_cases ["type"]=='forecast']
    df_forecast = pd.merge(df_deaths, df_cases, left_index=True, right_index=True)[["confirm", "deaths"]]
    df_forecast = df_forecast.iloc[:40]
    df_forecast["type"] = "counterfactual"

    data = pd.concat([data, df_forecast])
    data = data.reset_index()
    rt_df, inf_df = estimate_rt(data, path_to_save=path_to_cf)

# Estimate all Rt
data = bog_agg_df.copy()
data = data[["confirm", "deaths"]]
path_to_cf = os.path.join(results_dir, 'conterfactuals' )
rt_df, inf_df = estimate_rt(data, path_to_save=path_to_cf)
