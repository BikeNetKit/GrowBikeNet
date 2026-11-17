import ast
import pickle

import geopandas as gpd
import networkx as nx
import osmnx as ox
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from shapely.geometry import LineString, MultiLineString, Point

from growbikenet import constants, settings
from growbikenet.utils import (
    _get_grid_seed_points,
    _get_weighted_distances,
    _order_df,
    _remove_edge_overlaps,
    create_gdf_with_geoms,
    filter_points_distant_from_osm_nodes,
)

settings.export_path = {
    "results":"./results/",
    "plots":"./results/plots/",
}
settings.crs_result = '3857' # Leave for testing temporarily at the old value. Change to 4326 when re-doing test data.
constants._CRS_CALCULATIONS = '3857' # Leave for testing temporarily at the old value. Change to auto when re-doing test data.


@pytest.fixture
def test_data_ordering(method):
    df = pd.DataFrame((6, 2, 4), columns=[method])
    return df


@pytest.fixture
def validation_data_ordering(method):
    ordered_df = pd.DataFrame(
        ([6, 0], [4, 1], [2, 2]), columns=[method, "ordering"]
    )
    return ordered_df


@pytest.fixture
def method():
    return "betweenness"


def test__order_df(test_data_ordering, method, validation_data_ordering):
    assert_frame_equal(
        _order_df(test_data_ordering, method),
        validation_data_ordering,
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
        "./tests/test_data/oelde_growable_network.gpkg", layer="nodes"
    ).set_index("osmid")
    streets_edges = gpd.read_file(
        "./tests/test_data/oelde_growable_network.gpkg", layer="edges"
    ).set_index(["u", "v", "key"])
    streets = ox.convert.graph_from_gdfs(streets_nodes, streets_edges)
    return streets

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


# create_gdf_with_geoms
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
    gdf = gdf.set_index(['u','v'])
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
    gdf = gdf.set_index(['u','v'])
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
