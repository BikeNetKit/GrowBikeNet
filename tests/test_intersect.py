import pytest

from src.functions import *

@pytest.fixture
def create_geom_1():
    linestring = LineString([(0, 0), (1, 1), (2, 2)])
    return linestring

@pytest.fixture
def create_geom_2():
    linestring = LineString([(3, 3), (4, 4), (5, 5)])
    return linestring

def test_intersect(create_geom_1, create_geom_2):
    assert intersects_properly(create_geom_1, create_geom_2) is False