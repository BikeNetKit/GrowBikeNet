"""Utility functions for growbikenet."""

from . import constants
from . import settings
import os
from collections import defaultdict
import re
import numpy as np
import pandas as pd
import geopandas as gpd
import warnings
import networkx as nx
import osmnx as ox
import scipy # scipy is needed by osmnx.distance.nearest_nodes()
from scipy.spatial import Delaunay
import shapely
from shapely.prepared import prep
from shapely.geometry import Point, LineString, MultiLineString
from shapely.affinity import rotate
from shapely.strtree import STRtree
from pyproj import Transformer
from tqdm import tqdm


def _validate_settings():
    """ Check if user settings input is valid. If not, raise an exception or warning
    
    Parameters
    ----------
    See settings

    Returns
    -------
    True
    """

    if type(settings.crs_projected) is not str:
        raise TypeError("settings.crs_projected must be a string")
    if settings.export_file_format != "geojson" and settings.export_file_format != "gpkg":
        raise ValueError("settings.export_file_format must be 'geojson' or 'gpkg'")
    # To do: check export_path
    if type(settings.seed_point_snap_distance) is not int and settings.seed_point_snap_distance != 'auto':
        raise TypeError("settings.seed_point_snap_distance must be 'auto' or an integer")
    if type(settings.seed_point_snap_distance) is int and settings.seed_point_snap_distance <= 0:
        raise ValueError("settings.seed_point_snap_distance must be a positive integer")
    return True


