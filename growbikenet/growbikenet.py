from . import constants
from . import settings
import os
import numpy as np
import networkx as nx
import osmnx as ox
import geopandas as gpd
import pandas as pd
import warnings
from tqdm.auto import tqdm
import time
from growbikenet.functions import (
    add_path_to_df,
    add_point_data_to_net,
    add_trip_data_to_net,
    bike_infra_mapping_gdf,
    create_gdf_with_geoms,
    df_from_graph,
    download_network,
    export_data_to_file,
    export_plots_to_file,
    filter_points_distant_from_osm_nodes,
    get_principal_bearing,
    import_network,
    initialize_progress_bar,
    map_edges_to_bike_infrastructure,
    node_to_edge_attributes,
    orientation_order,
    slugify,
    snap_points_to_osm_nodes,
    update_with_existing_bike_network,
    weigh_edges,
    _acquire_network,
    _angulate_seed_points,
    _compute_edge_metrics,
    _create_delaunay_edges,
    _create_seed_points,
    _get_weighted_distances,
    _import_data_files,
    _order_df,
    _postprocess_edges,
    _prepare_export,
    _print_header,
    _print_footer,
    _remove_edge_overlaps,
    _reset_auto_settings,
    _resolve_auto_parameters,
    _route,
    _snap_filter_seed_points,
    _update_seed_points_with_existing_bike_network,
    _validate_parameters,
    _validate_settings,
)


