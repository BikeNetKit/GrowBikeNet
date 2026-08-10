from growbikenet import constants
from growbikenet import settings
import geopandas as gpd
import os
import shutil
import pytest
import matplotlib.pyplot as plt
from growbikenet.visualization import (
    create_plots
)

# Consistent settings
settings.viz = {
    "bike_to_grow":{
        "color": "#999999",
        "line_width": 0.75,
    },
    "bike_grown":{
        "color": "#096a51",
        "line_width": 3,
    },
    "bike_existing":{
        "color": "#9999cc",
        "line_width": 2,
    },
    "seed_point":{
        "color": "#000000",
        "edgecolor": "#FFFFFF",
        "markersize": 60,
    },
    "dpi": 150,
}
settings.export_path["plots"] = "./tests/test_data/plots_temp/"
settings.crs_result = '3857' # Leave for testing temporarily at the old value. Change to 4326 when re-doing test data.

@pytest.fixture
def validation_gdf_athens_without_bikenw():
    gdf = gpd.read_file("./tests/test_data/athens_growbikenet_without-bikenw.gpkg", layer='Grown bike network')
    return gdf

@pytest.fixture
def validation_seed_points_athens_without_bikenw():
    gdf = gpd.read_file("./tests/test_data/athens_growbikenet_without-bikenw.gpkg", layer='Seed points')
    return gdf

@pytest.mark.mpl_image_compare(baseline_dir="test_data",
                            filename="athens_without-bikenw.png")
def test_create_plots_case_success_without_bikenw(validation_gdf_athens_without_bikenw, validation_seed_points_athens_without_bikenw):
    """Verify that the same last plot is created for the case without existing bike network
    """

    ordering = "betweenness"
    with_existing_bike_network = 0

    # Create directory
    os.makedirs(settings.export_path['plots']+"ordering_"+ordering+"/", exist_ok=True)

    # Run function
    figs = create_plots(validation_gdf_athens_without_bikenw, validation_seed_points_athens_without_bikenw, ordering, with_existing_bike_network)

    # Remove directory
    shutil.rmtree(settings.export_path['plots'])

    return figs[-1]


@pytest.fixture
def validation_gdf_athens_with_bikenw():
    gdf = gpd.read_file("./tests/test_data/athens_growbikenet_with-bikenw.gpkg", layer='Grown bike network')
    return gdf

@pytest.fixture
def validation_seed_points_athens_with_bikenw():
    gdf = gpd.read_file("./tests/test_data/athens_growbikenet_with-bikenw.gpkg", layer='Seed points')
    return gdf

@pytest.fixture
def validation_existing_gdf_athens_with_bikenw():
    gdf = gpd.read_file("./tests/test_data/athens_growbikenet_with-bikenw.gpkg", layer='Existing bike network')
    return gdf

@pytest.mark.mpl_image_compare(baseline_dir="test_data",
                            filename="athens_with-bikenw.png")
def test_create_plots_case_success_with_bikenw(validation_gdf_athens_with_bikenw, validation_seed_points_athens_with_bikenw, validation_existing_gdf_athens_with_bikenw):
    """Verify that the same last plot is created for the case with existing bike network
    """

    ordering = "betweenness"
    with_existing_bike_network = 1

    # Add existing bike network on top
    validation_gdf_athens_with_bikenw.loc[-1] = validation_existing_gdf_athens_with_bikenw.iloc[0]
    validation_gdf_athens_with_bikenw.index = validation_gdf_athens_with_bikenw.index+1
    validation_gdf_athens_with_bikenw.sort_index(inplace=True)
    
    # Create directory
    os.makedirs(settings.export_path['plots']+"ordering_"+ordering+"/", exist_ok=True)

    # Run function
    figs = create_plots(validation_gdf_athens_with_bikenw, validation_seed_points_athens_with_bikenw, ordering, with_existing_bike_network)

    # Remove directory
    shutil.rmtree(settings.export_path['plots'])

    return figs[-1]