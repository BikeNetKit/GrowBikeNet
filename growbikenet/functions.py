import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx
import osmnx as ox
from shapely.prepared import prep
from shapely.geometry import Point, LineString, MultiLineString
from itertools import combinations
from slugify import slugify


def intersects_properly(geom1, geom2):
    """
    helper function to check whether newly to be added edge intersects with already added edges
    for 2 shapely geometries, check whether they "properly intersect" (i.e. intersect but not touch, i.e. don't share endpoints)

    Parameters
    ----------
    geom1 : shapely geometry
        A shapely geometry, for example shapely.geometry.Point() or shapely.geometry.LineString()
    geom2 : shapely geometry
        A shapely geometry, for example shapely.geometry.Point() or shapely.geometry.LineString()

    Returns
    -------
    boolean
        Returns true if the two provided geometries intersect but do not touch
    """
    return geom1.intersects(geom2) and not geom1.touches(geom2)


def prepare_network(city_name, proj_crs, network_type='all', custom_filter=None):
    """Download and prepare a street network from OSM via OSMnx

    Downloads a network with a given network_type and custom_filter using ox.graph_from_place.
    Then, stores the undirected OSM data in gdfs and projects using proj_crs.

    Parameters
    ----------
    city_name : str
        Name of the city that the analysis should be performed on.
    proj_crs : str, default '3857'
        Coordinate reference system that is used to project osm data. Default is '3857' (WGS 84 / Pseudo-Mercator).
    network_type : {“all”, “all_public”, “bike”, “drive”, “drive_service”, “walk”} 
        What type of street network to retrieve if custom_filter is None.
    custom_filter : (str | list[str] | None)
        A custom ways filter to be used instead of the network_type presets

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
    if custom_filter:
        ox.settings.useful_tags_way.extend(custom_filter)
    g = ox.graph_from_place(
    city_name, network_type=network_type, custom_filter=custom_filter
    )
    g_undir = g.to_undirected().copy() # convert to undirected (dropping OSMnx keys!)

    # Export osmnx data to gdfs
    nodes, edges = nx_to_nodes_edges(g_undir, proj_crs)
    return nodes, edges, g_undir

def nx_to_nodes_edges(G, proj_crs='3857'):
    """Get nodes and projected edges from networkX graph

    Parameters
    ----------
    G : networkx.classes.multigraph.MultiGraph
        networkX graph, undirected
    proj_crs : str, default '3857'
        Coordinate reference system that is used to project osm data. Default is '3857' (WGS 84 / Pseudo-Mercator).

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
    
    # Replace after dropping edges with key = 1
    edges = edges.loc[:,:,0].copy()
    # This also means we are dropping the "key" level from edge index (u,v,key becomes: u,v)

    # Project geometries of nodes, edges, seed points
    edges = edges.to_crs(proj_crs)
    nodes = nodes.to_crs(proj_crs)

    # Add osm ID as column to node gdf
    nodes["osmid"] = nodes.index
    return nodes, edges
    
