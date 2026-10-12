"""Main calls from the `growbikenet` procedure. These functions are called
once from the `growbikenet` module.
"""

import os
import re
import warnings
from collections import defaultdict

import numpy as np
import pandas as pd

from . import constants, settings, osm

pd.set_option('display.max_columns', None) # for debugging
import datetime

import geopandas as gpd
import networkx as nx
import osmnx as ox
from tqdm import tqdm

from growbikenet.visualization import generate_plots
from growbikenet.utils import (
    add_point_data_to_net,
    add_trip_data_to_net,
    assign_pbi_to_edges,
    bike_infra_mapping_gdf,
    create_gdf_with_geoms,
    df_from_graph
    download_network,
    filter_network_by_component_length,
    filter_points_distant_from_osm_nodes,
    get_principal_bearing,
    import_network,
    initialize_progress_bar,
    nodelist_to_edgetuples,
    node_to_edge_attributes,
    nx_to_nodes_edges,
    orientation_order,
    prepare_nodes_edges,
    route_nodepairs,
    set_path_to_pbi,
    slugify,
    snap_points_to_osm_nodes,
    update_with_existing_bike_network,
    weigh_edges,
    _create_delaunay_edges,
    _get_existing_network_seed_points,
    _get_grid_seed_points,
    _get_tags_seed_points,
    _get_weighted_distances,
    _order_df,
    _prepare_seed_points,
    _remove_edge_overlaps,
    _resolve_crs_calculations,
    _update_seed_points_with_existing_bike_network,
)


def _gbn_validate_settings():
    """ Check if user settings input is valid. If not, raise an exception or 
    warning.

    Returns
    -------
    setting_was_auto : dict
        Dictionary remembering which setting or constant was set to auto, so 
        it can be reset to auto in the end.
    """

    if type(constants._CRS_CALCULATIONS) is not str:
        raise TypeError("constants._CRS_CALCULATIONS must be a string")
    if settings.export_file_format != "geojson" and settings.export_file_format != "gpkg":
        raise ValueError("settings.export_file_format must be 'geojson' or 'gpkg'")
    # To do: check export_path
    if type(settings.seed_point_snap_distance) is not int and settings.seed_point_snap_distance != 'auto':
        raise TypeError("settings.seed_point_snap_distance must be 'auto' or an integer")
    if type(settings.seed_point_snap_distance) is int and settings.seed_point_snap_distance <= 0:
        raise ValueError("settings.seed_point_snap_distance must be a positive integer")

    setting_was_auto = {'crs_calculations': False, 'crs_viz': False}
    # Ask whether constants._CRS_CALCULATIONS was 'auto' ahead of network 
    # construction, as 'auto' is resolved inside `prepare_nodes_edges()`.
    if constants._CRS_CALCULATIONS == 'auto':
        setting_was_auto['crs_calculations'] = True
    if settings.viz["crs"] == 'auto':
        setting_was_auto['crs_viz'] = True
    return setting_was_auto


