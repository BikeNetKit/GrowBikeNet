import pytest
import geopandas as gpd
import osmnx as ox
from growbikenet.growbikenet import growbikenet

@pytest.fixture
def create_validation_gdf_oelde():
    gdf = gpd.read_file("./tests/test_data/oelde_growbikenet.gpkg", layer='Grown bike network')
    return gdf

@pytest.fixture
def create_validation_gdf_athens():
    gdf = gpd.read_file("./tests/test_data/athens_growbikenet_with-bikenw.gpkg", layer='Grown bike network')
    return gdf

def test_growbikenet_case_success_online(create_validation_gdf_oelde):
    """Verify that the online version of growbikenet works as intended.
    This test might brake whenever Oelde is changed too much on OSM!
    """
    create_validation_gdf_oelde.equals(
        growbikenet(
            city_name="Oelde",
            ranking="betweenness_centrality",
            export_data=False,
        )
    )

def test_growbikenet_case_success_offline1(create_validation_gdf_oelde):
    """Verify that the offline version of growbikenet works as intended.
    """
    create_validation_gdf_oelde.equals(
        growbikenet(
            city_name="Oelde",
            ranking="betweenness_centrality",
            export_data=False,
            import_files={"street_network":"./tests/test_data/oelde_street_network.gpkg"},
        )
    )

def test_growbikenet_case_success_offline2(create_validation_gdf_athens):
    """Verify that the offline version of growbikenet works as intended, with existing bike network.
    """
    create_validation_gdf_athens.equals(
        growbikenet(
            city_name="Municipality of Athens",
            ranking="betweenness_centrality",
            export_data=False,
            existing_network_spacing='auto',
            import_files={
                "city_boundary":"./tests/test_data/athens_city_boundary.gpkg",
                "street_network":"./tests/test_data/athens_street_network.gpkg",
                "bike_network":"./tests/test_data/athens_bike_network.gpkg",
            }
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
