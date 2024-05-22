# -*- coding: utf-8 -*-
"""get_osm_data_final_vkr.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1eCFM_x5R5vvGyNq3cDyQojTDiP50RRbJ

## Подготовительная работа
* [Installing a Library Permanently in Colab](https://saturncloud.io/blog/how-to-install-a-library-permanently-in-colab/)
"""

## connect google drive
from google.colab import drive


drive.mount('/content/drive')

!pip install virtualenv
!virtualenv /content/drive/MyDrive/vkr/kmu/virtual_env

import sys


venv_path = "/content/drive/MyDrive/vkr/kmu/virtual_env/lib/python3.10/site-packages"
if venv_path not in sys.path:
  # add the path of the virtual environment site-packages to colab system path
  sys.path.append(venv_path)
sys.path

"""## Выгрузка данных из OSM

```bash
!source /content/drive/MyDrive/vkr/kmu/virtual_env/bin/activate; pip install pyrosm contextily mapclassify osmnx
```
"""

!pip freeze

"""### Конфигурация"""

DIR_OSM = '/content/drive/MyDrive/vkr/kmu/src/osm/'
CITY = 'SanktPetersburg'
##BBOX = [30.2561753, 59.929385, 30.3637657, 59.9832816]
BBOX = [30.2665719, 59.8913232, 30.4101337, 59.9632426]
UTM_ZONE = 32636

config = {
    'dir_osm': DIR_OSM,
    'city': CITY,
    'crs': UTM_ZONE,
    'filters': {
        'buildings': {
            'all': {
                'building': True
            },
            'residential_only': {
                'building': [
                'apartments',
                'residential'
              ]
            }
        },
        'POIs': {
            'shop': [
                'convenience',
                'supermarket',
                'mall',
                'greengrocer'
            ],
            'amenity': [
                'pharmacy',
                'university',
                'school',
                'kindergarten',
                'clinic',
                'car_wash'
            ],
            'healthcare': [
                'clinic'
            ]
        },
        'network_type': [
            'walking',
            'driving'
        ]
    },
    'bbox': BBOX
}

"""### Логирование

<details>
<summary> Log levels</summary>

```py
logging.debug("A DEBUG Message")
logging.info("An INFO")
logging.warning("A WARNING")
logging.error("An ERROR")
logging.critical("A message of CRITICAL severity")
```
</details>
"""

!pwd

import logging
import datetime

start = datetime.datetime.today().strftime("%Y_%m_%d")

logger = logging.getLogger()
fhandler = logging.FileHandler(filename=config["dir_osm"]+'get_osm_data_'+start+'.log', mode='w')
logger.addHandler(fhandler)
logger.setLevel(logging.INFO)

"""### All data"""

from pyrosm import get_data, OSM


# download data for the city
fp = get_data(dataset=config['city'], directory=config['dir_osm'])
logger.info(f'data was downloaded to {fp}')

if 'bbox' in config:
  osm = OSM(fp, bounding_box=config['bbox'])
  logger.info(f'work with bbox: {config["bbox"]}')
else:
  osm = OSM(fp)
  logger.info(f'work with all city: {config["city"]}')

"""### Buildings"""

buildings_type = config['filters']['buildings']['residential_only']
#buildings_type = config["filters"]["buildings"]["all"]

buildings = osm.get_data_by_custom_criteria(custom_filter=buildings_type, tags_as_columns=['building', 'building:levels', 'addr:country', 'addr:city', 'addr:street', 'addr:housenumber', 'lon', 'lat', 'osm_type']).set_index('id')
logger.info(f'get buildings by filter {buildings_type}')

buildings.head(2)

buildings = buildings.rename(columns={'building:levels': 'levels',
                          'addr:country': 'country',
                          'addr:city': 'city',
                          'addr:street':'street',
                          'addr:housenumber': 'housenumber'})

buildings.info()

buildings.version.value_counts()

buildings.osm_type.value_counts()

buildings.housenumber.isnull().sum()

buildings = buildings.dropna(subset=["housenumber"])
logger.info(f'drop buildings without housenumber')

