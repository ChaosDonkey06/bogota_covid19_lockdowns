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

import sys


re_write_bool  = bool(sys.argv[0])

rpy2.robjects.numpy2ri.activate()
epinow2 = importr("EpiNow2")
base    = importr('base')

generation_time   = epinow2.get_generation_time(disease = "SARS-CoV-2", source = "ganyani")
incubation_period = epinow2.get_incubation_period(disease = "SARS-CoV-2", source = "lauer")
reporting_delay   = epinow2.estimate_delay(ro.r.rlnorm(1000,  ro.r.log(3), 1),
                                  max_value = 15, bootstraps = 1)


data_dir_mnps = config.get_property('geo_dir')
data_dir      = config.get_property('data_dir')
fb_ppl_data   = config.get_property('covid_fb')
results_dir   = config.get_property('results_dir')

data_cases_path = os.path.join(fb_ppl_data, 'agglomerated', 'geometry')

cases_df = pd.read_csv(os.path.join(data_cases_path, 'cases.csv'), parse_dates=["date_time"])
cases_bog_df = cases_df.groupby('date_time').sum()[["num_cases", "num_diseased"]]
cases_bog_df = cases_bog_df.resample('1D').sum().reset_index().rename(columns={'date_time': 'date', 'num_cases': 'confirm', 'num_diseased': 'death'})

r_df_bogota_loc = ro.conversion.py2rpy(cases_bog_df[['date','confirm']])
r_df_bogota_loc[0]  = base.as_Date(r_df_bogota_loc[0], format= "%Y-%m-%d")
bogota_rt = epinow2.epinow(reported_cases = r_df_bogota_loc,
                    generation_time = generation_time,
                    delays = epinow2.delay_opts(incubation_period, reporting_delay),
                    rt = epinow2.rt_opts(prior = ro.r.list(mean = 2, sd = 0.2)),
                    stan = epinow2.stan_opts(cores = 4))#, verborse=ro.r.TRUE)

inf_df = pd.DataFrame( bogota_rt[0][0] )
inf_df.to_csv( os.path.join(results_dir, 'bog_rt', 'infections_df_{}_confirmation.csv'.format(l)) )
rt_df  = pd.DataFrame( bogota_rt[0][1] )
rt_df.to_csv( os.path.join(results_dir, 'bog_rt', 'rt_df_{}_confirmation.csv'.format(l)) )