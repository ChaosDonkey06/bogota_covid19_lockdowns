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


from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
from mpl_toolkits.axes_grid.inset_locator import inset_axes

from matplotlib.dates import date2num, num2date
from matplotlib.colors import ListedColormap
from matplotlib import dates as mdates
from matplotlib.patches import Patch
from matplotlib import pyplot as plt
from matplotlib import ticker


from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

from datetime import date, timedelta

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

df_bogota = pd.read_csv(os.path.join(data_dir, 'cases', 'cases_prepared.csv'), index_col=None).rename(columns={'date_time': 'date'})

with localconverter(ro.default_converter + pandas2ri.converter):
    r_df_bogota = ro.conversion.py2rpy(df_bogota[['date','confirm', 'region']])


r_df_bogota[0]  = base.as_Date(r_df_bogota[0], format= "%Y-%m-%d")

df_bogota['poly_id']   = df_bogota['region'].map(lambda x: x.split('-')[0].strip() )
df_bogota['poly_name'] = df_bogota['region'].map(lambda x: x.split('-')[-1].strip())

path_to_save = '/Users/chaosdonkey06/Dropbox/bogota_rotating_lockdowns'
poly_ids = [ '{0:02d}'.format(n) for n in range(1,20)]

g1 = ['Chapinero', 'Los Mártires', 'San Cristóbal', 'Tunjuelito',
    'Rafael Uribe Uribe', 'Ciudad Bolívar', 'Santa Fe', 'Usme']
g2 = ['Bosa', 'Antonio Nariño', 'Kennedy', 'Puente Aranda', 'Fontibón']
g3 = ['Suba', 'Engativá', 'Barrios Unidos']
g4 = ['Usaquén', 'Chapinero', 'Santa Fe', 'La Candelaria', 'Teusaquillo', 'Puente Aranda', 'Antonio Nariño']

all_localities = list(set(g1+g2+g3+g4))

rt_df_all = []
for idx, l in enumerate(np.unique(all_localities)):
    df_bogota_loc = df_bogota[df_bogota.poly_name==l]
    poly_id = df_bogota_loc['poly_id'].iloc[0]
    cases = df_bogota[df_bogota.poly_id==poly_id]

    rt_df = pd.read_csv(os.path.join(path_to_save, 'rt', 'rt_df_{}_confirmation.csv'.format(poly_id)))
    rt_df['region']    = l
    rt_df['region_id'] = poly_id
    rt_df_all.append(rt_df)
rt_df_all = pd.concat(rt_df_all)
rt_df_all = rt_df_all[rt_df_all.type=='estimate']
rt_df_all = rt_df_all[rt_df_all.variable=='R']

rt_df_all['date'] = rt_df_all['date'].map(lambda x: pd.to_datetime(0)+timedelta(days=x))
rt_df_all = rt_df_all[['date', 'median', 'mean', 'lower_90', 'lower_50', 'lower_20', 'upper_20', 'upper_50', 'upper_90', 'region', 'region_id']]

rt_df_all.to_csv(os.path.join(path_to_save, 'rt_merged_all.csv'))