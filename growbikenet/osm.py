"""Global constants related to OpenStreetMap(OSM).

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
PBI_CUSTOM_FILTER : list[str]
    Custom filter for protected bicycle infrastructure (pbi).
PBI_DICT : dict
    Dictionary for protected bicycle infrastructure (pbi), for single criteria.
PBI_DICT_SUB : dict
    Dictionary for protected bicycle infrastructure (pbi), with one 
    sub-criterion. For example, highway~path AND bicycle~designated. Always 
    adds a second criterion access!~private.
ROUTING_PENALTY : dict, default {0: 1.5, 1: 1}
    Factor to multiply length of non-pbi/pbi for routing, to avoid routing
    through parallel streets when slightly longer pbi is available. By 
    default, non-pbi counts as 50% longer than pbi.
"""

# Populate ox.settings.useful_tags_way to make application of custom filter possible
import osmnx as ox
for custom_tag in ["highway", "cycleway", "bicycle", "cycleway:right", "cycleway:left", "cycleway:both", "cyclestreet", "access", "area", "service", "motor_vehicle", "motorcar"]: # This list should contain all tags used in any custom filters
    if custom_tag not in ox.settings.useful_tags_way:
        ox.settings.useful_tags_way.extend(custom_tag)


GROWABLE_NETWORK_CUSTOM_FILTER = [ # adapted from https://github.com/gboeing/osmnx/blob/2fc39cb2792ff869881b99f724a2d97f0e958667/osmnx/_overpass.py#L77
    # Car infra - Instead of excluding what we don't want, we only include what we want. Note: we are OK with alleys and driveways
    '["highway"~"motorway|trunk|primary|secondary|tertiary|residential|motorway_link|trunk_link|primary_link|secondary_link|tertiary_link|service|unclassified"]["highway"!~"abandoned|construction|no|planned|platform|proposed|raceway|razed|rest_area|services"]["service"!~"emergency_access|parking|parking_aisle|private"]["area"!~"yes"]["access"!~"private"]["motor_vehicle"!~"no"]["motorcar"!~"no"]',
    # Bike infra, copied from PBI_CUSTOM_FILTER
    '["highway"~"cycleway|living_street"]',
    '["highway"~"path|pedestrian|footway"]["bicycle"~"designated|yes|permissive"]["access"!~"private"]',
    '["cyclestreet"~"yes"]',
    '["bicycle_road"~"yes"]',
    '["cycleway"~"track"]',
    '["cycleway:right"~"track|opposite_track"]', # opposite_track is deprecated, but could still exist
    '["cycleway:left"~"track|opposite_track"]', # opposite_track is deprecated, but could still exist
    '["cycleway:both"~"track|opposite_track"]', # opposite_track is deprecated, but could still exist
]

GROWABLE_NETWORK_TYPE = 'drive'

PBI_CUSTOM_FILTER = [
    '["highway"~"cycleway|living_street"]',
    '["highway"~"path|pedestrian|footway"]["bicycle"~"designated|yes|permissive"]["access"!~"private"]',
    '["cyclestreet"~"yes"]',
    '["bicycle_road"~"yes"]',
    '["cycleway"~"track"]',
    '["cycleway:right"~"track|opposite_track"]', # opposite_track is deprecated, but could still exist
    '["cycleway:left"~"track|opposite_track"]', # opposite_track is deprecated, but could still exist
    '["cycleway:both"~"track|opposite_track"]', # opposite_track is deprecated, but could still exist
]

PBI_DICT = {
    'highway': ['cycleway','living_street'],
    'cyclestreet': ['yes'],
    'bicycle_road': ['yes'],
    'cycleway': ['track'],
    'cycleway:right': ['track','opposite_track'],
    'cycleway:left': ['track','opposite_track'],
    'cycleway:both': ['track','opposite_track'],
}
PBI_DICT_SUB = {
    'highway': [
        ['path','pedestrian','footway'],
        {'bicycle': ['designated','yes','permissive']},
    ]
}

ROUTING_PENALTY = {0: 1.5, 1: 1}

