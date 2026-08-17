"""Global settings for growbikenet that can be configured by the user.

crs_result : str, default '4326'
    EPSG code of the coordinate reference system for the resulting geodataframe
    and exported data. If '4326' (WGS84) and `export_file_format` is set to 
    'geojson', data is exported via the RFC7946 standard.
export_path : dict(str)
    Paths to results and plots folders to save data and plots.
export_file_format : {'gpkg', 'geojson'}, default 'gpkg'
    File format for the data export, relevant if `export_data` is set to True. 
    If exporting as geojson, generates extra files for seed points and city 
    boundary. If exporting as gkpg, these are added all in one file as extra 
    layers.
import_data_impact : float, default 9
    Impact of imported trip or point data on results. Must be non-negative.
import_data_trip_point_balance : float, default 0.5
    Impact of imported trip data versus point data on results. Must be between 
    0 and 1, where 0 means no trip impact and full point impact, 1 means full 
    trip impact and no point impact, and 0.5 means balanced impact of both. If 
    only the trip data is imported, this variable is treated as 1; if only the 
    point data is imported, this variable is treated as 0 - meaning in such a 
    case the data impact is controlled only by `settings.import_data_impact`.
import_path : str
    Path to import files (as defined in growbikenet's import_files parameter).
import_point_data_snap_distance : int, default 500
    Maximum distance between point data and network links for snapping, in 
    meters.
import_trip_data_snap_distance : int, default 500
    Maximum distance between trip data and network links for snapping, in 
    meters.
random_seed : int, default 43
    Random number generator seed for reproducibility
seed_point_snap_distance : 'auto' or int, default 'auto'
    Maximum distance between raw seed points and osm nodes for snapping, 
    in meters.
    Auto-value is ceil(`seed_point_grid_spacing`*
    `constants._SEED_POINT_SNAP_DISTANCE_FACTOR`). If integer, must be positive. 
    The default values for seed_point_grid_spacing of 1000/1154/1707 are: 
    250/289/427
seed_point_type_name : str, default 'file'
    The name of the seed points in the exported file name, when 
    `seed_point_type` is set to 'file'.
silent : bool, default False
    If set to True, suppresses all user feedback. Useful for batch exports.
viz : dict
    Dictionary of visualization settings:

    - 'bike_to_grow' : dict
        Dictionary of properties for the bicycle network to grow but not yet grown.
    - 'bike_grown' : dict
        Dictionary of properties for the bicycle network grown.
    - 'bike_existing' : dict
        Dictionary of properties for the existing bicycle network.
    - 'seed_point' : dict
        Dictionary of properties for the seed points. Set 'markersize' to 0 to hide them.
    - 'crs' : str, default 'auto'
        The CRS used for plotting. Option 'auto' sets a local azimuthal projection centered on the network. Otherwise, for Europe '3035' (LAEA) and globally '54035' (Equal Earth) or '54030' (Robinson) also produce good results.
"""

crs_result = '4326'
export_path = {
    "results":"./results/",
    "plots":"./results/plots/",
}
export_file_format = 'gpkg'
import_data_impact = 9
import_data_trip_point_balance = 0.5
import_path = "./"
import_point_data_snap_distance = 500
import_trip_data_snap_distance = 500
random_seed = 43 # off-by-one error
seed_point_snap_distance = 'auto'
seed_point_type_name = 'file'
silent = False

# Viz/plot settings
viz = {
    'bike_to_grow':{
        'color': '#999999',
        'line_width': 0.75,
    },
    'bike_grown':{
        'color': '#096a51',
        'line_width': 3,
    },
    'bike_existing':{
        'color': '#9999cc',
        'line_width': 2,
    },
    'seed_point':{
        'color': '#000000',
        'edgecolor': '#FFFFFF',
        'markersize': 40,
    },
    'dpi': 150,
    'crs': 'auto',
}