import pytest
import osmnx as ox
import pandas as pd
import geopandas as gpd
import ast
from pandas.testing import assert_frame_equal
from growbikenet.functions import (
    get_principal_bearing,
    get_grid_seed_points,
    filter_seed_points,
    rank_df,
    # intersects_properly,
    remove_edge_overlaps,
    add_trip_data_to_net
)
from shapely.geometry import Point, LineString, MultiLineString
import networkx as nx


# @pytest.fixture
# def geom_1():
#     linestring = LineString([(0, 0), (1, 1), (2, 2)])
#     return linestring


# @pytest.fixture
# def geom_2():
#     linestring = LineString([(3, 3), (4, 4), (5, 5)])
#     return linestring


# def test_intersects_properly(geom_1, geom_2):
#     assert intersects_properly(geom_1, geom_2) is False


@pytest.fixture
def test_data_rank(method):
    df = pd.DataFrame((6, 2, 4), columns=[method])
    return df


@pytest.fixture
def validation_data_rank(method):
    ranked_df = pd.DataFrame(
        ([6, 0], [4, 1], [2, 2]), columns=[method, "rank"]
    )
    return ranked_df


@pytest.fixture
def method():
    return "betweenness_centrality"


def test_rank_df(test_data_rank, method, validation_data_rank):
    assert_frame_equal(
        rank_df(test_data_rank, method),
        validation_data_rank,
        check_dtype=False,
    )


@pytest.fixture
def seed_point_delta():
    return 500


@pytest.fixture
def snapped_seed_points():
    d = {
        "osmid": ["1", "2", "3"],
        "geometry_generated": [Point(1000, 1000), Point(2000, 2000), Point(3000, 3000)],
    }
    gdf = gpd.GeoDataFrame(d, geometry="geometry_generated", crs="EPSG:3857")
    gdf["geometry_osm"] = gpd.GeoSeries(
        [Point(1001, 1001), Point(10000, 10000), Point(3001, 3001)], crs="EPSG:3857"
    )
    return gdf


@pytest.fixture
def filtered_seed_points():
    d = {"osmid": ["1", "3"], "geometry": [Point(1001, 1001), Point(3001, 3001)]}
    gdf = gpd.GeoDataFrame(d, geometry="geometry", crs="EPSG:3857")
    gdf = gdf.set_index("osmid")
    gdf["osmid"] = gdf.index
    gdf = gdf.iloc[:, [1, 0]]
    return gdf


def test_filter_seed_points(
    snapped_seed_points, filtered_seed_points, seed_point_delta
):
    assert_frame_equal(
        filter_seed_points(snapped_seed_points, seed_point_delta),
        filtered_seed_points,
        check_dtype=False,
    )


@pytest.fixture
def validation_streets():
    streets_nodes = gpd.read_file(
        "./tests/test_data/oelde_streets.gpkg", layer="nodes"
    ).set_index("osmid")
    streets_edges = gpd.read_file(
        "./tests/test_data/oelde_streets.gpkg", layer="edges"
    ).set_index(["u", "v", "key"])
    streets = ox.convert.graph_from_gdfs(streets_nodes, streets_edges)
    return streets


def test_get_principal_bearing(validation_streets):
    assert get_principal_bearing(validation_streets) == 65.0


@pytest.fixture
def validation_grid():
    grid = gpd.read_file("./tests/test_data/oelde_grid.gpkg")
    return grid


def test_get_grid_seed_points(validation_grid, validation_streets):
    edges = ox.convert.graph_to_gdfs(
        validation_streets,
        nodes=False,
        edges=True,
        node_geometry=False,
        fill_edge_geometry=False,
    )
    validation_grid.equals(get_grid_seed_points(edges, 1707, 65.0))


@pytest.fixture
def ordered_edges():
    d = {"geometry": [
    MultiLineString([((1,4), (2,4)), ((2,2), (3,2)), ((4,2), (6,2))]), # existing bike network
    LineString([(1,2), (3,2)]),
    LineString([(5,2), (7,2)]),
    LineString([(5,1), (5,2), (6,2), (6,4)]),
    LineString([(4,2), (7,2)]),
    LineString([(3,4), (4,4)])
     ]}
    gdf = gpd.GeoDataFrame(d, geometry="geometry", crs="EPSG:3857")
    return gdf

