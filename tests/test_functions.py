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
    add_trip_data_to_net
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
def node_seed_points():
    # Nodes of the graph
    A = (800,1800)
    B = (1300,1800)
    C = (1800,1800)
    D = (800,1300)
    E = (1300,1300)
    F = (1800,1300)
    G = (800,800)
    H = (1300,800)

    d = {
        'osmid': [1, 2, 3, 4, 5, 6, 7, 8],
        'geometry':[Point(A), Point(B), Point(C), Point(D), Point(E), Point(F), Point(G), Point(H)]
    }

    nodes = gpd.GeoDataFrame(d, geometry='geometry', crs = "EPSG:3857")
    nodes = nodes.set_index('osmid')

    return nodes

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

    # Auxiliary nodes
    I = (1050,1950)
    J = (1340,1700)
    K = (900,1250)
    L = (1500,1250)
    M = (1150,1100)

    e = {
        'pair': [(1,2), (1,4), (2,3), (2,5), (3,6), (4,5), (4,7), (5,6), (5,8), (6,8), (7,8)],
        'dist': [583.10, 500, 500, 509.70, 500, 514.92, 500, 510.29, 585.41, 707.11, 500],
        'geometry': [
            LineString([A,I,B]),
            LineString([A,D]),
            LineString([B,C]),
            LineString([B,J,E]),
            LineString([C,F]),
            LineString([D,K,E]),
            LineString([D,G]),
            LineString([E,L,F]),
            LineString([E,M,H]),
            LineString([F,H]),
            LineString([G,H]),
        ]
    }
    edges = gpd.GeoDataFrame(e, geometry="geometry", crs = "EPSG:3857")

    return edges

@pytest.fixture
def trips_data():
    # Points from trips data          In ESPG:3857
    O0 = Point(0.014499, 0.022)          # (1614,2449)
    D0 = Point(0.016969, 0.015074)       # (1889,1678)
    O1 = Point(0.015891, 0.009459)       # (1769,1053)
    D1 = Point(0.009226, 0.016502)       # (1027,1837)
    O2 = Point(0.007744,0.013376)        # (862,1489)
    D2 = Point(0.006558,0.011768)        # (730,1310)
    O3 = Point(0.014624, 0.012019)       # (1628,1338)
    D3 = Point(0.006576, 0.01325)        # (732,1475)
    O4 = Point(0.009549, 0.013906)       # (1063,1548)
    D4 = Point(0.010034, 0.006728)       # (1117,749)
    O5 = Point(0.009388, 0.009675)       # (1045,1077)
    D5 = Point(0.009432,0.007519)        # (1050,837)
    O6 = Point(0.007537, 0.00928)        # (839,1033)
    D6 = Point(0.012011,0.013888)        # (1337,1546)
        

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

    I = (1050,1950)
    J = (1340,1700)
    K = (900,1250)
    L = (1500,1250)
    M = (1150,1100)

    e = {
        'pair': [(1,2), (1,4), (2,3), (2,5), (3,6), (4,5), (4,7), (5,6), (5,8), (6,8), (7,8)],
        'dist': [583.10, 500, 500, 509.70, 500, 514.92, 500, 510.29, 585.41, 707.11, 500],
        'num_trips': [0, 1, 0, 0, 0, 4, 2, 3, 1, 0, 0],
        'geometry': [
            LineString([A,I,B]),
            LineString([A,D]),
            LineString([B,C]),
            LineString([B,J,E]),
            LineString([C,F]),
            LineString([D,K,E]),
            LineString([D,G]),
            LineString([E,L,F]),
            LineString([E,M,H]),
            LineString([F,H]),
            LineString([G,H]),
        ]
    }
    edges = gpd.GeoDataFrame(e, geometry="geometry", crs = "EPSG:3857")

    return edges

def test_add_trip_data_to_net_case_success_simple(trips_data, node_seed_points, routed_edges, routed_edges_with_data):
    assert_frame_equal(
        add_trip_data_to_net(
            trips_data, 
            node_seed_points,
            routed_edges,
            '3857'
        ),
        routed_edges_with_data
    )