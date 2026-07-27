from growbikenet import constants
from growbikenet import settings
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
    create_gdf_with_geoms
)
from shapely.geometry import Point, LineString, MultiLineString
import ast


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
    snapped_seed_points, filtered_seed_points
):
    settings.seed_point_snap_distance = 500
    constants.SEED_POINT_GRID_SPACING_FACTOR = 0.25
    assert_frame_equal(
        filter_seed_points(snapped_seed_points),
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