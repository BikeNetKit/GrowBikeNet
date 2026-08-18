"""Global constants for `growbikenet` that can be tweaked during development, but 
should not be changed later by the user. Especially technical or internal 
constants start with an underscore.

PBI_CUSTOM_FILTER : list[str]
    Custom filter for protected bicycle infrastructure (pbi).
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
GROWABLE_NETWORK_CUSTOM_FILTER : list[str] or None
    Custom filter for all infrastructure elements that are considered as 
    growable by `growbikenet`. By default, `growbikenet` uses a custom filter 
    to retrieve the combined drive and pbi (protected bicycle infrastructure) 
    network. To only consider the drive network, set 
    `GROWABLE_NETWORK_CUSTOM_FILTER` to None and `GROWABLE_NETWORK_TYPE` to 
    'drive'. However, doing so can lead to issues: 
    https://github.com/BikeNetKit/GrowBikeNet/issues/255. 
GROWABLE_NETWORK_TYPE : {'drive', 'all', 'all_public', 'bike', 'drive_service', 'walk'}, default 'drive' 
        What type of street network to retrieve for the growable network if `GROWABLE_NETWORK_CUSTOM_FILTER` is None.
REORDER : bool, default True
    Decision whether ordering should be reordered after edge removal, as edge 
    removal can leave gaps.

_CRS_CALCULATIONS : str, default '3857'
    EPSG code of the coordinate reference system that is used to project OSM 
    data for calculations. The default '3857' is WGS 84 / Pseudo-Mercator. Note 
    that the CRS for plotting is not set here, but in `settings.viz['crs']`.
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
    of `existing_network_spacing`.
_BUFFER_SEED_POINTS_EXNW_FACTOR : float, default 0.5
    Factor to multiply `existing_network_spacing` with, to determine which 
    previously determined seed points (grid or rail) to drop that are too close 
    to the extra existing network points.
_BEARING_BINS : int, default 72
    Number of bins to determine bearing. e.g. 72 will create 5 degrees bins.

References
----------
.. [1] G. Boeing, `Urban spatial order: Street network orientation, configuration, and entropy`, Applied Network Science 4, 67 (2019)
"""

PBI_CUSTOM_FILTER = [
    '["highway"~"cycleway|living_street"]',
    '["highway"~"path|pedestrian"]["bicycle"~"designated|yes|permissive"]["access"!~"private"]',
    '["cyclestreet"]',
    '["cycleway"~"track"]',
    '["cycleway:right"~"track|opposite_track"]', # opposite_track is deprecated, but could still exist
    '["cycleway:left"~"track|opposite_track"]', # opposite_track is deprecated, but could still exist
    '["cycleway:both"~"track|opposite_track"]', # opposite_track is deprecated, but could still exist
]
# Populate ox.settings.useful_tags_way to make application of custom filter possible
import osmnx as ox
for custom_tag in ["highway", "cycleway", "bicycle", "cycleway:right", "cycleway:left", "cycleway:both", "cyclestreet", "access", "area", "service", "motor_vehicle", "motorcar"]: # This list should contain all tags used in any custom filters
    if custom_tag not in ox.settings.useful_tags_way:
        ox.settings.useful_tags_way.extend(custom_tag)

EXISTING_NETWORK_MINIMUM_COMPONENT_LENGTH = 100 

GRID_SPACING_TRIANGULATE = 1707 # a=2b/(2-sqrt(2))
GRID_SPACING_QUADRANGULATE = 1000 # a=2b
GRID_SPACING_TRIANGLE = 1154 # h/2=b=a*sqrt(3)/4 -> a=4b/sqrt(3)

GROWABLE_NETWORK_CUSTOM_FILTER = [ # adapted from https://github.com/gboeing/osmnx/blob/2fc39cb2792ff869881b99f724a2d97f0e958667/osmnx/_overpass.py#L77
    # Car infra - Instead of excluding what we don't want, we only include what we want. Note: we are OK with alleys and driveways
    '["highway"~"motorway|trunk|primary|secondary|tertiary|residential|motorway_link|trunk_link|primary_link|secondary_link|tertiary_link|service|unclassified"]["highway"!~"abandoned|construction|no|planned|platform|proposed|raceway|razed|rest_area|services"]["service"!~"emergency_access|parking|parking_aisle|private"]["area"!~"yes"]["access"!~"private"]["motor_vehicle"!~"no"]["motorcar"!~"no"]',
    # Bike infra, copied from PBI_CUSTOM_FILTER
    '["highway"~"cycleway|living_street"]',
    '["highway"~"path|pedestrian"]["bicycle"~"designated|yes|permissive"]["access"!~"private"]',
    '["cyclestreet"]',
    '["cycleway"~"track"]',
    '["cycleway:right"~"track|opposite_track"]', # opposite_track is deprecated, but could still exist
    '["cycleway:left"~"track|opposite_track"]', # opposite_track is deprecated, but could still exist
    '["cycleway:both"~"track|opposite_track"]', # opposite_track is deprecated, but could still exist
]
GROWABLE_NETWORK_TYPE = 'drive'

REORDER = True


_CRS_CALCULATIONS = '3857'
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