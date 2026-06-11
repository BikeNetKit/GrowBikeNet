"""Example of growbikenet used during package development."""

import growbikenet as gbn

edges_ranked = gbn.growbikenet(
	"Oelde",
	street_network_file="./tests/test_data/oelde_streets.gpkg",
	seed_point_type='file',
	seed_points_file="./tests/test_data/oelde_seed_points.gpkg",
	export_file_format="gpkg"
	)