def _gbn_validate_parameters(
        city_query,
        ordering,
        seed_point_type,
        seed_point_grid_spacing,
        seed_point_linking,
        existing_network_spacing,
        export_data,
        city_id,
        export_plots,
        import_files,
        seed_point_tags,
    ):
    """ Check if user parameter input is valid. If not, raise an exception or 
    warning.
    
    Parameters
    ----------
    Same as `growbikenet.growbikenet()`
    Additionally:
    constants._PRESET_TAGS : dict
        Dictionary of preset seed point tags.

    Returns
    -------
    True
    """

    if type(city_query) is not str:
        raise TypeError("city_query must be a string")
    if type(ordering) is not str:
        raise TypeError("ordering must be a string")
    if ordering not in ["betweenness", "closeness", "random"]:
        raise ValueError(
            "ordering must be either 'betweenness', 'closeness', or 'random'"
        )
    if seed_point_type not in ['auto', 'grid_square', 'grid_triangle', 'rail', 'school', 'park', 'file', 'tags']:
        raise ValueError("seed_point_type must be 'auto' or 'grid_square' or 'grid_triangle' or 'rail' or 'school' or 'park' or 'file' or 'tags'")
    if type(seed_point_grid_spacing) is not int and seed_point_grid_spacing != 'auto':
        raise TypeError("seed_point_grid_spacing must be 'auto' or an integer")
    if type(seed_point_grid_spacing) is int and seed_point_grid_spacing <= 0:
        raise ValueError("seed_point_grid_spacing must be a positive integer")
    if type(import_files) is not dict:
        raise TypeError("import_files must be a dictionary")
    # Prepare special case import_files. Turn it into a defaultdict where missing keys are None.
    import_files = defaultdict(lambda: None, import_files)
    if seed_point_type == 'file' and import_files['seed_points'] is None:
        raise ValueError("With seed_point_type 'file', a seed_points file must be provided")
    if seed_point_type == 'tags' and seed_point_tags is None:
        raise ValueError("With seed_point_type 'tags', seed_point_tags must be provided")
    if seed_point_linking not in ['auto', 'triangulate_delaunay', 'quadrangulate']:    
        raise ValueError("seed_point_linking must be 'auto' or 'triangulate_delaunay' or 'quadrangulate'")
    if seed_point_linking == 'quadrangulate' and (seed_point_type != 'grid_square' or existing_network_spacing is not None):
        raise ValueError("With seed_point_linking 'quadrangulate', seed_point_type must be set to 'grid_square' and existing_network_spacing must be set to None")
    if type(existing_network_spacing) is not int and existing_network_spacing is not None and existing_network_spacing != 'auto':
        raise TypeError("existing_network_spacing must be None or 'auto' or a positive integer")
    if type(existing_network_spacing) is int and existing_network_spacing <= 0:
        raise ValueError("existing_network_spacing must be None or a positive integer")
    if type(existing_network_spacing) is int and seed_point_grid_spacing is int and existing_network_spacing >= seed_point_grid_spacing:
        warnings.warn("existing_network_spacing is recommended to be smaller than seed_point_grid_spacing, ideally around a third, to ensure that the existing bicycle network is built first.")
    if type(export_data) is not bool:
        raise TypeError("export_data must be a boolean")
    if city_id is not None and type(city_id) is not str:
        raise TypeError("city_id must be None or a string")
    if type(city_id) is str and (
        len(city_id) < 1 or len(slugify(city_id)) < 1
    ):
        raise ValueError(
            "city_id must contain at least one non-special character"
        )
    if type(export_plots) is not bool:
        raise TypeError("export_plots must be a boolean")

    # Import files
    for filename in ['city_boundary','growable_network','bike_network','seed_points','point_data','trip_data']:
        if type(import_files[filename]) is str and not os.path.isfile(settings.import_path+import_files[filename]):
            raise FileNotFoundError(filename+" not found")
        
    if seed_point_tags is not None and type(seed_point_tags) is not dict:
        raise TypeError("seed_point_tags must be None or a dictionary")

    return import_files


def _gbn_resolve_auto_parameters(
        seed_point_type,
        seed_point_grid_spacing,
        seed_point_linking,
        existing_network_spacing,
        g,
        import_files,
    ):
    """Resolve auto parameters their inconsistencies, and settings.
    
    Parameters
    ----------
    Several parameters from `growbikenet.growbikenet()`.
    
    Additionally:
    g : networkx.classes.multigraph.MultiGraph
        Street network.

    Returns
    -------
    Several parameters from `growbikenet.growbikenet()`.
    """
    phi = orientation_order(g)
    
    if import_files['seed_points']:
        seed_point_type = 'file'
        seed_point_linking = 'triangulate_delaunay' 

    if seed_point_type == 'auto':
        if phi>constants._PHI_LIMITS[1] and existing_network_spacing is None: # Case grid. For example, Barcelona, Manhattan. Incompatible with existing_network_spacing not None.
            seed_point_type = 'grid_square'
            if seed_point_linking == 'auto':
                seed_point_linking = 'quadrangulate'
        elif (phi>constants._PHI_LIMITS[1] and existing_network_spacing is not None) or (phi<=constants._PHI_LIMITS[1] and phi>constants._PHI_LIMITS[0]): # Case contains some grid elements. For example, Prague, Budapest. Or, it should have been quadrangulation but existing_network_spacing is not None.
            seed_point_type = 'grid_square'
            if seed_point_linking == 'auto':
                seed_point_linking = 'triangulate_delaunay'
        elif phi<=constants._PHI_LIMITS[0]: # Case negligible grid elements. For example, Berlin, London
            seed_point_type = 'grid_triangle'
            if seed_point_linking == 'auto':
                seed_point_linking = 'triangulate_delaunay'
            elif seed_point_linking == 'quadrangulate': # Quadrangulation incompatible with seed_point_type grid_triangle from auto
                seed_point_linking = 'triangulate_delaunay'
                warnings.warn("seed_point_linking 'quadrangulate' is incompatible with automatically selected seed_point_type 'grid_triangle'. Changing seed_point_linking to 'triangulate_delaunay'.")
    else:
        if seed_point_linking == 'auto':
            if seed_point_type != 'grid_square': # Everything is triangulated, but the grid could also be quadrangulated
                seed_point_linking = 'triangulate_delaunay'
            else: # Case 'grid_square'
                if phi>constants._PHI_LIMITS[1] and existing_network_spacing is None: # Case grid. For example, Barcelona, Manhattan. We can quadrangulate, except when existing_network_spacing is not None - in that case, just triangulate again.
                    seed_point_linking = 'quadrangulate'
                else:
                    seed_point_linking = 'triangulate_delaunay'

    if seed_point_grid_spacing == 'auto': 
        # These values ensure that any point in the city is always within b=500m of the network (if seed points snap perfectly).
        # In comments, general equations for arbitrary buffer distance b
        if seed_point_type == 'grid_square' and seed_point_linking == 'triangulate_delaunay':
            seed_point_grid_spacing = constants.GRID_SPACING_TRIANGULATE # a=2b/(2-sqrt(2))
        elif seed_point_type == 'grid_square' and seed_point_linking == 'quadrangulate':
            seed_point_grid_spacing = constants.GRID_SPACING_QUADRANGULATE # a=2b
        elif seed_point_type == 'grid_triangle':
            seed_point_grid_spacing = constants.GRID_SPACING_TRIANGLE # h/2=b=a*sqrt(3)/4 -> a=4b/sqrt(3)
        else:
            seed_point_grid_spacing = constants.GRID_SPACING_TRIANGULATE

    if settings.seed_point_snap_distance == 'auto':
        settings.seed_point_snap_distance = int(np.ceil(seed_point_grid_spacing*constants._SEED_POINT_SNAP_DISTANCE_FACTOR))

    if existing_network_spacing == 'auto':
        existing_network_spacing = int(np.ceil(seed_point_grid_spacing*constants._EXISTING_NETWORK_SPACING_FACTOR))

    # Set import data balance to 0 or 1 if only one data set is imported
    if import_files['point_data'] is not None and import_files['trip_data'] is None:
        settings.import_data_trip_point_balance = 0
    elif import_files['trip_data'] is not None and import_files['point_data'] is None:
        settings.import_data_trip_point_balance = 1

    return seed_point_type, seed_point_grid_spacing, seed_point_linking, existing_network_spacing


