import pytest
import geopandas as gpd
import osmnx as ox
from growbikenet.growbikenet import growbikenet

@pytest.fixture
def create_validation_gdf():
    gdf = gpd.read_file("./tests/test_data/oelde_growbikenet.gpkg", layer='Grown bike network')
    return gdf

def test_growbikenet_case_success(create_validation_gdf):
    create_validation_gdf.equals(
        growbikenet(
            city_name="Oelde",
            proj_crs="3857",
            ranking="betweenness_centrality",
            export_data=False,
            export_plots=False,
            export_video=False,
        )
    )

def test_growbikenet_case_fail_rail1():
    """Verify that when there are too few rail stations (Oelde), a 
    RunTimeError is thrown.
    """
    with pytest.raises(Exception):
        growbikenet(
            "Oelde",
            seed_point_type='rail',
        )

def test_growbikenet_case_fail_rail2():
    """Verify that in the absence of rail stations (Andorra), an 
    osmnx._errors.InsufficientResponseError is thrown.
    """
    with pytest.raises(ox._errors.InsufficientResponseError):
        growbikenet(
            "Andorra",
            seed_point_type='rail',
        )

def test_growbikenet_case_fail_existing_network():
    """Verify that in the absence of an existing bike network (Hallettsville), an 
    osmnx._errors.InsufficientResponseError is thrown.
    """
    with pytest.raises(ox._errors.InsufficientResponseError):
        growbikenet(
            "Hallettsville",
            existing_network_spacing=500,
        )
