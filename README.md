# GrowBikeNet

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

Source code for the project *GrowBikeNet*, building on [the code from the research paper](https://github.com/mszell/bikenwgrowth) *Growing Urban Bicycle Networks*.

## Installation
To install and use the code, you need to have installed [JupyterLab](https://pypi.org/project/jupyterlab/).

First clone the repository:

```
git clone https://github.com/BikeNetKit/GrowBikeNet.git
```

Go to the cloned folder and create a new virtual environment, see below. 

### Installation with pixi

Installation with [`pixi`](https://pixi.prefix.dev/latest/) is fastest and most stable. Setup a new virtual environment using the `environment.yml` file:

```
pixi init --import environment.yml
```

Now build the environment and run it:

```
pixi run jupyter lab
```

An instance of Jupyter lab is automatically going to open in your browser after the environment is built.

### Installation with pip/mamba/conda

Alternatively, use pip, or [`mamba`](https://mamba.readthedocs.io/en/latest/index.html) (or `conda`, which is slower).

<details><summary>Instructions</summary>

You can either create a new virtual environment then install the necessary dependencies with `pip` using the `requirements.txt` file:

```
pip install -r requirements.txt
```

Or create a new environment with the dependencies with `conda` or [`mamba`](https://mamba.readthedocs.io/en/latest/index.html) using the `environment.yml` file:

```
mamba env create -f environment.yml
```
Then, install the virtual environment's kernel in Jupyter:

```
mamba activate growbikenet
ipython kernel install --user --name=growbikenet
mamba deactivate
```

You can now run `jupyter lab` with kernel `growbikenet` (Kernel > Change Kernel > growbikenet).
</details>

## Repository structure

```
├── growbikenet             <- Packaged functions and visualizations
├── tests                   <- tests to execute to ensure functionality
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


