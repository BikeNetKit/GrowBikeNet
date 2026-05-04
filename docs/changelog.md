# Changelog

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
