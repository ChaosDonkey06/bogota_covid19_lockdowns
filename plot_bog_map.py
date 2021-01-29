import itertools
import numpy as np
import pandas as pd
import seaborn as sns
from tqdm import tqdm
import geopandas as gpd
from shapely import wkt
import geopandas as gpd
import contextily as ctx
from datetime import timedelta
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
import os, sys
from global_config import config

geo_dir       = config.get_property('geo_dir')
results_dir   = config.get_property('results_dir')

path_to_bog_polygon = os.path.join(geo_dir, 'localities', 'localities_shapefile.shp')


# Read bogota polygons divided by localities.
polygons_bog = gpd.read_file( path_to_bog_polygon )
polygons_bog = polygons_bog.rename(columns={'location_i': 'location_id'})

g1 = ['Chapinero', 'Los Mártires', 'San Cristóbal', 'Tunjuelito',
    'Rafael Uribe Uribe', 'Ciudad Bolívar', 'Santa Fe', 'Usme']
g2 = ['Bosa', 'Antonio Nariño', 'Kennedy', 'Puente Aranda', 'Fontibón']
g3 = ['Suba', 'Engativá', 'Barrios Unidos']
g4 = ['Usaquén', 'Chapinero', 'Santa Fe', 'La Candelaria', 'Teusaquillo', 'Puente Aranda', 'Antonio Nariño']

def plot_movement_polygons(df_polygons, title, clim_max=700, col_name='value', cmap = 'coolwarm', labels = True, path_to_save = None):
    fig, ax = plt.subplots(1,1, figsize=(10, 20))

    # Plot base polygon
    df_polygons.plot(ax=ax, edgecolor='black', facecolor='white', cmap=cmap,)

    # Plot values as linestring
    ax.set_title(title, fontsize = 16)
    ax.set_axis_off()
    if labels:
        df_polygons.apply(lambda p: ax.text(s=p['label'], x=p.geometry.centroid.coords[0][0], y = p.geometry.centroid.coords[0][1], ha='center'), axis=1)
    if path_to_save:
        fig.savefig(path_to_save, bbox_inches='tight', dpi=400)