if 'lon' in buildings.columns or 'lat' in buildings.columns:
  buildings = buildings.drop(index=buildings[buildings.lon.notna() == True].index)
  logger.info('drop point buildings')

buildings = buildings[['building', 'levels', 'country', 'city', 'street', 'housenumber', 'osm_type', 'geometry']].to_crs(config['crs'])
logger.info(f'project buildings to {buildings.crs.to_string()}')

"""POINT(x, y)
* x --> lon (долгота)
* y --> lat (широта)
"""

buildings.head(2)

buildings.country.value_counts()

buildings.city.value_counts()

buildings.country = buildings.country.fillna('RU')
buildings.city = buildings.city.fillna('Санкт-Петербург')

buildings['centroid'] = buildings.centroid
buildings['centroid_x'] = buildings.centroid.x
buildings['centroid_y'] = buildings.centroid.y

logger.info(f'add building centroid')

buildings.head(2)

import contextily as cx
from matplotlib import pyplot as plt
import datetime

start = datetime.datetime.today().strftime("%Y_%m_%d")

with plt.style.context("ggplot"):
  ax = buildings.plot(column='building', figsize=(20, 10), legend=True, linewidth=0.4, legend_kwds=dict(loc='upper right', ncol=1))
  #ax = buildings['centroid'].plot(ax=ax, markersize=2)
  cx.add_basemap(ax=ax, crs=buildings.crs.to_string(), source=cx.providers.CartoDB.Voyager)
  ax.set_title('Buildings', fontsize=15, fontweight='bold')
  fp = config['dir_osm']+'images/buildings_'+start+'.png'
  plt.savefig(fp, bbox_inches='tight')
  logger.info(f'save buildings to {fp}')
  plt.show()

import contextily as cx
from matplotlib import pyplot as plt
import datetime

start = datetime.datetime.today().strftime("%Y_%m_%d")

with plt.style.context("ggplot"):
  ax = buildings.plot(column='building', edgecolor='black', figsize=(20, 10), legend=True, linewidth=0.4, legend_kwds=dict(loc='upper right', ncol=1))
  ax = buildings['centroid'].plot(ax=ax, edgecolor='black', markersize=30)
  #plt.setp(ax, xlim=(352000, 353000), ylim=(6647000, 6648000))
  plt.setp(ax, xlim=(348500, 349500), ylim=(6649000, 6650000))

  cx.add_basemap(ax=ax, crs=buildings.crs.to_string(), source=cx.providers.CartoDB.Voyager)

  ax.set_title('Buildings', fontsize=15, fontweight='bold')
  fp = config['dir_osm']+'images/buildings_zoom_'+start+'.png'
  plt.savefig(fp, bbox_inches='tight')
  logger.info(f'save buildings to {fp}')
  plt.show()

#buildings.explore(column='building', tiles="CartoDB positron")

import datetime

start = datetime.datetime.today().strftime("%Y_%m_%d")

fp = ''
if 'bbox' in config:
  fp = DIR_OSM + 'spb_bbox_' + start + '.gpkg'
  buildings.drop(columns='centroid').to_file(fp, driver='GPKG', layer='buildings', encoding='utf-8')
  logger.info(f'save buildings to {fp}')
else:
  fp = DIR_OSM + 'spb_' + start + '.gpkg'
  buildings.drop(columns='centroid').to_file(fp, driver='GPKG', layer='buildings', encoding='utf-8')
  logger.info(f'save buildings to {fp}')

from geopandas import read_file


buildings_from_gpkg = read_file(fp, layer='buildings').set_index('id')

if buildings.shape[0] == buildings_from_gpkg.shape[0] and buildings.crs == buildings_from_gpkg.crs:
  logger.info(f'buildings successfully loaded from gpkg')

buildings_from_gpkg.head(2)

"""### POIs"""

pois_type = config["filters"]["POIs"]

pois = osm.get_data_by_custom_criteria(custom_filter=pois_type, tags_as_columns=["shop", "amenity", "healthcare", "name"]).set_index('id')
logger.info(f'get pois by filter {pois_type}')

pois.head(2)

