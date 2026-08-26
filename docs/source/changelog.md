# Changelog

## Version 0.13.1 (2026-08-26)

- 🐛 Deleted zero length geometries
- 🐛 Accounted for all edge cases of bike network components, tested on 403 cities
- 🐛 Added length check for snapped seed points
- ♻️ Simplified `_update_seed_points_with_existing_bike_network()`
- ♻️ Moved `allow_edge_overlaps` to settings
- 📝 Added css for docs dataframes and polished docs
- 📝 Added usage docs 6 and 7, completing docs

## Version 0.13.0 (2026-08-14)

- 🐛 Changed street network to growable network
- 🐛 Removed isolated seed points
- ✨ Added custom filter constants
- 🎨 Polished settings, especially with CRS
- ✨ Added silent setting
- ✨ Added script for video generation
- 🎨 Improved exported data, implemented RFC7946 for geojson
- ♻️ Renamed several parameters and functions
- ⬆️ Added Python 3.13 and 3.14 support
- ➕ Added scipy dependency
- 📝 Added and polished usage docs

## Version 0.12.0 (2026-08-05)

- ✨ Implemented point and trip data import with weighted growth
- 📝 Added and polished several usage docs
- ♻️ Renamed many variables, functions, and added underscores for internal ones
- 📈 Overhauled plot creation
- 👷 Added pytest-mpl for plot testing
- 👷 Added codecov
- 🐛 Updated docs and code with warnings to ensure key 0 edges
- 👷 Removed unused release-please
- ✅ Removed online tests temporarily
- 📝 Fixed docs source variable, added edit button and key navigation

## Version 0.11.1 (2026-07-17)

- 🐛 Fixed validate seed point bug
- 🐛 Fixed loading of docs modules
- ♻️ Refactored import_files via defaultdict

## Version 0.11.0 (2026-06-29)

- ✨ Implemented bike network import
- ✨ Added minimum component length filter for bike net seed points
- ♻️ Refactored all imported files into one dict parameter
- ♻️ Refactored settings and constants into their own modules
- ✨ Added auto option for existing_network_spacing
- 📝 Added changelog to docs
- 📝 Deployed docs on new custom URL

## Version 0.10.3 (2026-06-17)

- ➖ Removed unneeded dependencies
- 📌 Pinned dependencies consistently
- 🔥 Removed video code, temporarily

## Version 0.10.2 (2026-06-17)

- 🐛 Fixed wrong street network definition "all_public", to "drive"
- 🐛 Fixed existing bike net not being usable with street net file
- 📝 Added more usage docs

## Version 0.10.1 (2026-06-15)

- 🐛 Added missing checks for seed_point_tags
- 📝 Added first usage docs
- ♻️ Renamed seed_points_file parameter for consistency

## Version 0.10.0 (2026-06-11)

- ✨ Added auto options for seed points
- ♻️ Refactored code: parameter validation
- ✨ Added triangular grid
- ✨ Added quadrangulation
- 🎨 Renamed variables for better readability

## Version 0.9.0 (2026-06-09)

- ✨ Added import from file for street network and seed points
- ✨ Added custom and preset tags: rail, school, park
- 📝 Polished docstrings
- ✅ Add test cases and examples


## Version 0.8.1 (2026-06-06)

- 🐛 Fixed custom filter
- 📝 Polished docs and user feedback
- ➖ Removed unneeded dependencies from env files


## Version 0.8.0 (2026-05-24)

- 📝 Big docs update: Added content to all pages, with furo style
- 📝 Cleaned up readme: Moved install info to docs, removed bloat, added funders
- 🐛 Fixed edge overlap removal
- 💄 Added polished tqdm progress bars
- 🐛 Fixed and refactored data retrieval via polygon
- 🐛 Fixed failing docs
- ➖ Removed unneeded dependencies from env files


## Version 0.7.1 (2026-05-04)

- 🧹 Make edge overlap removal ~5x faster


## Version 0.7.0 (2026-05-04)

- 🆕 Added option to grow from existing bicycle network
- 🆕 Added option to fetch data from OSM via shape file
- 🆕 Export to GPKG or GeoJSON
- 🐛 Fixed and polished precommit hooks
- 🧹 Update folder structure for results
- 🆕 Export seed points and city boundary too
- 💾 Round exported coordinates for smaller file sizes
- 🧹 Removed "all" ranking option


## Version 0.6.0 (2026-04-28)

- 🔧 Bug fix for metric calculation
- ⬆️ Implemented delaunay triangulation for performance improvements
- ⬆️ Improved readme to distuingish between use/development


## Version 0.5.2 (2026-04-10)

- ✨ Initial release ✨
- 🔧 Full reimplementation of code from paper "Growing Urban Bicycle Networks" https://github.com/mszell/bikenwgrowth
- ⬆️ Automated testing via pytest as well as pipeline for package deployment to pip
