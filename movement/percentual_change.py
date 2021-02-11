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
from matplotlib import dates as mdates
from matplotlib import ticker
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from matplotlib import pyplot as plt

import geopandas as gpd
from shapely import wkt

data_movement = config.get_property('covid_fb')
data_dir_mnps = config.get_property('geo_dir')
data_dir      = config.get_property('data_dir')
results_dir   = config.get_property('results_dir')

rt_df_all = pd.read_csv(os.path.join(results_dir, 'rt_merged_all.csv'), index_col='date')
rt_df_all.drop(columns=['Unnamed: 0'])


movement_df = pd.read_csv(os.path.join(data_movement, 'agglomerated', 'geometry', 'movement.csv'))
manz_gdf    = gpd.GeoDataFrame(pd.read_csv(os.path.join(data_movement, 'agglomerated', 'geometry', 'polygons.csv')))
manz_gdf['geometry'] = manz_gdf['geometry'].apply(wkt.loads)
manz_gdf = gpd.GeoDataFrame(manz_gdf, geometry='geometry')
manz_gdf = manz_gdf[['poly_id', 'attr_area',  'poly_name', 'poly_lon', 'poly_lat', 'geometry']]
manz_gdf.crs = "EPSG:4326"

localities_gdf            = gpd.read_file( os.path.join(data_dir_mnps, 'localities', 'localities_shapefile.shp'))
localities_gdf             = localities_gdf.rename(columns={'location_i': 'location_id'})
localities_gdf.crs = "EPSG:4326"


merged_polygons_df = gpd.sjoin(localities_gdf, manz_gdf, how="inner", op='intersects')
poly_id2locality   = {x.poly_id: x.label for idx, x in  merged_polygons_df[['poly_id', 'label']].iterrows()}

movement_df = movement_df.set_index('date_time')
movement_df['start_poly_id'] = movement_df['start_poly_id'].map(poly_id2locality)
movement_df['end_poly_id'] = movement_df['end_poly_id'].map(poly_id2locality)
movement_df = movement_df.groupby(['date_time','start_poly_id', 'end_poly_id']).sum().reset_index().set_index('date_time')

g1 = ['Chapinero', 'Los Mártires', 'San Cristóbal', 'Tunjuelito',
    'Rafael Uribe Uribe', 'Ciudad Bolívar', 'Santa Fe', 'Usme']
g2 = ['Bosa', 'Antonio Nariño', 'Kennedy', 'Puente Aranda', 'Fontibón']
g3 = ['Suba', 'Engativá', 'Barrios Unidos']
g4 = ['Usaquén', 'Chapinero', 'Santa Fe', 'La Candelaria',
    'Teusaquillo', 'Puente Aranda', 'Antonio Nariño']