pois.info()

pois.version.value_counts()

pois.osm_type.value_counts()

pois.name.isnull().sum()

pois = pois.dropna(subset=["name"])
logger.info(f'drop unnamed pois')

pois.shape

pois.loc[~pois.shop.isin(config['filters']['POIs']['shop']), 'shop'] = ""
pois.loc[~pois.amenity.isin(config['filters']['POIs']['amenity']), 'amenity'] = ""
pois.loc[~pois.healthcare.isin(config['filters']['POIs']['healthcare']), 'healthcare'] = ""

pois['pois'] = pois.shop + pois.amenity + pois.healthcare
pois.loc[pois.pois == 'clinicclinic', 'pois'] = 'clinic'

logger.info(f'add pois type')

pois['pois_cat'] = ''

pois.loc[pois.shop.isin(config['filters']['POIs']['shop']), 'pois_cat'] = "shop"
pois.loc[pois.pois == 'pharmacy', 'pois_cat'] = "pharmacy"
pois.loc[pois.pois.isin(['university', 'school', 'kindergarten']), 'pois_cat'] = "education"
pois.loc[pois.pois == 'clinic', 'pois_cat'] = "clinics"
#leisure
pois.loc[pois.pois == 'car_wash', 'pois_cat'] = "custom"

logger.info(f'add pois category')

pois.head(2)

pois.pois_cat.value_counts()

pois = pois[['pois', 'pois_cat', 'name', 'osm_type', 'geometry']].to_crs(config['crs'])
logger.info(f'project pois to {pois.crs.to_string()}')
pois.head(2)

pois['geometry'] = pois.centroid
pois['centroid_x'] = pois.geometry.x
pois['centroid_y'] = pois.geometry.y

logger.info(f'replace pois geometry to centroid')

pois.head(2)

import contextily as cx
from matplotlib import pyplot as plt
import datetime

start = datetime.datetime.today().strftime("%Y_%m_%d")

with plt.style.context('ggplot'):
  ax = pois.plot(column='pois_cat', figsize=(20,10), legend=True, markersize=10, legend_kwds=dict(loc='upper right', ncol=2))
  cx.add_basemap(ax=ax, crs=pois.crs.to_string(), source=cx.providers.CartoDB.Voyager)
  ax.set_title('POIs', fontsize=15, fontweight='bold')
  fp = config['dir_osm']+'images/pois_'+start+'.png'
  plt.savefig(fp, bbox_inches='tight')
  logger.info(f'save pois to {fp}')
  plt.show()

import contextily as cx
from matplotlib import pyplot as plt
import datetime

# function to add value labels
def addlabels(x, y, s):
    for i in range(len(x)):
        plt.text(x.iloc[i], y.iloc[i], s.iloc[i], fontsize = 10)

start = datetime.datetime.today().strftime("%Y_%m_%d")

pois_zoom = pois[((348500 <= pois.centroid_x) & (pois.centroid_x <= 349500)) & ((6649000 <= pois.centroid_y) & (pois.centroid_y <= 6650000))]

with plt.style.context('ggplot'):
  ax = pois_zoom.plot(column='pois_cat', figsize=(20, 10), legend=True, edgecolor='black', markersize=30, legend_kwds=dict(loc='upper right', ncol=2))
  #plt.setp(ax, xlim=(352000, 353000), ylim=(6647000, 6648000))
  plt.setp(ax, xlim=(348500, 349500), ylim=(6649000, 6650000))
  # calling the function to add value labels
  addlabels(pois_zoom.centroid_x, pois_zoom.centroid_y, pois_zoom.name)

  cx.add_basemap(ax=ax, crs=pois_zoom.crs.to_string(), source=cx.providers.CartoDB.Voyager)
  ax.set_title('POIs', fontsize=15, fontweight='bold')

  fp = config['dir_osm']+'images/pois_zoom_'+start+'.png'
  plt.savefig(fp, bbox_inches='tight')
  logger.info(f'save pois to {fp}')
  plt.show()

#pois.explore(column='pois', tiles="CartoDB positron")

import datetime