def get_correct_edgetuples(edge_gdf, nodelist):
    """
    Helper function that maps a node list (output of nx.shortest_paths)
    to the correct set of edge tuples that can be used for INDEXING THE EDGE GDF

    Parameters
    ----------
    edge_gdf: geopandas.geodataframe.GeoDataFrame
        The street network, in a projected coordinate reference system
    nodelist: list
        A list of nodes that make up source and targets of edges

    Returns
    -------
    edgelist_final: list
        List of edge tuples that can be used for INDEXING THE EDGE GDF
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
    while len(node_current)>0 and len(nodes_exnw)>1:
        # Find all too close nodes to the current nodes
        nodes_too_close = nodes_exnw.loc[(nodes_exnw.geometry.distance(Point(node_current.iloc[0].geometry)) <= existing_network_spacing)]
        nodes_too_close = nodes_too_close.iloc[:, :-1] # osmid is there twice now (once in the end), so it needs to be dropped
        
        # Delete the nodes that are too close to nodes_exnw
        nodes_exnw = nodes_exnw.overlay(nodes_too_close, how='difference')
        
        # Add current node to seed_points_exnw
        seed_points_exnw = pd.concat([seed_points_exnw, node_current], ignore_index=True)
        
        # Find the node in nodes_exnw that is closest to the existing seed points
        node_current = seed_points_exnw.sjoin_nearest(nodes_exnw, how="inner") 
        node_current = nodes_exnw[nodes_exnw.osmid == node_current["osmid_right"].values[0]]
    
    return seed_points_exnw

def get_grid_seed_points(edges, seed_point_spacing, principal_bearing):
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

    Returns
    -------
    seed_points: geopandas.geodataframe.GeoDataFrame
        Seed points, rotated by principal bearing, to be snapped, in the same projected coordinate reference system as edges
    """

    # Rotate edges counter to the principal bearing
    edges_temp = edges.copy()
    edges_temp.geometry = edges_temp.geometry.rotate(principal_bearing, origin=(0, 0))

    # Create grid
    # get convex hull around edge area
    hull = edges_temp.union_all().convex_hull
    # get bounds of hull
    xmin, ymin, xmax, ymax = hull.bounds

    # https://stackoverflow.com/questions/66010964/fastest-way-to-produce-a-grid-of-points-that-fall-within-a-polygon-or-shape
    # Populate hull bbox with evenly spaced seeding points
    points = []
    for x in np.arange(xmin, xmax, seed_point_spacing):
        for y in np.arange(ymin, ymax, seed_point_spacing):
            points.append(Point((round(x, 4), round(y, 4))))

    # Keep only those seed points that are within the hull polygon
    prep_polygon = prep(hull)
    valid_points = []
    valid_points.extend(filter(prep_polygon.contains, points))

    # store seed points in gdf
    seed_points = gpd.GeoDataFrame(
        {"geometry": valid_points},
        crs=edges.crs
    )

    # Rotate points back using the principal bearing
    seed_points.geometry = seed_points.geometry.rotate(-1 * principal_bearing, origin=(0, 0))

    return seed_points


def get_principal_bearing(G):
    """Determine the most common (principal) bearing, for the best grid orientation.

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

    bearingbins = 72  # number of bins to determine bearing. e.g. 72 will create 5 degrees bins

    bearings = {}
    # weight bearings by length (meters)
    city_bearings = []
    for u, v, k, d in G.edges(keys=True, data=True):
        try:
            city_bearings.extend([d['bearing']] * int(d['length']))
        except:  # Bearings cannot be calculated in rare edge cases
            pass
    b = pd.Series(city_bearings)
    bearings = pd.concat([b, b.map(reverse_bearing)]).reset_index(drop='True')
    bins = np.arange(bearingbins + 1) * 360 / bearingbins
    count = count_and_merge(bearingbins, bearings)
    principal_bearing = bins[np.where(count == max(count))][0]

    return principal_bearing


def reverse_bearing(x):
    """Reverse bearing.

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
    """
    snap generated seed_points to actual osm nodes
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
    # query nearest OSM nodes with sindex
    q = nodes.sindex.nearest(seed_points.geometry)
    seed_points["osmid"] = None
    seed_points.iloc[q[0], -1] = list(nodes.iloc[q[1]]["osmid"])

    # create a subset of OSM nodes - only those that seed points are snapped to
    nodes_subset = nodes.loc[
        nodes.osmid.isin(seed_points.osmid)
    ].copy().reset_index(drop=True)

    # merge seed points gdf (gives us the generated seed point location, "geometry_generated")
    # with nodes subset gdf (gives us all other columns)
    # (we need the geometry_generated column only for filtering by distance)
    seed_points_snapped = pd.merge(
        left=seed_points,
        right=nodes_subset,
        how="inner",
        on="osmid",
        suffixes=["_generated", "_osm"]
    )
    return seed_points_snapped


def filter_seed_points(seed_points_snapped, seed_point_delta):
    """
    remove seed_points that are further than delta away from an actual osm node
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
    # define our boolean distance_condition filter:
    # snapped seed points must be not more than seed_point_delta away
    # from their OSM nodes
    distance_condition = seed_points_snapped.geometry_generated.distance(
        seed_points_snapped.geometry_osm) <= seed_point_delta

    # filter seed_points_snapped df by distance condition
    seed_points_snapped = seed_points_snapped[distance_condition].reset_index(drop=True)
    seed_points_snapped = seed_points_snapped[
        ["osmid", "geometry_osm"]
    ]  # drop not-needed columns
    # rename geometry column
    seed_points_snapped = seed_points_snapped.rename(
        columns={"geometry_osm": "geometry"})

    # set "geometry" as geometry column
    seed_points_snapped = seed_points_snapped.set_geometry("geometry")
    # set osmid as *index* of this df
    seed_points_snapped = seed_points_snapped.set_index("osmid")
    seed_points_snapped["osmid"] = seed_points_snapped.index
    return seed_points_snapped


