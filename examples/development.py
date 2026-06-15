"""Example of growbikenet used during package development."""

import growbikenet as gbn

edges_ranked = gbn.growbikenet("Barcelona",
                              seed_point_type="park",
                              street_network_file="./Barcelona_streets.gpkg",
                              export_file_format="gpkg")

