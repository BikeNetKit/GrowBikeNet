from importlib import import_module
from unittest import mock

import pytest
import geopandas as gpd
import osmnx as ox
from growbikenet.growbikenet import growbikenet

growbikenet_module = import_module("growbikenet.growbikenet")

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

def test_growbikenet_case_success_online(validation_gdf_oelde):
    """Verify that the online version of growbikenet works as intended.
    This test might brake whenever Oelde is changed too much on OSM!
    """
    validation_gdf_oelde.equals(
        growbikenet(
            city_name="Oelde",
            ranking="betweenness_centrality",
            export_data=False,
        )
    )

def test_growbikenet_case_success_offline1(validation_gdf_oelde):
    """Verify that the offline version of growbikenet works as intended.
    """
    validation_gdf_oelde.equals(
        growbikenet(
            city_name="Oelde",
            ranking="betweenness_centrality",
            export_data=False,
            import_files={"street_network":"./tests/test_data/oelde_street_network.gpkg"},
        )
    )

def test_growbikenet_case_success_offline2(validation_gdf_athens):
    """Verify that the offline version of growbikenet works as intended, with existing bike network.
    """
    validation_gdf_athens.equals(
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
        growbikenet(
            city_name="Asti 16", # The 16 is needed to select the city, not the municipality (it doesn't matter here as the network is imported anyway, but it is important to know for exporting the street network asti_street_network.gpkg in the first place)
            ranking="betweenness_centrality",
            export_data=False,
            import_files={"street_network":"./tests/test_data/asti_street_network.gpkg"},
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


@pytest.mark.parametrize(
    ("existing_network_spacing", "expected_total"),
    [(None, 1), (500, 2)],
)
def test_import_progress_total(existing_network_spacing, expected_total):
    """Count the optional existing bike network in imported-network progress."""
    import_files = {
        "city_boundary": None,
        "street_network": "street_network.gpkg",
        "bike_network": "bike_network.gpkg",
    }

    with (
        mock.patch.object(growbikenet_module, "validate_settings"),
        mock.patch.object(
            growbikenet_module, "validate_parameters", return_value=import_files
        ),
        mock.patch.object(growbikenet_module, "tqdm") as tqdm_mock,
        mock.patch.object(
            growbikenet_module,
            "import_network",
            side_effect=RuntimeError("stop after progress setup"),
        ),
        pytest.raises(RuntimeError, match="stop after progress setup"),
    ):
        growbikenet_module.growbikenet(
            city_name="Test City",
            existing_network_spacing=existing_network_spacing,
            import_files=import_files,
        )

    assert tqdm_mock.call_args.kwargs["total"] == expected_total
