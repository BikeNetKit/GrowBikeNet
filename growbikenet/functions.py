"""Utility functions for growbikenet."""

import os
import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx
import osmnx as ox
from scipy.spatial import Delaunay
from shapely.prepared import prep
from shapely.geometry import Point, MultiLineString
from shapely.affinity import rotate
from tqdm import tqdm


def validate_parameters(
        city_name,
        crs_projected,
        ranking,
        seed_point_type,
        seed_point_grid_spacing,
        seed_point_delta,
        seed_point_linking,
        existing_network_spacing,
        export_data,
        export_file_format,
        export_data_slug,
        export_plots,
        export_video,
        allow_edge_overlaps,
        city_boundary_file,
        street_network_file,
        seed_points_file,
        seed_point_tags,
        PRESET_TAGS
    ):
    """ Check if user parameter input is valid. If not, raise an exception or warning
    
    Parameters
    ----------
    Same as growbikenet.growbikenet()
    Additionally:
    PRESET_TAGS : dict
        Dictionary of preset seed point tags.

    Returns
    -------
    True
    """

    if type(city_name) is not str:
        raise TypeError("city_name must be a string")
    if type(crs_projected) is not str:
        raise TypeError("crs_projected must be a string")
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
    if seed_point_type == 'file' and type(seed_points_file) is None:
        raise ValueError("With seed_point_type 'file', a seed_points_file must be provided")
    if seed_point_type == 'tags' and type(seed_points_file) is None:
        raise ValueError("With seed_point_type 'tags', seed_point_tags must be provided")
    if type(seed_point_delta) is not int and seed_point_delta != 'auto':
        raise TypeError("seed_point_delta must be 'auto' or an integer")
    if type(seed_point_delta) is int and seed_point_delta <= 0:
        raise ValueError("seed_point_delta must be a positive integer")
    if seed_point_linking not in ['auto', 'triangulate_delaunay', 'quadrangulate']:    
        raise ValueError("seed_point_linking must be 'auto' or 'triangulate_delaunay' or 'quadrangulate'")
    if seed_point_linking == 'quadrangulate' and (seed_point_type != 'grid_square' or existing_network_spacing is not None):
        raise ValueError("With seed_point_linking 'quadrangulate', seed_point_type must be set to 'grid_square' and existing_network_spacing must be set to None")
    if type(existing_network_spacing) is not int and existing_network_spacing is not None:
        raise TypeError("existing_network_spacing must be None or a positive integer")
    if type(existing_network_spacing) is int and existing_network_spacing <= 0:
        raise ValueError("existing_network_spacing must be None or a positive integer")
    if type(existing_network_spacing) is int and seed_point_grid_spacing is int and existing_network_spacing >= seed_point_grid_spacing:
        warnings.warn("existing_network_spacing is recommended to be smaller than seed_point_grid_spacing, ideally around a third, to ensure that the existing bicycle network is built first.")
    if type(export_data) is not bool:
        raise TypeError("export_data must be a boolean")
    if export_data_slug is not None and type(export_data_slug) is not str:
        raise TypeError("export_data_slug must be None or a string")
    if type(export_data_slug) is str and (
        len(export_data_slug) < 1 or len(slugify(export_data_slug)) < 1
    ):
        raise ValueError(
            "export_data_slug must contain at least one non-special character"
        )
    if export_file_format != "geojson" and export_file_format != "gpkg":
        raise ValueError("export_file_format must be 'geojson' or 'gpkg'")
    if type(export_plots) is not bool:
        raise TypeError("export_plots must be a boolean")
    if type(export_video) is not bool:
        raise TypeError("export_video must be a boolean")
    if city_boundary_file is not None and type(city_boundary_file) is not str:
        raise TypeError("city_boundary_file must be None or a string")
    if type(city_boundary_file) is str and not os.path.isfile(city_boundary_file):
        raise FileNotFoundError("city_boundary_file not found")
    if city_boundary_file is not None and street_network_file is not None:
        raise ValueError("city_boundary_file and street_network_file cannot both be set")
    if type(street_network_file) is str and not os.path.isfile(street_network_file):
        raise FileNotFoundError("street_network_file not found")
    if type(seed_points_file) is str and not os.path.isfile(seed_points_file):
        raise FileNotFoundError("seed_points_file not found")
    return True


