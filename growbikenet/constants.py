"""Global constants for `growbikenet` that can be tweaked during development, but 
should not be changed later by the user. Especially technical or internal 
constants start with an underscore.

EXISTING_NETWORK_MINIMUM_COMPONENT_LENGTH : int, default 100
    Minimum length a bike network component needs to have for seed points to 
    snap, in meters.
GRID_SPACING_TRIANGULATE : int, default 1707
    Grid spacing in meters for grid triangulation that ensures that any point 
    in the city is always within buffer distance b=500m of the network (if seed 
    points snap perfectly).
GRID_SPACING_QUADRANGULATE : int, default 1000
    Grid spacing in meters for quadrangulation that ensures that any point in 
    the city is always within buffer distance b=500m of the network (if seed 
    points snap perfectly).
GRID_SPACING_TRIANGLE : int, default 1154
    Grid spacing in meters for triangle grid that ensures that any point in the 
    city is always within buffer distance b=500m of the network (if seed points 
    snap perfectly).
REORDER : bool, default True
    Decision whether ordering should be reordered after edge removal, as edge 
    removal can leave gaps.
_CRS_CALCULATIONS : str, default 'auto'
    EPSG code of the coordinate reference system that is used to project OSM 
    data for calculations. This has to be a distance-preserving projected CRS, 
    so '3857' (WGS 84 / Pseudo-Mercator) would be wrong! Option 'auto' selects
    the best UTM via `estimate_utm_crs()`. Note that the CRS for plotting is 
    unrelated - it is instead set in `settings.viz['crs']`.
_PRESET_TAGS : dict
    Pre-defined tags to select tags as seed points
_PHI_LIMITS : list[float], default [0.02, 0.08]
    Two orientation order limits between street networks with:
    1) negligible grid elements, 2) some grid elements, 3) grid.
    We aimed to use the tercile limits from the paper [1]_ (Fig 2), but the 
    values here are lower for unknown reasons, also with the unweighted 
    version. Also, it was aimed to have Barcelona in the grid category. For 
    these reasons, the limits were lowered.
_SEED_POINT_SNAP_DISTANCE_FACTOR : float, default 0.25
    Factor to multiply `seed_point_grid_spacing` with, to determine auto value 
    of `seed_point_snap_distance`.
_EXISTING_NETWORK_SPACING_FACTOR : float, default 0.5
    Factor to multiply `seed_point_grid_spacing` with, to determine auto value 
    of `existing_network_spacing`. A value of 0.5 means that the seed points
    for the existing bicycle network will be twice as dense as the regular seed
    points.
_BUFFER_SEED_POINTS_EXNW_FACTOR : float, default 0.5
    Factor to multiply `existing_network_spacing` with, to determine which 
    previously determined seed points (grid or rail) to drop that are too close 
    to the extra existing network points. A value of 0.5 means that, if the 
    existing bicycle network is dense, almost all grid or rail seed points will
    be dropped.
_BEARING_BINS : int, default 72
    Number of bins to determine bearing. e.g. 72 will create 5 degrees bins.
_PROGRESS_BAR_LENGTH : int, default 23
    Character length of tqdm progress bars.
_PROGRESS_BAR_DESC_LENGTH : int, default 23
    Character length of tqdm progress bar descriptions. This is the space given 
    to text like "Importing network data ", which is at the maximum of 23 
    characters.
_ROUTING_PENALTY : dict, default {0: 1.5, 1: 1}
    Factor to multiply length of non-pbi/pbi for routing, to avoid routing
    through parallel streets when slightly longer pbi is available. By 
    default, non-pbi counts as 50% longer than pbi, reflected in the value 1.5.

References
----------
.. [1] G. Boeing, `Urban spatial order: Street network orientation, configuration, and entropy`, Applied Network Science 4, 67 (2019)
"""

EXISTING_NETWORK_MINIMUM_COMPONENT_LENGTH = 100 

GRID_SPACING_TRIANGULATE = 1707 # a=2b/(2-sqrt(2))
GRID_SPACING_QUADRANGULATE = 1000 # a=2b
GRID_SPACING_TRIANGLE = 1154 # h/2=b=a*sqrt(3)/4 -> a=4b/sqrt(3)

REORDER = True

_CRS_CALCULATIONS = 'auto'
_PRESET_TAGS = {
            "rail": {"railway": ["station", "halt"]},
            "school": {"amenity": ["kindergarten", "school", "college", "university"]},
            "park": {"leisure": ["park", "garden", "nature_reserve", "bathing_place"]},
            }

_PHI_LIMITS = [0.02, 0.08] # Tercile limits in the paper: 0.033, 0.161

_SEED_POINT_SNAP_DISTANCE_FACTOR = 0.25

_EXISTING_NETWORK_SPACING_FACTOR = 0.5

_BUFFER_SEED_POINTS_EXNW_FACTOR = 0.5

_BEARING_BINS = 72

_PROGRESS_BAR_LENGTH = 23
_PROGRESS_BAR_DESC_LENGTH = 23

_ROUTING_PENALTY = {0: 1.5, 1: 1}