@pytest.fixture
def ordered_edges_without_overlaps():
    d = {"geometry": [
    MultiLineString([((1,4), (2,4)), ((2,2), (3,2)), ((4,2), (6,2))]), # existing bike network
    LineString([(1,2), (2,2)]),
    LineString([(6,2), (7,2)]),
    MultiLineString([((5,1), (5,2)), ((6,2), (6,4))]),
    LineString([(3,4), (4,4)])
     ]}
    gdf = gpd.GeoDataFrame(d, geometry="geometry", crs="EPSG:3857")
    return gdf

def test_remove_edge_overlaps(ordered_edges, ordered_edges_without_overlaps):
    assert_frame_equal(
        remove_edge_overlaps(ordered_edges),
        ordered_edges_without_overlaps,
        check_dtype=False,
    )


@pytest.fixture
def triangulation_graph_trips():
    # Nodes of the graph
    A = (800,1800)
    B = (1300,2000)
    C = (1800,1800)
    D = (900,1400)
    E = (1300,1300)
    F = (1800,1200)
    G = (800,800)
    H = (1300,800)

    Z = (1150,1100)

    nodes = {
        'A': {'x': 800, 'y': 1800},
        'B': {'x': 1300, 'y': 2000},
        'C': {'x': 1800, 'y': 1800},
        'D': {'x': 900, 'y': 1400},
        'E': {'x': 1300, 'y': 1300},
        'F': {'x': 1800, 'y': 1200},
        'G': {'x': 800, 'y': 800},
        'H': {'x': 1300, 'y': 800}
    }

    AB = LineString([A, B])
    AD = LineString([A, D])
    BC = LineString([B, C])
    BE = LineString([B, E])
    CF = LineString([C, F])
    DE = LineString([D, E])
    DG = LineString([D, G])
    EF = LineString([E, F])
    EH = LineString([E, Z, H])
    FH = LineString([F, H])
    GH = LineString([G, H])

    edges = {
        ('A','B'): {'distance': AB.length, 'geometry': AB},
        ('A','D'): {'distance': AD.length, 'geometry': AD},
        ('B','C'): {'distance': BC.length, 'geometry': BC},
        ('B','E'): {'distance': BE.length, 'geometry': BE},
        ('C','F'): {'distance': CF.length, 'geometry': CF},
        ('D','E'): {'distance': DE.length, 'geometry': DE},
        ('D','G'): {'distance': DG.length, 'geometry': DG},
        ('E','F'): {'distance': EF.length, 'geometry': EF},
        ('E','H'): {'distance': EH.length, 'geometry': EH},
        ('F','H'): {'distance': FH.length, 'geometry': FH},
        ('G','H'): {'distance': GH.length, 'geometry': GH}
    }

    graph = nx.Graph()
    graph.add_nodes_from(nodes.keys())
    nx.set_node_attributes(graph, nodes)

    graph.add_edges_from(edges.keys())
    nx.set_edge_attributes(graph, edges)

    graph.graph["crs"] = '3857'

    return graph

@pytest.fixture
def trips_data():
    # Points from crashes data          In ESPG:3857
    D5 = Point(0.0089832,0.0080848)      # (1000,900)
    D6 = Point(0.0125764,0.014373)       # (1400,1600)
    O2 = Point(0.0080848,0.0134747)      # (900,1500)
    D2 = Point(0.0071865,0.0116781)      # (800,1300)
    D3 = Point(0.0062882,0.0134747)      # (700,1500)
    O4 = Point(0.0098815,0.0134747)      # (1100,1500)
    #O = Point(0.0161697,0.0026949)      # (1800,300)
    O3 = Point(0.014373,0.0116781)       # (1600,1300)
    O6 = Point(0.0071865,0.0089832)      # (800,1000)
    O5 = Point(0.0098815,0.0098815)      # (1100,1100)
    O0 = Point(0.014373,0.0215596)       # (1600,2400)
    D0 = Point(0.017068,0.0152714)       # (1900,1700)
    D4 = Point(0.0107798,0.0062882)      # (1200,700)
    D1 = Point(0.0089832,0.0161697)      # (1000,1800)
    O1 = Point(0.0161697,0.0098815)      # (1800,1100)
        

    t = {
        'o_lat': [O0.y, O1.y, O2.y, O3.y, O4.y, O5.y, O6.y],
        'o_lon': [O0.x, O1.x, O2.x, O3.x, O4.x, O5.x, O6.x],
        'd_lat': [D0.y, D1.y, D2.y, D3.y, D4.y, D5.y, D6.y],
        'd_lon': [D0.x, D1.x, D2.x, D3.x, D4.x, D5.x, D6.x],
        'num': [1, 1, 1, 2, 1, 1, 1]
    }

    trips = pd.DataFrame(t)

    return trips

