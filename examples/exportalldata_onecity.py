"""
Example for exporting all growbikenet data for one city.

Parameters
----------
nominatimstring : str, optional, default Bath
    The string to search for in nominatim/OSM.

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
>>> python exportalldata_onecity.py Barcelona
"""

import growbikenet as gbn
import sys

nominatimstring = "Bath"
if len(sys.argv) >= 2:
    nominatimstring = sys.argv[1]
print("Exporting data for " + nominatimstring)

for s in ["grid", "rail"]:
    for r in ["betweenness_centrality", "closeness_centrality"]:
        print("\n" + "Exporting " + r + ", " + s)
        gbn.growbikenet(
            city_name=nominatimstring,
            proj_crs="3857",
            ranking=r,
            seed_point_type=s,
            export_plots=False,
            export_video=False,
        )
