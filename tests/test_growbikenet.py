import geopandas as gpd
import pytest
import pandas as pd
pd.set_option('display.max_columns', None) # for debugging
from pandas.testing import assert_frame_equal
import growbikenet as gbn

import_path = './tests/test_data/'
valcols = ['source', 'target', 'ordering', 'length', 'length_cumulative']
gbn.settings.import_path = import_path


@pytest.fixture
def validation_gdf_betweenness_grid_fromscratch():
    gdf = gpd.read_file(import_path+"badalona-growbikenet-betweenness-grid_square-from_scratch.geojson")
    return gdf
def test_growbikenet_betweenness_grid_fromscratch_success_offline(validation_gdf_betweenness_grid_fromscratch):
    """Verify that the offline version of growbikenet works as intended.
    betweenness, grid, from scratch
    """
    gbn.constants._CRS_CALCULATIONS = 'auto'
    edges_ordered = gbn.growbikenet(
        city_query="Badalona",
        ordering="betweenness",
        export_data=False,
        import_files={
            "growable_network":"badalona_growable_network.gpkg",
        },
    )
    assert_frame_equal(
        validation_gdf_betweenness_grid_fromscratch[valcols],
        edges_ordered[valcols],
        check_dtype=False,
    )

@pytest.fixture
def validation_gdf_betweenness_grid_frombikenw():
    gdf = gpd.read_file(import_path+"badalona-growbikenet-betweenness-grid_square-from_bikenw.geojson")
    return gdf
def test_growbikenet_betweenness_grid_frombikenw_success_offline(validation_gdf_betweenness_grid_frombikenw):
    """Verify that the offline version of growbikenet works as intended.
    betweenness, grid, from bikenw
    """
    gbn.constants._CRS_CALCULATIONS = 'auto'
    edges_ordered = gbn.growbikenet(
        city_query="Badalona",
        ordering="betweenness",
        existing_network_spacing='auto',
        export_data=False,
        import_files={
            "growable_network":"badalona_growable_network.gpkg",
            "bike_network":"badalona_bike_network.gpkg",
        },
    )
    l = len(validation_gdf_betweenness_grid_frombikenw)
    edges_ordered = edges_ordered[valcols].iloc[1:]
    edges_ordered.index = edges_ordered.index-1
    assert_frame_equal(
        validation_gdf_betweenness_grid_frombikenw[valcols],
        edges_ordered.reindex_like(validation_gdf_betweenness_grid_frombikenw[valcols]),
        check_dtype=False,
    )

@pytest.fixture
def validation_gdf_betweenness_railstations_fromscratch():
    gdf = gpd.read_file(import_path+"badalona-growbikenet-betweenness-rail_stations-from_scratch.geojson")
    return gdf
def test_growbikenet_betweenness_railstations_fromscratch_success_offline(validation_gdf_betweenness_railstations_fromscratch):
    """Verify that the offline version of growbikenet works as intended.
    betweenness, rail_stations, from scratch
    """
    gbn.constants._CRS_CALCULATIONS = 'auto'
    edges_ordered = gbn.growbikenet(
        city_query="Badalona",
        ordering="betweenness",
        export_data=False,
        import_files={
            "growable_network":"badalona_growable_network.gpkg",
            "seed_points":"badalona_rail_stations.gpkg",
        },
    )
    assert_frame_equal(
        validation_gdf_betweenness_railstations_fromscratch[valcols],
        edges_ordered[valcols],
        check_dtype=False,
    )

@pytest.fixture
def validation_gdf_closeness_grid_fromscratch():
    gdf = gpd.read_file(import_path+"badalona-growbikenet-closeness-grid_square-from_scratch.geojson")
    return gdf
def test_growbikenet_closeness_grid_fromscratch_success_offline(validation_gdf_closeness_grid_fromscratch):
    """Verify that the offline version of growbikenet works as intended.
    closeness, grid, from scratch
    """
    gbn.constants._CRS_CALCULATIONS = 'auto'
    edges_ordered = gbn.growbikenet(
        city_query="Badalona",
        ordering="closeness",
        export_data=False,
        import_files={
            "growable_network":"badalona_growable_network.gpkg",
        },
    )
    assert_frame_equal(
        validation_gdf_closeness_grid_fromscratch[valcols],
        edges_ordered[valcols],
        check_dtype=False,
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
    gdf = gpd.read_file(import_path+"turin_alpha1.gpkg", layer='Grown bike network')
    return gdf

@pytest.fixture
def validation_gdf_turin_alpha0_4():
    gdf = gpd.read_file(import_path+"turin_alpha0_4.gpkg", layer='Grown bike network')
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
                'growable_network':"turin_growable_network.gpkg",
                'point_data':"turin_crashes.gpkg",
                'trip_data':"turin_trips.csv",
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
                'growable_network':"turin_growable_network.gpkg",
                'trip_data':"turin_trips.csv",
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
                'growable_network':"turin_growable_network.gpkg",
                'point_data':"turin_crashes.gpkg",
                'trip_data':"turin_trips.csv",
            },
        )
    )