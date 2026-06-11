"""Example of growbikenet used during package development."""

import growbikenet as gbn

edges_ranked = gbn.growbikenet(
	"Hallettsville",
    existing_network_spacing=500,
	)
