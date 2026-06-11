# Changelog

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