def _validate_parameters(
        city_query,
        ranking,
        seed_point_type,
        seed_point_grid_spacing,
        seed_point_linking,
        existing_network_spacing,
        export_data,
        city_id,
        export_plots,
        # export_video,
        allow_edge_overlaps,
        import_files,
        seed_point_tags,
    ):
    """ Check if user parameter input is valid. If not, raise an exception or warning
    
    Parameters
    ----------
    Same as growbikenet.growbikenet()
    Additionally:
    constants._PRESET_TAGS : dict
        Dictionary of preset seed point tags.

    Returns
    -------
    True
    """

    if type(city_query) is not str:
        raise TypeError("city_query must be a string")
    if type(ranking) is not str:
        raise TypeError("ranking must be a string")
    if ranking not in ["betweenness_centrality", "closeness_centrality", "random"]:
        raise ValueError(
            "ranking must be either 'betweenness_centrality', 'closeness_centrality', or 'random'"
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
    # if type(export_video) is not bool:
    #     raise TypeError("export_video must be a boolean")

    # Import files
    for filename in ['city_boundary','street_network','bike_network','seed_points','point_data','trip_data']:
        if type(import_files[filename]) is str and not os.path.isfile(settings.import_path+import_files[filename]):
            raise FileNotFoundError(filename+" not found")
        
    if seed_point_tags is not None and type(seed_point_tags) is not dict:
        raise TypeError("seed_point_tags must be None or a dictionary")

    return import_files


def slugify(s): 
    """Slugify a string
    
    Source: https://github.com/Chalarangelo/30-seconds-of-code/blob/master/content/snippets/python/s/slugify.md

    Parameters
    ----------
    s : str
        String to slufigy

    Returns
    -------
    s : str
        Slugified string
    """
    s = s.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s


def _resolve_auto_parameters(
        seed_point_type,
        seed_point_grid_spacing,
        seed_point_linking,
        existing_network_spacing,
        phi,
        import_files,
    ):
    """Resolve auto parameters, their inconsistencies, and settings
    
    Parameters
    ----------
    seed_point_* and existing_network_spacing and import_files from growbikenet.growbikenet()
    
    Additionally:
    phi : float
        Weighted orientation order

    Returns
    -------
    seed_point_* and existing_network_spacing from growbikenet.growbikenet()
    """
    
    if import_files['seed_points']:
        seed_point_type = 'file'
        seed_point_linking = 'triangulate_delaunay' 

    if seed_point_type == 'auto':
        if phi>constants._PHI_LIMITS[1]: # Case grid. For example, Barcelona, Manhattan
            seed_point_type = 'grid_square'
            if seed_point_linking == 'auto':
                seed_point_linking = 'quadrangulate'
                if existing_network_spacing is not None: # Case incompatible with existing_network_spacing not None 
                    existing_network_spacing = None
                    warnings.warn("Automatically chosen seed_point_linking 'quadrangulate' is incompatible with existing_network_spacing not set to None. Changing existing_network_spacing to None.")
        elif phi<=constants._PHI_LIMITS[1] and phi>constants._PHI_LIMITS[0]: # Case contains some grid elements. For example, Prague, Budapest
            seed_point_type = 'grid_square'
            if seed_point_linking == 'auto':
                seed_point_linking = 'triangulate_delaunay'
        elif phi<=constants._PHI_LIMITS[0]: # Case negligible grid elements. For example, Berlin, London
            seed_point_type = 'grid_triangle'
            if seed_point_linking == 'auto':
                seed_point_linking = 'triangulate_delaunay'
            elif seed_point_linking == 'quadrangulate': # Case incompatible auto-type and set linking
                seed_point_linking = 'triangulate_delaunay'
                warnings.warn("seed_point_linking 'quadrangulate' is incompatible with automatically selected seed_point_type. Changing seed_point_linking to 'triangulate_delaunay'.")
    else:
        if seed_point_linking == 'auto':
            if seed_point_type != 'grid_square': # Everything is triangulated, but the grid could also be quadrangulated
                seed_point_linking = 'triangulate_delaunay'
            else:
                if phi>constants._PHI_LIMITS[1]: # Case grid. For example, Barcelona, Manhattan
                    seed_point_linking = 'quadrangulate'
                    if existing_network_spacing is not None: # Case incompatible with existing_network_spacing not None 
                        existing_network_spacing = None
                        warnings.warn("Automatically chosen seed_point_linking 'quadrangulate' is incompatible with existing_network_spacing not set to None. Changing existing_network_spacing to None.")
                elif phi<=constants._PHI_LIMITS[1] and phi>constants._PHI_LIMITS[0]: # Case contains some grid elements. For example, Prague, Budapest
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


def add_trip_data_to_net(trips, A, crs_projected=settings.crs_projected, matching_distance=settings.import_trip_data_snap_distance):
    """Match trip data to network edges

    First, match origin and destination points given in trips to the nodes. Only consider trips where both origins and nodes are matched within matching_distance. Then, for each trip, find the shortest path over the edges from matched origin node to matched destination node, and add 1 (or optionally "num" if column provided in trips) to the affected edges.

    Parameters
    ----------
    trips : pandas DataFrame
        A df of unprojected origin-destination coordinates (columns: o_lat, o_lon, d_lat, d_lon), with each row encoding a trip, in unprojected crs EPSG:4326. Optional with a column "num" containing an integer. This could be (number of) trip events. If "num" column is not provided, assumes 1 per trip.
    A: networkx.graph
        Graph created from triangulation edge list
    crs_projected : str
        Coordinate reference system that is used to project spatial data.
    matching_distance : int
        Matching distance in meters. Set via settings.import_trip_data_snap_distance.

    Returns
    -------
    graph_with_data : networkx.graph
        The same graph created from triangulation edges list, but with a new edge attribute "num_trips" populated with the summed up "num" values of all trips where both origins and destinations could be matched to the closest network nodes within matching_distance. 
    """

    graph_with_data = A.copy()

    transformer = Transformer.from_crs("EPSG:4326", crs_projected, always_xy=True)

    # If column "num" is not provided assume 1 trip per origin-destination (OD) pair
    if 'num' in trips.columns:
        nums = trips['num']
    else:
        nums = [1] * len(trips)


    # Project trip data
    trips_projected = trips.copy()
    trips_projected['o_lon'], trips_projected['o_lat'] = transformer.transform(trips['o_lon'], trips['o_lat'])
    trips_projected['d_lon'], trips_projected['d_lat'] = transformer.transform(trips['d_lon'], trips['d_lat'])

    # Match given origins and destinations to the closest nodes in the network
    o_nodes, o_distances = ox.distance.nearest_nodes(graph_with_data, trips_projected['o_lon'], trips_projected['o_lat'], return_dist=True)
    d_nodes, d_distances = ox.distance.nearest_nodes(graph_with_data, trips_projected['d_lon'], trips_projected['d_lat'], return_dist=True)


    # Add number of trips to graph
    trip_dict = dict(zip(graph_with_data.edges, [0] * len(graph_with_data.edges)))

    for o_node, o_distance, d_node, d_distance, num in zip(o_nodes, o_distances, d_nodes, d_distances, nums):

        # If:
        #   - origin and destination are snapped to the same node, or
        #   - origin is >500m away from the snapped node, or
        #   - destination is >500m away from the snapped node
        # no trips are added
        if o_node == d_node or o_distance > matching_distance or d_distance > matching_distance:
            continue  

        # Get shortest path between the snapped orgin and destination nodes
        path = nx.shortest_path(graph_with_data, source=o_node, target=d_node, weight="distance")
        path_edges = list(zip(path[:-1], path[1:]))


        # Add the number of trips to each edge of the shortest path
        for i, edge_id in enumerate(path_edges):
            if edge_id in trip_dict.keys():
                trip_dict[edge_id] += num

            else:
                edge_id = (path[i + 1], path[i])  # Inverse node order
                if edge_id in trip_dict.keys():
                    trip_dict[edge_id] += num

    nx.set_edge_attributes(graph_with_data, trip_dict, "num_trips")

    return graph_with_data


def add_point_data_to_net(points, edges, crs_projected=settings.crs_projected, matching_distance=settings.import_point_data_snap_distance):
    """Match point data to network edges

    Parameters
    ----------
    points : geopandas.geodataframe.GeoDataFrame
        A gdf of unprojected point geometries, optional having a column "num" containing an integer. This could be (number of) point events like crashes or citizen feedback to improve bike infrastructure. If "num" column is not provided, assumes 1 per point.
    edges : geopandas.geodataframe.GeoDataFrame
        A gdf of projected spatial network edges. This is the routed network of seed points.
    crs_projected : str
        Coordinate reference system that is used to project osm data.
    matching_distance : int
        Matching distance in meters. Set via settings.import_point_data_snap_distance.

    Returns
    -------
    edges_with_data : geopandas.geodataframe.GeoDataFrame
        The same spatial network edges, but with a new int column "num_points" populated with the summed up "num" values of all points, matched to the closest links if within matching_distance. 
    """

    edges_with_data = edges.copy()

    points_projected = points.to_crs(crs_projected)

    # If column "num" is not provided assume 1 event per point
    if 'num' in points_projected.columns:
        nums = points_projected['num']
    else:
        nums = [1] * len(points_projected)

    # Initialize the 'num_points' column to 0 for all edges
    edges_with_data['num_points'] = 0 * len(edges_with_data)

    # Get geometries of edges and points
    edges_geoms = edges_with_data['geometry']
    points_geoms = points_projected['geometry']

    # Build an r-tree spatial index by position for subsequent iloc
    rtree = STRtree(edges_geoms)    
                            
    for point in points_geoms.items(): # point = (id, POINT(x, y))

        # Query the tree for all the edges within the matching distance of the point
        edges_within_matching_distance = rtree.query(
            point[1],
            predicate='dwithin',
            distance=matching_distance
        )

        # If no edges are within the matching distance, continue to the next point
        if len(edges_within_matching_distance) == 0:
            continue

        # Calculate the distances from the point to each of the edges, and round to 10 decimal places to avoid floating point precision issues
        distances = []
        for edge in edges_within_matching_distance:
            distance = np.around(shapely.distance(point[1], edges_geoms.iloc[edge]), decimals=10)
            distances.append(distance)

        # Get the edges that are closest to the point
        closest_edges = edges_within_matching_distance[np.where(distances == np.min(distances))]

        # Get the lowest index of the closest edges
        closest_edges_min_index = np.sort(closest_edges)[0]

        # Get the number of events at the point
        num = nums[point[0]]

        # Add the number of events to the nearest edge
        edges_with_data.loc[closest_edges_min_index, 'num_points'] += num

    # Move the 'geometry' column to the end of the GeoDataFrame
    # Necessary for testing the function
    cols = [c for c in edges_with_data.columns if c != 'geometry'] + ['geometry']
    edges_with_data = edges_with_data[cols]

    return edges_with_data


def import_network(street_network, import_path=settings.import_path):
    """Import and project a street network from gpkg file

    For all edges between a pair of nodes u and v there must be one edge with key 0.

    Parameters
    ----------
    street_network : str
        The street network will be loaded from this file. Must be a gpkg file in unprojected crs EPSG:4326 with layers nodes and edges, with the structure that a osmnx street network g has after saving its undirected version via ox.io.save_graph_geopackage(). For example:
        >>> g = ox.graph_from_place("Barcelona", network_type='drive')
        >>> g = nx.MultiGraph(ox.convert.to_digraph(g))
        >>> ox.io.save_graph_geopackage(g, "Barcelona_streets.gpkg")
    import_path : str, default settings.import_path
        Path to import files.

    Returns
    -------
    nodes : geopandas.geodataframe.GeoDataFrame
        Extracted OSM nodes, projected
    edges : geopandas.geodataframe.GeoDataFrame
        Extracted OSM edges, projected
    g_undir : networkx.classes.multigraph.MultiGraph
        Extracted networkX graph, undirected
    city_boundary_gdf : geopandas.geodataframe.GeoDataFrame
        Convex hull of the street network
    """

    nodes = gpd.read_file(import_path+street_network, layer='nodes')
    edges = gpd.read_file(import_path+street_network, layer='edges')

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


def prepare_nodes_edges(nodes, edges, crs_projected=settings.crs_projected):
    """Project and prepare nodes and edges for further use

    For all edges between a pair of nodes u and v there must be one edge with key 0.
    
    Parameters
    ----------
    nodes : geopandas.geodataframe.GeoDataFrame
        OSM nodes, unprojected
    edges : geopandas.geodataframe.GeoDataFrame
        OSM edges, unprojected
    crs_projected : str
        EPSG code of the coordinate reference system that is used to project osm data. 
        
    Returns
    -------
    nodes : geopandas.geodataframe.GeoDataFrame
        OSM nodes, projected, osmid is index
    edges : geopandas.geodataframe.GeoDataFrame
        OSM edges, projected
    """

    if not edges.empty:
        # Drop edges with key != 0, effectively making it a non-multigraph
        edges = edges.loc[:,:,0].copy()
        # This also means we are dropping the "key" level from the edge multiindex (u,v,key becomes u,v)
        # To do: Instead of assuming key 0 edges exist (which is often not the case), only retain the shortest edges as in osmnx.convert.to_digraph(), independent of the key.

        # Project geometries of nodes, edges
        edges = edges.to_crs(crs_projected)

    nodes = nodes.to_crs(crs_projected)

    # Add osm ID as column to node gdf
    nodes["osmid"] = nodes.index
    return nodes, edges


def download_network(city_query, network_type='drive', custom_filter=None, retain_all=True, city_boundary_geometry=None):
    """Download and prepare a street network from OSM via OSMnx

    Downloads a network with a given network_type and custom_filter using ox.graph_from_place.
    Then, stores the undirected OSM data in gdfs and projects using settings.crs_projected.

    Parameters
    ----------
    city_query : str
        Name of the city that the analysis should be performed on. Overruled (for data fetching) if city_boundary or street_network is set.
    network_type : {'all', 'all_public', 'bike', 'drive', 'drive_service', 'walk'} 
        What type of street network to retrieve if custom_filter is None.
    custom_filter : (str | list[str] | None)
        A custom ways filter to be used instead of the network_type presets
    retain_all : bool, default True
        If True, return the entire graph even if it is not connected, useful for disconnected bicycle networks. If False, retain only the largest weakly connected component, useful for road networks.
    city_boundary_geometry : (shapely Polygon | shapely MultiPolygon | None), default None
        If not set to None, the study area will be selected from this geometry.

    Returns
    -------
    nodes : geopandas.geodataframe.GeoDataFrame
        Extracted OSM nodes, projected
    edges : geopandas.geodataframe.GeoDataFrame
        Extracted OSM edges, projected
    g_undir : networkx.classes.multigraph.MultiGraph
        Extracted networkX graph, undirected
    """

    # Fetch street network data from osmnx
    if city_boundary_geometry is None:
        g = ox.graph_from_place(
        city_query, network_type=network_type, custom_filter=custom_filter, retain_all=retain_all
        )
    else:
        g = ox.graph_from_polygon(
        city_boundary_geometry, network_type=network_type, custom_filter=custom_filter, retain_all=retain_all
        )

    g_undir = g.to_undirected().copy() # convert to undirected (dropping OSMnx keys!)

    # Export osmnx data to gdfs
    nodes, edges = nx_to_nodes_edges(g_undir)
    return nodes, edges, g_undir


def nx_to_nodes_edges(G):
    """Get nodes and projected edges from networkX graph
    
    Parameters
    ----------
    G : networkx.classes.multigraph.MultiGraph
        networkX graph, undirected
        
    Returns
    -------
    nodes : geopandas.geodataframe.GeoDataFrame
        Extracted OSM nodes, projected, osmid is index
    edges : geopandas.geodataframe.GeoDataFrame
        Extracted OSM edges, projected
    """
    nodes, edges = ox.graph_to_gdfs(
    G,
    nodes=True,
    edges=True,
    node_geometry=True,
    fill_edge_geometry=True
    )

    nodes, edges = prepare_nodes_edges(nodes, edges)
    return nodes, edges
    

def _get_correct_edgetuples(edge_gdf, nodelist):
    """Map a node list (from nx.shortest_paths) to the correct set of edge tuples that can be used for indexing the edge geodataframe

    Parameters
    ----------
    edge_gdf: geopandas.geodataframe.GeoDataFrame
        The street network, in a projected coordinate reference system
    nodelist: list
        A list of nodes that make up source and targets of edges

    Returns
    -------
    edgelist_final: list
        List of edge tuples that can be used for indexing the edge geodataframe
    """
    edgelist_prelim = zip(nodelist, nodelist[1:])
    edgelist_final = []
    for edge_prelim in edgelist_prelim:
        if edge_prelim in edge_gdf.index:
            edgelist_final.append(edge_prelim)
        else:
            edgelist_final.append(tuple([edge_prelim[1], edge_prelim[0]]))
    return edgelist_final


def _get_existing_network_seed_points(nodes_exnw, existing_network_spacing):
    """Get seed points on an existing bicycle network
    
    Start with the first (arbitrary) node from nodes_exnw. Then, for each node: Delete all other nodes closer than existing_network_spacing, proceed with the closest of the remaining nodes. Finish once all nodes are found or deleted.
    
    Parameters
    ----------
    nodes_exnw: geopandas.geodataframe.GeoDataFrame
        Nodes of the existing bicycle network, in a projected coordinate reference system.
    existing_network_spacing: int
        Distance between seed points, in meters.
    Returns
    -------
    seed_points_exnw: geopandas.geodataframe.GeoDataFrame
        Seed points, already part of the network, in the same projected coordinate reference system as edges
    """
    # Start with the first (arbitrary) node from nodes_exnw
    node_current = nodes_exnw.iloc[[0]]

    seed_points_exnw = gpd.GeoDataFrame()
    while len(node_current)>0 and len(nodes_exnw)>0:
        # Find all too close nodes to the current nodes
        nodes_too_close = nodes_exnw.loc[(nodes_exnw.geometry.distance(Point(node_current.iloc[0].geometry)) <= existing_network_spacing)]
        nodes_too_close = nodes_too_close.iloc[:, :-1] # osmid is there twice now (once in the end), so it needs to be dropped

        # Delete the nodes that are too close to nodes_exnw
        nodes_exnw = nodes_exnw.overlay(nodes_too_close, how='difference')

        # Add current node to seed_points_exnw
        seed_points_exnw = pd.concat([seed_points_exnw, node_current], ignore_index=True)

        # Find the node in nodes_exnw that is closest to the existing seed points
        node_current = seed_points_exnw.sjoin_nearest(nodes_exnw, how="inner") 
        if len(node_current)>0: # Current nodes could already be depleted here. Then loop will stop.
            node_current = nodes_exnw[nodes_exnw.osmid == node_current["osmid_right"].values[0]]

    return seed_points_exnw


def update_with_existing_bike_network(city_query, g_undir, import_files, city_boundary_geometry=None):
    """Update street network with existing bike network

    Downloads a network of protected bike infrastructure from OSM (retaining all connected components) or imports it from a local file and merges it to a given street network graph g_undir.
    
    Parameters
    ----------
    city_query : str
        Name of the city that the analysis should be performed on. Overruled (for data fetching) if city_boundary_geometry is set.
    g_undir : networkx.classes.multigraph.MultiGraph
        Street network networkX graph, undirected
    import_files : dict
        Dictionary containing the key "bike_network" and value None or a string with the path of a bicycle network to import. Must be a gpkg file in unprojected crs EPSG:4326 with layers nodes and edges, with the structure that an undirected osmnx bike network has after saved via ox.io.save_graph_geopackage().
    city_boundary_geometry : (shapely Polygon | shapely MultiPolygon | None), default None
        If not set to None, the study area will be selected from this geometry.

    Returns
    -------
    nodes : geopandas.geodataframe.GeoDataFrame
        Updated OSM nodes of the street network, projected
    edges : geopandas.geodataframe.GeoDataFrame
        Updated OSM edges of the street network, projected
    g_undir : networkx.classes.multigraph.MultiGraph
        Updated street networkX graph, undirected
    nodes_exnw : geopandas.geodataframe.GeoDataFrame
        OSM nodes of the corresponding bike network, projected
    edges_exnw : geopandas.geodataframe.GeoDataFrame
        OSM edges of the corresponding bike network, projected
    """
    if import_files['bike_network'] is not None:
        # Import and preprocess data from file
        nodes_exnw, edges_exnw, g_undir_exnw, _ = import_network(import_files['bike_network'])
    else:
        # Fetch protected bike network data from osmnx
        # Due to retain_all=True, this fetches all the connected components
        nodes_exnw, edges_exnw, g_undir_exnw = download_network(city_query, custom_filter=constants.PBI_CUSTOM_FILTER, retain_all=True, city_boundary_geometry=city_boundary_geometry)

    g_undir = nx.compose(g_undir_exnw, g_undir) # Merge to be sure we have everything from both

    # Intermezzo: Get filtered existing network by component length
    nodes_exnw_filtered, _, _ = filter_network_by_component_length(g_undir_exnw)

    # Now we could have some leftover bike infra that is disconnected from the street network and thus not routable.
    # We delete those parts next:
    # Take largest connected component lcc of the merged network
    lcc = max(nx.connected_components(g_undir), key=len)
    g_undir = g_undir.subgraph(lcc).copy() 
    # Restrict nodes and edges of the existing bike net to this lcc
    valid_node_osmids = g_undir.nodes()
    nodes_exnw = nodes_exnw[nodes_exnw['osmid'].isin(valid_node_osmids)]
    nodes_exnw_filtered = nodes_exnw_filtered[nodes_exnw_filtered['osmid'].isin(valid_node_osmids)]
    # edges_exnw has a MultiIndex ('u','v'), so we must use get_level_values, see https://stackoverflow.com/a/18835121
    edges_exnw = edges_exnw.iloc[edges_exnw.index.get_level_values('u').isin(valid_node_osmids)]
    edges_exnw = edges_exnw.iloc[edges_exnw.index.get_level_values('v').isin(valid_node_osmids)]
    nodes, edges = nx_to_nodes_edges(g_undir)

    return nodes, edges, g_undir, nodes_exnw, edges_exnw, g_undir_exnw, nodes_exnw_filtered


def filter_network_by_component_length(g_undir):
    """Filter a network to remove too short components
    
    The application is that g_undir is all the components of the existing bicycle network, but we do not snap seed points to components shorter than constants.EXISTING_NETWORK_MINIMUM_COMPONENT_LENGTH. So we create a new set of nodes where the nodes from the too small components are removed.

    Parameters
    ----------
    g_undir : networkx.classes.multigraph.MultiGraph
        Street network networkX graph, undirected

    Returns
    -------
    nodes_filtered : geopandas.geodataframe.GeoDataFrame
        Filtered OSM nodes of the street network, projected
    edges_filtered : geopandas.geodataframe.GeoDataFrame
        Filtered OSM edges of the street network, projected
    g_undir_filtered : networkx.classes.multigraph.MultiGraph
        Filtered street networkX graph, undirected
    """

    g_undir_filtered = nx.MultiGraph()
    components_by_length = [g_undir.subgraph(c).copy() for c in sorted(nx.connected_components(g_undir), key=lambda c: sum([l[-1] for l in g_undir.subgraph(c).copy().edges.data('length')]), reverse=True)]
    for c in components_by_length: # Create the union of long enough components. Probably there is a way to do this faster/vectorized.
        if c.number_of_edges() and sum([l[-1] for l in c.edges.data('length')]) >= constants.EXISTING_NETWORK_MINIMUM_COMPONENT_LENGTH: # no matter the min length, remove isolated nodes
            g_undir_filtered = nx.union(g_undir_filtered, c)
        else:
            break
    # Get nodes_exnw_filtered
    nodes_filtered, edges_filtered = ox.graph_to_gdfs(
        g_undir_filtered,
        nodes=True,
        edges=True,
        node_geometry=True,
        fill_edge_geometry=True
        )
    nodes_filtered, _ = prepare_nodes_edges(nodes_filtered, gpd.GeoDataFrame())
    return nodes_filtered, edges_filtered, g_undir_filtered


def _update_seed_points_with_existing_bike_network(seed_points_snapped, nodes_exnw, existing_network_spacing):
    """Update seed points with existing bike network

    Updates given snapped seed points by incorporating seed points from an existing bike network.
    
    Parameters
    ----------
    seed_points_snapped : geopandas.geodataframe.GeoDataFrame
        Snapped seed points on the street network, constructed with seed_point_grid_spacing
    nodes_exnw : geopandas.geodataframe.GeoDataFrame
        Nodes of the existing bike network, after shortest components below constants.EXISTING_NETWORK_MINIMUM_COMPONENT_LENGTH have been filtered out
    existing_network_spacing : int
        Positive integer denoting spacing between seed points, in meters, only on the existing bicycle network.

    Returns
    -------
    seed_points_snapped : geopandas.geodataframe.GeoDataFrame
        Snapped seed points incorporating both street grid and existing bike network
    """

    # If the existing bicycle network is used, create extra seed points on it. They are by construction already snapped.
    seed_points_exnw = _get_existing_network_seed_points(nodes_exnw, existing_network_spacing)
    seed_points_exnw.to_crs(settings.crs_projected, inplace=True)

    # Afterwards, drop all previously determined seed points (grid or rail) that are now too close to these extra points.
    buffer_seed_points_exnw = gpd.GeoDataFrame(seed_points_exnw.buffer(existing_network_spacing*constants._BUFFER_SEED_POINTS_EXNW_FACTOR))
    buffer_seed_points_exnw = buffer_seed_points_exnw.rename(columns={0:'geometry'}).set_geometry('geometry') # https://gis.stackexchange.com/questions/266098/how-to-convert-a-geoseries-to-a-geodataframe-with-geopandas
    buffer_seed_points_exnw.to_crs(settings.crs_projected, inplace=True)

    # Delete the seed points that are too close to seed_points_exnw via its buffer
    seed_points_snapped = seed_points_snapped.overlay(buffer_seed_points_exnw, how='difference')

    # Merge original snapped points with new existing network points (=already snapped)
    seed_points_snapped = seed_points_snapped.overlay(seed_points_exnw, how='union')

    # Bring back to original form (geometry and osmid columns, osmid index)
    # This is a bit of a mess but it works. Simplify it in the future.
    seed_points_snapped.loc[seed_points_snapped['osmid_1'].isnull(), 'osmid_1'] = seed_points_snapped['osmid_2'] # _1 comes from one side, _2 from the other. One has NaNs, the other too. https://stackoverflow.com/a/60132614
    seed_points_snapped = seed_points_snapped[['osmid_1','geometry']]
    seed_points_snapped.rename(columns={"osmid_1": "osmid"}, inplace=True)
    seed_points_snapped.set_index("osmid", drop=False, inplace=True)
    return seed_points_snapped


def _get_grid_seed_points(edges, seed_point_spacing, principal_bearing, seed_point_type='grid_square'):
    """Get grid seed points for street network, rotated by principal bearing

    Adapted from: https://github.com/gboeing/osmnx-examples/blob/v0.11/notebooks/17-street-network-orientations.ipynb

    Parameters
    ----------
    edges: geopandas.geodataframe.GeoDataFrame
        The street network, in a projected coordinate reference system
    seed_point_spacing: int
        Distance between seed points, in meters
    principal_bearing: float
        Principal bearing (most common bearing of streets)
    seed_point_type: str ('grid_square' | 'grid_triangle')

    Returns
    -------
    seed_points: geopandas.geodataframe.GeoDataFrame
        Seed points, rotated by principal bearing, to be snapped to the street network, in the same projected coordinate reference system as edges
    seed_network: networkx graph
        If seed_point_type is 'grid_square', quadrangulated network of the seed_points, where node ids are the seed_points. 
        If seed_point_type is 'grid_triangle', empty network because the seed points will be triangulated.
    """

    # Rotate edges counter to the principal bearing
    edges_temp = edges.copy()
    edges_temp.geometry = edges_temp.geometry.rotate(principal_bearing, origin=(0, 0))

    # Create grid
    # get convex hull around edge area
    hull = edges_temp.union_all().convex_hull
    # get bounds of hull
    xmin, ymin, xmax, ymax = hull.bounds
    xmin = int(xmin); ymin = int(ymin); xmax = int(xmax); ymax = int(ymax); # Round to meters

    # https://stackoverflow.com/questions/66010964/fastest-way-to-produce-a-grid-of-points-that-fall-within-a-polygon-or-shape
    # Populate hull bbox with evenly spaced seeding points
    points = []
    if seed_point_type == 'grid_square':
        x_array = list(range(xmin, xmax+seed_point_spacing, seed_point_spacing)) # overshoot by one
        y_array = list(range(ymin, ymax+seed_point_spacing, seed_point_spacing))
        for x in x_array:
            for y in y_array:
                points.append(Point(x, y))
    elif seed_point_type == 'grid_triangle':
        h = np.sqrt(3)/2
        x_array = list(np.arange(xmin, xmax+seed_point_spacing, seed_point_spacing)) # overshoot by one
        y_array = list(np.arange(ymin, ymax+seed_point_spacing, seed_point_spacing*2*h))
        for x in x_array:
            for y in y_array: # Build two rows in each step: one regular, one staggered
                points.append(Point(x, y))
                points.append(Point(x - 0.5*seed_point_spacing, y + h*seed_point_spacing))

    # Keep only those seed points that are within the hull polygon
    prep_polygon = prep(hull)
    valid_points = []
    valid_points.extend(filter(prep_polygon.contains, points))
    valid_points_coords = set([(p.x, p.y) for p in valid_points])

    # store seed points in gdf
    seed_points = gpd.GeoDataFrame({"geometry": valid_points}, crs=edges.crs)

    # Rotate points back using the principal bearing
    seed_points.geometry = seed_points.geometry.rotate(
        -1 * principal_bearing, origin=(0, 0)
    )

    # Create, prune, and rotate also a seed network, for quadrangulation
    if seed_point_type == 'grid_square':
        seed_network = nx.grid_2d_graph(x_array, y_array)
        invalid_nodes = set(seed_network.nodes) - valid_points_coords
        seed_network.remove_nodes_from(invalid_nodes)
        nx.relabel_nodes(
            seed_network,
            lambda xy: rotate(Point(xy[0],xy[1]), -1 * principal_bearing, origin=(0, 0)),
            copy=False
            )
    elif seed_point_type == 'grid_triangle':
        seed_network = nx.Graph() # We could create a triangular lattice, but triangulation will do the job anyway

    return seed_points, seed_network


def _prepare_seed_points(seed_points):
    """Project and prepare seed points for further use
    
    Parameters
    ----------
    seed_points: geopandas.geodataframe.GeoDataFrame
        Unprojected seed points
        
    Returns
    -------
    seed_points: geopandas.geodataframe.GeoDataFrame
        Projected and prepared seed points.
    """
    seed_points = seed_points[seed_points["geometry"].type == "Point"]
    seed_points.to_crs(settings.crs_projected, inplace=True)
    # To do optional: merge closeby seed points
    return seed_points


def _get_tags_seed_points(city_query, tags, city_boundary_geometry=None):
    """Get tags seed points for a city

    Parameters
    ----------
    city_query : str
        Name of the city that the analysis should be performed on. This is the query string used to fetch the data from nominatim. Overruled (for data fetching) if city_boundary_geometry is set.
    tags : None | dict[str, bool | str | list[str]], default None
        Geocodable tags, see [3]_. For example, tags={"railway": ["station", "halt"]} will retrieve exactly the same as seed_point_type='rail'.
    city_boundary_geometry : (shapely Polygon | shapely MultiPolygon | None), default None
        If not set to None, the study area will be selected from this geometry.

    Returns
    -------
    seed_points: geopandas.geodataframe.GeoDataFrame
        Seed points, rotated by principal bearing, to be snapped to the street network, in the same projected coordinate reference system as edges

    References
    ----------
    .. [3] https://osmnx.readthedocs.io/en/stable/user-reference.html#osmnx.features.features_from_place    
    """

    if city_boundary_geometry:
        seed_points = ox.features_from_polygon(
            city_boundary_geometry, tags
        )
    else:
        seed_points = ox.features_from_place(
            city_query, tags
        )
    seed_points = _prepare_seed_points(seed_points)
    return seed_points


def get_principal_bearing(G):
    """Determine the most common (principal) bearing, for the best grid orientation

    Adapted from: https://github.com/gboeing/osmnx-examples/blob/v0.11/notebooks/17-street-network-orientations.ipynb
    The bearing is determined from edges weighted by length.

    Parameters
    ----------
    G : networkx MultiGraph (undirected)
        The graph from which to determine the principal bearing. Its coordinate reference system must be geographical, not projected.

    Returns
    -------
    principal_bearing: float
        The principal bearing, precise to 5 degrees.
    """

    bearings = {}
    # weight bearings by length (meters)
    city_bearings = []
    for u, v, k, d in G.edges(keys=True, data=True):
        try:
            city_bearings.extend([d["bearing"]] * int(d["length"]))
        except:  # noqa (To do: make specific and remove noqa)
            pass  # Bearings cannot be calculated in rare edge cases.
    b = pd.Series(city_bearings)
    bearings = pd.concat([b, b.map(_reverse_bearing)]).reset_index(drop="True")
    bins = np.arange(constants._BEARING_BINS + 1) * 360 / constants._BEARING_BINS
    count = _count_and_merge(constants._BEARING_BINS, bearings)
    principal_bearing = bins[np.where(count == max(count))][0]

    return principal_bearing


def _reverse_bearing(x):
    """Reverse bearing

    Adapted from: https://github.com/gboeing/osmnx-examples/blob/v0.11/notebooks/17-street-network-orientations.ipynb

    Parameters
    ----------
    x: float
        The bearing to reverse

    Returns
    -------
    x_rev: float
        The reversed bearing
    """
    x_rev = x + 180 if x < 180 else x - 180
    return x_rev


def _count_and_merge(n, bearings):
    """Double, then merge bins to avoid edge effects

    Make twice as many bins as desired, then merge them in pairs.
    Prevents bin-edge effects around common values like 0° and 90°.
    Adapted from: https://github.com/gboeing/osmnx-examples/blob/v0.11/notebooks/17-street-network-orientations.ipynb

    Parameters
    ----------
    n: int
        Number of bins
    bearings: pandas.Series
        Series of bearings

    Returns
    -------
    bearings_merged: numpy.ndarray, dtype=int
        The frequencies of the new merged bearings
    """
    n *= 2
    bins = np.arange(n + 1) * 360 / n
    count, _ = np.histogram(bearings, bins=bins)

    # move the last bin to the front, so eg 0.01° and 359.99° will be binned together
    count = np.roll(count, 1)
    bearings_merged = count[::2] + count[1::2]
    return bearings_merged


def snap_points_to_osm_nodes(points, nodes):
    """Snap points to osm nodes

    Parameters
    ----------
    points: geopandas.geodataframe.GeoDataFrame
        Points that were created within city area, to be snapped to actual osm nodes
    nodes: geopandas.geodataframe.GeoDataFrame
        Actual osm nodes, downloaded from osmnx

    Returns
    -------
    points_snapped: geopandas.geodataframe.GeoDataFrame
        Points with additional information about geometries of osm nodes that nodes were snapped to

    """
    # Ensure same CRS
    if points.crs != nodes.crs:
        points = points.to_crs(nodes.crs)

    # Find nearest nodes (returns indices)
    idx_seed, idx_nodes = nodes.sindex.nearest(points.geometry, return_all=False)

    # Assign osmid safely
    points = points.copy()
    points["osmid"] = nodes.iloc[idx_nodes]["osmid"].values

    # Keep original geometry
    points = points.rename(columns={"geometry": "geometry_generated"})

    # Attach node geometry + attributes
    nodes_subset = nodes[["osmid", "geometry"]].rename(
        columns={"geometry": "geometry_osm"}
    )

    points = points.reset_index(drop=True)
    nodes_subset = nodes_subset.reset_index(drop=True)

    points_snapped = points.merge(nodes_subset, on="osmid", how="left")

    points_snapped.set_geometry("geometry_osm")

    return points_snapped


def filter_points_distant_from_osm_nodes(points_snapped, snap_distance=settings.seed_point_snap_distance):
    """Remove points that are further than the snap distance away from an actual osm node

    Parameters
    ----------
    points_snapped : geopandas.geodataframe.GeoDataFrame
        Points with additional information about geometries of osm nodes that seed nodes were snapped to.
    snap_distance : int
        Maximum distance between raw seed points and osm nodes for snapping, in meters.

    Returns
    -------
    points_snapped_filtered : geopandas.geodataframe.GeoDataFrame
        points within snap distance away from an actual osm node; only columns are osmid and the associated osm geometry
    """
    gdf = points_snapped.copy()

    # Compute distance
    gdf["snap_dist"] = gdf.geometry_generated.distance(gdf.geometry_osm)

    # Filter by threshold
    gdf = gdf[gdf["snap_dist"] <= snap_distance].copy()

    # Drop duplicates: one row per osmid
    gdf = gdf.sort_values("snap_dist").drop_duplicates("osmid")

    # Keep only node geometry
    gdf = gdf[["osmid", "geometry_osm"]].rename(columns={"geometry_osm": "geometry"})

    # Set geometry + index
    gdf = gdf.set_geometry("geometry")
    gdf = gdf.set_index("osmid", drop=False)

    points_snapped_filtered = gdf.copy()

    return points_snapped_filtered


def _create_delaunay_edges(nodes_gdf):
    """Create df with edges that are part of Delaunay triangulation

    Note that the original paper [1]_ uses minimum weight triangulation, but Delaunay triangulation is much faster due to the Delaunay scipy function and gives in most cases identical results. Triangulation and metrics (betweenness, closeness) are calculated for the abstract network for which egde lengths are taken from the routed network.

    Parameters
    ----------
    nodes_gdf: geopandas.geodataframe.GeoDataFrame
        seed points with osmid and corresponding point geometry

    Returns
    -------
    df : pandas.DataFrame
        DataFrame with Edge pairs and singled out source and target nodes

    References
    ----------
    .. [1] M. Szell, S. Mimar, T. Perlman, G. Ghoshal, R. Sinatra, "Growing urban bicycle networks", Scientific Reports 12, 6765 (2022)
    """
    # Ensure projected CRS
    if nodes_gdf.crs.is_geographic:
        raise ValueError("CRS must be projected for triangulation.")

    # Extract coordinates
    coords = np.array([(geom.x, geom.y) for geom in nodes_gdf.geometry])
    osmids = nodes_gdf["osmid"].values

    # Compute triangulation
    tri = Delaunay(coords)

    edges_set = set()

    # Each triangle has 3 edges
    for simplex in tri.simplices:
        i, j, k = simplex

        edges_set.add(tuple(sorted((i, j))))
        edges_set.add(tuple(sorted((j, k))))
        edges_set.add(tuple(sorted((i, k))))

    pairs = []
    sources = []
    targets = []

    for i, j in edges_set:
        pairs.append((osmids[i], osmids[j]))
        sources.append(osmids[i])
        targets.append(osmids[j])

    df = pd.DataFrame(
        {
            "pair": pairs,
            "source": sources,
            "target": targets,
        }
    )

    return df


def _remove_edge_overlaps(edges_in):
    """In the grown network, remove edge overlaps stepwise

    Parameters
    ----------
    edges_in: geopandas.geodataframe.GeoDataFrame
        The grown bike network, in a projected coordinate reference system

    Returns
    -------
    edges_out: geopandas.geodataframe.GeoDataFrame
        The grown bike network without edge overlaps, in a projected coordinate reference system
    """
    edges_out = edges_in.copy()
    grown_net = MultiLineString()
    for row in tqdm(
        edges_in.itertuples(),
        desc="{:<23}".format("Removing edge overlaps"),
        leave=True,
        unit="edge",
        total=len(list(edges_in.itertuples())),
        bar_format='{l_bar}{bar:16}{r_bar}',
        ):
        grown_net_new = grown_net | row.geometry # Calculate union
        if grown_net_new.length > grown_net.length: # Something was added
            grown_net_diff = row.geometry - grown_net # Calculate difference
            # print(row.geometry, grown_net, grown_net_diff)
            edges_out.loc[row.Index, ['geometry']] = grown_net_diff # Add difference
            grown_net = grown_net_new # Only update if something was added
        else: # There was nothing added, so we delete the row
            edges_out.drop(index=row.Index, inplace=True)
    edges_out.drop_duplicates(inplace=True) # How can duplicates happen??
    edges_out.reset_index(drop=True, inplace=True)

    return edges_out

def df_from_graph(A, method):
    """Create a dataframe from an input graph

    Parameters
    ----------
    A: networkx.graph
        Graph created from triangulation edge list
    method: str
        Method used to rank edges. Must be 'betweenness_centrality' (default), 'closeness_centrality', or 'random'.

    Returns
    -------
    df: pandas.DataFrame
        Dataframe with source and target information for each edge, as well as edge attributes as columns
    """

    if method != "random":
        attrs = {
            edge: {
                method: data.get(method),
                "geometry": data.get("geometry"),
            }
            for edge, data in A.edges.items()
        }
        df = pd.DataFrame.from_dict(attrs, orient="index", columns=[method, "geometry"])
    else:
        attrs = {
            edge: {
                "geometry": data.get("geometry"),
            }
            for edge, data in A.edges.items()
        }
        df = pd.DataFrame.from_dict(attrs, orient="index", columns=["geometry"])
    df["node_tuple"] = df.index
    df["source"] = [t[0] for t in df.node_tuple]
    df["target"] = [t[1] for t in df.node_tuple]
    df.drop(columns=["node_tuple"], inplace=True)
    return df


def _rank_df(df, method):
    """Rank dataframe by specified method

    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with source and target information for each edge, as well as edge attributes as columns
    method: str
        Method used to rank edges. Must be 'betweenness_centrality' (default), 'closeness_centrality', or 'random'.

    Results
    -------
    df: pandas.DataFrame
        Dataframe sorted by specified ranking method.
    """
    if method == "random": # ranking is random
        df["rank"] = np.random.permutation(np.arange(df.shape[0]))
        df = df.sort_values(by="rank", ascending=False)
        df.reset_index(drop=True, inplace=True)
        df["rank"] = (
            df.index
        )  
    else: # ranking is the order of appearance in the method's ranking
        df = df.sort_values(by=method, ascending=False)
        df.reset_index(drop=True, inplace=True)
        df["rank"] = (
            df.index
        )  
    return df


def node_to_edge_attributes(values_nodes, edges):
    """Map node to edge attributes.

    Creates edge attributes by taking the average values of adjacent node attributes.

    Parameters
    ----------
    values_nodes : dict
        Keys: node ids, Values: Node attributes (for example a scalar)
    edges : networkx.classes.reportviews.EdgeView
        A view of edge attributes of a networkx graph. Could also be a list of tuples of node ids.

    Returns
    -------
    values_edges: dict
        Keys: tuples of node ids, Values: Edge attributes
    """
    values_edges = {}
    for u, v in edges:
        values_edges[(u, v)] = 0.5 * (values_nodes[u] + values_nodes[v])
    return values_edges


def add_path_to_df(df, edges, g_undir):
    """Map each unrouted edge to a merged geometry of corresponding osmnx edges (routed on g_undir)

    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with information about edges
    edges: geopandas.geodataframe.GeoDataFrame
        The street network, in a projected coordinate reference system
    g_undir: networkx.graph undirected
        graph to use for routing

    Returns
    -------
    df: pandas.DataFrame
        Dataframe with added path nodes and path edges
    """
    paths = []
    for _, row in df.iterrows():
        paths.append(
            nx.shortest_path(
                G=g_undir,
                source=int(row.source),
                target=int(row.target),
                weight="length",
            )
        )
    df["path_nodes"] = paths
    df["path_edges"] = df.path_nodes.apply(lambda x: _get_correct_edgetuples(edges, x))
    return df


def create_gdf_with_geoms(df, edges):
    """Merge path geometries and create geodataframe

    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with path nodes and path edges
    edges: geopandas.GeoDataFrame
        The street network, in a projected coordinate reference system

    Returns
    -------
    gdf: geopandas.GeoDataFrame
        projected GeoDataFrame with path nodes and path edges and merged geometries
    """
    # Get geometry by merging all geoms from edge gdf
    try:
        df["geometry"] = df.path_edges.apply(lambda x: MultiLineString(list(edges.loc[x].geometry)))
    except KeyError as e:
        e.add_note("NOTE: For all edges between a pair of nodes u and v there must be one edge with key 0. It is possible that this issue caused the KeyError.")
        raise
    # Convert edges into a gdf
    gdf = gpd.GeoDataFrame(df, crs=edges.crs, geometry="geometry")
    # Merge multilinestring into linestring where possible (should be possible everywhere)
    gdf["geometry"] = gdf.line_merge()
    return gdf


def orientation_order(g_undir):
    """Calculate a graph's weighted orientation order phi, see [1]_

    Whether phi is weighted or unweighted does not matter much, but for the purpose of growing bike networks, weighted seems more appropriate.
    Note that the values here are lower than in the paper [1]_ for unknown reasons, also with the unweighted version.

    Parameters
    ----------
    g_undir : networkx.classes.multigraph.MultiGraph
        networkX street network, undirected, weighted with "length"

    Returns
    -------
    phi : float
        Weighted orientation order

    References
    ----------
    .. [1] G. Boeing, "Urban spatial order: Street network orientation, configuration, and entropy", Applied Network Science 4, 67 (2019)
    """
    Hw = ox.bearing.orientation_entropy(g_undir, weight="length")
    Hg = 1.386
    Hmax = 3.584
    phi = 1 - ((Hw-Hg)/(Hmax-Hg))**2
    return phi

def _get_weighted_distances(B, num_types):
    """Get weighted distances by edge attribute num_types

    The calculation follows [1]_, only without +1 in the numerator and with a small epsilon to prevent division by zero.

    Parameters
    ----------
    B : networkx.classes.multigraph.MultiGraph
        The routed, grown bicycle network graph, where edges have the attribute num_types. The numerical attribute "distance" must exist for all edges.
    num_types : str
        Name of the attribute to weight the distances

    Returns
    -------
    dist_weighted_by_types_dict : dict
        Dictionary where keys are the edges (tuples of node ids), and values are the weighted distances following [1]_

    References
    ----------
    .. [1] P. Folco, L. Gauvin, M. Tizzoni, M. Szell, "Data-driven micromobility network planning for demand and safety", Environment and planning B: Urban analytics and city science 50(8), 2087-2102 (2023)
    """

    num_types_dict = nx.get_edge_attributes(B, num_types)
    dist_dict = nx.get_edge_attributes(B, "distance")
    num_types_per_km_dict = {}

    for k,d in dist_dict.items():
        num_types_per_km_dict[k] = 1000*num_types_dict[k]/d
    max_nt = max(num_types_per_km_dict.values())

    dist_weighted_by_types_dict = {}
    for k,d in dist_dict.items():
        dist_weighted_by_types_dict[k] = d/(1+settings.import_data_impact*(num_types_per_km_dict[k]/(max_nt+1e-10))) 

    return dist_weighted_by_types_dict