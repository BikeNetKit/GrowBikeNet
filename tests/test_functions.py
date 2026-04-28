import pytest
from pandas.testing import assert_frame_equal
from growbikenet.functions import *


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
    ranked_df = pd.DataFrame(([6, 0], [4, 1], [2, 2]), columns=[method, "ordering"])
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
def create_validation_triangulation():
    linestring = LineString([Point(1001, 1001), Point(3001, 3001)])
    pair = "1", "3"
    d = {
        "pair": [list(pair)],
        "potential_edge": [linestring],
        "dist": [linestring.length],
    }
    df = pd.DataFrame(d)
    return df


def test_create_potential_triangulation(
    create_validation_triangulation, create_filtered_seed_points
):
    assert_frame_equal(
        create_potential_triangulation(create_filtered_seed_points),
        create_validation_triangulation,
        check_dtype=False,
    )


@pytest.fixture
def create_unfiltered_triangulation():
    linestring_1_3 = LineString([Point(1001, 1001), Point(3001, 3001)])
    linestring_1_2 = LineString([Point(1001, 1001), Point(3001, 2001)])
    linestring_2_3 = LineString([Point(3001, 2001), Point(3001, 3001)])
    linestring_2_4 = LineString([Point(3001, 2001), Point(1001, 3001)])
    d = {
        "pair": [["1", "3"], ["1", "2"], ["2", "3"], ["2", "4"]],
        "potential_edge": [
            linestring_1_3,
            linestring_1_2,
            linestring_2_3,
            linestring_2_4,
        ],
        "dist": [
            linestring_1_3.length,
            linestring_1_2.length,
            linestring_2_3.length,
            linestring_2_4.length,
        ],
    }
    df = pd.DataFrame(d)
    return df


@pytest.fixture
def create_validation_filtered_triangulation():
    edge_list = [["1", "3"], ["1", "2"], ["2", "3"]]
    return edge_list


def test_filter_triangulation(
    create_unfiltered_triangulation, create_validation_filtered_triangulation
):
    assert (
        filter_triangulation(create_unfiltered_triangulation)
        == create_validation_filtered_triangulation
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


# TO DO. The code below is not working yet
# # get_existing_network_seed_points
# @pytest.fixture
# def define_existing_network_spacing():
#     return 500

# @pytest.fixture
# def create_existing_network_nodes():
#     d = {'osmid': ['1', '2', '3', '4', '5'], 'geometry': [Point(1000, 1000), Point(2000, 2000), Point(3000, 3000), Point(3100, 3100), Point(3200, 3200)]}
#     gdf = gpd.GeoDataFrame(d, geometry='geometry', crs='EPSG:3857')
#     gdf = gdf.set_index('osmid')
#     gdf['osmid'] = gdf.index
#     return gdf

# @pytest.fixture
# def create_existing_network_seed_points():
#     d = {'osmid': ['1', '2', '3'], 'geometry': [Point(1000, 1000), Point(2000, 2000), Point(3000, 3000)]}
#     gdf = gpd.GeoDataFrame(d, geometry = 'geometry', crs='EPSG:3857')
#     gdf = gdf.set_index('osmid')
#     gdf['osmid'] = gdf.index
#     return gdf

# def test_get_existing_network_seed_points(define_existing_network_spacing, create_existing_network_nodes, create_existing_network_seed_points):
#     assert_frame_equal(get_existing_network_seed_points(create_existing_network_nodes, define_existing_network_spacing), create_existing_network_seed_points, check_dtype=False)
