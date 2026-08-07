"""Example of growbikenet used during package development."""

import growbikenet as gbn

edges_ranked = gbn.growbikenet("Andorra la Vella", 
    export_data = True,
    export_plots=True,
    import_files={
        # 'street_network':"./tests/test_data/andorra-la-vella_street_network.gpkg",
        'street_network':"./tests/test_data/andorra.osm.pbf",
        # 'street_network':"./tests/test_data/andorra-la-vella.osm.pbf",
        'city_boundary':"./tests/test_data/andorra-la-vella_boundary.geojson",
        },
    )