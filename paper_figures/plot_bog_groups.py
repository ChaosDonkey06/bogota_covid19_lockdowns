from datetime import timedelta
import contextily as ctx
import geopandas as gpd
from shapely import wkt
import geopandas as gpd
from tqdm import tqdm
import seaborn as sns
import pandas as pd
import numpy as np
import itertools

from shapely.geometry import Point, LineString
from global_config import config
import matplotlib.pyplot as plt
import os, sys

geo_dir       = config.get_property('geo_dir')
results_dir   = config.get_property('results_dir')

path_to_bog_polygon = os.path.join(geo_dir, 'localities', 'localities_shapefile.shp')

# Read bogota polygons divided by localities.
polygons_bog = gpd.read_file( path_to_bog_polygon )
polygons_bog = polygons_bog.rename(columns={'location_i': 'location_id'})

g1           = ['Chapinero', 'Los Mártires', 'San Cristóbal', 'Tunjuelito',
              'Rafael Uribe Uribe', 'Ciudad Bolívar', 'Santa Fe', 'Usme']
g2           = ['Bosa', 'Antonio Nariño', 'Kennedy', 'Puente Aranda', 'Fontibón']
g3           = ['Suba', 'Engativá', 'Barrios Unidos']
g4           = ['Usaquén', 'Chapinero', 'Santa Fe', 'La Candelaria', 'Teusaquillo', 'Puente Aranda', 'Antonio Nariño']
dict_correct = {'Los Martires': 'Los Mártires', 'Fontibon': 'Fontibón', 'Engativa': 'Engativá',
                            'San Cristobal': 'San Cristóbal', 'Usaquen': 'Usaquén',
                            'Ciudad Bolivar': 'Ciudad Bolívar', 'Candelaria': 'La Candelaria'}
polygons_bog['label'] = polygons_bog['label'].replace(dict_correct)

polygons_bog["group_1"]       = None
polygons_bog["group_1_label"] = None

polygons_bog["group_2"]       = None
polygons_bog["group_2_label"] = None

polygons_bog["group_3"] = None
polygons_bog["group_3_label"] = None

polygons_bog["group_4"]       = None
polygons_bog["group_4_label"] = None

for loc in g1:
    polygons_bog["group_1"][polygons_bog.label==loc]       = True
    polygons_bog["group_1_label"][polygons_bog.label==loc] = loc

for loc in g2:
    polygons_bog["group_2"][polygons_bog.label==loc]=True
    polygons_bog["group_2_label"][polygons_bog.label==loc]=loc

for loc in g3:
    polygons_bog["group_3"][polygons_bog.label==loc]=True
    polygons_bog["group_3_label"][polygons_bog.label==loc]=loc

for loc in g4:
    polygons_bog["group_4"][polygons_bog.label==loc]=True
    polygons_bog["group_4_label"][polygons_bog.label==loc]=loc

def plot_bog_specified_column(df_polygons, title, col_name='value', cmap = 'seismic_r', labels = True, path_to_save = None):
    fig, ax = plt.subplots(1,1, figsize=(10, 20))

    maps1 = polygons_bog.plot(ax=ax, edgecolor='black', alpha=0.3, facecolor='Grey', linewidth=1)
    maps2 = polygons_bog.plot(ax=ax, edgecolor='gray', column=col_name, cmap=cmap, alpha=0.8, linewidth=1)

    # Plot values as linestring
    ax.set_title(title, fontsize = 16)
    ax.set_axis_off()

    if labels:
        df_polygons.apply(lambda p: ax.text(s=p[col_name+'_label'], x=p.geometry.centroid.coords[0][0], y = p.geometry.centroid.coords[0][1], ha='center', fontsize=15), axis=1)

    if path_to_save:
        fig.savefig(path_to_save, bbox_inches='tight', dpi=300, transparent=True)

path_to_figs = os.path.join(results_dir, 'figures', 'maps_group')
plot_bog_specified_column(polygons_bog, None, col_name='group_1', cmap = 'seismic_r', labels = True, path_to_save = os.path.join(path_to_figs, 'group_1.png'))
plot_bog_specified_column(polygons_bog, None, col_name='group_2', cmap = 'seismic_r', labels = True, path_to_save = os.path.join(path_to_figs, 'group_2.png'))
plot_bog_specified_column(polygons_bog, None, col_name='group_3', cmap = 'seismic_r', labels = True, path_to_save = os.path.join(path_to_figs, 'group_3.png'))
plot_bog_specified_column(polygons_bog, None, col_name='group_4', cmap = 'seismic_r', labels = True, path_to_save = os.path.join(path_to_figs, 'group_4.png'))
