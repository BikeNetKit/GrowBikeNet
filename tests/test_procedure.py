import pytest
import growbikenet
from growbikenet import constants, settings
from growbikenet._procedure import (
    _gbn_validate_settings,
    _gbn_validate_parameters
)


def test_gbn_validate_settings():
    constants._CRS_CALCULATIONS = False
    with pytest.raises(TypeError):
        _gbn_validate_settings()
    constants._CRS_CALCULATIONS = 'auto'
    settings.export_file_format = 'test'
    with pytest.raises(ValueError):
        _gbn_validate_settings()
    settings.export_file_format = 'gpkg'
    settings.seed_point_snap_distance = 'test'
    with pytest.raises(TypeError):
        _gbn_validate_settings()
    settings.seed_point_snap_distance = -3
    with pytest.raises(ValueError):
        _gbn_validate_settings()

settings.seed_point_snap_distance = 'auto'

def test_gbn_validate_parameters():
    with pytest.raises(TypeError):
        _gbn_validate_parameters(city_query=7, ordering='betweenness', seed_point_type='auto', seed_point_grid_spacing='auto', seed_point_linking='auto', existing_network_spacing='auto', export_data=True, city_id=None, export_plots=False, import_files={}, seed_point_tags=None)
    with pytest.raises(TypeError):
        _gbn_validate_parameters(city_query='Oelde', ordering=7, seed_point_type='auto',
                                 seed_point_grid_spacing='auto', seed_point_linking='auto',
                                 existing_network_spacing='auto', export_data=True, city_id=None, export_plots=False,
                                 import_files={}, seed_point_tags=None)
    with pytest.raises(ValueError):
        _gbn_validate_parameters(city_query='Oelde', ordering='auto', seed_point_type='auto',
                                 seed_point_grid_spacing='auto', seed_point_linking='auto',
                                 existing_network_spacing='auto', export_data=True, city_id=None, export_plots=False,
                                 import_files={}, seed_point_tags=None)
    with pytest.raises(ValueError):
        _gbn_validate_parameters(city_query='Oelde', ordering='betweenness', seed_point_type='test',
                                 seed_point_grid_spacing='auto', seed_point_linking='auto',
                                 existing_network_spacing='auto', export_data=True, city_id=None, export_plots=False,
                                 import_files={}, seed_point_tags=None)
    with pytest.raises(TypeError):
        _gbn_validate_parameters(city_query='Oelde', ordering='betweenness', seed_point_type='auto',
                                 seed_point_grid_spacing='test', seed_point_linking='auto',
                                 existing_network_spacing='auto', export_data=True, city_id=None, export_plots=False,
                                 import_files={}, seed_point_tags=None)
    with pytest.raises(ValueError):
        _gbn_validate_parameters(city_query='Oelde', ordering='betweenness', seed_point_type='auto',
                                 seed_point_grid_spacing=-2, seed_point_linking='auto',
                                 existing_network_spacing='auto', export_data=True, city_id=None, export_plots=False,
                                 import_files={}, seed_point_tags=None)
    with pytest.raises(TypeError):
        _gbn_validate_parameters(city_query='Oelde', ordering='betweenness', seed_point_type='auto',
                                 seed_point_grid_spacing='auto', seed_point_linking='auto',
                                 existing_network_spacing='auto', export_data=True, city_id=None, export_plots=False,
                                 import_files=7, seed_point_tags=None)
    with pytest.raises(ValueError):
        _gbn_validate_parameters(city_query='Oelde', ordering='betweenness', seed_point_type='file',
                                 seed_point_grid_spacing='auto', seed_point_linking='auto',
                                 existing_network_spacing='auto', export_data=True, city_id=None, export_plots=False,
                                 import_files={}, seed_point_tags=None)
    with pytest.raises(ValueError):
        _gbn_validate_parameters(city_query='Oelde', ordering='betweenness', seed_point_type='tags',
                                 seed_point_grid_spacing='auto', seed_point_linking='auto',
                                 existing_network_spacing='auto', export_data=True, city_id=None, export_plots=False,
                                 import_files={}, seed_point_tags=None)
    with pytest.raises(ValueError):
        _gbn_validate_parameters(city_query='Oelde', ordering='betweenness', seed_point_type='auto',
                                 seed_point_grid_spacing='auto', seed_point_linking='test',
                                 existing_network_spacing='auto', export_data=True, city_id=None, export_plots=False,
                                 import_files={}, seed_point_tags=None)
    with pytest.raises(ValueError):
        _gbn_validate_parameters(city_query='Oelde', ordering='betweenness', seed_point_type='auto',
                                 seed_point_grid_spacing='auto', seed_point_linking='quadrangulate',
                                 existing_network_spacing='auto', export_data=True, city_id=None, export_plots=False,
                                 import_files={}, seed_point_tags=None)
    with pytest.raises(TypeError):
        _gbn_validate_parameters(city_query='Oelde', ordering='betweenness', seed_point_type='auto',
                                 seed_point_grid_spacing='auto', seed_point_linking='auto',
                                 existing_network_spacing='test', export_data=True, city_id=None, export_plots=False,
                                 import_files={}, seed_point_tags=None)
    with pytest.raises(ValueError):
        _gbn_validate_parameters(city_query='Oelde', ordering='betweenness', seed_point_type='auto',
                                 seed_point_grid_spacing='auto', seed_point_linking='auto',
                                 existing_network_spacing=-2, export_data=True, city_id=None, export_plots=False,
                                 import_files={}, seed_point_tags=None)
    with pytest.raises(TypeError):
        _gbn_validate_parameters(city_query='Oelde', ordering='betweenness', seed_point_type='auto',
                                 seed_point_grid_spacing='auto', seed_point_linking='auto',
                                 existing_network_spacing='auto', export_data='test', city_id=None, export_plots=False,
                                 import_files={}, seed_point_tags=None)
    with pytest.raises(TypeError):
        _gbn_validate_parameters(city_query='Oelde', ordering='betweenness', seed_point_type='auto',
                                 seed_point_grid_spacing='auto', seed_point_linking='auto',
                                 existing_network_spacing='auto', export_data=True, city_id=7, export_plots=False,
                                 import_files={}, seed_point_tags=None)
    with pytest.raises(ValueError):
        _gbn_validate_parameters(city_query='Oelde', ordering='betweenness', seed_point_type='auto',
                                 seed_point_grid_spacing='auto', seed_point_linking='auto',
                                 existing_network_spacing='auto', export_data=True, city_id='', export_plots=False,
                                 import_files={}, seed_point_tags=None)
    with pytest.raises(TypeError):
        _gbn_validate_parameters(city_query='Oelde', ordering='betweenness', seed_point_type='auto',
                                 seed_point_grid_spacing='auto', seed_point_linking='auto',
                                 existing_network_spacing='auto', export_data=True, city_id=None, export_plots='test',
                                 import_files={}, seed_point_tags=None)
    with pytest.raises(FileNotFoundError):
        _gbn_validate_parameters(city_query='Oelde', ordering='betweenness', seed_point_type='auto',
                                 seed_point_grid_spacing='auto', seed_point_linking='auto',
                                 existing_network_spacing='auto', export_data=True, city_id=None, export_plots=False,
                                 import_files={'city_boundary': 'test'}, seed_point_tags=None)
    with pytest.raises(TypeError):
        _gbn_validate_parameters(city_query='Oelde', ordering='betweenness', seed_point_type='auto',
                                 seed_point_grid_spacing='auto', seed_point_linking='auto',
                                 existing_network_spacing='auto', export_data=True, city_id=None, export_plots=False,
                                 import_files={}, seed_point_tags='test')