def _gbn_print_header(city_query, ordering, seed_point_type, existing_network_spacing):
    """Print header.
    """
    if not settings.silent:
        print((constants._PROGRESS_BAR_DESC_LENGTH+constants._PROGRESS_BAR_LENGTH)*"=")
        print("RUNNING GROWBIKENET FOR CITY: " + city_query)
        print(ordering + " | " + seed_point_type + " | " + ("from existing bike network " if existing_network_spacing else "from scratch"))
        print((constants._PROGRESS_BAR_DESC_LENGTH+constants._PROGRESS_BAR_LENGTH)*"-"+"╮")


def _gbn_print_footer(export_data, export_plots, endtime, starttime):
    """Print footer.
    """
    if not settings.silent:
        print((constants._PROGRESS_BAR_DESC_LENGTH+constants._PROGRESS_BAR_LENGTH)*"-"+"╯")
        if export_data:
            print("Data exported to "+settings.export_path['results'])
        if export_plots:
            print("Plots exported to "+settings.export_path['plots'])
        if export_data or export_plots:
            print((constants._PROGRESS_BAR_DESC_LENGTH+constants._PROGRESS_BAR_LENGTH)*"-")
        print("FINISHED IN " + str(datetime.timedelta(seconds = round(endtime - starttime))))
        print((constants._PROGRESS_BAR_DESC_LENGTH+constants._PROGRESS_BAR_LENGTH)*"=")


def _gbn_import_data_files(import_files):
    """Import data files.
    """
    num_data_files = int(bool(import_files['point_data'])) + int(bool(import_files['trip_data']))
    point_data = None
    trip_data = None
    if num_data_files:
        progress_bar = initialize_progress_bar("Importing data files", num_data_files, "file")
        if import_files['point_data']:
            point_data = gpd.read_file(settings.import_path+import_files['point_data'])
            progress_bar.update(1)
        if import_files['trip_data']:
            trip_data = pd.read_csv(settings.import_path+import_files['trip_data'])
            progress_bar.update(1)
        progress_bar.close()
    return num_data_files, point_data, trip_data


def _gbn_acquire_network(import_files, existing_network_spacing, city_query):
    """Import or download networks, prepare them, and create boundary.
    """
    if import_files['growable_network'] is not None:
        ### Import and preprocess data from file
        city_boundary_exists = True
        progress_bar = initialize_progress_bar("Importing network data", 1+int(bool(existing_network_spacing)), "network")
        nodes, edges, g_undir, city_boundary_gdf = import_network(import_files['growable_network'])
        city_boundary_geometry = city_boundary_gdf.geometry[0]
        progress_bar.update(1)
    else:
        ### Download and preprocess data from OSM
        city_boundary_exists = True
        progress_bar = initialize_progress_bar("Downloading OSM data", 1+int(bool(existing_network_spacing)), "network")
        # Get city boundary 
        if import_files['city_boundary']:
            city_boundary_shp = gpd.read_file(settings.import_path+import_files['city_boundary'])
            city_boundary_gdf = city_boundary_shp.iloc[[0]]    
        else:
            city_boundary_gdf = ox.geocoder.geocode_to_gdf(city_query)
        city_boundary_geometry = city_boundary_gdf.geometry[0]
        # Fetch growable network data from osmnx
        # Due to retain_all=False, this fetches the largest connected component
        nodes, edges, g_undir = download_network(city_query, network_type=constants.GROWABLE_NETWORK_TYPE, custom_filter=constants.GROWABLE_NETWORK_CUSTOM_FILTER, retain_all=False, city_boundary_geometry=city_boundary_geometry)
        progress_bar.update(1)

    # Update g_undir: Add the existing bike network
    if existing_network_spacing is not None: 
        nodes, edges, g_undir, nodes_exnw, edges_exnw, g_undir_exnw, nodes_exnw_filtered = update_with_existing_bike_network(city_query, g_undir, import_files=import_files, city_boundary_geometry=city_boundary_geometry)
        progress_bar.update(1)
    else:
        nodes_exnw = edges_exnw = g_undir_exnw = nodes_exnw_filtered = None

    # Update g_undir: Add bearings
    ox.bearing.add_edge_bearings(g_undir)

    progress_bar.close()

    return city_boundary_exists, nodes, edges, g_undir, nodes_exnw, edges_exnw, g_undir_exnw, nodes_exnw_filtered, city_boundary_geometry, city_boundary_gdf


