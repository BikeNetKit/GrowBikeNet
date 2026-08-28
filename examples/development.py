"""Example of growbikenet used during package development."""

import growbikenet as gbn

gbn.constants._CRS_CALCULATIONS = 'auto'
gbn.settings.export_file_format = "geojson"
edges_ordered = gbn.growbikenet("Municipality of Athens",
                               export_data=True,
                               existing_network_spacing='auto',
                               # import_files={'growable_network':'./tests/test_data/athens_growable_network.gpkg',
                               # 'bike_network':'./tests/test_data/athens_bike_network.gpkg'},
                               export_plots=True,
                               )