from growbikenet import constants
from growbikenet import settings
import pytest
import osmnx as ox
import networkx as nx
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, MultiLineString
import ast
from pandas.testing import assert_frame_equal
import shapely
import pickle
from growbikenet.functions import (
    get_principal_bearing,
    _get_grid_seed_points,
    filter_points_distant_from_osm_nodes,
    _rank_df,
    # intersects_properly,
    _remove_edge_overlaps,
    add_point_data_to_net,
    add_trip_data_to_net,
    create_gdf_with_geoms,
    _get_weighted_distances,
    slugify,
)

settings.export_path = {
    "results":"./results/",
    "plots":"./results/plots/",
}

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
    return "betweenness"


def test__rank_df(test_data_rank, method, validation_data_rank):
    assert_frame_equal(
        _rank_df(test_data_rank, method),
        validation_data_rank,
        check_dtype=False,
    )


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


def test_filter_points_distant_from_osm_nodes(
    snapped_seed_points, filtered_seed_points
):
    settings.seed_point_snap_distance = 500
    constants._SEED_POINT_GRID_SPACING_FACTOR = 0.25
    assert_frame_equal(
        filter_points_distant_from_osm_nodes(snapped_seed_points, settings.seed_point_snap_distance),
        filtered_seed_points,
        check_dtype=False,
    )


@pytest.fixture
def validation_streets():
    streets_nodes = gpd.read_file(
        "./tests/test_data/oelde_street_network.gpkg", layer="nodes"
    ).set_index("osmid")
    streets_edges = gpd.read_file(
        "./tests/test_data/oelde_street_network.gpkg", layer="edges"
    ).set_index(["u", "v", "key"])
    streets = ox.convert.graph_from_gdfs(streets_nodes, streets_edges)
    return streets


def test_get_principal_bearing(validation_streets):
    assert get_principal_bearing(validation_streets) == 65.0


@pytest.fixture
def validation_grid():
    grid = gpd.read_file("./tests/test_data/oelde_grid.gpkg")
    return grid


def test__get_grid_seed_points(validation_grid, validation_streets):
    edges = ox.convert.graph_to_gdfs(
        validation_streets,
        nodes=False,
        edges=True,
        node_geometry=False,
        fill_edge_geometry=False,
    )
    validation_grid.equals(_get_grid_seed_points(edges, 1707, 65.0))


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

def test__remove_edge_overlaps(ordered_edges, ordered_edges_without_overlaps):
    assert_frame_equal(
        _remove_edge_overlaps(ordered_edges),
        ordered_edges_without_overlaps,
        check_dtype=False,
    )



@pytest.fixture
def routed_edges_crashes():
    # Nodes of the graph
    A = (800,1800)
    B = (1300,2000)
    C = (1800,1800)
    D = (900,1400)
    E = (1300,1300)
    F = (1800,1200)
    G = (800,800)
    H = (1300,800)

    # Auxiliary nodes
    Z = (1150,1100)

    g = {
        'geometry': [
            LineString([A,B]),
            LineString([A,D]),
            LineString([B,C]),
            LineString([B,E]),
            LineString([C,F]),
            LineString([D,E]),
            LineString([D,G]),
            LineString([E,F]),
            LineString([E,Z,H]),
            LineString([F,H]),
            LineString([G,H])
        ]
    }
    graph = gpd.GeoDataFrame(g, geometry="geometry", crs = "EPSG:3857")
    return graph