def _gbn_create_seed_points(existing_network_spacing, seed_point_type, g_undir, edges, nodes, seed_point_grid_spacing, import_files, city_query, seed_point_tags, city_boundary_geometry):
    """Create seed points.
    """
    progress_bar = initialize_progress_bar("Creating seed points", 3+int(bool(existing_network_spacing)))
    seed_network = nx.Graph() # This is only relevant for some methods
    if seed_point_type == 'grid_square' or seed_point_type == 'grid_triangle':
        # Bearings work on unprojected graph
        principal_bearing = get_principal_bearing(g_undir)

        # But this is on the projected edges now
        seed_points, seed_network = _get_grid_seed_points(
            edges, seed_point_grid_spacing, principal_bearing, seed_point_type
        ) # The seed_network is only relevant for quadrangulation
    elif seed_point_type in constants._PRESET_TAGS:
        seed_point_tags = constants._PRESET_TAGS[seed_point_type]
    elif seed_point_type == 'file':
        seed_points = gpd.read_file(settings.import_path+import_files['seed_points'])
        seed_points = _prepare_seed_points(seed_points)

    if seed_point_type == 'tags' or seed_point_type in constants._PRESET_TAGS:
        seed_points = _get_tags_seed_points(city_query, tags=seed_point_tags, city_boundary_geometry=city_boundary_geometry)
    progress_bar.update(1)
    return seed_points, seed_network, progress_bar


def _gbn_snap_filter_seed_points(progress_bar, seed_points, seed_network, nodes, seed_point_linking, existing_network_spacing, nodes_exnw_filtered):
    """Snap and filter seed points.
    """
    seed_points_snapped = snap_points_to_osm_nodes(seed_points, nodes)
    if seed_point_linking == 'quadrangulate': # Map geometry to osmid
        mapping = {row.geometry_generated: row.osmid for row in seed_points_snapped.itertuples()}
        nx.relabel_nodes(seed_network, mapping, copy=False)
    progress_bar.update(1)
    seed_points_snapped_filtered = filter_points_distant_from_osm_nodes(seed_points_snapped, settings.seed_point_snap_distance)
    if seed_point_linking == 'quadrangulate': # Remove all filtered out nodes
        filtered_nodes = set(seed_points_snapped.osmid) - set(seed_points_snapped_filtered.osmid)
        seed_network.remove_nodes_from(filtered_nodes)
        seed_network = seed_network.subgraph(sorted(nx.connected_components(seed_network), key=len, reverse=True)[0]) # Keep only the largest connected component (the network might have fallen apart)
    progress_bar.update(1)

    if existing_network_spacing is not None:
        seed_points_snapped_filtered = _update_seed_points_with_existing_bike_network(seed_points_snapped_filtered, nodes_exnw_filtered, existing_network_spacing)
        progress_bar.update(1)
    progress_bar.close()

    # Abort if less than 3 seed points. Triangulation needs at least 3.
    if len(seed_points_snapped_filtered) < 3:
        raise RuntimeError("Found less than 3 seed points, but more are needed.")
    return seed_points_snapped_filtered


def _gbn_angulate_seed_points(seed_point_linking, seed_points_snapped_filtered, seed_network):
    """Triangulate or quadrangulate seed points or seed point network.
    """
    if seed_point_linking != 'quadrangulate':
        # Triangulation and metrics (betweenness, closeness) are calculated for the unrouted, abstract network for which egde lengths are taken from the routed network.
        progress_bar = initialize_progress_bar("Triangulation", 1)
        # Create unrouted network with delaunay triangulation edges
        grown_bikenet_edges_abstract = _create_delaunay_edges(seed_points_snapped_filtered)
    else: # Build the same dataframe structure for the abstract network from the seed_network.edges
        progress_bar = initialize_progress_bar("Quadrangulation", 1)
        grown_bikenet_edges_abstract = pd.DataFrame({
            'pair': seed_network.edges,
            'source': [e[0] for e in seed_network.edges],
            'target': [e[1] for e in seed_network.edges]
            }) # Afterwards, all steps are identical
    progress_bar.update(1)
    progress_bar.close()
    return grown_bikenet_edges_abstract


