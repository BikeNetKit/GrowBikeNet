'''Constants for growbikenet.'''

# Pre-defined tags to select tags as seed points
PRESET_TAGS = {
            "rail": {"railway": ["station", "halt"]},
            "school": {"amenity": ["kindergarten", "school", "college", "university"]},
            "park": {"leisure": ["park", "garden", "nature_reserve", "bathing_place"]},
            }

# Orientation order limits between street networks with:
# 1) negligible grid elements, 2) some grid elements, 3) grid.
# We aimed to use the tercile limits from the paper [3]_ (Fig 2), but the values
# here are lower for unknown reasons, also with the unweighted version. Also, it was aimed to have Barcelona in the grid category. For these reasons, the limits were lowered.
PHI_LIMITS = [0.02, 0.08] # Tercile limits in the paper: 0.033, 0.161

# Minimum length a bike network component needs to have for seed points to snap
EXISTING_NETWORK_MINIMUM_COMPONENT_LENGTH = 100 