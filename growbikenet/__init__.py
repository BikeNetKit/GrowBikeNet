import contextlib
from importlib.metadata import PackageNotFoundError, version

from . import functions
from . import visualizations
from growbikenet.growbikenet import growbikenet

__author__ = "MS, AV, MK"
__author_email__ = "email@domain.com"

with contextlib.suppress(PackageNotFoundError):
    __version__ = version("growbikenet")