def create_potential_triangulation(seed_points_snapped):
    """
    create df with all potential edges in triangulation, ordered by length
    Parameters
    ----------
    seed_points_snapped: geopandas.geodataframe.GeoDataFrame
        seed points with osmid and corresponding point geometry

    Returns
    -------
    df: pandas.DataFrame
        Dataframe with egde pairs, edge geometries and distance of potential triangulation
    """
    pairs = []
    potential_edges = []
    distances = []

    for pair in combinations(seed_points_snapped["osmid"], 2):
        edge = LineString(seed_points_snapped.loc[list(pair)].geometry)

        pairs.append(pair)
        potential_edges.append(edge)
        distances.append(edge.length)

    df = pd.DataFrame(
        {
            "pair": pairs,
            "potential_edge": potential_edges,
            "dist": distances
        }
    )

    df = df.sort_values(by="dist", ascending=True).reset_index(drop=True)
    df = df[df["dist"] > 0].reset_index(drop=True)  # only keep distances > 0
    return df


def filter_triangulation(df):
    """
    filter edges that intersect with existing edges
    iterate through all potential edges; if they do not intersect with existing edges add to multilinestring
    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with edge pairs, edge geometries and distance of potential triangulation

    Returns
    -------
    edge_list: list
        List of edge pairs that are part of the final triangulation
    """
    current_edges = MultiLineString()
    edge_list = []

    for i, row in df.iterrows():
        new_edge = row.potential_edge
        pair = row.pair
        if not intersects_properly(current_edges, new_edge):
            current_edges = MultiLineString([linestring for linestring in current_edges.geoms] + [new_edge])
            edge_list.append(pair)
    return edge_list


def df_from_graph(A, method):
    """
    create a dataframe from an input graph
    Parameters
    ----------
    A: networkx.graph
        graph created from triangulation edge list
    method: string
        Method choosen by user for sorting, for example betweenness centrality

    Returns
    -------
    df: pandas.DataFrame
        Dataframe with source and target information for each edge, as well as edge attributes as columns
    """
    df = pd.DataFrame.from_dict(
        nx.get_edge_attributes(
            G=A,
            name=method,
        ),
        orient="index",
        columns=[method]
    )
    df["node_tuple"] = df.index
    df["source"] = [t[0] for t in df.node_tuple]
    df["target"] = [t[1] for t in df.node_tuple]
    df.drop(columns=["node_tuple"], inplace=True)
    return df


def rank_df(df, method):
    """
    rank df by specified sorting method
    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with source and target information for each edge, as well as edge attributes as columns
    method: string
        Method choosen by user for sorting, for example betweenness centrality

    Results
    -------
    df: pandas.DataFrame
        Dataframe sorted by specified sorting method
    """
    df = df.sort_values(by=method, ascending=False)
    df.reset_index(drop=True, inplace=True)
    df["ordering"] = df.index  # ranking is simply the order of appearance in the betweenness ranking
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


def add_path_to_df(df, edges, g):
    """
    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe with information about edges
    edges: geopandas.geodataframe.GeoDataFrame
        The street network, in a projected coordinate reference system
    g: networkx.graph undirected
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
                G=g,  # !! use undirected graph here
                source=int(row.source),
                target=int(row.target),
                weight='length')
        )
    df["path_nodes"] = paths
    df["path_edges"] = df.path_nodes.apply(lambda x: get_correct_edgetuples(edges, x))
    return df


def create_gdf_with_geoms(df, edges):
    """
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
    # get geometry by merging all geoms from edge gdf
    df["geometry"] = df.path_edges.apply(
        lambda x: edges.loc[x].geometry.union_all()
    )
    # convert edges into a gdf
    gdf = gpd.GeoDataFrame(df, crs=edges.crs, geometry="geometry")
    # merge multilinestring into linestring where possible (should be possible everywhere)
    gdf["geometry"] = gdf.line_merge()
    return gdf
