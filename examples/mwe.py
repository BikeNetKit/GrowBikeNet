"""Minimum working example of growbikenet."""

import growbikenet as gbn

edges_ranked = gbn.growbikenet("Lyon", export_file_format="gpkg", existing_network_spacing=None, import_network_file="streettest.gpkg")
