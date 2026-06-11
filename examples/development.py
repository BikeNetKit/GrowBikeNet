"""Example of growbikenet used during package development."""

import growbikenet as gbn

edges_ranked = gbn.growbikenet("Paris", seed_point_type='grid_square', seed_point_linking='quadrangulate', export_file_format="gpkg")
