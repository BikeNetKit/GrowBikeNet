import pytest
from pandas.testing import assert_frame_equal
from src.functions import *

@pytest.fixture
def create_geom_1():
    linestring = LineString([(0, 0), (1, 1), (2, 2)])
    return linestring

@pytest.fixture
def create_geom_2():
    linestring = LineString([(3, 3), (4, 4), (5, 5)])
    return linestring

def test_intersect(create_geom_1, create_geom_2):
    assert intersects_properly(create_geom_1, create_geom_2) is False

@pytest.fixture
def create_test_data_rank():
    df = pd.DataFrame((6, 2, 4), columns=['betweenness_centrality'])
    return df

@pytest.fixture
def create_validation_data_rank():
    ranked_df = pd.DataFrame(([6, 0], [4, 1], [2, 2]), columns=['betweenness_centrality','ordering'])
    return ranked_df

@pytest.fixture
def method():
    return "betweenness_centrality"

def test_rank(create_test_data_rank, method, create_validation_data_rank):
    assert_frame_equal(rank_df(create_test_data_rank, method), create_validation_data_rank, check_dtype=False)

@pytest.fixture
def define_seed_point_delta():
    return 500

@pytest.fixture
def create_snapped_seed_points():
    d = {'osmid': ['1', '2', '3'], 'geometry_generated': [Point(1000, 1000), Point(2000, 2000), Point(3000, 3000)]}
    gdf = gpd.GeoDataFrame(d, geometry='geometry_generated', crs='EPSG:3857')
    gdf['geometry_osm'] = gpd.GeoSeries([Point(1001, 1001), Point(10000, 10000), Point(3001, 3001)], crs='EPSG:3857')
    return gdf

@pytest.fixture
def create_filtered_seed_points():
    d = {'osmid':['1','3'], 'geometry':[Point(1001,1001), Point(3001,3001)]}
    gdf = gpd.GeoDataFrame(d, geometry = 'geometry', crs='EPSG:3857')
    gdf = gdf.set_index('osmid')
    gdf['osmid'] = gdf.index
    return gdf

def test_seed_point_filter(create_snapped_seed_points, create_filtered_seed_points, define_seed_point_delta):
    assert_frame_equal(filter_seed_points(create_snapped_seed_points, define_seed_point_delta), create_filtered_seed_points, check_dtype=False)

@pytest.fixture
def create_validation_triangulation():
    linestring = LineString([Point(1001,1001), Point(3001, 3001)])
    pair = '1', '3'
    d = {'pair': [list(pair)], 'potential_edge': [linestring], 'dist': [linestring.length]}
    df = pd.DataFrame(d)
    return df

def test_triangulation_creation(create_validation_triangulation, create_filtered_seed_points):
    assert_frame_equal(create_potential_triangulation(create_filtered_seed_points), create_validation_triangulation, check_dtype=False)

#def test_triangulation_filter():
