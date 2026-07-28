from growbikenet import constants
from growbikenet import settings
import geopandas as gpd
import os
import shutil
import pytest
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
settings.export_path = {
    "plots":"./tests/test_data/plots_temp/",
    "videos":"./tests/test_data/videos_temp/",
}

@pytest.fixture
def validation_plot_without_bikenw():
    plot = open("./tests/test_data/athens_without-bikenw_0058.png","rb").read()
    return plot

@pytest.fixture
def validation_gdf_athens_without_bikenw():
    gdf = gpd.read_file("./tests/test_data/athens_growbikenet_without-bikenw.gpkg", layer='Grown bike network')
    return gdf

@pytest.fixture
def validation_seed_points_athens_without_bikenw():
    gdf = gpd.read_file("./tests/test_data/athens_growbikenet_without-bikenw.gpkg", layer='Seed points')
    return gdf

def test_create_plots_case_success_without_bikenw(validation_plot_without_bikenw, validation_gdf_athens_without_bikenw, validation_seed_points_athens_without_bikenw):
    """Verify that the same last plot at step 58 is created for the case without existing bike network
    """

    ranking = "betweenness_centrality"
    with_existing_bike_network = 0

    # Create directory
    os.makedirs(settings.export_path['plots']+"ordering_"+ranking+"/", exist_ok=True)

    # Run function
    create_plots(validation_gdf_athens_without_bikenw, validation_seed_points_athens_without_bikenw, ranking, with_existing_bike_network)

    assert validation_plot_without_bikenw == open(settings.export_path['plots']+"ordering_betweenness_centrality/0058.png","rb").read()

    # Remove directory
    shutil.rmtree(settings.export_path['plots'])


@pytest.fixture
def validation_plot_with_bikenw():
    plot = open("./tests/test_data/athens_with-bikenw_0069.png","rb").read()
    return plot

@pytest.fixture
def validation_existing_gdf_athens_with_bikenw():
    gdf = gpd.read_file("./tests/test_data/athens_growbikenet_with-bikenw.gpkg", layer='Existing bike network')
    return gdf

@pytest.fixture
def validation_gdf_athens_with_bikenw():
    gdf = gpd.read_file("./tests/test_data/athens_growbikenet_with-bikenw.gpkg", layer='Grown bike network')
    return gdf

@pytest.fixture
def validation_seed_points_athens_with_bikenw():
    gdf = gpd.read_file("./tests/test_data/athens_growbikenet_with-bikenw.gpkg", layer='Seed points')
    return gdf

def test_create_plots_case_success_with_bikenw(validation_plot_with_bikenw, validation_gdf_athens_with_bikenw, validation_seed_points_athens_with_bikenw, validation_existing_gdf_athens_with_bikenw):
    """Verify that the same plot at step 69 is created for the case with existing bike network
    """

    ranking = "betweenness_centrality"
    with_existing_bike_network = 1

    # Create directory
    os.makedirs(settings.export_path['plots']+"ordering_"+ranking+"/", exist_ok=True)
    
    # Add existing bike network on top
    validation_gdf_athens_with_bikenw.loc[-1] = validation_existing_gdf_athens_with_bikenw.iloc[0]
    validation_gdf_athens_with_bikenw.index = validation_gdf_athens_with_bikenw.index+1
    validation_gdf_athens_with_bikenw.sort_index(inplace=True)

    # Run function
    create_plots(validation_gdf_athens_with_bikenw, validation_seed_points_athens_with_bikenw, ranking, with_existing_bike_network)

    assert validation_plot_with_bikenw == open(settings.export_path['plots']+"ordering_betweenness_centrality/0069.png","rb").read()

    # Remove directory
    shutil.rmtree(settings.export_path['plots']) 
    