import contextlib
from importlib.metadata import PackageNotFoundError, version

from . import functions
from . import visualization
from growbikenet.growbikenet import growbikenet

__author__ = "Michael Szell, Manuel Knepper, Anastassia Vybornova"
__author_email__ = "michael@szell.net"

with contextlib.suppress(PackageNotFoundError):
    __version__ = version("growbikenet")
