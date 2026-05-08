"""
Example for exporting all growbikenet data for one city.

Parameters
----------
city_name : str
    Name of the city that the analysis should be performed on. This is the query string used to fetch the data from nominatim.
export_file_format : str, optional, default "geojson"
    File format for the data export. Default "geojson", also possible "gpkg". If exporting as geojson, generates extra files for seed points and city boundary. If exporting as gkpg, these are added all in one file as extra layers.

Notes
-------
Exports data into four files:
[slug]-betweenness_centrality-grid.gpkg
[slug]-betweenness_centrality-rail.gpkg
[slug]-closeness_centrality-grid.gpkg
[slug]-closeness_centrality-rail.gpkg
    Data is saved into the current working directory.
    slug is a string id created out of nominatimstring.

Examples
--------
>>> python exportalldata_onecity.py Barcelona gpkg
"""

import growbikenet as gbn
import sys

city_name = "Barcelona"
export_file_format = "geojson"
city_boundary_file = None

if len(sys.argv) >= 2:
    city_name = sys.argv[1]
if len(sys.argv) >= 3:
    export_file_format = sys.argv[2]
if len(sys.argv) >= 4:
    city_boundary_file = sys.argv[3]
    
print("Exporting " + export_file_format + " data for " + city_name)

for seed_point_type in ["grid", "rail"]:
    for ranking in ["betweenness_centrality", "closeness_centrality", "random"]:
        for ens in [None, 500]:
            if ens: ens_string = ", with existing bike network"
            else: ens_string = ""
            print("\n" + "Exporting " + seed_point_type + ", " + ranking + ens_string)
            gbn.growbikenet(
                city_name=city_name,
                ranking=ranking,
                seed_point_type=seed_point_type,
                export_data=True,
                export_plots=False,
                export_video=False,
                export_file_format=export_file_format,
                existing_network_spacing=ens,
                city_boundary_file=city_boundary_file,
            )