def _gbn_reset_auto_settings(setting_was_auto):
    """Reset settings and constants to auto.
    """
    if setting_was_auto['crs_calculations']:
        constants._CRS_CALCULATIONS = 'auto'
    if setting_was_auto['crs_viz']:
        settings.viz["crs"] = 'auto'


def _gbn_route(g_undir, edges, grown_bikenet_edges_abstract, seed_points_snapped_filtered, num_data_files, point_data, trip_data):
    """Weigh edges, route, make graph object, add point and trip data.
    """
    progress_bar = initialize_progress_bar("Routing", 3)

    # Add pbi and weight before calculating shortest paths
    g_undir = assign_pbi_to_edges(g_undir)
    edges = bike_infra_mapping_gdf(g_undir, edges)
    g_undir = weigh_edges(g_undir, constants._ROUTING_PENALTY)

    # Map each unrouted edge to a merged geometry of corresponding OSMnx edges (routed on g_undir)
    grown_bikenet_edges_abstract = route_nodepairs(grown_bikenet_edges_abstract, edges, g_undir)
    progress_bar.update(1)
    grown_bikenet_edges = create_gdf_with_geoms(grown_bikenet_edges_abstract, edges)
    progress_bar.update(1)

    # Add distances between source and target from geometry
    grown_bikenet_edges["dist"] = grown_bikenet_edges["geometry"].length

    node_lon = seed_points_snapped_filtered.geometry.x # Needed for add_trip_data_to_net()
    node_lat = seed_points_snapped_filtered.geometry.y # Needed for add_trip_data_to_net()
    edge_list = grown_bikenet_edges["pair"]
    print(edge_list)
    sys.exit()
    dist_list = grown_bikenet_edges["dist"]
    dist_dict = dict(zip(edge_list, dist_list))
    geom_dict = dict(zip(edge_list, grown_bikenet_edges["geometry"].tolist()))
    # Add point data to edges
    if point_data is not None:
        grown_bikenet_edges = add_point_data_to_net(point_data, grown_bikenet_edges)
        num_points_list = grown_bikenet_edges["num_points"]
        num_points_dict = dict(zip(edge_list, num_points_list))

    # Make graph object from edge list
    B = nx.Graph() # B like bike network
    B.add_nodes_from(seed_points_snapped_filtered.index)
    nx.set_node_attributes(B, node_lon, "x") # Needed for add_trip_data_to_net()
    nx.set_node_attributes(B, node_lat, "y") # Needed for add_trip_data_to_net()
    B.add_edges_from(edge_list)
    nx.set_edge_attributes(B, dist_dict, "distance")
    nx.set_edge_attributes(B, geom_dict, "geometry")
    if point_data is not None:
        nx.set_edge_attributes(B, num_points_dict, "num_points")
    B.graph["crs"] = constants._CRS_CALCULATIONS # Needed for add_trip_data_to_net()
    B = B.subgraph(sorted(nx.connected_components(B), key=len, reverse=True)[0]) # Keep only the largest connected component (the network might have fallen apart)
    seed_points_snapped_filtered = seed_points_snapped_filtered[seed_points_snapped_filtered.index.isin(B.nodes)] # Remove seed points from disconnected components

    if num_data_files:
        # Add trip data to edges
        if trip_data is not None:
            B = add_trip_data_to_net(trip_data, B)

        # Compute weighted distances
        if trip_data is not None:
            dist_weighted_by_trips_dict = _get_weighted_distances(B, "num_trips") # d_trip in [2]_
        if point_data is not None:
            dist_weighted_by_points_dict = _get_weighted_distances(B, "num_points") # d_crash in [2]_

        # Combine them
        dist_weighted_dict = {}
        if trip_data is not None and point_data is not None:
            for k in dist_weighted_by_trips_dict:
                dist_weighted_dict[k] = settings.import_data_trip_point_balance*dist_weighted_by_trips_dict[k] + (1-settings.import_data_trip_point_balance)*dist_weighted_by_points_dict[k] # d_{W} in [2]_
        elif trip_data is not None and point_data is None:
            dist_weighted_dict = dist_weighted_by_trips_dict
        elif trip_data is None and point_data is not None:
            dist_weighted_dict = dist_weighted_by_points_dict

        metric_weight = "distance_weighted"
        nx.set_edge_attributes(B, dist_weighted_dict, metric_weight)
    else:
        metric_weight = "distance"

    progress_bar.update(1)
    progress_bar.close()

    return B, metric_weight


