# Bike Net Kit / Grow Bike Net

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Docs](https://github.com/BikeNetKit/GrowBikeNet/actions/workflows/docs.yml/badge.svg)](https://github.com/BikeNetKit/GrowBikeNet/actions/workflows/docs.yml)
[![Test](https://github.com/BikeNetKit/GrowBikeNet/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/BikeNetKit/GrowBikeNet/actions/workflows/test.yml)

The Python package `growbikenet` grows an urban bicycle network from scratch or from an existing bicycle network. 

The software downloads and pre-processes data from OpenStreetMap, prepares seed points to connect, runs simulations, saves the results, create plots and videos. The source code builds on [the code from the research paper](https://github.com/mszell/bikenwgrowth) _Growing Urban Bicycle Networks_ and on [the code from the research paper](https://github.com/pietrofolco/Data-driven_bicycle_network_planning_for_demand_and_safety) _Data-driven micromobility network planning for demand and safety_.

**Publication** (primary): [https://doi.org/10.1038/s41598-022-10783-y](https://doi.org/10.1038/s41598-022-10783-y)  
**Publication** (secondary): [https://doi.org/10.1177/23998083221135611](https://doi.org/10.1177/23998083221135611)

## Installation

### The easy way

The currently best way to install GrowBikeNet is using pip:

```
pip install growbikenet
```

<!-- > [!IMPORTANT]  
> As of 2026-05-04, the conda-forge installation is not yet working. We will remove this note once it works.

The best way to install GrowBikeNet is using [`conda`](https://docs.conda.io/projects/conda/en/latest/index.html) and the `conda-forge` channel:

```
conda install -c conda-forge growbikenet
``` -->

If this does not work, consult our [installation docs](https://bikenetkit.github.io/GrowBikeNet/usage/installation/).

### Advanced and development installations
 See our [installation docs](https://bikenetkit.github.io/GrowBikeNet/usage/installation/) for details.

## Usage
We provide a minimum working example in two formats:

- Python script ([examples/mwe.py](examples/mwe.py))
- Jupyter notebook ([examples/mwe.ipynb](examples/mwe.ipynb))

## Docs
Find more information in our docs: https://bikenetkit.github.io/GrowBikeNet/

## Repository structure
```
├── growbikenet             <- Packaged functions and visualizations
├── tests                   <- Tests to execute to ensure functionality
├── .gitignore              <- Files and folders ignored by git
├── .pre-commit-config.yaml <- Pre-commit hooks used
├── README.md
├── environment.yml         <- Environment file to set up the environment using conda/mamba/pixi
```

## Supported by
Development of BikeNetKit/GrowBikeNet was supported by the Innovation Fund Denmark and the EU HORIZON grant JUST STREETS.

[![Innovation Fund Denmark](https://raw.githubusercontent.com/BikeNetKit/GrowBikeNet/tree/main/docs/_static/logo_innovationfund.png)](https://innovationsfonden.dk/en) [![European Union](https://raw.githubusercontent.com/BikeNetKit/GrowBikeNet/tree/main/docs/_static/logo_eu.png)](https://commission.europa.eu/index_en) [![JUST STREETS](https://raw.githubusercontent.com/BikeNetKit/GrowBikeNet/tree/main/docs/_static/logo_juststreets.png)](https://www.just-streets.eu/) 


