"""
Script for exporting some growbikenet data for one city.

Parameters
----------
city_query : str
    Search string for the city that the analysis should be performed on. This is the query used to fetch the data from nominatim. Overruled for data fetching if city_boundary or street_network is set.
city_name : str, default None
    If set, the slugified city_name is used as the filename of the data export. For example, "Athens" will use "athens" in filenames. If set to None, the slugified city_query is used as the filename of the data export. It is useful to set city_name for cities where the city_query is not the city name, for example "Municipality of Athens" vs "Athens".
export_file_format : str, default "geojson"
    File format for the data export. Default "geojson", also possible "gpkg". If exporting as geojson, generates extra files for seed points and city boundary. If exporting as gkpg, these are added all in one file as extra layers.
city_boundary : (str | None), default None
    If not set to None, the study area will be selected from the (Multi)Polygon provided in the city_boundary shape or gpkg file, ideally in unprojected latitude-longitude degrees (EPSG:4326), but EPSG:3857 also works. For example, "./tests/test_data/copenhagen_city_boundary.shp".

Notes
-------
Exports data into four files:
[slug]-betweenness_centrality-grid.gpkg
[slug]-betweenness_centrality-rail.gpkg
[slug]-closeness_centrality-grid.gpkg
[slug]-closeness_centrality-rail.gpkg
    Data is saved into the current working directory.
    slug is a string id created out of city_query.

Examples
--------
>>> python batchexport_onecity.py Barcelona Barcelona gpkg
"""

# WHICH DATA TO EXPORT?
export_seed_point_type = ['grid_square', "rail"] # Full array: ['grid_square', "rail"]
export_ranking = ["betweenness_centrality", "closeness_centrality"] # Full array: ["betweenness_centrality", "closeness_centrality", "random""]
export_existing_network_spacing = [None, 500] # Full array: [None, 500]

# Main
import growbikenet as gbn
import sys
from growbikenet.functions import slugify

city_query = "Barcelona"
city_name = "Barcelona"
export_file_format = "geojson"
city_boundary = None

if len(sys.argv) >= 2:
    city_query = sys.argv[1]
if len(sys.argv) >= 3:
    city_name = sys.argv[2]
if len(sys.argv) >= 4:
    export_file_format = sys.argv[3]
if len(sys.argv) >= 5:
    city_boundary = sys.argv[4]

city_name = slugify(city_name)

for seed_point_type in export_seed_point_type:
    for ranking in export_ranking:
        for existing_network_spacing in export_existing_network_spacing:
            gbn.growbikenet(
                city_query,
                ranking=ranking,
                seed_point_type=seed_point_type,
                export_data=True,
                export_plots=False,
                export_video=False,
                export_file_format=export_file_format,
                existing_network_spacing=existing_network_spacing,
                city_name=city_name,
                city_boundary=city_boundary,
            )