def _gbn_reroute(edges_ordered, edges, g_undir, grown_bikenet_edges_abstract):
    """Reroute all edges, set pbi iteratively.

    The point of rerouting is to go through all abstract edges one by one in 
    their determined ordering. In each step, reroute with pbi penalties, and 
    then set the routed path to pbi. That way newly routed paths assume that
    all previously routed paths are already pbi, and go more likely through 
    those previous paths, preventing "nile delta" artefacts to some extent, and
    making the resulting grown network shorter / more effective.

    Parameters
    ----------
    edges_ordered : geopandas.geodataframe.GeoDataFrame
        Geodataframe of all edges in street network ordered by the `ordering` 
        method, in projected CRS `constants._CRS_CALCULATIONS`.
    edges : geopandas.geodataframe.GeoDataFrame
        Edges of the growable network, in projected CRS 
        `constants._CRS_CALCULATIONS`.
    g_undir : networkx.classes.multigraph.MultiGraph
        NetworkX graph of growable network, undirected.
    grown_bikenet_edges_abstract : pandas.DataFrame
        Dataframe of abstract edges.

    Returns
    -------
    edges_reordered : geopandas.geodataframe.GeoDataFrame
        Geodataframe of all edges in street network ordered by the `ordering` 
        method, and reordered to account for pbi dynamically, in projected CRS 
        `constants._CRS_CALCULATIONS`. If `settings.reroute` is set to False,
        returns the input `edges_ordered`.
    """
    if not settings.reroute: # Do nothing
        return edges_ordered
    else:
        edges_reordered = edges_ordered.copy()

        for edge in tqdm(
            edges_ordered.itertuples(index=True),
                desc=("{:<"+str(constants._PROGRESS_BAR_DESC_LENGTH)+"}").format("Rerouting"),
                leave=True,
                unit="edge",
                total=len(list(edges_ordered.itertuples())),
                bar_format='{l_bar}{bar:'+str(constants._PROGRESS_BAR_LENGTH-7)+'}{r_bar}',
                disable=settings.silent,
            ):
            i = grown_bikenet_edges_abstract.index[(grown_bikenet_edges_abstract['source']==edge.source) & (grown_bikenet_edges_abstract['target']==edge.target)] # grown_bikenet_edges_abstract was never reordered like the edges. Need to match.
            grown_bikenet_edges_abstract_onerow = grown_bikenet_edges_abstract.iloc[i].drop(columns=['path_nodes', 'path_edges'])
            g_undir = set_path_to_pbi(edge.source, edge.target, edges, g_undir)
            g_undir = weigh_edges(g_undir, constants._ROUTING_PENALTY)
            grown_bikenet_edges_abstract_onerow = route_nodepairs(grown_bikenet_edges_abstract_onerow, edges, g_undir)
            grown_bikenet_edge = create_gdf_with_geoms(grown_bikenet_edges_abstract_onerow, edges)
            if not grown_bikenet_edge.empty: # To do: How can it be empty? See _get_weighted_distances()
                edges_reordered.loc[edge.Index, "geometry"] = grown_bikenet_edge['geometry'].iloc[0]
            
        return edges_reordered


def _gbn_compute_edge_metrics(ordering, B, metric_weight):
    """Compute edge metrics.
    """
    progress_bar = initialize_progress_bar("Computing edge metrics", 2)

    # The ordering=="random" case has no edge attributes and is handled in _order_df
    if ordering == "betweenness":
        # Add betweenness attributes to edges
        bc_values = nx.edge_betweenness_centrality(
            B, weight=metric_weight, normalized=True
        )
        nx.set_edge_attributes(B, bc_values, name="betweenness")
    elif ordering == "closeness":
        # Add closeness attributes to nodes and edges
        cc_values_nodes = nx.closeness_centrality(B, distance=metric_weight)
        nx.set_node_attributes(B, cc_values_nodes, name="closeness")
        cc_values = node_to_edge_attributes(cc_values_nodes, B.edges)
        nx.set_edge_attributes(B, cc_values, name="closeness")
    progress_bar.update(1)

    # Export attributes to gdfs:
    # Create dataframe and add method as edge attribute
    edges_ordered = df_from_graph(B, ordering)

    # Order edges by specified method
    edges_ordered = _order_df(edges_ordered, ordering)

    edges_ordered = gpd.GeoDataFrame(edges_ordered, crs=constants._CRS_CALCULATIONS, geometry="geometry")
    progress_bar.update(1)
    progress_bar.close()

    return edges_ordered