def resolve_auto_parameters(
        seed_point_type,
        seed_point_grid_spacing,
        seed_point_delta,
        seed_point_linking,
        existing_network_spacing,
        phi,
        PHI_LIMITS
    ):
    """Resolve auto parameters and parameter inconsistencies
    
    Parameters
    ----------
    seed_point_* and existing_network_spacing from growbikenet.growbikenet()
    
    Additionally:
    phi : float
        Weighted orientation order
    PHI_LIMITS : list
        Limits for phi between seed point type categories

    Returns
    -------
    seed_point_* and existing_network_spacing from growbikenet.growbikenet()
    """
    
    if seed_point_type == 'auto':
        if phi>PHI_LIMITS[1]: # Case grid. For example, Barcelona, Manhattan
            seed_point_type = 'grid_square'
            if seed_point_linking == 'auto':
                seed_point_linking = 'quadrangulate'
                if existing_network_spacing is not None: # Case incompatible with existing_network_spacing not None 
                    existing_network_spacing = None
                    warnings.warn("Automatically chosen seed_point_linking 'quadrangulate' is incompatible with existing_network_spacing not set to None. Changing existing_network_spacing to None.")
        elif phi<=PHI_LIMITS[1] and phi>PHI_LIMITS[0]: # Case contains some grid elements. For example, Prague, Budapest
            seed_point_type = 'grid_square'
            if seed_point_linking == 'auto':
                seed_point_linking = 'triangulate_delaunay'
        elif phi<=PHI_LIMITS[0]: # Case negligible grid elements. For example, Berlin, London
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
                if phi>PHI_LIMITS[1]: # Case grid. For example, Barcelona, Manhattan
                    seed_point_linking = 'quadrangulate'
                    if existing_network_spacing is not None: # Case incompatible with existing_network_spacing not None 
                        existing_network_spacing = None
                        warnings.warn("Automatically chosen seed_point_linking 'quadrangulate' is incompatible with existing_network_spacing not set to None. Changing existing_network_spacing to None.")
                elif phi<=PHI_LIMITS[1] and phi>PHI_LIMITS[0]: # Case contains some grid elements. For example, Prague, Budapest
                    seed_point_linking = 'triangulate_delaunay'

    if seed_point_grid_spacing == 'auto': 
        # These values ensure that any point in the city is always within b=500m of the network (if seed points snap perfectly).
        # In comments, general equations for arbitrary buffer distance b
        if seed_point_type == 'grid_square' and seed_point_linking == 'triangulate_delaunay':
            seed_point_grid_spacing = 1707 # a=2b/(2-sqrt(2))
        elif seed_point_type == 'grid_square' and seed_point_linking == 'quadrangulate':
            seed_point_grid_spacing = 1000 # a=2b
        elif seed_point_type == 'grid_triangle':
            seed_point_grid_spacing = 1154 # h/2=b=a*sqrt(3)/4 -> a=4b/sqrt(3)
        else:
            seed_point_grid_spacing = 1707

    if seed_point_delta == 'auto':
        seed_point_delta = int(np.ceil(seed_point_grid_spacing/4))

    return seed_point_type, seed_point_grid_spacing, seed_point_delta, seed_point_linking, existing_network_spacing

