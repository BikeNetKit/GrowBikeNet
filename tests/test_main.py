import pytest
from growbikenet.growbikenet import *

@pytest.fixture
def create_validation_gdf():
    gdf = gpd.read_file("./tests/test_data/a_edges.gpkg")
    return gdf

def test_growbikenet_main(create_validation_gdf):
    gdf = create_validation_gdf
    gdf.equals(growbikenet(city_name='Oelde', proj_crs='3857', ranking='betweenness_centrality', export_plots=False,
                           export_video=False))