import pytest
import geopandas as gpd
import osmnx as ox
import growbikenet as gbn
from pandas.testing import assert_frame_equal

gbn.settings.export_path = {
    "results":"./results/",
    "plots":"./results/plots/",
}
gbn.settings.crs_result = '3857' # Leave for testing temporarily at the old value. Change to 4326 when re-doing test data.

@pytest.fixture
def validation_gdf_oelde():
    gdf = gpd.read_file("./tests/test_data/oelde_growbikenet.gpkg", layer='Grown bike network')
    return gdf

@pytest.fixture
def validation_gdf_athens():
    gdf = gpd.read_file("./tests/test_data/athens_growbikenet_with-bikenw.gpkg", layer='Grown bike network')
    return gdf

@pytest.fixture
def validation_gdf_asti():
    gdf = gpd.read_file("./tests/test_data/asti_growbikenet.gpkg", layer='Grown bike network')
    return gdf

# def test_growbikenet_case_success_online(validation_gdf_oelde):
#     """Verify that the online version of growbikenet works as intended.
#     This test might brake whenever Oelde is changed too much on OSM!
#     """
#     validation_gdf_oelde.equals(
#         gbn.growbikenet(
#             city_query="Oelde",
#             ranking="betweenness",
#             export_data=False,
#         )
#     )

def test_growbikenet_case_success_offline1(validation_gdf_oelde):
    """Verify that the offline version of growbikenet works as intended.
    """
    validation_gdf_oelde.equals(
        gbn.growbikenet(
            city_query="Oelde",
            ranking="betweenness",
            export_data=False,
            import_files={"street_network":"./tests/test_data/oelde_street_network.gpkg"},
        )
    )

def test_growbikenet_case_success_offline2(validation_gdf_athens):
    """Verify that the offline version of growbikenet works as intended, with existing bike network.
    """
    validation_gdf_athens.equals(
        gbn.growbikenet(
            city_query="Municipality of Athens",
            ranking="betweenness",
            export_data=False,
            existing_network_spacing='auto',
            import_files={
                "city_boundary":"./tests/test_data/athens_city_boundary.gpkg",
                "street_network":"./tests/test_data/athens_street_network.gpkg",
                "bike_network":"./tests/test_data/athens_bike_network.gpkg",
            }
        )
    )

def test_growbikenet_case_success_offline3(validation_gdf_asti):
    """Verify that the offline version of growbikenet works as intended. 
    Asti has previously caused a KeyError.

    To get the correct asti_street_network.gpkg, run the following:
    >>> city_boundary_gdf = ox.geocoder.geocode_to_gdf("Asti 16")
    >>> g = ox.graph_from_polygon(city_boundary_gdf.geometry[0], network_type="drive")
    >>> g = nx.MultiGraph(ox.convert.to_digraph(g))
    >>> ox.io.save_graph_geopackage(g, "asti_street_network.gpkg")
    """
    validation_gdf_asti.equals(
        gbn.growbikenet(
            city_query="Asti 16", # The 16 is needed to select the city, not the municipality (it doesn't matter here as the network is imported anyway, but it is important to know for exporting the street network asti_street_network.gpkg in the first place)
            ranking="betweenness",
            export_data=False,
            import_files={"street_network":"./tests/test_data/asti_street_network.gpkg"},
        )
    )

# def test_growbikenet_case_fail_rail1():
#     """Verify that when there are too few rail stations (Oelde), a 
#     RunTimeError is thrown.
#     """
#     with pytest.raises(Exception):
#         gbn.growbikenet(
#             "Oelde",
#             seed_point_type='rail',
#         )

# def test_growbikenet_case_fail_rail2():
#     """Verify that in the absence of rail stations (Andorra), an 
#     osmnx._errors.InsufficientResponseError is thrown.
#     """
#     with pytest.raises(ox._errors.InsufficientResponseError):
#         gbn.growbikenet(
#             "Andorra",
#             seed_point_type='rail',
#         )

# def test_growbikenet_case_fail_existing_network():
#     """Verify that in the absence of an existing bike network (Hallettsville), an 
#     osmnx._errors.InsufficientResponseError is thrown.
#     """
#     with pytest.raises(ox._errors.InsufficientResponseError):
#         gbn.growbikenet(
#             "Hallettsville",
#             existing_network_spacing=500,
#         )



# Tests with settings


@pytest.fixture
def validation_gdf_turin_alpha1():
    gdf = gpd.read_file("./tests/test_data/turin_alpha1.gpkg", layer='Grown bike network')
    return gdf

@pytest.fixture
def validation_gdf_turin_alpha0_4():
    gdf = gpd.read_file("./tests/test_data/turin_alpha0_4.gpkg", layer='Grown bike network')
    return gdf

def test_growbikenet_case_success_offline_import_data1(validation_gdf_turin_alpha1):
    """Verify that the offline version of growbikenet works as intended with import data sets.
    """
    gbn.settings.import_data_impact = 9
    gbn.settings.import_data_trip_point_balance = 1 # alpha

    validation_gdf_turin_alpha1.equals(
        gbn.growbikenet(
            "Turin", 
            import_files={
                'street_network':"./tests/test_data/turin_street_network.gpkg",
                'point_data':"./tests/test_data/turin_crashes.gpkg",
                'trip_data':"./tests/test_data/turin_trips.csv",
            },
        )
    )

def test_growbikenet_case_success_offline_import_data2(validation_gdf_turin_alpha1):
    """Verify that the offline version of growbikenet works as intended with import data sets.
    """
    gbn.settings.import_data_impact = 9
    gbn.settings.import_data_trip_point_balance = 1 # alpha
    
    validation_gdf_turin_alpha1.equals(
        gbn.growbikenet(
            "Turin", 
            import_files={
                'street_network':"./tests/test_data/turin_street_network.gpkg",
                'trip_data':"./tests/test_data/turin_trips.csv",
            },
        )
    )

def test_growbikenet_case_success_offline_import_data3(validation_gdf_turin_alpha0_4):
    """Verify that the offline version of growbikenet works as intended with import data sets.
    """
    gbn.settings.import_data_impact = 9
    gbn.settings.import_data_trip_point_balance = 0.4 # alpha

    validation_gdf_turin_alpha0_4.equals( 
        gbn.growbikenet(
            "Turin",
            import_files={
                'street_network':"./tests/test_data/turin_street_network.gpkg",
                'point_data':"./tests/test_data/turin_crashes.gpkg",
                'trip_data':"./tests/test_data/turin_trips.csv",
            },
        )
    )