start = datetime.datetime.today().strftime("%Y_%m_%d")

fp = ''
if 'bbox' in config:
  fp = DIR_OSM + 'spb_bbox_' + start + '.gpkg'
  pois.to_file(fp, driver='GPKG', layer='pois', encoding='utf-8')
  logger.info(f'save pois to {fp}')
else:
  fp = DIR_OSM + 'spb_' + start + '.gpkg'
  pois.to_file(fp, driver='GPKG', layer='pois', encoding='utf-8')
  logger.info(f'save pois to {fp}')

from geopandas import read_file


pois_from_gpkg = read_file(fp, layer='pois').set_index('id')

if pois.shape[0] == pois_from_gpkg.shape[0] and pois.crs == pois_from_gpkg.crs:
  logger.info(f'pois successfully loaded from gpkg')

pois_from_gpkg.head(2)

"""### Network"""

network_type = config['filters']['network_type'][0]
#network_type = config['filters']['network_type'][1]

nodes, edges = osm.get_network(nodes=True, network_type=network_type)

if network_type == 'walking':
  logger.info(f'get {network_type} nodes and edges by exclude filter {osm.conf.network_filters.walking}')
  edges.oneway = edges.oneway.fillna('no')

  indexes = [i for i, flag in edges.oneway.items() if type(flag) != str]
  edges.loc[indexes, 'oneway'] = 'no'

  indexes = [i for i, flag in edges.highway.items() if type(flag) != str]
  edges.loc[indexes, 'highway'] = edges.highway.value_counts().index[0] # 'footway'


elif network_type == 'driving':
  logger.info(f'get {network_type} nodes and edges by exclude filter {osm.conf.network_filters.driving}')
  edges.oneway = edges.oneway.fillna('yes')

  indexes = [i for i, flag in edges.oneway.items() if type(flag) != str]
  edges.loc[indexes, 'oneway'] = 'yes'

  indexes = [i for i, flag in edges.highway.items() if type(flag) != str]
  edges.loc[indexes, 'highway'] = edges.highway.value_counts().index[0] # 'service'

nodes.head(2)

nodes.info()

edges.head(2)

edges.info()

graph = osm.to_graph(nodes, edges, graph_type='networkx')
logger.info(f'convert {network_type} nodes and edges to networkx graph')

from osmnx import simplify_graph, graph_to_gdfs


graph_s = simplify_graph(graph)
logger.info(f'simplify {network_type} graph')

nodes_s = graph_to_gdfs(graph_s, edges=False)
edges_s = graph_to_gdfs(graph_s, nodes=False)
logger.info(f'get {network_type} nodes and edges of simplified graph')

if network_type == 'walking':
  edges_s.oneway = edges_s.oneway.fillna('no')

  indexes = [i for i, flag in edges_s.oneway.items() if type(flag)!= str]
  edges_s.loc[indexes, 'oneway'] = 'no'

  indexes = [i for i, flag in edges_s.highway.items() if type(flag) != str]
  edges_s.loc[indexes, 'highway'] = edges_s.highway.value_counts().index[0] # 'footway'

elif network_type == 'driving':
  edges_s.oneway = edges_s.oneway.fillna('yes')
  indexes = [i for i, flag in edges_s.oneway.items() if type(flag) != str]
  edges_s.loc[indexes, 'oneway'] = 'yes'

  indexes = [i for i, flag in edges_s.highway.items() if type(flag) != str]
  edges_s.loc[indexes, 'highway'] = edges_s.highway.value_counts().index[0] # 'service'

nodes_s = nodes_s.rename(columns={'osmid':'id'}).set_index('id')[['geometry']].to_crs(config['crs'])
nodes_s['x'] = nodes_s.geometry.x
nodes_s['y'] = nodes_s.geometry.y
logger.info(f'project {network_type} nodes to {nodes_s.crs.to_string()}')
nodes_s.head(2)

edges_s = edges_s.reset_index()[['u', 'v', 'length', 'oneway', 'highway', 'geometry']].to_crs(config['crs'])
logger.info(f'project {network_type} edges to {nodes_s.crs.to_string()}')
edges_s.head(2)

