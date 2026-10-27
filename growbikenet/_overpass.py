"""Overpass settings for `growbikenet`. Do not change."""

_op_ref = "GrowBikeNet Python package (https://github.com/BikeNetKit/GrowBikeNet)"

import osmnx.settings as oxs
oxs.http_user_agent = _op_ref
oxs.http_referer = _op_ref