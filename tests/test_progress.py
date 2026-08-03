from importlib import import_module
from unittest import mock

import pytest

growbikenet_module = import_module("growbikenet.growbikenet")


@pytest.mark.parametrize(
    ("existing_network_spacing", "expected_total"),
    [(None, 1), (500, 2)],
)
def test_import_progress_total(existing_network_spacing, expected_total):
    """Count the optional existing bike network in imported-network progress."""
    import_files = {
        "city_boundary": None,
        "street_network": "street_network.gpkg",
        "bike_network": "bike_network.gpkg",
    }

    with (
        mock.patch.object(growbikenet_module, "validate_settings"),
        mock.patch.object(
            growbikenet_module, "validate_parameters", return_value=import_files
        ),
        mock.patch.object(growbikenet_module, "tqdm") as tqdm_mock,
        mock.patch.object(
            growbikenet_module,
            "import_network",
            side_effect=RuntimeError("stop after progress setup"),
        ),
        pytest.raises(RuntimeError, match="stop after progress setup"),
    ):
        growbikenet_module.growbikenet(
            city_name="Test City",
            existing_network_spacing=existing_network_spacing,
            import_files=import_files,
        )

    assert tqdm_mock.call_args.kwargs["total"] == expected_total