nodes = nodes.set_index('id')[['geometry']].to_crs(config['crs'])
nodes['x'] = nodes.geometry.x
nodes['y'] = nodes.geometry.y
logger.info(f'project {network_type} nodes of origin graph to {nodes.crs.to_string()}')

edges = edges.reset_index()[['u', 'v', 'length', 'oneway', 'highway', 'geometry']].to_crs(config['crs'])
logger.info(f'project {network_type} edges of origin graph to {nodes.crs.to_string()}')

import contextily as cx
from matplotlib import pyplot as plt
import datetime

start = datetime.datetime.today().strftime("%Y_%m_%d")

with plt.style.context('ggplot'):
  fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))

  # plot edges and nodes of origin graph
  ax1 = edges.plot(ax=axes[0], color="gray", linewidth=0.2)
  ax1 = nodes.plot(ax=ax1, color="red", markersize=0.3)
  cx.add_basemap(ax=ax1, crs=nodes.crs.to_string(), source=cx.providers.CartoDB.Voyager)

  # plot edges and nodes of simplified graph
  ax2 = edges_s.plot(ax=axes[1], color="gray", linewidth=0.2)
  ax2 = nodes_s.plot(ax=ax2, color="red", markersize=0.3)
  cx.add_basemap(ax=ax2, crs=nodes_s.crs.to_string(), source=cx.providers.CartoDB.Voyager)

  # add titles to maps
  ax1.set_title(f'Origin {network_type} graph (nodes: {len(nodes)}, edges: {len(edges)})', fontsize=10, fontweight='bold')
  ax2.set_title(f'Simplified {network_type} graph (nodes: {len(nodes_s)}, edges: {len(edges_s)}', fontsize=10, fontweight='bold')

  fp = config['dir_osm']+f'images/{network_type}_graph_compare_'+start+'.png'
  plt.savefig(fp, bbox_inches='tight')
  logger.info(f'save {network_type} graph to {fp}')
  plt.show()

import contextily as cx
from matplotlib import pyplot as plt
import datetime

start = datetime.datetime.today().strftime("%Y_%m_%d")

with plt.style.context('ggplot'):
  fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))

  # plot edges and nodes of origin graph
  ax1 = edges.plot(ax=axes[0], color="gray", linewidth=0.2)
  ax1 = nodes.plot(ax=ax1, color="red", markersize=1)
  #plt.setp(ax1, xlim=(349000, 349500), ylim=(6650000, 6650500))
  #plt.setp(ax1, xlim=(352500, 354000), ylim=(6646000, 6648000))
  plt.setp(ax1, xlim=(352000, 353250), ylim=(6647000, 6647750))
  cx.add_basemap(ax=ax1, crs=nodes.crs.to_string(), source=cx.providers.CartoDB.Voyager)

  # plot edges and nodes of simplified graph
  ax2 = edges_s.plot(ax=axes[1], color="gray", linewidth=0.2)
  ax2 = nodes_s.plot(ax=ax2, color="red", markersize=3)
  #plt.setp(ax2, xlim=(349000, 349500), ylim=(6650000, 6650500))
  #plt.setp(ax2, xlim=(352500, 354000), ylim=(6646000, 6648000))
  plt.setp(ax2, xlim=(352000, 353250), ylim=(6647000, 6647750))
  cx.add_basemap(ax=ax2, crs=nodes_s.crs.to_string(), source=cx.providers.CartoDB.Voyager)

  # add titles to maps
  ax1.set_title(f'Origin {network_type} graph (nodes: {len(nodes)}, edges: {len(edges)})', fontsize=10, fontweight='bold')
  ax2.set_title(f'Simplified {network_type} graph (nodes: {len(nodes_s)}, edges: {len(edges_s)}', fontsize=10, fontweight='bold')

  fp = config['dir_osm']+f'images/{network_type}_graph_compare_zoom_'+start+'.png'
  plt.savefig(fp, bbox_inches='tight')
  logger.info(f'save {network_type} graph to {fp}')
  plt.show()

import contextily as cx
from matplotlib import pyplot as plt
import datetime