def import_network(street_network_file, crs_projected):
    """Import and project a street network from gpkg file

    Parameters
    ----------
    street_network_file : str
        The street network will be loaded from this file. Must be a gpkg file in unprojected crs EPSG:4326 with layers nodes and edges, with the structure that a osmnx street network g has after saved its undirected version via ox.io.save_graph_geopackage(). For example:
        >>> g = ox.graph_from_place("Barcelona", network_type='all_public')
        >>> ox.io.save_graph_geopackage(g.to_undirected(), "Barcelona_streets.gpkg")
    crs_projected : str
        Coordinate reference system that is used to project osm data.

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

    nodes = gpd.read_file(street_network_file, layer='nodes')
    edges = gpd.read_file(street_network_file, layer='edges')

    # Set indices as required by osmnx.convert.graph_from_gdfs
    # See: https://osmnx.readthedocs.io/en/stable/user-reference.html#osmnx.utils_graph.graph_from_gdfs
    nodes = nodes.set_index(['osmid'])
    edges = edges.set_index(['u', 'v', 'key'])

    g = ox.convert.graph_from_gdfs(nodes, edges)
    g_undir = g.to_undirected().copy() # convert to undirected (dropping OSMnx keys!)

    city_boundary_gdf = gpd.GeoDataFrame(gpd.GeoSeries(nodes.union_all().convex_hull), geometry=0, crs=nodes.crs) # We do this before the projection of nodes below
    # To do: To be super-correct, the hull should be buffered by seed_point_delta (in degrees due to being unprojected)

    nodes, edges = prepare_nodes_edges(nodes, edges, crs_projected)

    return nodes, edges, g_undir, city_boundary_gdf


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


def prepare_nodes_edges(nodes, edges, crs_projected):
    """Project and prepare nodes and edges for further use
    
    Parameters
    ----------
    nodes : geopandas.geodataframe.GeoDataFrame
        OSM nodes, unprojected
    edges : geopandas.geodataframe.GeoDataFrame
        OSM edges, unprojected
    crs_projected : str
        Coordinate reference system that is used to project osm data.
        
    Returns
    -------
    nodes : geopandas.geodataframe.GeoDataFrame
        OSM nodes, projected, osmid is index
    edges : geopandas.geodataframe.GeoDataFrame
        OSM edges, projected
    """

    # Replace after dropping edges with key = 1
    edges = edges.loc[:,:,0].copy()
    # This also means we are dropping the "key" level from edge index (u,v,key becomes: u,v)

    # Project geometries of nodes, edges
    edges = edges.to_crs(crs_projected)
    nodes = nodes.to_crs(crs_projected)

    # Add osm ID as column to node gdf
    nodes["osmid"] = nodes.index
    return nodes, edges


def download_network(city_name, crs_projected, network_type='all_public', custom_filter=None, retain_all=True, city_boundary_geometry=None):
    """Download and prepare a street network from OSM via OSMnx

    Downloads a network with a given network_type and custom_filter using ox.graph_from_place.
    Then, stores the undirected OSM data in gdfs and projects using crs_projected.

    Parameters
    ----------
    city_name : str
        Name of the city that the analysis should be performed on. Overruled (for data fetching) if city_boundary_geometry is set.
    crs_projected : str
        Coordinate reference system that is used to project osm data.
    network_type : {“all”, “all_public”, “bike”, “drive”, “drive_service”, “walk”} 
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
        city_name, network_type=network_type, custom_filter=custom_filter, retain_all=retain_all
        )
    else:
        g = ox.graph_from_polygon(
        city_boundary_geometry, network_type=network_type, custom_filter=custom_filter, retain_all=retain_all
        )

    g_undir = g.to_undirected().copy() # convert to undirected (dropping OSMnx keys!)

    # Export osmnx data to gdfs
    nodes, edges = nx_to_nodes_edges(g_undir, crs_projected)
    return nodes, edges, g_undir


def nx_to_nodes_edges(G, crs_projected):
    """Get nodes and projected edges from networkX graph
    
    Parameters
    ----------
    G : networkx.classes.multigraph.MultiGraph
        networkX graph, undirected
    crs_projected : str
        Coordinate reference system that is used to project osm data.
        
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

    nodes, edges = prepare_nodes_edges(nodes, edges, crs_projected)
    return nodes, edges
    

def get_correct_edgetuples(edge_gdf, nodelist):
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


def get_existing_network_seed_points(nodes_exnw, existing_network_spacing):
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


def update_with_existing_bike_network(city_name, crs_projected, g_undir, city_boundary_geometry=None):
    """Update street network with existing bike network

    Downloads a network of protected bike infrastructure from OSM (retaining all connected components) and merges it to a given street network graph g_undir.
    
    Parameters
    ----------
    city_name : str
        Name of the city that the analysis should be performed on. Overruled (for data fetching) if city_boundary_geometry is set.
    crs_projected : str
        Coordinate reference system that is used to project osm data.
    g_undir : networkx.classes.multigraph.MultiGraph
        Street network networkX graph, undirected
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
    cf = ['["cycleway"~"track"]',
          '["highway"~"cycleway"]',
          '["highway"~"path"]["bicycle"~"designated"]',
          '["cycleway:right"~"track"]',
          '["cycleway:left"~"track"]',
          '["cycleway:both"~"track"]',
          '["cycleway:right"~"opposite_track"]', # deprecated, but could still exist
          '["cycleway:left"~"opposite_track"]', # deprecated, but could still exist
          '["cycleway:both"~"opposite_track"]', # deprecated, but could still exist
          '["cyclestreet"]',
          '["highway"~"living_street"]'
        ]
    for custom_tag in ["cycleway", "bicycle", "cycleway:right", "cycleway:left", "cycleway:both", "cyclestreet"]:
        if custom_tag not in ox.settings.useful_tags_way:
            ox.settings.useful_tags_way.extend(custom_tag)
    # Fetch protected bike network data from osmnx
    # Due to retain_all=True, this fetches all the connected components
    nodes_exnw, edges_exnw, g_undir_exnw = download_network(city_name, crs_projected, custom_filter=cf, retain_all=True, city_boundary_geometry=city_boundary_geometry)
    g_undir = nx.compose(g_undir_exnw, g_undir) # Merge to be sure we have everything from both

    # Now we could have some leftover bike infra that is disconnected from the street network and thus not routable.
    # We delete those parts next:
    # Take largest connected component lcc of the merged network
    lcc = max(nx.connected_components(g_undir), key=len)
    g_undir = g_undir.subgraph(lcc).copy() 
    # Restrict nodes and edges of the existing bike net to this lcc
    valid_node_osmids = g_undir.nodes()
    nodes_exnw = nodes_exnw[nodes_exnw['osmid'].isin(valid_node_osmids)]
    # edges_exnw has a MultiIndex ('u','v'), so we must use get_level_values, see https://stackoverflow.com/a/18835121
    edges_exnw = edges_exnw.iloc[edges_exnw.index.get_level_values('u').isin(valid_node_osmids)]
    edges_exnw = edges_exnw.iloc[edges_exnw.index.get_level_values('v').isin(valid_node_osmids)]
    nodes, edges = nx_to_nodes_edges(g_undir, crs_projected)

    return nodes, edges, g_undir, nodes_exnw, edges_exnw


