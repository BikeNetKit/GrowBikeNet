"""Example of growbikenet used during package development."""

import growbikenet as gbn

edges_ranked = gbn.growbikenet(
	"Oelde",
	street_network_file="./tests/test_data/oelde_streets.gpkg",
	seed_point_type='triangular',
	export_file_format="gpkg"
	)
