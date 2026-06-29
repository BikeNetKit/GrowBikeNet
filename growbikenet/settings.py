'''
Global settings for growbikenet that can be configured by the user.

export_path : dict(str | Path)
    Paths to results, plots, and video folders to save data, plots, and videos. 
import_path : str | Path
    Path to import files (as defined in growbikenet's import_files parameter).
crs_projected : str, default '3857'
    EPSG code of the coordinate reference system that is used to project osm data. Default is '3857' (WGS 84 / Pseudo-Mercator). If this web mercator projection is not needed, then for Europe '3035' (LAEA) and globally '54035' (Equal Earth) is better.

'''



export_path = {
    "results":"./results/",
    "plots":"./results/plots/",
    "videos":"./results/videos/",
}

import_path = "./"

crs_projected = '3857'