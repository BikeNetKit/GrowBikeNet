"""
Script for exporting some growbikenet data for one city.

Parameters
----------
city_query : str
    Search string for the city that the analysis should be performed on. This is the query used to fetch the data from nominatim. Overruled for data fetching if city_boundary or street_network is set.
city_id : str, default None
    If set, the slugified city_id is used as the filename of the data export. For example, "Athens" will use "athens" in filenames. If set to None, the slugified city_query is used as the filename of the data export. It is useful to set city_id for cities where the city_query is not the city name, for example "Municipality of Athens" vs "Athens".
export_file_format : str, default "geojson"
    File format for the data export. Default "geojson", also possible "gpkg". If exporting as geojson, generates extra files for seed points and city boundary. If exporting as gkpg, these are added all in one file as extra layers.
city_boundary : (str | None), default None
    If not set to None, the study area will be selected from the (Multi)Polygon provided in the city_boundary shape or gpkg file, ideally in unprojected latitude-longitude degrees (EPSG:4326), but EPSG:3857 also works. For example, "./tests/test_data/copenhagen_city_boundary.shp".
street_network : str
    The street network is loaded from this file. Must be a gpkg file in unprojected crs EPSG:4326 with layers nodes and edges, with the structure that an undirected osmnx street network g has after saved via ox.io.save_graph_geopackage().
bike_network : st
    The existing bike network is loaded from this file. Must be a gpkg file in unprojected crs EPSG:4326 with layers nodes and edges, with the structure that an undirected osmnx bike network has after saved via ox.io.save_graph_geopackage().

Notes
-------
Exports data into four files:
[slug]-betweenness_centrality-grid.gpkg
[slug]-betweenness_centrality-rail.gpkg
[slug]-closeness_centrality-grid.gpkg
[slug]-closeness_centrality-rail.gpkg
    Data is saved into the current working directory.
    slug is a string id created out of city_id.

Examples
--------
>>> python batchexport_onecity.py Barcelona Barcelona_es geojson boundaries/barcelona_es.geojson street_networks/barcelona_es.gpkg bike_networks/barcelona_es.gpkg
"""

# WHICH DATA TO EXPORT?
export_seed_point_types = ['auto', 'rail', 'school'] # Full array: ['auto', 'rail', 'school']
export_rankings = ['betweenness_centrality', 'closeness_centrality'] # Full array: ['betweenness_centrality', 'closeness_centrality', 'random']
export_existing_network_spacings = [None, 'auto'] # Full array: [None, 'auto']

# Main
import growbikenet as gbn
import sys
from growbikenet.functions import slugify
from growbikenet import settings

city_query = "Barcelona"
city_id = "barcelona_es"
settings.export_file_format = "geojson"
city_boundary = "boundaries/barcelona_es.geojson"
street_network = "street_networks/barcelona_es.gpkg"
bike_network = "bike_networks/barcelona_es.gpkg"

if len(sys.argv) >= 2:
    city_query = sys.argv[1]
if len(sys.argv) >= 3:
    city_id = sys.argv[2]
if len(sys.argv) >= 4:
    settings.export_file_format = sys.argv[3]
if len(sys.argv) >= 5:
    city_boundary = sys.argv[4]
if len(sys.argv) >= 6:
    street_network = sys.argv[5]
if len(sys.argv) >= 7:
    bike_network = sys.argv[6]

city_id = slugify(city_id)

for seed_point_type in export_seed_point_types:
    for ranking in export_rankings:
        for existing_network_spacing in export_existing_network_spacings:
            if seed_point_type == 'auto' and existing_network_spacing == 'auto':
                seed_point_linking = 'triangulate_delaunay'
            else:
                seed_point_linking = 'auto'
            gbn.growbikenet(
                city_query,
                ranking=ranking,
                seed_point_type=seed_point_type,
                seed_point_linking=seed_point_linking,
                export_data=True,
                export_plots=False,
                existing_network_spacing=existing_network_spacing,
                city_id=city_id,
                import_files={"city_boundary": city_boundary, "street_network": street_network, "bike_network": bike_network},
            )
# Temporary hack to replace generated with real city boundary
import shutil
shutil.copyfile(city_boundary, "./results/"+city_id+"-city_boundary.geojson")