@pytest.fixture
def crashes_data():
    # Points from crashes data          In ESPG:3857
    I = Point(0.0089832,0.0080848)      # (1000,900)
    J = Point(0.0125764,0.014373)       # (1400,1600)
    K = Point(0.0080848,0.0134747)      # (900,1500)
    L = Point(0.0071865,0.0116781)      # (800,1300)
    M = Point(0.0062882,0.0134747)      # (700,1500)
    N = Point(0.0098815,0.0134747)      # (1100,1500)
    O = Point(0.0161697,0.0026949)      # (1800,300)
    P = Point(0.014373,0.0116781)       # (1600,1300)
    Q = Point(0.0071865,0.0089832)      # (800,1000)
    R = Point(0.0098815,0.0098815)      # (1100,1100)
    S = Point(0.014373,0.0215596)       # (1600,2400)
    T = Point(0.017068,0.0152714)       # (1900,1700)
    U = Point(0.0107798,0.0062882)      # (1200,700)
    V = Point(0.0089832,0.0161697)      # (1000,1800)
    W = Point(0.0161697,0.0098815)      # (1800,1100)

    c = {
        'geometry': [I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W],
        'num': [1,1,2,3,1,1,1,3,5,1,1,1,1,2,1]
    }
    crashes = gpd.GeoDataFrame(c, geometry="geometry", crs = "EPSG:4326")
    return crashes

@pytest.fixture
def routed_edges_with_crashes_data():
    # Nodes of the graph
    A = (800,1800)
    B = (1300,2000)
    C = (1800,1800)
    D = (900,1400)
    E = (1300,1300)
    F = (1800,1200)
    G = (800,800)
    H = (1300,800)

    # Auxiliary nodes
    Z = (1150,1100)

    g = {
        'num_points': [
            2,  #[A,B]
            3,  #[A,D]
            1,  #[B,C]
            1,  #[B,E]
            1,  #[C,F]
            1,  #[D,E]
            8,  #[D,G]
            3,  #[E,F]
            1,  #[E,Z,H]
            1,  #[F,H]
            2,  #[G,H]
        ],
        'geometry': [
            LineString([A,B]),
            LineString([A,D]),
            LineString([B,C]),
            LineString([B,E]),
            LineString([C,F]),
            LineString([D,E]),
            LineString([D,G]),
            LineString([E,F]),
            LineString([E,Z,H]),
            LineString([F,H]),
            LineString([G,H]),
        ]
    }
    graph = gpd.GeoDataFrame(g, geometry="geometry", crs = "EPSG:3857")
    return graph

def test_add_point_data_to_net_case_success_simple(routed_edges_crashes, crashes_data, routed_edges_with_crashes_data):
    assert_frame_equal(
        add_point_data_to_net(crashes_data, routed_edges_crashes, '3857'),
        routed_edges_with_crashes_data,
        check_dtype=False
    )


@pytest.fixture
def turin_routed_edges_crashes():
    g = gpd.read_file("./tests/test_data/turin_edges_gdf.gpkg")
    return g

@pytest.fixture
def turin_accidents_data():
    c = gpd.read_file("./tests/test_data/turin_crashes.gpkg")
    return c

@pytest.fixture
def turin_routed_edges_with_crashes_data():
    g = gpd.read_file("./tests/test_data/turin_edges_gdf_with_crashes.gpkg")
    return g

def test_add_point_data_to_net_case_success_turin(turin_accidents_data, turin_routed_edges_crashes, turin_routed_edges_with_crashes_data):
    result = add_point_data_to_net(turin_accidents_data, turin_routed_edges_crashes, '3857')

    diff_mask = result['num_points'] != turin_routed_edges_with_crashes_data['num_points']
    if diff_mask.any():
        print("\n\nDifferences found:")
        print(result.loc[diff_mask, ['num_points']])
        print("\nExpected:")
        print(turin_routed_edges_with_crashes_data.loc[diff_mask, ['num_points']])
    
    assert_frame_equal(
        add_point_data_to_net(turin_accidents_data, turin_routed_edges_crashes, '3857'),
        turin_routed_edges_with_crashes_data,
        check_dtype=False
    )
    Z = (1150,1100)


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

    # Auxiliary nodes
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

    # Auxiliary nodes
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
def turin_triangulation_graph_trips():
    nodes = pd.read_csv(f"./tests/test_data/turin_triangulation_nodes_trips.csv", sep = ";", index_col='osmid').to_dict(orient='index')

    edges_gdf = gpd.read_file(f"./tests/test_data/turin_triangulation_edges_trips.gpkg")
    edges_gdf.set_index(['u', 'v'], inplace=True)
    edges = edges_gdf.to_dict(orient='index')

    graph_att = pd.read_csv(f"./tests/test_data/turin_triangulation_graph_trips.csv").loc[0,:].to_dict()

    graph = nx.Graph()
    graph.add_nodes_from(nodes.keys())
    nx.set_node_attributes(graph, nodes)

    graph.add_edges_from(edges.keys())
    nx.set_edge_attributes(graph, edges)

    graph.graph = graph_att
    return graph

