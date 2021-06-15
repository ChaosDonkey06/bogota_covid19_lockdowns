from global_config import config
import pandas as pd
import numpy as np
import os

from rpy2.robjects.conversion import localconverter
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
import rpy2.robjects.numpy2ri
import rpy2.robjects as ro
import rpy2

from datetime import date, timedelta
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
fb_ppl_data   = config.get_property('covid_fb')
data_dir      = config.get_property('data_dir')
results_dir   = config.get_property('results_dir')

fb_ppl_data = '/Users/chaosdonkey06/Dropbox/covid_fb/data/data_stages/colombia'

data_cases_path = os.path.join(fb_ppl_data, 'agglomerated', 'geometry')

cases_df = pd.read_csv(os.path.join(data_cases_path, 'cases.csv'), parse_dates=["date_time"])
cases_df = cases_df[cases_df.poly_id==11001]

dict_correct = {'Los Martires': 'Los Mártires', 'Fontibon': 'Fontibón', 'Engativa': 'Engativá',
                            'San Cristobal': 'San Cristóbal', 'Usaquen': 'Usaquén',
                            'Ciudad Bolivar': 'Ciudad Bolívar', 'Candelaria': 'La Candelaria'}

#cases_df["poly_id"]   = cases_df["poly_id"].apply(lambda s:   s.replace("colombia_bogota_localidad_",""))
#cases_df["poly_name"] = cases_df["poly_id"].apply(lambda s:   ' '.join( [word.capitalize() for word in s.replace("colombia_bogota_localidad_","").split('_') ] ) )
#cases_df["poly_name"] = cases_df["poly_name"].replace( dict_correct )



#cases_bog_df = cases_df.groupby(['poly_id', 'poly_name', 'date_time']).sum()[["num_cases", "num_diseased", "num_infected_in_icu"]]
#cases_bog_df = cases_bog_df.unstack([0,1]).resample('1D').sum().stack().stack()

cases_bog_df = cases_df.copy()
cases_bog_df = cases_bog_df.reset_index().groupby('date_time').sum()
cases_bog_df = cases_bog_df.reset_index().rename(columns={'date_time': 'date', 'num_cases': 'confirm'})[["date", "confirm", "num_diseased"]]
cases_bog_df = cases_bog_df.set_index("date").resample('1D').sum().reset_index()

with localconverter(ro.default_converter + pandas2ri.converter):
    r_df_bogota_loc = ro.conversion.py2rpy(cases_bog_df[['date','confirm']])
r_df_bogota_loc[0]  = base.as_Date(r_df_bogota_loc[0], format= "%Y-%m-%d")

bogota_rt = epinow2.epinow(reported_cases = r_df_bogota_loc,
                    generation_time = generation_time,
                    delays = epinow2.delay_opts(incubation_period, reporting_delay),
                    rt = epinow2.rt_opts(prior = ro.r.list(mean = 2, sd = 0.2)),
                    stan = epinow2.stan_opts(cores = 4))#, verborse=ro.r.TRUE)

l='bog'
inf_df = pd.DataFrame( bogota_rt[0][0] )
inf_df.to_csv( os.path.join(results_dir, 'bog_rt', 'infections_df_{}_confirmation.csv'.format(l)) )
rt_df  = pd.DataFrame( bogota_rt[0][1] )

# rt_df['date'] = rt_df['date'].map(lambda x: pd.to_datetime(0)+timedelta(days=x))
rt_df.to_csv( os.path.join(results_dir, 'bog_rt', 'rt_df_{}_confirmation.csv'.format(l)), index=False)