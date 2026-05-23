=============
Installation
=============

The easy way
~~~~~~~~~~~~

The currently best way to install GrowBikeNet is using pip:

::

   pip install growbikenet

.. raw:: html

   <!-- > [!IMPORTANT]  
   > As of 2026-05-04, the conda-forge installation is not yet working. We will remove this note once it works.

   The best way to install GrowBikeNet is using [`conda`](https://docs.conda.io/projects/conda/en/latest/index.html) and the `conda-forge` channel:

   ```
   conda install -c conda-forge growbikenet
   ``` -->

Advanced installations
~~~~~~~~~~~~~~~~~~~~~~

Set up environment
^^^^^^^^^^^^^^^^^^

The main step is to set up a virtual environment ``gbnenv`` in which to
install the package, and then to use or run the environment.

With Pixi
'''''''''

Installation with ```Pixi`` <https://pixi.prefix.dev/latest/>`__ is
fastest and most stable:

::

   pixi init gbnenv
   pixi add --pypi growbikenet

At this point you can run growbikenet in the environment, for example as
such:

::

   pixi run python examples/mwe.py

..

   | [!NOTE]
   | The first time you run code with Pixi, it might take a minute
     longer, as Pixi resolves the environment’s dependencies only at
     this point.

*Alternatively*, or if you run into issues, `clone this
repository <https://github.com/BikeNetKit/growbikenet/archive/refs/heads/main.zip>`__
and create the environment via the
```environment.yml`` <environment.yml>`__ file:

::

   pixi init --import environment.yml

With mamba/conda/pip
''''''''''''''''''''

Alternatively to Pixi, use
```mamba`` <https://mamba.readthedocs.io/en/latest/index.html>`__ or
```conda`` <https://docs.conda.io/projects/conda/en/latest/index.html>`__.

.. raw:: html

   <details>

.. raw:: html

   <summary>

Instructions

.. raw:: html

   </summary>

..

   | [!IMPORTANT]
   | As of 2026-05-04, the conda-forge installation is not yet working.
     We will remove this note once it works.

::

   mamba create -n gbnenv -c conda-forge growbikenet
   mamba activate gbnenv

*Alternatively*, or if you run into issues, `clone this
repository <https://github.com/BikeNetKit/growbikenet/archive/refs/heads/main.zip>`__
and create the environment via the
```environment.yml`` <environment.yml>`__ file:

::

   mamba env create --file environment.yml
   mamba activate gbnenv
   pip install growbikenet

.. raw:: html

   </details>

Run growbikenet in Jupyter lab
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After having set up the environment above, if you wish to run
growbikenet via `JupyterLab <https://pypi.org/project/jupyterlab/>`__,
follow the

.. raw:: html

   <details>

.. raw:: html

   <summary>

Instructions

.. raw:: html

   </summary>

.. _with-pixi-1:

With Pixi
^^^^^^^^^

Running growbikenet in Jupter lab with
```Pixi`` <https://pixi.prefix.dev/latest/>`__ is straightforward:

::

   pixi run jupyter lab

An instance of Jupyter lab is automatically going to open in your
browser after the environment is built.

With mamba/conda
^^^^^^^^^^^^^^^^

Using mamba/conda, run:

::

   mamba activate gbnenv
   ipython kernel install --user --name=gbnenv
   mamba deactivate
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

.. raw:: html

   </details>

Development installation
------------------------

If you want to develop the project, `clone this
repository <https://github.com/BikeNetKit/growbikenet/archive/refs/heads/main.zip>`__
and create the environment via the
```environment-dev.yml`` <environment-dev.yml>`__ file:

::

   pixi init --import environment-dev.yml

The developemt environment is called ``gbnenvdev``. Make sure to also
read `our contribution
guidelines <https://github.com/BikeNetKit/FixBikeNet?tab=contributing-ov-file>`__.
