"""Global settings for growbikenet that can be configured by the user.

crs_projected : str, default '3857'
    EPSG code of the coordinate reference system that is used to project osm data. Default is '3857' (WGS 84 / Pseudo-Mercator). If this web mercator projection is not needed, then for Europe '3035' (LAEA) and globally '54035' (Equal Earth) or '54030' (Robinson) is better.
export_path : dict(str)
    Paths to results and plots folders to save data and plots.
export_file_format : str ('geojson' | 'gpkg'), default 'gpkg'
    File format for the data export, relevant if export_data set to True. If exporting as geojson, generates extra files for seed points and city boundary. If exporting as gkpg, these are added all in one file as extra layers.
import_data_impact : float, default 9
    Impact of imported trip or point data on results. Must be non-negative.
import_data_trip_point_balance : float, default 0.5
    Impact of imported trip data versus point data on results. Must be between 0 and 1, where 0 means no trip impact and full point impact, 1 means full trip impact and no point impact, and 0.5 means balanced impact of both. If only the trip data is imported, this variable is automatically set to 1; if only the point data is imported, this variable is automatically set to 0 - meaning in such a case the data impact is controlled only by settings.import_data_impact.
import_path : str
    Path to import files (as defined in growbikenet's import_files parameter).
random_seed : int
    Random number generator seed for reproducibility
seed_point_snap_distance : 'auto' | int, default 'auto'
    Maximum distance between raw seed points and osm nodes for snapping, in meters.
    Auto-value is ceil(seed_point_grid_spacing*constants._SEED_POINT_SNAP_DISTANCE_FACTOR). If integer, must be positive.
viz : dict
    Dictionary of visualization settings
"""

crs_projected = '3857'
export_path = {
    "results":"./results/",
    "plots":"./results/plots/",
}
export_file_format = 'gpkg'
import_path = "./"
random_seed = 42
seed_point_snap_distance = 'auto'

# Viz/plot settings
viz = {
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