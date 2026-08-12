"""Example of growbikenet used during package development."""

import growbikenet as gbn

# gbn.settings.seed_point_type_name = "Hollaritti-yo"
gbn.settings.export_file_format = 'geojson'

edges_ordered = gbn.growbikenet("Oelde", seed_point_type='file', import_files={'street_network':"./tests/test_data/oelde_street_network.gpkg", 'seed_points':"./tests/test_data/oelde_seed_points.gpkg"})