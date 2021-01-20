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

import rpy2
import numpy as np
from rpy2.robjects.packages import importr
import rpy2.robjects.numpy2ri
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri

rpy2.robjects.numpy2ri.activate()
epinow2 = importr("EpiNow2")
dplyr   = importr('dplyr')

generation_time   = epinow2.get_generation_time(disease = "SARS-CoV-2", source = "ganyani")
incubation_period = epinow2.get_incubation_period(disease = "SARS-CoV-2", source = "lauer")
reporting_delay   = epinow2.estimate_delay(ro.r.rlnorm(1000,  ro.r.log(3), 1),
                                  max_value = 15, bootstraps = 1)


loc_df = cases_df[['01 - Usaquén']].reset_index()
loc_df = loc_df.rename(columns={'date_time': 'date', '01 - Usaquén': 'confirm'})
loc_df = loc_df.set_index('date')[['confirm']].resample('D').sum().reset_index()
loc_df['date'] = loc_df['date'].map(lambda x: str(x.strftime( "%Y-%m-%d")))

from rpy2.robjects.conversion import localconverter
with localconverter(ro.default_converter + pandas2ri.converter):
    r_from_pd_df = ro.conversion.py2rpy(loc_df[['date','confirm']])

base = importr('base')

r_from_pd_df = dplyr.mutate(r_from_pd_df, date= base.as_Date(date, format= "%Y-%m-%d"))

bogota_rt = epinow2.epinow(reported_cases = r_from_pd_df,
                    generation_time = generation_time,
                    delays = epinow2.delay_opts(incubation_period, reporting_delay),
                    rt = epinow2.rt_opts(prior = ro.r.list(mean = 2, sd = 0.2)),
                    stan = epinow2.stan_opts(cores = 4))