=============
Installation
=============

The easy way
~~~~~~~~~~~~

The currently default way to install GrowBikeNet is using pip:

::

   pip install growbikenet

If this does not work, follow the instructions below.

Advanced installations
~~~~~~~~~~~~~~~~~~~~~~

The main step is to set up a virtual environment ``gbnenv`` in which to
install the package, and then to use or run the environment. Use either of the methods below.

With conda/pip
^^^^^^^^^^^^^^

Installation with `conda <https://docs.conda.io/projects/conda/en/latest/index.html>`__ (or the faster `mamba <https://mamba.readthedocs.io/en/latest/index.html>`__).

The conda-forge installation is not yet working. Therefore, you need to `clone the
repository <https://github.com/BikeNetKit/growbikenet/archive/refs/heads/main.zip>`__
and create the environment via the
``environment.yml`` file:

::

   conda env create --file environment.yml
   conda activate gbnenv
   pip install growbikenet


With Pixi
^^^^^^^^^

Installation with `Pixi <https://pixi.prefix.dev/latest/>`__.

First, `clone this
repository <https://github.com/BikeNetKit/growbikenet/archive/refs/heads/main.zip>`__
and create the environment via the
``environment.yml`` file:

::

   pixi init --import environment.yml

At this point you can run growbikenet in the environment, for example as
such:

::

   pixi run python examples/mwe.py

..

   | The first time you run code with Pixi, it might take a minute
     longer, as Pixi resolves the environment’s dependencies only at
     this point.


Run growbikenet in Jupyter lab
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After having set up the environment above, if you wish to run
growbikenet via `JupyterLab <https://pypi.org/project/jupyterlab/>`__,
follow the corresponding instructions below.

With conda
^^^^^^^^^^

Using `conda <https://docs.conda.io/projects/conda/en/latest/index.html>`__ (or the faster `mamba <https://mamba.readthedocs.io/en/latest/index.html>`__), run:

::

   conda activate gbnenv
   ipython kernel install --user --name=gbnenv
   conda deactivate
   jupyter lab

Once Jupyter lab opens, switch the kernel (Kernel > Change Kernel >
gbnenv)

With pip
^^^^^^^^

Using pip, run:

::

   pip install --user ipykernel
   python -m ipykernel install --user --name=gbnenv
   jupyter lab

Once Jupyter lab opens, switch the kernel (Kernel > Change Kernel >
gbnenv)


With Pixi
^^^^^^^^^

Running growbikenet in Jupter lab with
`Pixi <https://pixi.prefix.dev/latest/>`__ is straightforward:

::

   pixi run jupyter lab

An instance of Jupyter lab is automatically going to open in your
browser after the environment is built.

Development installation
~~~~~~~~~~~~~~~~~~~~~~~~

If you want to develop the project, `clone this
repository <https://github.com/BikeNetKit/growbikenet/archive/refs/heads/main.zip>`__
and create the environment via the
``environment-dev.yml`` file:

::

   pixi init --import environment-dev.yml

The development environment is called ``gbnenvdev``. Make sure to also
read `our contribution
guidelines <https://github.com/BikeNetKit/GrowBikeNet?tab=contributing-ov-file#contributing-to-bikenetkit>`__.
