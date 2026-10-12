"""
GrowBikeNet is a Python package to grow an urban bicycle network from scratch 
or from an existing bicycle network.

Full documentation at: https://docs.bikenetkit.org/GrowBikeNet/

If you use GrowBikeNet, please cite: https://doi.org/10.1038/s41598-022-10783-y
"""

import contextlib
from importlib.metadata import PackageNotFoundError, version

from growbikenet.growbikenet import growbikenet
from . import constants
from . import growbikenet
from . import osm
from . import settings
from . import utils
from . import visualization

__author__ = "GrowBikeNet contributors"
__author_email__ = "michael@szell.net"

with contextlib.suppress(PackageNotFoundError):
    __version__ = version("growbikenet")