@pytest.fixture
def turin_trips_data():
    t = pd.read_csv("./tests/test_data/turin_trips.csv")
    return t

@pytest.fixture
def turin_triangulation_graph_with_trips_data():
    nodes = pd.read_csv(f"./tests/test_data/turin_triangulation_nodes_with_trips.csv", sep = ";", index_col='osmid').to_dict(orient='index')

    edges_gdf = gpd.read_file(f"./tests/test_data/turin_triangulation_edges_with_trips.gpkg")
    edges_gdf.set_index(['u', 'v'], inplace=True)
    edges = edges_gdf.to_dict(orient='index')

    graph_att = pd.read_csv(f"./tests/test_data/turin_triangulation_graph_with_trips.csv").loc[0,:].to_dict()

    graph = nx.Graph()
    graph.add_nodes_from(nodes.keys())
    nx.set_node_attributes(graph, nodes)

    graph.add_edges_from(edges.keys())
    nx.set_edge_attributes(graph, edges)

    graph.graph = graph_att
    return graph

def test_add_trip_data_to_net_case_success_turin(turin_trips_data, turin_triangulation_graph_trips, turin_triangulation_graph_with_trips_data):
    result = add_trip_data_to_net(
                turin_trips_data, 
                turin_triangulation_graph_trips,
                '3857'
            )
    expected = turin_triangulation_graph_with_trips_data
    assert result.nodes == expected.nodes, "Nodes are not the same"
    assert result.adj == expected.adj, "Edges are not the same"
    assert result.graph == expected.graph, "Graphs are not the same"


@pytest.fixture
def routed_triangulation():
    df = pd.DataFrame(
        {
            'pair': [('A','G'), ('A','H'),('G','J'),('H','J')],
            'source': ['A','A','G','H'],
            'target': ['G','H','J','J'],
            'path_nodes': [['A','B','C','D','E','F','G'], ['A','B','H'], ['G','J'], ['H','F','I','J']],
            'path_edges': [
                [('A','B'),('B','C'),('C','D'),('D','E'),('E','F'),('F','G')],
                [('A','B'),('B','H')],
                [('G','J')],
                [('H','F'),('F','I'),('I','J')]
            ]
        }
    )
    return df

@pytest.fixture
def network_edges():
    A = (4,9)
    B = (2,9)
    C = (1.5,9.5)
    D = (2,10)
    E = (3,10)
    F = (3,8)
    G = (5.5,8)
    H = (1.5,8)
    I = (3,7)
    J = (3.5,7)

    AB = LineString([A,B])
    BC = LineString([B,C])
    CD = LineString([C,D])
    DE = LineString([D,E])
    EF = LineString([E,F])
    FG = LineString([F,G])
    BH = LineString([B,H])
    HF = LineString([H,F])
    FI = LineString([F,I])
    IJ = LineString([I,J])
    GJ = LineString([G,J])

    gdf = gpd.GeoDataFrame(
        {
            'u': ['A','B','C','D','E','F','B','H','F','I','G'],
            'v': ['B','C','D','E','F','G','H','F','I','J','J']
        },
        crs = '3857',
        geometry = [AB, BC, CD, DE, EF, FG, BH, HF, FI, IJ, GJ]
    )
    gdf.set_index(['u','v'], inplace = True)
    return gdf

