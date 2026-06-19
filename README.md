# Bike Net Kit / Grow Bike Net

[![Docs](https://github.com/BikeNetKit/GrowBikeNet/actions/workflows/docs.yml/badge.svg)](https://bikenetkit.github.io/GrowBikeNet/)
[![Test](https://github.com/BikeNetKit/GrowBikeNet/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/BikeNetKit/GrowBikeNet/actions/workflows/test.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/growbikenet)](https://pypi.org/project/growbikenet/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Human created](https://raw.githubusercontent.com/BikeNetKit/.github/refs/heads/main/profile/_static/badge_humancreated.svg)

The Python package `growbikenet` grows an urban bicycle network from scratch or from an existing bicycle network. 

The software downloads and pre-processes data from OpenStreetMap, prepares seed points to connect, runs simulations, saves the results, creates plots and videos. The source code builds on [the code from the research paper](https://github.com/mszell/bikenwgrowth) _Growing Urban Bicycle Networks_ and on [the code from the research paper](https://github.com/pietrofolco/Data-driven_bicycle_network_planning_for_demand_and_safety) _Data-driven micromobility network planning for demand and safety_.

**Publication** (primary): [https://doi.org/10.1038/s41598-022-10783-y](https://doi.org/10.1038/s41598-022-10783-y)  
**Publication** (secondary): [https://doi.org/10.1177/23998083221135611](https://doi.org/10.1177/23998083221135611)

## Installation

### The easy way

The best way to install GrowBikeNet is using [`conda`](https://docs.conda.io/projects/conda/en/latest/index.html) (or the faster [`mamba`](https://mamba.readthedocs.io/en/latest/index.html)) via the `conda-forge` channel:

```
conda install -c conda-forge growbikenet
```

### Advanced and development installations
For more installation options, see our [Installation docs](https://bikenetkit.github.io/GrowBikeNet/installation/).

## Usage
We provide a minimum working example in two formats:

- Python script ([examples/mwe.py](examples/mwe.py))
- Jupyter notebook ([examples/mwe.ipynb](examples/mwe.ipynb))

For a walkthrough with illustrative examples, see our [Usage docs](https://bikenetkit.github.io/GrowBikeNet/usage/).

## Docs
Find more information in our docs: [https://bikenetkit.github.io/GrowBikeNet/](https://bikenetkit.github.io/GrowBikeNet/)


## Supported by
Development of BikeNetKit/GrowBikeNet was supported by the [Innovation Fund Denmark](https://innovationsfonden.dk/en), the EU HORIZON project [JUST STREETS](https://www.just-streets.eu), and the [Data Science Section](https://en.itu.dk/Research/Sections-and-research-groups/Data-Science) of IT University of Copenhagen.


[![Innovation Fund Denmark](https://raw.githubusercontent.com/BikeNetKit/.github/refs/heads/main/profile/_static/logo_innovationfund.png)](https://innovationsfonden.dk/en) &emsp;&emsp; [![European Union](https://raw.githubusercontent.com/BikeNetKit/.github/refs/heads/main/profile/_static/logo_eu.png)](https://commission.europa.eu/index_en) &ensp; [![JUST STREETS](https://raw.githubusercontent.com/BikeNetKit/.github/refs/heads/main/profile/_static/logo_juststreets.png)](https://www.just-streets.eu/) 


