'''
Global constants for growbikenet that can be tweaked during development, but should not be changed later by the user.

PBI_CUSTOM_FILTER : list
    Custom filter for protected bicycle infrastructure (pbi)
PRESET_TAGS : dict
    Pre-defined tags to select tags as seed points
PHI_LIMITS : list
    Two orientation order limits between street networks with:
    1) negligible grid elements, 2) some grid elements, 3) grid.
    We aimed to use the tercile limits from the paper [3]_ (Fig 2), but the values here are lower for unknown reasons, also with the unweighted version. Also, it was aimed to have Barcelona in the grid category. For these reasons, the limits were lowered.
EXISTING_NETWORK_MINIMUM_COMPONENT_LENGTH : int
    Minimum length a bike network component needs to have for seed points to snap
'''


PBI_CUSTOM_FILTER = ['["cycleway"~"track"]',
          '["highway"~"cycleway"]',
          '["highway"~"path"]["bicycle"~"designated"]',
          '["cycleway:right"~"track"]',
          '["cycleway:left"~"track"]',
          '["cycleway:both"~"track"]',
          '["cycleway:right"~"opposite_track"]', # deprecated, but could still exist
          '["cycleway:left"~"opposite_track"]', # deprecated, but could still exist
          '["cycleway:both"~"opposite_track"]', # deprecated, but could still exist
          '["cyclestreet"]',
          '["highway"~"living_street"]'
        ]
# Populate ox.settings.useful_tags_way to make application of custom filter possible
import osmnx as ox
for custom_tag in ["cycleway", "bicycle", "cycleway:right", "cycleway:left", "cycleway:both", "cyclestreet"]:
    if custom_tag not in ox.settings.useful_tags_way:
        ox.settings.useful_tags_way.extend(custom_tag)

PRESET_TAGS = {
            "rail": {"railway": ["station", "halt"]},
            "school": {"amenity": ["kindergarten", "school", "college", "university"]},
            "park": {"leisure": ["park", "garden", "nature_reserve", "bathing_place"]},
            }

PHI_LIMITS = [0.02, 0.08] # Tercile limits in the paper: 0.033, 0.161

EXISTING_NETWORK_MINIMUM_COMPONENT_LENGTH = 100 
