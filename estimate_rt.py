from global_config import config
import pandas as pd
import numpy as np
import rpy2
import os

from rpy2.robjects.conversion import localconverter
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
import rpy2.robjects.numpy2ri
import rpy2.robjects as ro


rpy2.robjects.numpy2ri.activate()
epinow2 = importr("EpiNow2")
dplyr   = importr('dplyr')
base    = importr('base')

generation_time   = epinow2.get_generation_time(disease = "SARS-CoV-2", source = "ganyani")
incubation_period = epinow2.get_incubation_period(disease = "SARS-CoV-2", source = "lauer")
reporting_delay   = epinow2.estimate_delay(ro.r.rlnorm(1000,  ro.r.log(3), 1),
                                  max_value = 15, bootstraps = 1)


data_dir_mnps = config.get_property('geo_dir')
data_dir      = config.get_property('data_dir')
results_dir   = config.get_property('results_dir')

df_bogota = pd.read_csv(os.path.join(data_dir, 'cases', 'cases_prepared.csv'),index_col=None).rename(columns={'date_time': 'date'})

with localconverter(ro.default_converter + pandas2ri.converter):
    r_df_bogota = ro.conversion.py2rpy(df_bogota[['date','confirm', 'region']])


r_df_bogota[0]  = base.as_Date(r_df_bogota[0], format= "%Y-%m-%d")

bogota_rt = epinow2.epinow(reported_cases = r_df_bogota,
                    generation_time = generation_time,
                    delays = epinow2.delay_opts(incubation_period, reporting_delay),
                    rt = epinow2.rt_opts(prior = ro.r.list(mean = 2, sd = 0.2)),
                    stan = epinow2.stan_opts(cores = 4))