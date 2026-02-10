import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx
from shapely.prepared import prep
from shapely.geometry import Point, LineString, MultiLineString
from itertools import combinations

# helper function to check whether newly to be added edge intersects with already added edges
def intersects_properly(geom1, geom2):
    '''
    for 2 shapely geometries, check whether they "properly intersect" (i.e. intersect but not touch, i.e. don't share endpoints)
    '''
    return geom1.intersects(geom2) and not geom1.touches(geom2)

def get_correct_edgetuples(edge_gdf, nodelist):
    '''
    helper function that maps a node list (output of nx.shortest_paths)
    to the correct set of edge tuples that can be used for INDEXING THE EDGE GDF
    '''
    edgelist_prelim = zip(nodelist, nodelist[1:])
    edgelist_final = []
    for edge_prelim in edgelist_prelim:
        if edge_prelim in edge_gdf.index:
            edgelist_final.append(edge_prelim)
        else:
            edgelist_final.append(tuple([edge_prelim[1], edge_prelim[0]]))
    return edgelist_final

# create seed points for greedy triangulation
def get_seed_points (edges, proj_crs, seed_point_spacing):
    # get convex hull around edge area
    hull = edges.union_all().convex_hull
    # get bounds of hull
    latmin, lonmin, latmax, lonmax = hull.bounds

    # https://stackoverflow.com/questions/66010964/fastest-way-to-produce-a-grid-of-points-that-fall-within-a-polygon-or-shape
    # populate hull bbox with evenly spaced seeding points
    points = []
    for lat in np.arange(latmin, latmax, seed_point_spacing):
        for lon in np.arange(lonmin, lonmax, seed_point_spacing):
            points.append(Point((round(lat, 4), round(lon, 4))))

    # keep only those seed points that are within the hull polygon
    prep_polygon = prep(hull)
    valid_points = []
    valid_points.extend(filter(prep_polygon.contains, points))

    # store seed points in gdf
    seed_points = gpd.GeoDataFrame(
        {"geometry": valid_points},
        crs=proj_crs
    )
    return seed_points

# snap generated seed_points to actual osm nodes
def snap_seed_points(seed_points, nodes):
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

# remove seed_points that are further than delta away from an actual osm node
def filter_seed_points(seed_points_snapped, seed_point_delta):
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

# create df with all potential edges in triangulation
def create_potential_triangulation(seed_points_snapped):
    # get list of potential edges, ordered by length
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

# filter edges that intersect with existing edges
def filter_triangulation(df):
    # iterate through all potential edges;
    # if they dont intersect with existing edges add to multilinestring

    current_edges = MultiLineString()
    edge_list = []

    for i, row in df.iterrows():
        new_edge = row.potential_edge
        pair = row.pair
        if not intersects_properly(current_edges, new_edge):
            current_edges = MultiLineString([linestring for linestring in current_edges.geoms] + [new_edge])
            edge_list.append(pair)
    return edge_list

# create a dataframe from an input graph
def df_from_graph(A, method):
    a_edges = pd.DataFrame.from_dict(
        nx.get_edge_attributes(
            G=A,
            name=method,
        ),
        orient="index",
        columns=[method]
    )
    a_edges["node_tuple"] = a_edges.index
    a_edges["source"] = [t[0] for t in a_edges.node_tuple]
    a_edges["target"] = [t[1] for t in a_edges.node_tuple]
    a_edges.drop(columns=["node_tuple"], inplace=True)
    return a_edges

# rank df by specified sorting metric
def rank_df(df, method):
    # rank by attribute/sorting metric
    a_edges = df.sort_values(by=method, ascending=False)
    a_edges.reset_index(drop=True, inplace=True)
    a_edges["rank"] = a_edges.index  # ranking is simply the order of appearance in the betweenness ranking
    return a_edges