def import_network(growable_network):
    """Import and project a street network from gpkg file.

    Parameters
    ----------
    growable_network : str
        The street network is loaded from this file. Must be a gpkg file 
        in unprojected CRS EPSG:4326 with layers nodes and edges, with the 
        structure that a OSMnx street network ``g`` has after saving its 
        undirected version via ``ox.io.save_graph_geopackage()``. For example:

        >>> g = ox.graph_from_place("Barcelona", network_type='drive')
        >>> g = nx.MultiGraph(ox.convert.to_digraph(g))
        >>> ox.io.save_graph_geopackage(g, "Barcelona_streets.gpkg")
    import_path : str, default `settings.import_path`
        Path to import files.

    Returns
    -------
    nodes : geopandas.geodataframe.GeoDataFrame
        Extracted OSM nodes, projected.
    edges : geopandas.geodataframe.GeoDataFrame
        Extracted OSM edges, projected.
    g_undir : networkx.classes.multigraph.MultiGraph
        Extracted networkX graph, undirected.
    city_boundary_gdf : geopandas.geodataframe.GeoDataFrame
        Convex hull of the street network.

    Notes
    -----
    For all edges between a pair of nodes u and v there must be one edge with 
    key 0.
    """

    nodes = gpd.read_file(settings.import_path+growable_network, layer='nodes')
    edges = gpd.read_file(settings.import_path+growable_network, layer='edges')

    # Set indices as required by osmnx.convert.graph_from_gdfs
    # See: https://osmnx.readthedocs.io/en/stable/user-reference.html#osmnx.utils_graph.graph_from_gdfs
    nodes = nodes.set_index(['osmid'])
    edges = edges.set_index(['u', 'v', 'key'])

    g = ox.convert.graph_from_gdfs(nodes, edges)
    g_undir = g.to_undirected().copy() # convert to undirected (dropping OSMnx keys!)

    city_boundary_gdf = gpd.GeoDataFrame(gpd.GeoSeries(nodes.union_all().convex_hull), geometry=0, crs=nodes.crs) # We do this before the projection of nodes below
    # To do: To be super-correct, the hull should be buffered by settings.seed_point_snap_distance (in degrees due to being unprojected)

    nodes, edges = prepare_nodes_edges(nodes, edges)

    return nodes, edges, g_undir, city_boundary_gdf


def _gbn_postprocess_edges(existing_network_spacing, edges_exnw, edges_ordered):
    """Postprocess edges: Add bike net on top, remove overlaps, add length 
    metrics, reorder, reproject.
    """
    # Add existing bike network on top, https://stackoverflow.com/a/43408736
    if existing_network_spacing:
        existing_bikenet = gpd.GeoDataFrame({c: None for c in edges_ordered.columns}, index=[-1], crs=constants._CRS_CALCULATIONS)
        existing_bikenet.loc[-1, 'geometry'] = gpd.GeoSeries(edges_exnw.geometry).union_all()
        edges_ordered.loc[-1] = existing_bikenet.loc[-1]
        edges_ordered.index = edges_ordered.index+1
        edges_ordered.sort_index(inplace=True)
        edges_ordered.crs = constants._CRS_CALCULATIONS

    # Remove edge overlaps
    if not settings.allow_edge_overlaps:
        edges_ordered = _remove_edge_overlaps(edges_ordered) # Can take a while, could be sped up.

    # Add lengths and cumulative lengths, rounded to integer meters
    edges_ordered['length'] = edges_ordered.geometry.length
    edges_ordered['length_cumulative'] = edges_ordered.geometry.length.cumsum()
    edges_ordered = edges_ordered.astype({'length': int, 'length_cumulative': int})

    if constants.REORDER:
        edges_ordered['ordering'] = edges_ordered.index

    # Back to unprojected (potentially). No more calculations after here.
    edges_ordered.to_crs(epsg=settings.crs_result, inplace=True)

    return edges_ordered


def _gbn_prepare_export(export_data, export_plots, city_id, city_query, existing_network_spacing, seed_point_type, ordering):
    """Prepare export: Create folder and filename for exported data
    """
    if export_data or export_plots:
        os.makedirs(settings.export_path['results'], exist_ok=True)
        if city_id is None:
            city_string = slugify(city_query)
        else:
            city_string = slugify(city_id)
        if existing_network_spacing:
            exnw_string = "from_bikenw"
        else:
            exnw_string = "from_scratch"
        if seed_point_type == "file":
            seed_point_string = slugify(settings.seed_point_type_name)
        else:
            seed_point_string = seed_point_type
        export_data_filename = city_string + "-growbikenet-" + ordering + "-" + seed_point_string + "-" + exnw_string + "." + settings.export_file_format
        export_strings = {
            "export_data_filename": export_data_filename,
            "city_string": city_string,
            "exnw_string": exnw_string,
            "seed_point_string": seed_point_string,
        }
        return export_strings