def update_seed_points_with_existing_bike_network(seed_points_snapped, nodes_exnw, existing_network_spacing, crs_projected):
    """Update seed points with existing bike network

    Updates given snapped seed points by incorporating seed points from an existing bike network.
    
    Parameters
    ----------
    seed_points_snapped : geopandas.geodataframe.GeoDataFrame
        Snapped seed points on the street network, constructed with seed_point_grid_spacing
    nodes_exnw : geopandas.geodataframe.GeoDataFrame
        Nodes of the existing bike network
    existing_network_spacing : int
        Positive integer denoting spacing between seed points, in meters, only on the existing bicycle network.
    crs_projected : str
        Coordinate reference system that is used to project osm data.

    Returns
    -------
    seed_points_snapped : geopandas.geodataframe.GeoDataFrame
        Snapped seed points incorporating both street grid and existing bike network
    """

    # If the existing bicycle network is used, create extra seed points on it. They are by construction already snapped.
    seed_points_exnw = get_existing_network_seed_points(nodes_exnw, existing_network_spacing)
    seed_points_exnw.to_crs(crs_projected, inplace=True)

    # Afterwards, drop all previously determined seed points (grid or rail) that are now too close to these extra points.
    buffer_seed_points_exnw = gpd.GeoDataFrame(seed_points_exnw.buffer(existing_network_spacing/2)) # To do: Think more about this factor
    buffer_seed_points_exnw = buffer_seed_points_exnw.rename(columns={0:'geometry'}).set_geometry('geometry') # https://gis.stackexchange.com/questions/266098/how-to-convert-a-geoseries-to-a-geodataframe-with-geopandas
    buffer_seed_points_exnw.to_crs(crs_projected, inplace=True)

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


def get_grid_seed_points(edges, seed_point_spacing, principal_bearing, seed_point_type='grid_square'):
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


def prepare_seed_points(seed_points, crs_projected):
    """Project and prepare seed points for further use
    
    Parameters
    ----------
    seed_points: geopandas.geodataframe.GeoDataFrame
        Unprojected seed points
    crs_projected : str
        Coordinate reference system that is used to project the seed points.
        
    Returns
    -------
    seed_points: geopandas.geodataframe.GeoDataFrame
        Projected and prepared seed points.
    """
    seed_points = seed_points[seed_points["geometry"].type == "Point"]
    seed_points.to_crs(crs_projected, inplace=True)
    # To do optional: merge closeby seed points
    return seed_points


