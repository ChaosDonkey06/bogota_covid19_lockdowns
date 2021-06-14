
import matplotlib.pyplot as plt
import scipy.io as sio
import pandas as pd
import numpy as np
import os

import sys


sys.path.insert(0,'..')
from global_config import config


for loc in lockdowns:
    print("Fitting counterfactual for lockdown {}".format(loc["code"]))
    data = bog_agg_df.loc[:loc["start_date"]][["confirm", "deaths"]].rename(columns={"smoothed_confirm": "confirmed", "smoothed_deaths": "death"})
    df_deaths, df_cases = fit_forecast(data, pop=8181047, path_to_save=os.path.join( results_dir, 'conterfactuals', loc["code"]) )