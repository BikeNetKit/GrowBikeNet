"""
Script for exporting some growbikenet data for one city.

Parameters
----------
city_name : str
    Name of the city that the analysis should be performed on. This is the query string used to fetch the data from nominatim. Overruled (for data fetching) if city_boundary_file is set.
export_data_slug : str, optional, default None
    If not set to None, the city_name will be slugified and used as the slug in the filename of the data export
export_file_format : str, optional, default "geojson"
    File format for the data export. Default "geojson", also possible "gpkg". If exporting as geojson, generates extra files for seed points and city boundary. If exporting as gkpg, these are added all in one file as extra layers.
city_boundary_file : (str | None), default None
    If not set to None, the study area will be selected from the (Multi)Polygon provided in the city_boundary_file shape file, ideally in unprojected latitude-longitude degrees (EPSG:4326), but EPSG:3857 also works. For example, "./tests/test_data/copenhagen.shp".

Notes
-------
Exports data into four files:
[slug]-betweenness_centrality-grid.gpkg
[slug]-betweenness_centrality-rail.gpkg
[slug]-closeness_centrality-grid.gpkg
[slug]-closeness_centrality-rail.gpkg
    Data is saved into the current working directory.
    slug is a string id created out of city_name.

Examples
--------
>>> python batchexport_onecity.py Barcelona Barcelona gpkg
"""

# WHICH DATA TO EXPORT?
export_seed_point_type = ["grid", "rail"] # Full array: ["grid", "rail"]
export_ranking = ["betweenness_centrality", "closeness_centrality"] # Full array: ["betweenness_centrality", "closeness_centrality", "random""]
export_existing_network_spacing = [None, 500] # Full array: [None, 500]

# Main
import growbikenet as gbn
import sys
from slugify import slugify

city_name = "Barcelona"
export_data_slug = "Barcelona"
export_file_format = "geojson"
city_boundary_file = None

if len(sys.argv) >= 2:
    city_name = sys.argv[1]
if len(sys.argv) >= 3:
    export_data_slug = sys.argv[2]
if len(sys.argv) >= 4:
    export_file_format = sys.argv[3]
if len(sys.argv) >= 5:
    city_boundary_file = sys.argv[4]

export_data_slug = slugify(export_data_slug)

for seed_point_type in export_seed_point_type:
    for ranking in export_ranking:
        for existing_network_spacing in export_existing_network_spacing:
            gbn.growbikenet(
                city_name=city_name,
                ranking=ranking,
                seed_point_type=seed_point_type,
                export_data=True,
                export_plots=False,
                export_video=False,
                export_file_format=export_file_format,
                existing_network_spacing=existing_network_spacing,
                export_data_slug=export_data_slug,
                city_boundary_file=city_boundary_file,
            )