def get_tags_seed_points(city_name, crs_projected, tags, city_boundary_geometry=None):
    """Get tags seed points for a city

    Parameters
    ----------
    city_name : str
        Name of the city that the analysis should be performed on. This is the query string used to fetch the data from nominatim. Overruled (for data fetching) if city_boundary_geometry is set.
    crs_projected : str
        Coordinate reference system that is used to project osm data. Default is '3857' (WGS 84 / Pseudo-Mercator). If this web mercator projection is not needed, then for Europe '3035' (LAEA) and globally '54035' (Equal Earth) is better.
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
            city_name, tags
        )
    seed_points = prepare_seed_points(seed_points, crs_projected)
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

    bearingbins = (
        72  # number of bins to determine bearing. e.g. 72 will create 5 degrees bins
    )

    bearings = {}
    # weight bearings by length (meters)
    city_bearings = []
    for u, v, k, d in G.edges(keys=True, data=True):
        try:
            city_bearings.extend([d["bearing"]] * int(d["length"]))
        except:  # noqa (To do: make specific and remove noqa)
            pass  # Bearings cannot be calculated in rare edge cases.
    b = pd.Series(city_bearings)
    bearings = pd.concat([b, b.map(reverse_bearing)]).reset_index(drop="True")
    bins = np.arange(bearingbins + 1) * 360 / bearingbins
    count = count_and_merge(bearingbins, bearings)
    principal_bearing = bins[np.where(count == max(count))][0]

    return principal_bearing


def reverse_bearing(x):
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


def count_and_merge(n, bearings):
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


def snap_seed_points(seed_points, nodes):
    """Snap generated seed_points to actual osm nodes

    Parameters
    ----------
    seed_points: geopandas.geodataframe.GeoDataFrame
        Seed points that were created within city area, to be snapped to actual osm nodes
    nodes: geopandas.geodataframe.GeoDataFrame
        actual osm nodes, downloaded from osmnx

    Returns
    -------
    seed_points_snapped: geopandas.geodataframe.GeoDataFrame
        seed_points with additional information about geometries of osm nodes that seed nodes were snapped to

    """
    # Ensure same CRS
    if seed_points.crs != nodes.crs:
        seed_points = seed_points.to_crs(nodes.crs)

    # Find nearest nodes (returns indices)
    idx_seed, idx_nodes = nodes.sindex.nearest(seed_points.geometry, return_all=False)

    # Assign osmid safely
    seed_points = seed_points.copy()
    seed_points["osmid"] = nodes.iloc[idx_nodes]["osmid"].values

    # Keep original geometry
    seed_points = seed_points.rename(columns={"geometry": "geometry_generated"})

    # Attach node geometry + attributes
    nodes_subset = nodes[["osmid", "geometry"]].rename(
        columns={"geometry": "geometry_osm"}
    )

    seed_points = seed_points.reset_index(drop=True)
    nodes_subset = nodes_subset.reset_index(drop=True)

    seed_points_snapped = seed_points.merge(nodes_subset, on="osmid", how="left")

    seed_points_snapped.set_geometry("geometry_osm")

    return seed_points_snapped


def filter_seed_points(seed_points_snapped, seed_point_delta):
    """Remove seed_points that are further than delta away from an actual osm node

    Parameters
    ----------
    seed_points_snapped: geopandas.geodataframe.GeoDataFrame
        seed_points with additional information about geometries of osm nodes that seed nodes were snapped to
    seed_point_delta: int
        maximum distance a seed_point may be removed from an actual osm node

    Returns
    -------
    seed_points_snapped: geopandas.geodataframe.GeoDataFrame
        seed_points within delta away from an actual osm node, only columns are osmid and the associated osm geometry
    """
    gdf = seed_points_snapped.copy()

    # Compute distance
    gdf["snap_dist"] = gdf.geometry_generated.distance(gdf.geometry_osm)

    # Filter by threshold
    gdf = gdf[gdf["snap_dist"] <= seed_point_delta].copy()

    # Drop duplicates: one row per osmid
    gdf = gdf.sort_values("snap_dist").drop_duplicates("osmid")

    # Keep only node geometry
    gdf = gdf[["osmid", "geometry_osm"]].rename(columns={"geometry_osm": "geometry"})

    # Set geometry + index
    gdf = gdf.set_geometry("geometry")
    gdf = gdf.set_index("osmid", drop=False)

    seed_points_snapped = gdf.copy()

    return seed_points_snapped


def create_delaunay_edges(nodes_gdf):
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


def remove_edge_overlaps(edges_in):
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


def rank_df(df, method):
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
    df["path_edges"] = df.path_nodes.apply(lambda x: get_correct_edgetuples(edges, x))
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
    df["geometry"] = df.path_edges.apply(lambda x: edges.loc[x].geometry.union_all())
    # Convert edges into a gdf
    gdf = gpd.GeoDataFrame(df, crs=edges.crs, geometry="geometry")
    # Merge multilinestring into linestring where possible (should be possible everywhere)
    gdf["geometry"] = gdf.line_merge()
    return gdf
