"""Example of growbikenet used during package development."""

import growbikenet as gbn

edges_ranked = gbn.growbikenet("Municipality of Athens",
                                seed_point_linking="triangulate_delaunay",
                              existing_network_spacing=500,
                              export_file_format="gpkg")

