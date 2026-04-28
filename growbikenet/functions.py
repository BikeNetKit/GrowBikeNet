import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx
from scipy.spatial import Delaunay
from shapely.prepared import prep
from shapely.geometry import Point


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


def get_correct_edgetuples(edge_gdf, nodelist):
    """
    helper function that maps a node list (output of nx.shortest_paths)
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
    seed_points = gpd.GeoDataFrame({"geometry": valid_points}, crs=edges.crs)

    # Rotate points back using the principal bearing
    seed_points.geometry = seed_points.geometry.rotate(
        -1 * principal_bearing, origin=(0, 0)
    )

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

    Note that the original paper [1]_ uses minimum weight triangulation, but Delaunay triangulation is much faster due to the Delaunay scipy function and gives in most cases identical results. Triangulation is calculated for the abstract network, but metrics (betweenness, closeness) are calculated for the routed network accounting for lengths.

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


def df_from_graph(A, method):
    """Create a dataframe from an input graph

    Parameters
    ----------
    A: networkx.graph
        Graph created from triangulation edge list
    method: str
        Method used to rank edges. Must be 'betweenness_centrality' (default), 'closeness_centrality', or 'all'. If 'all', will also add a random ranking.

    Returns
    -------
    df: pandas.DataFrame
        Dataframe with source and target information for each edge, as well as edge attributes as columns
    """

    if method == "all":
        attrs = {
            edge: {
                "betweenness_centrality": data.get("betweenness_centrality"),
                "closeness_centrality": data.get("closeness_centrality"),
                "geometry": data.get("geometry"),
            }
            for edge, data in A.edges.items()
        }
        df = pd.DataFrame.from_dict(
            attrs,
            orient="index",
            columns=["betweenness_centrality", "closeness_centrality", "geometry"],
        )
    else:
        attrs = {
            edge: {
                method: data.get(method),
                "geometry": data.get("geometry"),
            }
            for edge, data in A.edges.items()
        }
        df = pd.DataFrame.from_dict(attrs, orient="index", columns=[method, "geometry"])
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
        Method used to rank edges. Must be 'betweenness_centrality' (default), 'closeness_centrality', or 'all'. If 'all', will also add a random ranking.

    Results
    -------
    df: pandas.DataFrame
        Dataframe sorted by specified ranking method.
    """
    if method == "all":
        for m in ["betweenness_centrality", "closeness_centrality"]:
            df = df.sort_values(by=m, ascending=False)
            df.reset_index(drop=True, inplace=True)
            df["ordering_" + m] = (
                df.index
            )  # ranking is the order of appearance in the method's ranking
        df["ordering_random"] = np.random.permutation(np.arange(df.shape[0]))
    else:
        df = df.sort_values(by=method, ascending=False)
        df.reset_index(drop=True, inplace=True)
        df["ordering_" + method] = (
            df.index
        )  # ranking is the order of appearance in the method's ranking
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
                weight="length",
            )
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
    df["geometry"] = df.path_edges.apply(lambda x: edges.loc[x].geometry.union_all())
    # convert edges into a gdf
    gdf = gpd.GeoDataFrame(df, crs=edges.crs, geometry="geometry")
    # merge multilinestring into linestring where possible (should be possible everywhere)
    gdf["geometry"] = gdf.line_merge()
    return gdf
