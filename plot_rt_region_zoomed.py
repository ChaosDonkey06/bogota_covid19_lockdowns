

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

all_localities = g1+g2+g3+g4

# color will now be an RGBA tuple
import pylab

def plot_rt_pannel_zoomed(cases_df, g1, all_loc, title, date1, date2, path_to_save_fig):

    fig, ax = plt.subplots(1, 1, figsize=(12.5, 7), sharex='all')

    NUM_COLORS = len(g1)
    cm = pylab.get_cmap('gist_ncar')

    for idx, l in enumerate(g1):
        print('Plotting rt estimates for loc {}'.format( l ))
        df_bogota_loc = cases_df[cases_df.poly_name==l]
        poly_id = df_bogota_loc['poly_id'].iloc[0]

        rt_df = pd.read_csv(os.path.join(path_to_save, 'rt', 'rt_df_{}_confirmation.csv'.format(poly_id)))
        rt_df = rt_df[rt_df.variable=='R']
        rt_df['date'] = pd.date_range(start=df_bogota_loc['date'].iloc[0], periods=len(rt_df) )
        rt_df= rt_df.iloc[:len(df_bogota_loc)]

        color = cm(1.*idx/NUM_COLORS)
        ax.fill_between(rt_df.date, rt_df.upper_90, rt_df.lower_90, alpha=0.2, color=color)
        ax.plot(rt_df.date, rt_df['median'], label=l, color=color)
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
        ax.set_title(title, fontsize=15)
        ax.set_ylabel(r'$R_t$', fontsize=15)
        ax.legend(fontsize=15)
        ax.set_ylim([0.4, 2.5])
        ax.axvline(x=pd.to_datetime(date1), ymin=0, ymax=3, color='k')
        ax.axvline(x=pd.to_datetime(date2), ymin=0, ymax=3, color='k', linestyle='--')
        ax.legend(loc='upper left')
    ax.set_xlim(rt_df.date.iloc[0]-timedelta(days=2), rt_df.date.iloc[-1]+timedelta(days=30))

    axins = zoomed_inset_axes(ax, 2, loc=1)#, zoom = 6)
    for idx, l in enumerate(g1):
        print('Plotting rt estimates for loc {}'.format( l ))
        df_bogota_loc = cases_df[cases_df.poly_name==l]
        poly_id = df_bogota_loc['poly_id'].iloc[0]

        rt_df = pd.read_csv(os.path.join(path_to_save, 'rt', 'rt_df_{}_confirmation.csv'.format(poly_id)))
        rt_df = rt_df[rt_df.variable=='R']
        rt_df['date'] = pd.date_range(start=df_bogota_loc['date'].iloc[0], periods=len(rt_df) )
        rt_df= rt_df.iloc[:len(df_bogota_loc)]

        color = cm(1.*idx/NUM_COLORS)
        axins.fill_between(rt_df.date, rt_df.upper_90, rt_df.lower_90, alpha=0.2, color=color)
        axins.plot(rt_df.date, rt_df['median'], label=l, color=color)

        # sub region of the original image
        axins.set_xlim(pd.to_datetime(date1)-timedelta(days=2), pd.to_datetime(date2)+timedelta(days=2))
        axins.set_ylim(0.75, 1.2)
    #axins.set_xticks(visible=False)
    #axins.set_yticks(visible=False)
    mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5")
    axins.xaxis.set_major_locator(mdates.MonthLocator())
    axins.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    axins.xaxis.set_minor_locator(mdates.DayLocator())
    axins.xaxis.set_major_locator(mdates.WeekdayLocator())
    axins.xaxis.set_major_locator(mdates.MonthLocator())
    axins.axvline(x=pd.to_datetime(date1), ymin=0, ymax=3, color='k')
    axins.axvline(x=pd.to_datetime(date2), ymin=0, ymax=3, color='k', linestyle='--')
    axins.axhline(y=1, color='k', linestyle='--')
    axins.tick_params(
        axis='both',          # changes apply to the x-axis
        which='major',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False)

    if path_to_save_fig:
        fig.savefig(path_to_save_fig, dpi=300,  bbox_inches='tight', transparent=True)



plot_rt_pannel_zoomed(df_bogota, g1, all_localities, title='Group 1', date1='2020-07-13', date2='2020-07-23', path_to_save_fig=os.path.join(path_to_save, 'grupo1_zoom.png'))
plt.close()

plot_rt_pannel_zoomed(df_bogota, g2, all_localities, title='Group 2', date1='2020-07-23', date2='2020-08-06', path_to_save_fig=os.path.join(path_to_save, 'Group2_zoom.png'))
plt.close()

plot_rt_pannel_zoomed(df_bogota, g3, all_localities, title='Group 3', date1='2020-07-31', date2='2020-08-14', path_to_save_fig=os.path.join(path_to_save, 'Group3_zoom.png'))
plt.close()

plot_rt_pannel_zoomed(df_bogota, g4, all_localities, title='Group 4', date1='2020-08-16', date2='2020-08-24', path_to_save_fig=os.path.join(path_to_save, 'grupo4_zoom.png'))
plt.close()