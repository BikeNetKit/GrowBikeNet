import pytest
import osmnx as ox
from pandas.testing import assert_frame_equal
from growbikenet.functions import *
from shapely.geometry import LineString


@pytest.fixture
def create_geom_1():
    linestring = LineString([(0, 0), (1, 1), (2, 2)])
    return linestring


@pytest.fixture
def create_geom_2():
    linestring = LineString([(3, 3), (4, 4), (5, 5)])
    return linestring


def test_intersects_properly(create_geom_1, create_geom_2):
    assert intersects_properly(create_geom_1, create_geom_2) is False


@pytest.fixture
def create_test_data_rank(method):
    df = pd.DataFrame((6, 2, 4), columns=[method])
    return df


@pytest.fixture
def create_validation_data_rank(method):
    ranked_df = pd.DataFrame(
        ([6, 0], [4, 1], [2, 2]), columns=[method, "ordering_betweenness_centrality"]
    )
    return ranked_df


@pytest.fixture
def method():
    return "betweenness_centrality"


def test_rank_df(create_test_data_rank, method, create_validation_data_rank):
    assert_frame_equal(
        rank_df(create_test_data_rank, method),
        create_validation_data_rank,
        check_dtype=False,
    )


@pytest.fixture
def define_seed_point_delta():
    return 500


@pytest.fixture
def create_snapped_seed_points():
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
def create_filtered_seed_points():
    d = {"osmid": ["1", "3"], "geometry": [Point(1001, 1001), Point(3001, 3001)]}
    gdf = gpd.GeoDataFrame(d, geometry="geometry", crs="EPSG:3857")
    gdf = gdf.set_index("osmid")
    gdf["osmid"] = gdf.index
    gdf = gdf.iloc[:, [1, 0]]
    return gdf


def test_filter_seed_points(
    create_snapped_seed_points, create_filtered_seed_points, define_seed_point_delta
):
    assert_frame_equal(
        filter_seed_points(create_snapped_seed_points, define_seed_point_delta),
        create_filtered_seed_points,
        check_dtype=False,
    )


@pytest.fixture
def create_validation_streets():
    streets_nodes = gpd.read_file(
        "./tests/test_data/oelde_streets.gpkg", layer="nodes"
    ).set_index("osmid")
    streets_edges = gpd.read_file(
        "./tests/test_data/oelde_streets.gpkg", layer="edges"
    ).set_index(["u", "v", "key"])
    streets = ox.convert.graph_from_gdfs(streets_nodes, streets_edges)
    return streets


def test_get_principal_bearing(create_validation_streets):
    assert get_principal_bearing(create_validation_streets) == 65.0


@pytest.fixture
def create_validation_grid():
    grid = gpd.read_file("./tests/test_data/oelde_grid.gpkg")
    return grid


def test_get_grid_seed_points(create_validation_grid, create_validation_streets):
    edges = ox.convert.graph_to_gdfs(
        create_validation_streets,
        nodes=False,
        edges=True,
        node_geometry=False,
        fill_edge_geometry=False,
    )
    create_validation_grid.equals(get_grid_seed_points(edges, 1707, 65.0))
