from global_config import config
import pandas as pd
import numpy as np
import pylab
import rpy2
import os

from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

from matplotlib.dates import date2num, num2date
from matplotlib.colors import ListedColormap
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from matplotlib.patches import Patch
from matplotlib import ticker

import geopandas as gpd
from shapely import wkt


data_movement = config.get_property('covid_fb')
data_dir_mnps = config.get_property('geo_dir')
data_dir      = config.get_property('data_dir')
results_dir   = config.get_property('results_dir')


g1 = ['Chapinero', 'Los Mártires', 'San Cristóbal', 'Tunjuelito',
    'Rafael Uribe Uribe', 'Ciudad Bolívar', 'Santa Fe', 'Usme']
g2 = ['Bosa', 'Antonio Nariño', 'Kennedy', 'Puente Aranda', 'Fontibón']
g3 = ['Suba', 'Engativá', 'Barrios Unidos']
g4 = ['Usaquén', 'Chapinero', 'Santa Fe', 'La Candelaria',
        'Teusaquillo', 'Puente Aranda', 'Antonio Nariño']

dict_info= {
            'g1': {'dates': (pd.to_datetime('2020-07-13'), pd.to_datetime('2020-07-26')), 'localities': g1},
            'g2': {'dates': (pd.to_datetime('2020-07-23'), pd.to_datetime('2020-08-06')), 'localities': g2},
            'g3': {'dates': (pd.to_datetime('2020-07-31'), pd.to_datetime('2020-08-14')), 'localities': g3},
            'g4': {'dates': (pd.to_datetime('2020-08-16'), pd.to_datetime('2020-08-27')), 'localities': g4}
            }

all_localities = set(g1+g2+g3+g4)
num_localities = len(all_localities)

rt_df = pd.read_csv(os.path.join(results_dir, 'rt_merged_all.csv'))
rt_df = rt_df.drop(columns=['Unnamed: 0'])
rt_df['date'] = pd.to_datetime(rt_df['date'])
cm = pylab.get_cmap('gist_ncar')



fig, ax = plt.subplots(1, 1, figsize=(15.5, 7))

dates_before = pd.date_range(end='2020-07-13', periods=15)
dates_after  = pd.date_range(start='2020-08-27', periods=15)

rt_df_before = rt_df.copy(); rt_df_before = rt_df_before[rt_df_before.date.isin(dates_before)]
rt_df_after = rt_df.copy(); rt_df_after = rt_df_after[rt_df_after.date.isin(dates_after)]


for idx, loc in enumerate(rt_df.region.unique()):
    color = cm(1.*idx/num_localities)

    rt_loc_before = rt_df_before.copy(); rt_loc_before = rt_loc_before[rt_loc_before.region==loc]
    ax.fill_between(rt_loc_before.date, rt_loc_before.upper_90, rt_loc_before.lower_90, alpha=0.2, color=color)
    ax.plot(rt_loc_before.date, rt_loc_before["median"], color=color, linewidth=0.5)

    rt_loc_after = rt_df_after.copy(); rt_loc_after = rt_loc_after[rt_loc_after.region==loc]
    ax.fill_between(rt_loc_after.date, rt_loc_after.upper_90, rt_loc_after.lower_90, alpha=0.2, color=color)
    ax.plot(rt_loc_after.date, rt_loc_after["median"], color=color, linewidth=0.5)


for idx, group_l in enumerate(dict_info.keys()):

    dates      = dict_info[group_l]['dates']
    localities = dict_info[group_l]['localities']

    date_range = pd.date_range(start=dates[0], end=dates[1])
    ax.axvspan(dates[0], dates[1], facecolor=cm(1.*idx/4), alpha=0.1)

    rt_df_lock = rt_df.copy(); rt_df_lock = rt_df_lock[rt_df_lock.region.isin(localities)];  rt_df_lock = rt_df_lock[rt_df_lock.date.isin(date_range)]
    rt_df_free = rt_df.copy(); rt_df_free = rt_df_free[~rt_df_free.region.isin(localities)]; rt_df_free = rt_df_free[rt_df_free.date.isin(date_range)]

    for loc in rt_df_lock.region.unique():
        rt_df_lock_loc = rt_df_lock.copy(); rt_df_lock_loc = rt_df_lock_loc[rt_df_lock_loc.region==loc]
        #ax.fill_between(rt_df_lock_loc.date, rt_df_lock_loc.upper_90, rt_df_lock_loc.lower_90, alpha=0.2, color='red')
        ax.plot(rt_df_lock_loc.date, rt_df_lock_loc["median"], color='red', linewidth=0.4)

    #for loc in rt_df_free.region.unique():
    #    ax.fill_between(rt_df_free.date, rt_df_free.upper_90, rt_df_free.lower_90, alpha=0.2, color='grey')
    #    ax.plot(rt_df_free.date, rt_df_free["median"], color='grey', alpha=0.1, linewidth=0.4)

    rt_df_lock  = rt_df_lock.groupby('date').mean().reset_index()
    lock_ribbon = ax.fill_between(rt_df_lock.date, rt_df_lock.upper_90, rt_df_lock.lower_90, alpha=0.2, color='red')
    lock_median = ax.plot(rt_df_lock.date, rt_df_lock["median"], color='red')

    rt_df_free  = rt_df_free.groupby('date').mean().reset_index()
    free_ribbon = ax.fill_between(rt_df_free.date, rt_df_free.upper_90, rt_df_free.lower_90, alpha=0.2, color='black')
    free_median = ax.plot(rt_df_free.date, rt_df_free["median"], color='black')

#ax.legend([lock_ribbon, '95% CI - Lockdown'])
#ax.legend([free_ribbon, '95% CI - Free'])

ax.axhline(y=1, color='k', linestyle='--')
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.xaxis.set_minor_locator(mdates.DayLocator())
ax.xaxis.set_major_locator(mdates.WeekdayLocator())
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.grid(which='major', axis='y', c='k', alpha=.1, zorder=-2)
ax.tick_params(axis='both', labelsize=15)
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.2f}"))
ax.set_title('Rotating lockdown effect', fontsize=15)
ax.set_ylabel(r'$R_t$', fontsize=15)
ax.legend(fontsize=15)
ax.legend(loc='upper left')
plt.show()
