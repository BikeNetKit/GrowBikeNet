"""Example of growbikenet used during package development."""

import growbikenet as gbn

gbn.settings.export_file_format = "geojson"
edges_ordered = gbn.growbikenet("Municipality of Athens",
                               export_data=True,
                               existing_network_spacing='auto')