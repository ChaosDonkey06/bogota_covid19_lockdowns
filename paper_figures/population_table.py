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
pop_df       = pd.read_csv(os.path.join(results_dir, 'data', 'demography', 'localities_ages.csv'))

g1 = ['Chapinero', 'Los Mártires', 'San Cristóbal', 'Tunjuelito',
    'Rafael Uribe Uribe', 'Ciudad Bolívar', 'Santa Fe', 'Usme']
g2 = ['Bosa', 'Antonio Nariño', 'Kennedy', 'Puente Aranda', 'Fontibón']
g3 = ['Suba', 'Engativá', 'Barrios Unidos']
g4 = ['Usaquén', 'Chapinero', 'Santa Fe', 'La Candelaria', 'Teusaquillo', 'Puente Aranda', 'Antonio Nariño']

dict_correct = {'Los Martires': 'Los Mártires', 'Fontibon': 'Fontibón', 'Engativa': 'Engativá',
                            'San Cristobal': 'San Cristóbal', 'Usaquen': 'Usaquén', 'Ciudad Bolivar': 'Ciudad Bolívar'}


pop_df['location'] = pop_df['location'].replace(dict_correct)

polygons_bog['label'] = polygons_bog['label'].replace(dict_correct)
polygons_bog["g1"] = 0
polygons_bog["g2"] = 0
polygons_bog["g3"] = 0
polygons_bog["g4"] = 0

polygons_bog.crs = {'init' :'epsg:4326'}
polygons_bog = polygons_bog.to_crs(epsg='6933')
polygons_bog['area'] = polygons_bog['geometry'].map(lambda x:  float(pd.to_numeric(x.area)/10**6))

pop_df = pop_df.groupby(['location','year']).sum().reset_index()
pop_df = pop_df.append({'location': 'Puente Aranda', 'year': 2017, 'total': 221906}, ignore_index=True)
pop_df = pop_df.set_index('location')

for loc in g1:
    polygons_bog["g1"][polygons_bog.label==loc]=1
for loc in g2:
    polygons_bog["g2"][polygons_bog.label==loc]=1
for loc in g3:
    polygons_bog["g3"][polygons_bog.label==loc]=1
for loc in g4:
    polygons_bog["g4"][polygons_bog.label==loc]=1


polygons_bog['population'] = polygons_bog["label"].map(lambda x: pop_df.loc[x]["total"])

lockdowns_info_df =  pd.DataFrame(columns=['group', 'dates', 'localites', 'population', 'area', 'population_density'])
lockdowns_info_df['group'] =['g1', 'g2', 'g3', 'g4']
lockdowns_info_df = lockdowns_info_df.set_index('group')

# localities in lockdown
lockdowns_info_df.loc['g1']['localites'] =  '|'.join(g1)
lockdowns_info_df.loc['g2']['localites'] =  '|'.join(g2)
lockdowns_info_df.loc['g3']['localites'] =  '|'.join(g3)
lockdowns_info_df.loc['g4']['localites'] =  '|'.join(g4)

# area
lockdowns_info_df.loc['g1']['area'] =  np.sum(polygons_bog['area']*polygons_bog['g1'])
lockdowns_info_df.loc['g2']['area'] =  np.sum(polygons_bog['area']*polygons_bog['g2'])
lockdowns_info_df.loc['g3']['area'] =  np.sum(polygons_bog['area']*polygons_bog['g3'])
lockdowns_info_df.loc['g4']['area'] =  np.sum(polygons_bog['area']*polygons_bog['g4'])

# population
lockdowns_info_df.loc['g1']['population'] =  np.sum(polygons_bog['population']*polygons_bog['g1'])
lockdowns_info_df.loc['g2']['population'] =  np.sum(polygons_bog['population']*polygons_bog['g2'])
lockdowns_info_df.loc['g3']['population'] =  np.sum(polygons_bog['population']*polygons_bog['g3'])
lockdowns_info_df.loc['g4']['population'] =  np.sum(polygons_bog['population']*polygons_bog['g4'])

lockdowns_info_df['population_density'] =  lockdowns_info_df['population']/lockdowns_info_df['area']


########
#polygons_bog = polygons_bog[["location_id", "label", "area", "population"]].rename(columns={'location_id': 'poly_id', 'label': 'poly_name'})
#polygons_bog.to_csv('/Users/chaosdonkey06/Dropbox/covid_fb/data/data_stages/bogota/agglomerated/geometry/polygons_pop.csv')