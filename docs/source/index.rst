.. GrowBikeNet documentation master file, created by
   sphinx-quickstart on Thu Feb 12 15:01:19 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GrowBikeNet |version| documentation
===================================

The Python package `growbikenet` grows an urban bicycle network from scratch or from an existing bicycle network. It is hosted on `Github <https://github.com/BikeNetKit/GrowBikeNet>`__, part of `BikeNetKit <https://bikenetkit.org>`__.

The software downloads and pre-processes data from OpenStreetMap,
prepares seed points to connect, runs simulations, saves the results,
create plots and videos. The source code builds on `the code from the
research paper <https://github.com/mszell/bikenwgrowth>`__ *Growing
Urban Bicycle Networks* and on `the code from the research
paper <https://github.com/pietrofolco/Data-driven_bicycle_network_planning_for_demand_and_safety>`__
*Data-driven micromobility network planning for demand and safety*.


Setup and use
-------------

To set up GrowBikeNet, see the :doc:`installation` page.
To use GrowBikeNet, the :doc:`getting_started` page
is a good place to start, which also explains how the package works in detail. For technical documentation, consult the :doc:`reference_user`.

.. Statement of need
.. =================

.. TBA

How to cite
-----------

If you use `growbikenet` in your research, please cite the paper `doi:10.1038/s41598-022-10783-y <https://doi.org/10.1038/s41598-022-10783-y>`__:

    M. Szell, S. Mimar, T. Perlman, G. Ghoshal, R. Sinatra. Growing urban bicycle networks. Scientific Reports 12, 6765 (2022). https://doi.org/10.1038/s41598-022-10783-y

Contributing
------------

If you want to contribute to the development of GrowBikeNet, please read the
`CONTRIBUTING.md <https://github.com/BikeNetKit/GrowBikeNet?tab=contributing-ov-file#contributing-to-bikenetkit>`__
file.

Supported by
------------

Development of BikeNetKit/GrowBikeNet was supported by the Innovation Fund Denmark
and the EU HORIZON grant JUST STREETS.

|Innovation Fund Denmark|   |European Union|  |JUST STREETS|

.. |Innovation Fund Denmark| image:: _static/logo_innovationfund.png
   :target: https://innovationsfonden.dk/en
.. |European Union| image:: _static/logo_eu.png
   :target: https://commission.europa.eu/index_en
.. |JUST STREETS| image:: _static/logo_juststreets.png
   :target: https://www.just-streets.eu/


Documentation contents
----------------------

.. toctree::
   :maxdepth: 1

   Home <self>
   installation
   getting_started
   reference_user
   reference_developer
   references
