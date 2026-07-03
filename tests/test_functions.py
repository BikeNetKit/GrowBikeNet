import pytest
import osmnx as ox
import pandas as pd
import geopandas as gpd
from pandas.testing import assert_frame_equal
from growbikenet.functions import (
    get_principal_bearing,
    get_grid_seed_points,
    filter_seed_points,
    rank_df,
    # intersects_properly,
    remove_edge_overlaps,
    add_point_data_to_net
)
from shapely.geometry import Point, LineString, MultiLineString


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
def routed_edges():
    # Nodes of the graph
    A = (800,1800)
    B = (1300,1800)
    C = (1800,1800)
    D = (800,1300)
    E = (1300,1300)
    F = (1800,1300)
    G = (800,800)
    H = (1300,800)
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
            MultiLineString([(E,Z),(Z,H)]),
            LineString([F,H]),
            LineString([G,H]),
        ]
    }
    graph = gpd.GeoDataFrame(g, geometry="geometry", crs = "EPSG:3857")

    return graph

@pytest.fixture
def crashes_data():
    # Points from crashes data          In ESPG:3857
    I = Point(0.009432,0.007519)        # (1050,837)
    J = Point(0.012011,0.013888)        # (1337,1546)
    K = Point(0.007744,0.013376)        # (862,1489)
    L = Point(0.006558,0.011768)        # (730,1310)
    M = Point(0.006576, 0.01325)        # (732,1475)
    N = Point(0.009549, 0.013906)       # (1063,1548)
    O = Point(0.015981, 0.0023)         # (1779,256)
    P = Point(0.014624, 0.012019)       # (1628,1338)
    Q = Point(0.007537, 0.00928)        # (839,1033)
    R = Point(0.009388, 0.009675)       # (1045,1077)
    S = Point(0.014499, 0.022)          # (1614,2449)
    T = Point(0.016969, 0.015074)       # (1889,1678)
    U = Point(0.010034, 0.006728)       # (1117,749)
    V = Point(0.009226, 0.016502)       # (1027,1837)
    W = Point(0.015891, 0.009459)       # (1769,1053)

    c = {
        'geometry': [I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W],
        'num': [1,1,2,3,1,1,1,3,5,1,1,1,1,2,1]
    }
    crashes = gpd.GeoDataFrame(c, geometry="geometry", crs = "EPSG:4326")

    return crashes


@pytest.fixture
def routed_edges_with_data():
    # Nodes of the graph
    A = (800,1800)
    B = (1300,1800)
    C = (1800,1800)
    D = (800,1300)
    E = (1300,1300)
    F = (1800,1300)
    G = (800,800)
    H = (1300,800)
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
            MultiLineString([(E,Z),(Z,H)]),
            LineString([F,H]),
            LineString([G,H]),
        ],
        'num_points': [
            2,  #[A,B]
            6,  #[A,D]
            0,  #[B,C]
            2,  #[B,E]
            1,  #[C,F]
            0,  #[D,E]
            5,  #[D,G]
            3,  #[E,F]
            1,  #[E,Z,H]
            1,  #[F,H]
            2,  #[G,H]
        ]
    }
    graph = gpd.GeoDataFrame(g, geometry="geometry", crs = "EPSG:3857")

    return graph
    
def test_add_point_data_to_net_case_success_simple(routed_edges, crashes_data, routed_edges_with_data):
    assert_frame_equal(
        add_point_data_to_net(crashes_data, routed_edges, '3857'),
        routed_edges_with_data,
        check_dtype=False,
    )