def _gbn_export_data_to_file(export_data, seed_points_snapped_filtered, city_boundary_exists, city_boundary_gdf, existing_network_spacing, edges_ordered, export_strings):
    """Export data.
    """
    
    if export_data:
        if len(edges_ordered)<1+bool(existing_network_spacing is not None):
            warnings.warn("Not enough space to grow links. No data was exported.")
        else:
            seed_points_snapped_filtered.drop(["osmid"], axis=1, inplace=True)
            seed_points_snapped_filtered.to_crs(epsg=settings.crs_result, inplace=True)
            if city_boundary_exists:
                city_boundary_gdf.to_crs(epsg=settings.crs_result, inplace=True)
            if settings.export_file_format == "geojson": # To do: Simplify ugly code duplications and make this an IO function
                progress_bar = initialize_progress_bar("Exporting data", 2+int(bool(existing_network_spacing))+int(city_boundary_exists), "file")
                if settings.crs_result == '4326': # Export with RFC7946="YES"
                    if existing_network_spacing:
                        existing_network = edges_ordered.iloc[[0]]
                        edges_ordered = edges_ordered.iloc[1:].astype({'source': int, 'target': int})
                        existing_network.to_file(settings.export_path['results']+export_strings['city_string']+"-growbikenet-existing_bike_network.geojson", driver="GeoJSON", RFC7946="YES")
                        progress_bar.update(1)
                        edges_ordered.to_file(settings.export_path['results']+export_strings['export_data_filename'], driver="GeoJSON", RFC7946="YES")
                        progress_bar.update(1)
                    else:
                        edges_ordered.to_file(settings.export_path['results']+export_strings['export_data_filename'], driver="GeoJSON", RFC7946="YES")
                        progress_bar.update(1)
                    seed_points_snapped_filtered.to_file(settings.export_path['results']+export_strings['city_string']+"-growbikenet-seed_points-"+export_strings['seed_point_string']+"-"+export_strings['exnw_string']+".geojson", driver="GeoJSON", RFC7946="YES")
                    progress_bar.update(1)
                    if city_boundary_exists: 
                        city_boundary_gdf.to_file(settings.export_path['results']+export_strings['city_string']+"-growbikenet-city_boundary.geojson", driver="GeoJSON", RFC7946="YES")
                        progress_bar.update(1)
                else:
                    if existing_network_spacing:
                        existing_network = edges_ordered.iloc[[0]]
                        edges_ordered = edges_ordered.iloc[1:].astype({'source': int, 'target': int})
                        existing_network.to_file(settings.export_path['results']+export_strings['city_string']+"-growbikenet-existing_bike_network.geojson", driver="GeoJSON")
                        progress_bar.update(1)
                        edges_ordered.to_file(settings.export_path['results']+export_strings['export_data_filename'], driver="GeoJSON")
                        progress_bar.update(1)
                    else:
                        edges_ordered.to_file(settings.export_path['results']+export_strings['export_data_filename'], driver="GeoJSON")
                        progress_bar.update(1)
                    seed_points_snapped_filtered.to_file(settings.export_path['results']+export_strings['city_string']+"-growbikenet-seed_points-"+export_strings['seed_point_string']+"-"+export_strings['exnw_string']+".geojson", driver="GeoJSON")
                    progress_bar.update(1)
                    if city_boundary_exists: 
                        city_boundary_gdf.to_file(settings.export_path['results']+export_strings['city_string']+"-growbikenet-city_boundary.geojson", driver="GeoJSON")
                        progress_bar.update(1)
            elif settings.export_file_format == "gpkg":
                progress_bar = initialize_progress_bar("Exporting data", 1, "file")
                f = settings.export_path['results']+export_strings['export_data_filename']
                if os.path.exists(f):
                    os.remove(f) # mode="w" does not work for to_file with gpkg. It always appends. Therefore, existing file needs to be deleted.
                if existing_network_spacing:
                    edges_ordered.iloc[[0]].to_file(f, driver="GPKG", layer="Existing bike network") 
                    edges_ordered.iloc[1:].to_file(f, driver="GPKG", layer="Grown bike network")
                else:
                    edges_ordered.to_file(f, driver="GPKG", layer="Grown bike network")
                seed_points_snapped_filtered.to_file(f, driver="GPKG", layer="Seed points")
                if city_boundary_exists: city_boundary_gdf.to_file(f, driver="GPKG", layer="City boundary")
                progress_bar.update(1)
            progress_bar.close()


def _gbn_export_plots_to_file(export_plots, ordering, edges_ordered, seed_points_snapped_filtered, existing_network_spacing):
    """Export plots.
    """
    if export_plots and len(edges_ordered)>=1+bool(existing_network_spacing is not None):
        os.makedirs(settings.export_path['plots']+"ordering_"+ordering+"/", exist_ok=True)
        
        if settings.viz["crs"] == "auto": # Make it local azimuthal by default
            network_center = edges_ordered.to_crs(constants._CRS_CALCULATIONS).dissolve().centroid.to_crs('4326') # Calculate centroid in projected CRS, then go back to unprojected CRS for lat lon
            settings.viz["crs"] = f"+proj=aeqd +R=6371000 +units=m +lat_0={network_center.y[0]} +lon_0={network_center.x[0]}" # The first coordinate x is the latitude

        generate_plots(
            edges_ordered,
            seed_points_snapped_filtered,
            ordering,
            bool(existing_network_spacing),
        )
