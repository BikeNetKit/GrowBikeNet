# GrowBikeNet

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Docs](https://github.com/BikeNetKit/GrowBikeNet/actions/workflows/docs.yml/badge.svg)](https://github.com/BikeNetKit/GrowBikeNet/actions/workflows/docs.yml)
[![Test](https://github.com/BikeNetKit/GrowBikeNet/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/BikeNetKit/GrowBikeNet/actions/workflows/test.yml)

Source code for the project _GrowBikeNet_, building on [the code from the research paper](https://github.com/mszell/bikenwgrowth) _Growing Urban Bicycle Networks_.

## Installation

### Set up environment

The main step is to set up a virtual environment `gbnenv` in which to install the package, and then to use or run the environment.

#### With Pixi

Installation with [`Pixi`](https://pixi.prefix.dev/latest/) is fastest and most stable:

```
pixi init gbnenv
pixi add --pypi growbikenet
```

At this point you can run growbikenet in the environment, for example as such:

```
pixi run python examples/mwe.py
```

> [!NOTE]  
> The first time you run code with Pixi, it might take a minute longer, as Pixi resolves the environment's dependencies only at this point.

_Alternatively_, or if you run into issues, [clone this repository](https://github.com/BikeNetKit/growbikenet/archive/refs/heads/main.zip) and create the environment via the [`environment.yml`](environment.yml) file:

```
pixi init --import environment.yml
```

#### With mamba/conda/pip

Alternatively to Pixi, use [`mamba`](https://mamba.readthedocs.io/en/latest/index.html) or [`conda`](https://docs.conda.io/projects/conda/en/latest/index.html).

<details><summary>Instructions</summary>

```
mamba create -n gbnenv -c conda-forge growbikenet
mamba activate gbnenv
```

_Alternatively_, or if you run into issues, [clone this repository](https://github.com/BikeNetKit/growbikenet/archive/refs/heads/main.zip) and create the environment via the [`environment.yml`](environment.yml) file:

```
mamba env create --file environment.yml
mamba activate gbnenv
pip install growbikenet
```

</details>

### Run growbikenet in Jupyter lab

After having set up the environment above, if you wish to run growbikenet via [JupyterLab](https://pypi.org/project/jupyterlab/), follow the

<details><summary>Instructions</summary>
#### With Pixi
Running growbikenet in Jupter lab with [`Pixi`](https://pixi.prefix.dev/latest/) is straightforward:

```
pixi run jupyter lab
```

An instance of Jupyter lab is automatically going to open in your browser after the environment is built.

#### With mamba/conda

Using mamba/conda, run:

```
mamba activate gbnenv
ipython kernel install --user --name=gbnenv
mamba deactivate
jupyter lab
```

Once Jupyter lab opens, switch the kernel (Kernel > Change Kernel > gbnenv)

#### With pip

Using pip, run:

```
pip install --user ipykernel
python -m ipykernel install --user --name=gbnenv
jupyter lab
```

Once Jupyter lab opens, switch the kernel (Kernel > Change Kernel > gbnenv)

</details>

## Development installation

If you want to develop the project, [clone this repository](https://github.com/BikeNetKit/growbikenet/archive/refs/heads/main.zip) and create the environment via the [`environment-dev.yml`](environment-dev.yml) file:

```
pixi init --import environment-dev.yml
```

The developemt environment is called `gbnenvdev`. Make sure to also read [our contribution guidelines](CONTRIBUTING.md).

## Usage

We provide a minimum working example in two formats:

- Python script ([examples/mwe.py](examples/mwe.py))
- Jupyter notebook ([examples/mwe.ipynb](examples/mwe.ipynb))

## Repository structure

```
├── growbikenet             <- Packaged functions and visualizations
├── tests                   <- Tests to execute to ensure functionality
├── .gitignore              <- Files and folders ignored by git
├── .pre-commit-config.yaml <- Pre-commit hooks used
├── README.md
├── environment.yml         <- Environment file to set up the environment using conda/mamba/pixi
```

## Credits

<!--Please cite as:
>AUTHOR1, AUTHOR2, and AUTHOR3, PROJECTNAME, JOURNAL (YYYY), DOIURL
-->

Development of GrowBikeNet was supported by the Danish Innovation Fund (Innovationsfonden).