@pytest.fixture
def triangulation_graph_with_trips_data():
    # Nodes of the graph
    A = (800,1800)
    B = (1300,2000)
    C = (1800,1800)
    D = (900,1400)
    E = (1300,1300)
    F = (1800,1200)
    G = (800,800)
    H = (1300,800)

    Z = (1150,1100)

    nodes = {
        'A': {'x': 800, 'y': 1800},
        'B': {'x': 1300, 'y': 2000},
        'C': {'x': 1800, 'y': 1800},
        'D': {'x': 900, 'y': 1400},
        'E': {'x': 1300, 'y': 1300},
        'F': {'x': 1800, 'y': 1200},
        'G': {'x': 800, 'y': 800},
        'H': {'x': 1300, 'y': 800}
    }

    AB = LineString([A, B])
    AD = LineString([A, D])
    BC = LineString([B, C])
    BE = LineString([B, E])
    CF = LineString([C, F])
    DE = LineString([D, E])
    DG = LineString([D, G])
    EF = LineString([E, F])
    EH = LineString([E, Z, H])
    FH = LineString([F, H])
    GH = LineString([G, H])

    edges = {
        ('A','B'): {'distance': AB.length, 'geometry': AB, 'num_trips': 0},
        ('A','D'): {'distance': AD.length, 'geometry': AD, 'num_trips': 1},
        ('B','C'): {'distance': BC.length, 'geometry': BC, 'num_trips': 0},
        ('B','E'): {'distance': BE.length, 'geometry': BE, 'num_trips': 0},
        ('C','F'): {'distance': CF.length, 'geometry': CF, 'num_trips': 0},
        ('D','E'): {'distance': DE.length, 'geometry': DE, 'num_trips': 6},
        ('D','G'): {'distance': DG.length, 'geometry': DG, 'num_trips': 2},
        ('E','F'): {'distance': EF.length, 'geometry': EF, 'num_trips': 3},
        ('E','H'): {'distance': EH.length, 'geometry': EH, 'num_trips': 1},
        ('F','H'): {'distance': FH.length, 'geometry': FH, 'num_trips': 0},
        ('G','H'): {'distance': GH.length, 'geometry': GH, 'num_trips': 0}
    }

    graph = nx.Graph()
    graph.add_nodes_from(nodes.keys())
    nx.set_node_attributes(graph, nodes)

    graph.add_edges_from(edges.keys())
    nx.set_edge_attributes(graph, edges)

    graph.graph["crs"] = '3857'

    return graph

def test_add_trip_data_to_net_case_success_simple(trips_data, triangulation_graph_trips, triangulation_graph_with_trips_data):
    result = add_trip_data_to_net(
                trips_data, 
                triangulation_graph_trips,
                '3857'
            )
    expected = triangulation_graph_with_trips_data

    assert result.nodes == expected.nodes, "Nodes are not the same"
    assert result.adj == expected.adj, "Edges are not the same"
    assert result.graph == expected.graph, "Graphs are not the same"

@pytest.fixture
def turin_routed_edges_v2():
    e = gpd.read_file("./tests/test_data/turin_edges_v2.gpkg")
    # because the tuples and lists are saved as strings
    e['pair'] = e['pair'].apply(ast.literal_eval)
    e['path_nodes'] = e['path_nodes'].apply(ast.literal_eval)
    e['path_edges'] = e['path_edges'].apply(ast.literal_eval)
    return e

@pytest.fixture
def turin_seed_nodes():
    n = gpd.read_file("./tests/test_data/turin_seed_points.gpkg")
    n.set_index('osmid', drop = False, inplace = True)
    return n

@pytest.fixture
def turin_trips_data():
    t = pd.read_csv("./tests/test_data/turin_trips.csv")
    return t

@pytest.fixture
def turin_routed_edges_with_trips():
    e = gpd.read_file("./tests/test_data/turin_edges_with_trips.gpkg")
    # because the tuples and lists are saved as strings
    e['pair'] = e['pair'].apply(ast.literal_eval)
    e['path_nodes'] = e['path_nodes'].apply(ast.literal_eval)
    e['path_edges'] = e['path_edges'].apply(ast.literal_eval)
    return e

def test_add_trip_data_to_net_case_success_turin(turin_trips_data, turin_seed_nodes, turin_routed_edges_v2, turin_routed_edges_with_trips):
    assert_frame_equal(
        add_trip_data_to_net(
            turin_trips_data, 
            turin_seed_nodes,
            turin_routed_edges_v2,
            '3857'
        ),
        turin_routed_edges_with_trips
    )