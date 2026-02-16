import pytest
from pandas.testing import assert_frame_equal
from src.functions import *

@pytest.fixture
def create_test_data():
    df = pd.DataFrame((6, 2, 4), columns=['betweenness_centrality'])
    return df

@pytest.fixture
def create_validation_data():
    ranked_df = pd.DataFrame(([6, 0], [4, 1], [2, 2]), columns=['betweenness_centrality','ordering'])
    return ranked_df

@pytest.fixture
def method():
    return "betweenness_centrality"

#@pytest.mark.parametrize(create_test_data, method, create_validation_data)
def test_rank(create_test_data, method, create_validation_data):
    assert_frame_equal(rank_df(create_validation_data, method), create_validation_data, check_dtype=False)