start = datetime.datetime.today().strftime("%Y_%m_%d")

with plt.style.context('ggplot'):
  fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(20, 20))

  # plot edges and nodes of origin graph
  ax1 = edges.plot(ax=axes[0], color="gray", linewidth=0.2)
  ax1 = nodes.plot(ax=ax1, color="red", markersize=1)
  #plt.setp(ax1, xlim=(349000, 349500), ylim=(6650000, 6650500))
  #plt.setp(ax1, xlim=(352500, 354000), ylim=(6646000, 6648000))
  plt.setp(ax1, xlim=(352000, 353250), ylim=(6647000, 6647750))
  cx.add_basemap(ax=ax1, crs=nodes.crs.to_string(), source=cx.providers.CartoDB.Voyager)

  # plot edges and nodes of simplified graph
  ax2 = edges_s.plot(ax=axes[1], color="gray", linewidth=0.2)
  ax2 = nodes_s.plot(ax=ax2, color="red", markersize=3)
  #plt.setp(ax2, xlim=(349000, 349500), ylim=(6650000, 6650500))
  #plt.setp(ax2, xlim=(352500, 354000), ylim=(6646000, 6648000))
  plt.setp(ax2, xlim=(352000, 353250), ylim=(6647000, 6647750))
  cx.add_basemap(ax=ax2, crs=nodes_s.crs.to_string(), source=cx.providers.CartoDB.Voyager)

  # add titles to maps
  ax1.set_title(f'Origin {network_type} graph (nodes: {len(nodes)}, edges: {len(edges)})', fontsize=10, fontweight='bold')
  ax2.set_title(f'Simplified {network_type} graph (nodes: {len(nodes_s)}, edges: {len(edges_s)}', fontsize=10, fontweight='bold')

  fp = config['dir_osm']+f'images/{network_type}_graph_compare_zoom_extra_'+start+'.png'
  plt.savefig(fp, bbox_inches='tight')
  logger.info(f'save {network_type} graph to {fp}')
  plt.show()

import datetime

start = datetime.datetime.today().strftime("%Y_%m_%d")

fp = ''
if 'bbox' in config:
  fp = DIR_OSM + 'spb_bbox_' + start + '.gpkg'
  nodes_s.to_file(fp, driver='GPKG', layer=f'{network_type}_nodes', encoding='utf-8')
  edges_s.to_file(fp, driver='GPKG', layer=f'{network_type}_edges', encoding='utf-8')
  logger.info(f'save {network_type} nodes and edges of simplified graph to {fp}')
else:
  fp = DIR_OSM + 'spb_' + start + '.gpkg'
  nodes_s.to_file(fp, driver='GPKG', layer=f'{network_type}_nodes', encoding='utf-8')
  edges_s.to_file(fp, driver='GPKG', layer=f'{network_type}_edges', encoding='utf-8')
  logger.info(f'save {network_type} nodes and edges of simplified graph to {fp}')

from geopandas import read_file


nodes_from_gpkg = read_file(fp, layer=f'{network_type}_nodes').set_index('id')
edges_from_gpkg = read_file(fp, layer=f'{network_type}_edges')

if nodes_s.shape[0] == nodes_from_gpkg.shape[0] and nodes_s.crs == nodes_from_gpkg.crs:
  logger.info(f'{network_type} nodes and edges of simplified graph successfully loaded from gpkg')

nodes_from_gpkg.head(2)

edges_from_gpkg.head(2)

"""## Заметки"""

from osmnx import projection, simplification


graph_s_proj = projection.project_graph(graph_s, to_crs=config['crs'])

# Simplify to get real intersections only
# (consolidate nodes within a distance from eachother)
walking_g_prj_simplified = simplification.consolidate_intersections(
    # Graph to simplify
    graph_s_proj,
    # buffer around each node (project the graph beforehand)
    tolerance=5,
    # Get result as graph (False to get nodes only as gdf)
    rebuild_graph=True,
    # no dead ends
    dead_ends=False,
    # Reconnect (False to get intersections only)
    reconnect_edges=True
)