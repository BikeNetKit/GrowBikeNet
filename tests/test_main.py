import pytest
from growbikenet.growbikenet import *

@pytest.fixture
def create_validation_gdf():
    gdf = gpd.read_file("./tests/test_data/oelde_growbikenet.gpkg")
    return gdf

def test_growbikenet(create_validation_gdf):
    create_validation_gdf.equals(growbikenet(city_name="Oelde", proj_crs='3857', ranking='all', export_data=False, export_plots=False,
                           export_video=False))