@pytest.fixture
def routed_triangulation_with_geoms():
    A = (4,9)
    B = (2,9)
    C = (1.5,9.5)
    D = (2,10)
    E = (3,10)
    F = (3,8)
    G = (5.5,8)
    H = (1.5,8)
    I = (3,7)
    J = (3.5,7)

    gdf = gpd.GeoDataFrame(
        {
            'pair': [('A','G'), ('A','H'),('G','J'),('H','J')],
            'source': ['A','A','G','H'],
            'target': ['G','H','J','J'],
            'path_nodes': [['A','B','C','D','E','F','G'], ['A','B','H'], ['G','J'], ['H','F','I','J']],
            'path_edges': [
                [('A','B'),('B','C'),('C','D'),('D','E'),('E','F'),('F','G')],
                [('A','B'),('B','H')],
                [('G','J')],
                [('H','F'),('F','I'),('I','J')]
            ],
            'geometry': [
                LineString([A,B,C,D,E,F,G]),
                LineString([A,B,H]),
                LineString([G,J]),
                LineString([H,F,I,J])
            ]
        },
        crs = '3857',
        geometry = 'geometry'
    )
    return gdf

def test_create_gdf_with_geoms_case_success_simple(routed_triangulation, network_edges, routed_triangulation_with_geoms):
    assert_frame_equal(
        create_gdf_with_geoms(
            routed_triangulation,
            network_edges
        ),
        routed_triangulation_with_geoms
    )


@pytest.fixture
def turin_routed_triangulation():
    df = pd.read_csv("./tests/test_data/turin_routed_triangulation_wout_geoms.csv",
                     sep = ";"
                     )
    df['pair'] = df['pair'].apply(ast.literal_eval)
    df['path_nodes'] = df['path_nodes'].apply(ast.literal_eval)
    df['path_edges'] = df['path_edges'].apply(ast.literal_eval)
    return df

@pytest.fixture
def turin_network_edges():
    gdf = gpd.read_file(
        "./tests/test_data/turin_edges.gpkg"
    )
    gdf.set_index(['u','v'], inplace=True)
    return gdf

@pytest.fixture
def turin_routed_triangulation_with_geoms():
    gdf = gpd.read_file(
        "./tests/test_data/turin_routed_triangulation_w_geoms.gpkg"
    )
    gdf['pair'] = gdf['pair'].apply(ast.literal_eval)
    gdf['path_nodes'] = gdf['path_nodes'].apply(ast.literal_eval)
    gdf['path_edges'] = gdf['path_edges'].apply(ast.literal_eval)
    return gdf

def test_create_gdf_with_geoms_case_success_turin(turin_routed_triangulation, turin_network_edges, turin_routed_triangulation_with_geoms):
    assert_frame_equal(
        create_gdf_with_geoms(
            turin_routed_triangulation, 
            turin_network_edges
        ),
        turin_routed_triangulation_with_geoms
    )

@pytest.fixture
def turin_B():
    B = pickle.load(open('./tests/test_data/turin_B.pickle', 'rb'))
    return B

@pytest.fixture
def turin_d_points():
    d = pickle.load(open('./tests/test_data/turin_d_points.pickle', 'rb'))
    return d

@pytest.fixture
def turin_d_trips():
    d = pickle.load(open('./tests/test_data/turin_d_trips.pickle', 'rb'))
    return d

def test__get_weighted_distances(turin_B, turin_d_points, turin_d_trips):
    assert turin_d_points == _get_weighted_distances(turin_B, "num_points")
    assert turin_d_trips == _get_weighted_distances(turin_B, "num_trips")


@pytest.fixture
def city_names():
    names = ["Aix-En-Provence", "Alcalá De Henares", "Almería", "Bielsko-Biala", "Chișinău", "Durrës", "L'Hospitalet De Llobregat", "Nîmes", "Umeå", "amsterdam_nl", "áéíóúàèìùòâêîôûäëïöüǎěǐǒǔãẽĩõũăåæçčıłñňøœřßșşšůŷÿźž"]
    return names

@pytest.fixture
def city_names_slugified():
    names = ["aixenprovence", "alcaladehenares", "almeria", "bielskobiala", "chisinau", "durres", "lhospitaletdellobregat", "nimes", "umea", "amsterdam_nl", "aeiouaeiouaeiouaeiouaeiouaeiouaaaccilnnoorssssuyyzz"]
    return names

def test_slugify(city_names, city_names_slugified):
    for n, ns in zip(city_names, city_names_slugified):
        assert slugify(n) == ns