def growbikenet(
    city_query,
    ordering='betweenness',
    seed_point_type='auto',
    seed_point_grid_spacing='auto',
    seed_point_linking='auto',
    existing_network_spacing=None,
    export_data=True,
    city_id=None,
    export_plots=False,
    import_files={},
    seed_point_tags=None,
):
    """Creates a list of urban street network edges ordered by an ordering 
    method.

    The edges form a subnetwork of a city's street network, interpreted as a 
    growing bicycle network following [1]_. By default, growth is from scratch, 
    but the existing bicycle network can also be used as a starting point [2]_.

    Parameters
    ----------
    city_query : str
        Search string for the city that the analysis should be performed on. 
        This is the query used to fetch the data from nominatim. Overruled for 
        data fetching if `city_boundary` or `growable_network` is set.
    ordering : {'betweenness', 'closeness', 'random'}, default 'betweenness'
        Method used to order the edges.
    seed_point_type : {'auto', 'grid_square', 'grid_triangle', 'rail', 'school', 'park', 'file', 'tags'}, default 'auto'

        - 'auto' selects 'grid_square' or 'grid_triangle' automatically depending on the street network's orientation entropy, see [3]_.
        - 'grid_square' creates a square grid. 
        - 'grid_triangle' creates a triangle grid. In this case, `seed_point_linking` must not be set to 'quadrangulate'.
        - 'rail', uses railway stations and halts.
        - 'school' uses kindergartens, schools, colleges, and universities.
        - 'park' uses parks, gardens, nature reserves, and public bathing places.
        - 'file' imports seed_point. In this case, the name of the seed points in the exported file name is controlled via `settings.seed_point_type_name`.
        - 'tags' uses geocodable `seed_point_tags`, see [4]_. 
    seed_point_grid_spacing : 'auto' or int, default 'auto'
        If `seed_point_type` is set to 'grid_square' or 'grid_triangle', this is the spacing between seed points, in meters. Auto-values for `seed_point_type`.

        - 'grid_square' with seed_point_linking 'triangulate_delaunay': 1707
        - 'grid_square' with seed_point_linking 'quadrangulate': 1000
        - 'grid_triangle': 1154
        - otherwise: 1707

        These values ensure that any point in the city is always within 500m of 
        the network (under perfect conditions). For the explanation of case 
        1707 see [1]_.
    seed_point_linking : {'auto', 'triangulate_delaunay', 'quadrangulate'}, default 'auto'
        The algorithm for linking up the seed points into an unrouted, abstract 
        network.

        - 'auto' selects 'triangulate_delaunay' or 'quadrangulate' automatically depending on the street network's orientation entropy, see [3]_.
        - 'triangulate_delaunay' uses Delaunay triangulation.
        - 'quadrangulate' uses quadrangulation, which only works for `seed_point_type` 'grid_square' and `existing_network_spacing` None. Useful for grid-like street networks like Manhattan or Barcelona.
    existing_network_spacing : None or 'auto' or int, default None
        Spacing between seed points, in meters, only on the existing bicycle 
        network. If set to None, the existing network is ignored. `existing_network_spacing` is recommended to be smaller than `seed_point_grid_spacing`, ideally around 50%, to ensure that the 
        existing bicycle network is built first. Option 'auto' sets `existing_network_spacing` to 50% of the `seed_point_grid_spacing`. 
        Independent of `existing_network_spacing`, all bicycle components 
        shorter than `constants.EXISTING_NETWORK_MINIMUM_COMPONENT_LENGTH` are 
        ignored.
    export_data : bool, default True
        If set to True, data is saved to a file. The filename is ``[slug]-growbikenet-[ordering]-from_scratch|from_bikenw-[seed_point_type].[settings.export_file_format]``, 
        depending on the respective parameters, and where ``[slug]`` is a 
        string id made out of `city_query` (or `city_id` if set).
    city_id : None or str, default None
        If set, the slugified `city_id` is used in the filename of the data 
        export. For example, a `city_id` "Athens" will slugify into "athens" in 
        filenames. If set to None, the slugified `city_query` is used in the 
        filename of the data export. It is useful to set a `city_id` for cities 
        where the `city_query` is not the city name, for example to set for a 
        `city_query` "Municipality of Athens" the `city_id` to "Athens".
    export_plots : bool, default False
        If set to True, plots are saved to files, overwriting existing ones.
    import_files: dict, default {}
        The following key:value entries can be set:

        - 'city_boundary' : None or str, default None
            If not set to None, the study area is selected from the 
            (Multi)Polygon provided in the city_boundary shape or gpkg file, 
            ideally in unprojected latitude-longitude degrees (EPSG:4326), but 
            EPSG:3857 also works. For example, './tests/test_data/copenhagen_city_boundary.shp'.
        - 'growable_network' : None or str, default None
            If not set to None, the growable street network is loaded from this 
            file. Must be a gpkg file in unprojected CRS EPSG:4326 with layers 
            nodes and edges, with the structure that an undirected OSMnx street 
            network ``g`` has after saved via 
            ``ox.io.save_graph_geopackage()``. For example:

            >>> g = ox.graph_from_place("Barcelona", network_type='drive')
            >>> g = nx.MultiGraph(ox.convert.to_digraph(g))
            >>> ox.io.save_graph_geopackage(g, 'Barcelona_streets.gpkg')

            To download a growable network that also includes existing bicycle infrastructure, as growbikenet does by default, replace the first 
            line in the above example by this line:

            >>> g = ox.graph_from_place("Barcelona", custom_filter=gbn.constants.GROWABLE_NETWORK_CUSTOM_FILTER)
        - 'bike_network' : None or str, default None
            If not set to None, the existing bike network is loaded from this 
            file. Must be a gpkg file in unprojected CRS EPSG:4326 with layers 
            nodes and edges, with the structure that an undirected OSMnx bike 
            network has after saved via ``ox.io.save_graph_geopackage()``.
        - 'seed_points' : None or str, default None
            If not set to None, the seed points is loaded from this file. Must 
            be a gpkg file in unprojected CRS EPSG:4326 containing only point 
            objects. For example, './tests/test_data/oelde_seed_points.shp'. `seed_point_type` must be set to 'file'. The name of the seed 
            points in the exported file name is controlled via `settings.seed_point_type_name`.
        - 'point_data' : None or str, default None
            If not set to None, an additional data set of points will be loaded 
            from this file, representing point events like traffic crashes or 
            citizen feedback to improve bike infrastructure. Must be a gpkg 
            file in unprojected CRS EPSG:4326 containing only point objects, 
            optionally with an int ``num`` column that encodes the number of 
            point events. The data set is used to re-prioritize the ordering of 
            the network links, controlled with `settings.import_data_impact` 
            and `settings.import_data_trip_point_balance`, following [2]_.
        - 'trip_data' : None or str, default None
            If not set to None, an additional data set of trips will be loaded 
            from this file, representing trip events for prioritizing bike 
            infrastructure growth. Must be a csv file in unprojected CRS 
            EPSG:4326 containing the following fields: 
            ``o_lat, o_lon, d_lat, d_lon``. Optionally there can be an int 
            ``num`` field that encodes the number of trips between each origin 
            and destination. The data set is used to re-prioritize the ordering 
            of the network links, controlled with `settings.import_data_impact` 
            and `settings.import_data_trip_point_balance`, following [2]_.
    seed_point_tags : None or dict[str, bool or str or list[str]], default None
        If not None, must be a geocodable `seed_point_tags`, see [4]_, and 
        `seed_point_type` must be set to 'tags'. For example, 
        ``seed_point_tags={'railway': ['station', 'halt']}`` retrieves exactly 
        the same as ``seed_point_type='rail'``.

    Returns
    -------
    edges_ordered : geopandas.geodataframe.GeoDataFrame
        Geodataframe of all edges in street network ordered by the `ordering` 
        method.

    Examples
    --------
    Minimum working example: Grow a bicycle network from scratch in Lyon.

    >>> edges_ordered = gbn.growbikenet("Lyon")

    Grow a bicycle network from scratch in Copenhagen, providing a study area 
    polygon to include also Frederiksberg and Amager.

    >>> edges_ordered = gbn.growbikenet("Copenhagen", import_files={'city_boundary':'./tests/test_data/copenhagen_city_boundary.shp'}) 

    Expand the existing bicycle network of Lyon, connecting all educational 
    institutions.

    >>> edges_ordered = gbn.growbikenet("Lyon", seed_point_type='school', existing_network_spacing='auto') 

    Grow a bicycle network in Oelde from scratch, working offline by importing 
    the street network and custom seed points from file.

    >>> edges_ordered = gbn.growbikenet("Oelde", seed_point_type='file', import_files={'growable_network':'./tests/test_data/oelde_growable_network.gpkg', 'seed_points':'./tests/test_data/oelde_seed_points.gpkg'})

    Notes
    -----
    The original paper [1]_ uses minimum weight triangulation, but Delaunay 
    triangulation is implemented much faster and in practice gives identical 
    results. Triangulation and metrics (betweenness, closeness) are calculated 
    for the unrouted, abstract network for which egde lengths are taken from 
    the routed network.

    References
    ----------
    .. [1] M. Szell, S. Mimar, T. Perlman, G. Ghoshal, R. Sinatra, `Growing urban bicycle networks`, Scientific Reports 12, 6765 (2022)
    .. [2] P. Folco, L. Gauvin, M. Tizzoni, M. Szell, `Data-driven micromobility network planning for demand and safety`, Environment and planning B: Urban analytics and city science 50(8), 2087-2102 (2023)
    .. [3] G. Boeing, `Urban spatial order: Street network orientation, configuration, and entropy`, Applied Network Science 4, 67 (2019)
    .. [4] https://osmnx.readthedocs.io/en/stable/user-reference.html#osmnx.features.features_from_place
    """

    # Setup
    starttime = time.time()
    np.random.seed(settings.random_seed)  # Set random number generator seed for reproducibility
    setting_was_auto = _validate_settings()
    import_files = _validate_parameters(city_query, ordering, seed_point_type, seed_point_grid_spacing, seed_point_linking, existing_network_spacing, export_data, city_id, export_plots, import_files, seed_point_tags)
    _print_header(city_query, ordering, seed_point_type, existing_network_spacing)

    ### Import data files
    num_data_files, point_data, trip_data = _import_data_files(import_files)

    ### Download/Import network
    city_boundary_exists, nodes, edges, g_undir, nodes_exnw, edges_exnw, g_undir_exnw, nodes_exnw_filtered, city_boundary_geometry, city_boundary_gdf = _acquire_network(import_files, existing_network_spacing, city_query)

    # Now that the graph is ready, resolve auto parameters
    seed_point_type, seed_point_grid_spacing, seed_point_linking, existing_network_spacing = _resolve_auto_parameters(seed_point_type, seed_point_grid_spacing, seed_point_linking, existing_network_spacing, orientation_order(g_undir), import_files)

    # At this point no parameter should be on 'auto' any longer and 
    # inconsistencies should be resolved.

    ### Create seed points
    seed_points, seed_network, progress_bar = _create_seed_points(existing_network_spacing, seed_point_type, g_undir, edges, nodes, seed_point_grid_spacing, import_files, city_query, seed_point_tags, city_boundary_geometry)
    
    # Snap and filter seed points to OSM nodes
    seed_points_snapped_filtered = _snap_filter_seed_points(progress_bar, seed_points, seed_network, nodes, seed_point_linking, existing_network_spacing, nodes_exnw_filtered)

    ### *angulate
    grown_bikenet_edges_abstract = _angulate_seed_points(seed_point_linking, seed_points_snapped_filtered, seed_network)

    ### Routing: Get routed geometry (LineString) for each abstract edge (row)
    B, metric_weight = _route(g_undir, edges, grown_bikenet_edges_abstract, seed_points_snapped_filtered, num_data_files, point_data, trip_data)

    ### Compute edge metrics
    edges_ordered = _compute_edge_metrics(ordering, B, metric_weight, )

    # To do: re-route edges dynamically, accounting for growing edges becoming pbi=1

    # Postprocess edges, like removing overlaps
    edges_ordered = _postprocess_edges(existing_network_spacing, edges_exnw, edges_ordered)

    # Generate export data filenames
    export_strings = _prepare_export(export_data, export_plots, city_id, city_query, existing_network_spacing, seed_point_type, ordering)

    ### Export data
    export_data_to_file(export_data, seed_points_snapped_filtered, city_boundary_exists, city_boundary_gdf, existing_network_spacing, edges_ordered, export_strings)

    ### Export plots
    export_plots_to_file(export_plots, ordering, edges_ordered, seed_points_snapped_filtered, existing_network_spacing)

    # Cleanup, finalize
    _reset_auto_settings(setting_was_auto)
    endtime = time.time()
    _print_footer(export_data, export_plots, endtime, starttime)

    return edges_ordered
