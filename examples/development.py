"""Example of growbikenet used during package development."""

import growbikenet as gbn

gbn.settings.export_file_format = 'geojson'
edges_ranked = gbn.growbikenet("Municipality of Athens",
                              existing_network_spacing='auto',
                              export_plots=True,)