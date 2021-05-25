from global_config import config
import pandas as pd
import numpy as np
import rpy2
import os

from matplotlib.dates import date2num, num2date
from matplotlib.colors import ListedColormap
from matplotlib import dates as mdates
from matplotlib.patches import Patch
from matplotlib import pyplot as plt
from matplotlib import ticker

from datetime import date, timedelta
import sys



data_dir_mnps = config.get_property('geo_dir')
fb_ppl_data   = config.get_property('covid_fb')
data_dir      = config.get_property('data_dir')
results_dir   = config.get_property('results_dir')


rt_df = pd.read_csv( os.path.join(results_dir, 'bog_rt', 'rt_df_bog_confirmation.csv') )
rt_df = rt_df[rt_df.variable=='R']
rt_df['date'] = rt_df['date'].map(lambda x: pd.to_datetime(0)+timedelta(days=x))
rt_df.to_csv(os.path.join(results_dir, 'bog_rt', 'rt.csv'))
#rt_df = rt_df[rt_df["type"]=="estimate"]

fig, ax = plt.subplots(1, 1, figsize=(12.5, 7))

ax.fill_between(rt_df.date, rt_df.upper_90, rt_df.lower_90, alpha=0.2)
ax.plot(rt_df.date, rt_df['median'])
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
ax.set_title('Bogotá D.C.', fontsize=15)
ax.set_ylabel(r'$R_t$', fontsize=15)
ax.legend(fontsize=15)
ax.set_ylim([0.6, 2])
