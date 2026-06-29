"""Global settings for growbikenet that can be configured by the user.

export_path : dict(str | Path)
    Paths to results, plots, and video folders to save data, plots, and videos. 
import_path : str | Path
    Path to import files (as defined in growbikenet's import_files parameter).
crs_projected : str, default '3857'
    EPSG code of the coordinate reference system that is used to project osm data. Default is '3857' (WGS 84 / Pseudo-Mercator). If this web mercator projection is not needed, then for Europe '3035' (LAEA) and globally '54035' (Equal Earth) is better.
export_file_format : str ('geojson' | 'gpkg'), default 'gpkg'
    File format for the data export, relevant if export_data set to True. If exporting as geojson, generates extra files for seed points and city boundary. If exporting as gkpg, these are added all in one file as extra layers.
seed_point_snap_distance : 'auto' | int, default 'auto'
    Maximum distance between raw seed points and osm nodes for snapping, in meters.
    Auto-value is ceil(seed_point_grid_spacing*constants.SEED_POINT_SNAP_DISTANCE_FACTOR). If integer, must be positive.
random_seed : int
    Random number generator seed for reproducibility
"""

export_path = {
    "results":"./results/",
    "plots":"./results/plots/",
    "videos":"./results/videos/",
}
import_path = "./"
crs_projected = '3857'
export_file_format = 'gpkg'
seed_point_snap_distance = 'auto'
random_seed = 42
